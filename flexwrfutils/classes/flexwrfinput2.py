from typing import TextIO, Any, List, Union
from pathlib import Path
import numpy as np
from datetime import datetime
import pandas as pd


class BaseArgument:
    def __init__(self, type=None, dummyline=None):
        self._type = type
        self._dummyline = dummyline
        self._value = None

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = self._type(value)

    def read(self, file: TextIO):
        line = file.readline()
        self.value = self.linecaster(line)

    def linecaster(self, line: str) -> Any:
        decoded_line = self._type(line.strip().split(" ")[0])
        return decoded_line


class StaticArgument(BaseArgument):
    @property
    def line(self):
        return self._dummyline.replace("#", str(self._value))


class DynamicArgument(BaseArgument):
    def __init__(self, type=None, dummyline=None):
        super().__init__(type, dummyline)
        self._n_values = 0
        self._value: List[self._type] = []

    def __len__(self):
        return len(self._value)

    def readline(self, file: TextIO):
        line = file.readline()
        self.append(self.linecaster(line))

    def read(self, file: TextIO, n_values):
        for i in range(n_values):
            line = file.readline()
            self.append(self.linecaster(line))

    @property
    def lines(self):
        lines = [self._dummyline.replace("#", str(value)) for value in self._value]
        return lines

    def append(self, value):
        self._value.append(value)
        self._n_values += 1

    def remove(self, index):
        self._value.remove(self.value[-1])
        self._n_values -= 1


class DatetimeArgument(StaticArgument):
    def __init__(self, dummyline=None):
        super().__init__(dummyline)
        self.time = str

    def linecaster(self, line: str) -> str:
        decoded_line = line.strip().split(" ")[:2]
        decoded_line = f"{decoded_line[0]} {decoded_line[1]}"
        return decoded_line

    @StaticArgument.value.setter
    def value(self, value: Union[str, np.datetime64, datetime]) -> str:
        if isinstance(value, str):
            self._value = value
        elif isinstance(value, np.datetime64):
            value = pd.to_datetime(value)
            value = value.strftime("%Y%m%d %H%M%S")
            self._value = value
        elif isinstance(value, datetime):
            value = value.strftime("%Y%m%d %H%M%S")
            self._value = value


class StaticSpecifierArgument(StaticArgument):
    def __init__(self, type=None, dummyline=None):
        super().__init__(type, dummyline)
        self._type = int
        self.children = []


class DynamicSpecifierArgument(BaseArgument):
    def __init__(
        self,
        specifier: StaticSpecifierArgument,
        type=None,
        dummyline=None,
    ):
        super().__init__(type, dummyline)
        self.specifier = specifier
        self._value: List[self._type] = []

    def __len__(self):
        return len(self._value)

    def readline(self, file: TextIO):
        line = file.readline()
        self.append(self.linecaster(line))

    def read(self, file: TextIO):
        n_values = self.specifier.value
        for i in range(n_values):
            line = file.readline()
            self._value.append(self.linecaster(line))

    @property
    def lines(self):
        lines = [self._dummyline.replace("#", str(value)) for value in self._value]
        return lines

    def append(self, value):
        self._value.append(value)
        self.specifier.value = len(self._value)

    def remove(self, index):
        self._value.remove(self.value[index])
        self.specifier.value = len(self._value)


#####################################
####### Actual Option Classes #######
#####################################


class Pathnames:
    def __init__(self):
        self._outputpath = StaticArgument(type=Path, dummyline="#/\n")
        self._inputpath = DynamicArgument(type=Path, dummyline="#/\n")
        self._availablepath = DynamicArgument(type=Path, dummyline="#/\n")

    def read(self, f: TextIO):
        f.readline()
        self.outputpath.read(f)
        while "====" not in self.peek_line(f):
            self.inputpath.readline(f)
            self.availablepath.readline(f)
        f.readline()

    @staticmethod
    def peek_line(f: TextIO):
        pos = f.tell()
        line = f.readline()
        f.seek(pos)
        return line

    @property
    def outputpath(self):
        return self._outputpath

    @outputpath.setter
    def outputpath(self, value):
        self.outputpath.value = value

    @property
    def inputpath(self):
        return self._inputpath

    @inputpath.setter
    def inputpath(self, value):
        self.inputpath.value = value

    @property
    def availablepath(self):
        return self._availablepath

    @availablepath.setter
    def availablepath(self, value):
        self.availablepath.value = value


class Command:
    def __init__(self):
        self._ldirect = StaticArgument(
            type=int,
            dummyline="    #                LDIRECT:          1 for forward simulation, -1 for backward simulation\n",
        )
        self._start = DatetimeArgument(
            dummyline="    #  YYYYMMDD HHMISS   beginning date of simulation\n"
        )
        self._stop = DatetimeArgument(
            dummyline="    #  YYYYMMDD HHMISS   beginning date of simulation\n"
        )
        self._outputrate = StaticArgument(
            type=int,
            dummyline="    #             SSSSS  (int)      output every SSSSS seconds\n",
        )
        self._averagerate = StaticArgument(
            type=int,
            dummyline="    #             SSSSS  (int)      time average of output (in SSSSS seconds)\n",
        )
        self._samplingrate = StaticArgument(
            type=int,
            dummyline="    #              SSSSS  (int)      sampling rate of output (in SSSSS seconds)\n",
        )
        self._splittingtime = StaticArgument(
            type=int,
            dummyline="    #        SSSSS  (int)      time constant for particle splitting (in seconds)\n",
        )
        self._syncronizationinterval = StaticArgument(
            type=int,
            dummyline="    #              SSSSS  (int)      synchronisation interval of flexpart (in seconds)\n",
        )
        self._ctl = StaticArgument(
            type=float,
            dummyline="    #.              CTL    (real)     factor by which time step must be smaller than tl\n",
        )
        self._ifine = StaticArgument(
            type=int,
            dummyline="    #               IFINE  (int)      decrease of time step for vertical motion by factor ifine\n",
        )
        self._iout = StaticArgument(
            type=int,
            dummyline="    #                IOUT              1 concentration, 2 mixing ratio, 3 both, 4 plume traject, 5=1+4\n",
        )
        self._ipout = StaticArgument(
            type=int,
            dummyline="    #                IPOUT             particle dump: 0 no, 1 every output interval, 2 only at end\n",
        )
        self._lsubgrid = StaticArgument(
            type=int,
            dummyline="    #                LSUBGRID          subgrid terrain effect parameterization: 1 yes, 0 no\n",
        )
        self._lconvection = StaticArgument(
            type=int,
            dummyline="    #                LCONVECTION       convection: 3 yes, 0 no\n",
        )
        self._dtconv = StaticArgument(
            type=float,
            dummyline="    #.            DT_CONV  (real)   time interval to call convection, seconds\n",
        )
        self._lagespectra = StaticArgument(
            type=int,
            dummyline="    #                LAGESPECTRA       age spectra: 1 yes, 0 no\n",
        )
        self._ipin = StaticArgument(
            type=int,
            dummyline="    #                IPIN              continue simulation with dumped particle data: 1 yes, 0 no\n",
        )
        self._iflux = StaticArgument(
            type=int,
            dummyline="    #                IFLUX             calculate fluxes: 1 yes, 0 no\n",
        )
        self._ioutputforeachrel = StaticArgument(
            type=int,
            dummyline="    #                IOUTPUTFOREACHREL CREATE AN OUPUT FILE FOR EACH RELEASE LOCATION: 1 YES, 0 NO\n",
        )
        self._mdomainfill = StaticArgument(
            type=int,
            dummyline="    #                MDOMAINFILL       domain-filling trajectory option: 1 yes, 0 no, 2 strat. o3 tracer\n",
        )
        self._indsource = StaticArgument(
            type=int,
            dummyline="    #                IND_SOURCE        1=mass unit , 2=mass mixing ratio unit\n",
        )
        self._indreceptor = StaticArgument(
            type=int,
            dummyline="    #                IND_RECEPTOR      1=mass unit , 2=mass mixing ratio unit\n",
        )
        self._nestedoutput = StaticArgument(
            type=int,
            dummyline="    #                NESTED_OUTPUT     shall nested output be used? 1 yes, 0 no\n",
        )
        self._linitcond = StaticArgument(
            type=int,
            dummyline="    #                LINIT_COND   INITIAL COND. FOR BW RUNS: 0=NO,1=MASS UNIT,2=MASS MIXING RATIO UNIT\n",
        )
        self._turboption = StaticArgument(
            type=int,
            dummyline="    #                TURB_OPTION       0=no turbulence; 1=diagnosed as in flexpart_ecmwf; 2 and 3=from tke.\n",
        )
        self._luoption = StaticArgument(
            type=int,
            dummyline="    #                LU_OPTION         0=old landuse (IGBP.dat); 1=landuse from WRF\n",
        )
        self._cblscheme = StaticArgument(
            type=int,
            dummyline="    #                CBL SCHEME        0=no, 1=yes. works if TURB_OPTION=1\n",
        )
        self._sfcoption = StaticArgument(
            type=int,
            dummyline="    #                SFC_OPTION        0=default computation of u*, hflux, pblh, 1=from wrf\n",
        )
        self._windoption = StaticArgument(
            type=int,
            dummyline="    #                WIND_OPTION       0=snapshot winds, 1=mean winds,2=snapshot eta-dot,-1=w based on divergence\n",
        )
        self._timeoption = StaticArgument(
            type=int,
            dummyline="    #                TIME_OPTION       1=correction of time validity for time-average wind,  0=no need\n",
        )
        self._outgridcoord = StaticArgument(
            type=int,
            dummyline="    #                OUTGRID_COORD     0=wrf grid(meters), 1=regular lat/lon grid\n",
        )
        self._releasecoord = StaticArgument(
            type=int,
            dummyline="    #                RELEASE_COORD     0=wrf grid(meters), 1=regular lat/lon grid\n",
        )
        self._iouttype = StaticArgument(
            type=int,
            dummyline="    #                IOUTTYPE          0=default binary, 1=ascii (for particle dump only),2=netcdf\n",
        )
        self._nctimerec = StaticArgument(
            type=int,
            dummyline="    #                NCTIMEREC (int)   Time frames per output file, only used for netcdf\n",
        )
        self._verbose = StaticArgument(
            type=int,
            dummyline="    #                VERBOSE           VERBOSE MODE,0=minimum, 100=maximum\n",
        )

    def read(self, f: TextIO):
        f.readline()
        self.ldirect.read(f)
        self.start.read(f)
        self.stop.read(f)
        self.outputrate.read(f)
        self.averagerate.read(f)
        self.samplingrate.read(f)
        self.splittingtime.read(f)
        self.syncronizationinterval.read(f)
        self.ctl.read(f)
        self.ifine.read(f)
        self.iout.read(f)
        self.ipout.read(f)
        self.lsubgrid.read(f)
        self.lconvection.read(f)
        self.dtconv.read(f)
        self.lagespectra.read(f)
        self.ipin.read(f)
        self.iflux.read(f)
        self.ioutputforeachrel.read(f)
        self.mdomainfill.read(f)
        self.indsource.read(f)
        self.indreceptor.read(f)
        self.nestedoutput.read(f)
        self.linitcond.read(f)
        self.turboption.read(f)
        self.luoption.read(f)
        self.cblscheme.read(f)
        self.sfcoption.read(f)
        self.windoption.read(f)
        self.timeoption.read(f)
        self.outgridcoord.read(f)
        self.releasecoord.read(f)
        self.iouttype.read(f)
        self.nctimerec.read(f)
        self.verbose.read(f)

    @property
    def ldirect(self):
        return self._ldirect

    @ldirect.setter
    def ldirect(self, value):
        self.ldirect.value = value

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, value):
        self.start.value = value

    @property
    def stop(self):
        return self._stop

    @stop.setter
    def stop(self, value):
        self.stop.value = value

    @property
    def outputrate(self):
        return self._outputrate

    @outputrate.setter
    def outputrate(self, value):
        self.outputrate.value = value

    @property
    def averagerate(self):
        return self._averagerate

    @averagerate.setter
    def averagerate(self, value):
        self.averagerate.value = value

    @property
    def samplingrate(self):
        return self._samplingrate

    @samplingrate.setter
    def samplingrate(self, value):
        self.samplingrate.value = value

    @property
    def splittingtime(self):
        return self._splittingtime

    @splittingtime.setter
    def splittingtime(self, value):
        self.splittingtime.value = value

    @property
    def syncronizationinterval(self):
        return self._syncronizationinterval

    @syncronizationinterval.setter
    def syncronizationinterval(self, value):
        self.syncronizationinterval.value = value

    @property
    def ctl(self):
        return self._ctl

    @ctl.setter
    def ctl(self, value):
        self.ctl.value = value

    @property
    def ifine(self):
        return self._ifine

    @ifine.setter
    def ifine(self, value):
        self.ifine.value = value

    @property
    def iout(self):
        return self._iout

    @iout.setter
    def iout(self, value):
        self.iout.value = value

    @property
    def ipout(self):
        return self._ipout

    @ipout.setter
    def ipout(self, value):
        self.ipout.value = value

    @property
    def lsubgrid(self):
        return self._lsubgrid

    @lsubgrid.setter
    def lsubgrid(self, value):
        self.lsubgrid.value = value

    @property
    def lconvection(self):
        return self._lconvection

    @lconvection.setter
    def lconvection(self, value):
        self.lconvection.value = value

    @property
    def dtconv(self):
        return self._dtconv

    @dtconv.setter
    def dtconv(self, value):
        self.dtconv.value = value

    @property
    def lagespectra(self):
        return self._lagespectra

    @lagespectra.setter
    def lagespectra(self, value):
        self.lagespectra.value = value

    @property
    def ipin(self):
        return self._ipin

    @ipin.setter
    def ipin(self, value):
        self.ipin.value = value

    @property
    def iflux(self):
        return self._iflux

    @iflux.setter
    def iflux(self, value):
        self.iflux.value = value

    @property
    def ioutputforeachrel(self):
        return self._ioutputforeachrel

    @ioutputforeachrel.setter
    def ioutputforeachrel(self, value):
        self.ioutputforeachrel.value = value

    @property
    def mdomainfill(self):
        return self._mdomainfill

    @mdomainfill.setter
    def mdomainfill(self, value):
        self.mdomainfill.value = value

    @property
    def indsource(self):
        return self._indsource

    @indsource.setter
    def indsource(self, value):
        self.indsource.value = value

    @property
    def indreceptor(self):
        return self._indreceptor

    @indreceptor.setter
    def indreceptor(self, value):
        self.indreceptor.value = value

    @property
    def nestedoutput(self):
        return self._nestedoutput

    @nestedoutput.setter
    def nestedoutput(self, value):
        self.nestedoutput.value = value

    @property
    def linitcond(self):
        return self._linitcond

    @linitcond.setter
    def linitcond(self, value):
        self.linitcond.value = value

    @property
    def turboption(self):
        return self._turboption

    @turboption.setter
    def turboption(self, value):
        self.turboption.value = value

    @property
    def luoption(self):
        return self._luoption

    @luoption.setter
    def luoption(self, value):
        self.luoption.value = value

    @property
    def cblscheme(self):
        return self._cblscheme

    @cblscheme.setter
    def cblscheme(self, value):
        self.cblscheme.value = value

    @property
    def sfcoption(self):
        return self._sfcoption

    @sfcoption.setter
    def sfcoption(self, value):
        self.sfcoption.value = value

    @property
    def windoption(self):
        return self._windoption

    @windoption.setter
    def windoption(self, value):
        self.windoption.value = value

    @property
    def timeoption(self):
        return self._timeoption

    @timeoption.setter
    def timeoption(self, value):
        self.timeoption.value = value

    @property
    def outgridcoord(self):
        return self._outgridcoord

    @outgridcoord.setter
    def outgridcoord(self, value):
        self.outgridcoord.value = value

    @property
    def releasecoord(self):
        return self._releasecoord

    @releasecoord.setter
    def releasecoord(self, value):
        self.releasecoord.value = value

    @property
    def iouttype(self):
        return self._iouttype

    @iouttype.setter
    def iouttype(self, value):
        self.iouttype.value = value

    @property
    def nctimerec(self):
        return self._nctimerec

    @nctimerec.setter
    def nctimerec(self, value):
        self.nctimerec.value = value

    @property
    def verbose(self):
        return self._verbose

    @verbose.setter
    def verbose(self, value):
        self.verbose.value = value


class Ageclasses:
    def __init__(self):
        self._nageclasses = StaticSpecifierArgument(
            dummyline="    #                NAGECLASS        number of age classes\n"
        )
        self._ageclasses = DynamicSpecifierArgument(
            self._nageclasses,
            type=int,
            dummyline="    #             SSSSSS  (int)    age class in SSSSS seconds\n",
        )

    def read(self, f):
        f.readline()
        self.nageclasses.read(f)
        self.ageclasses.read(f)

    @property
    def nageclasses(self):
        return self._nageclasses

    @nageclasses.setter
    def nageclasses(self, value):
        self.nageclasses.value = value

    @property
    def ageclasses(self):
        return self._ageclasses

    @ageclasses.setter
    def ageclasses(self, value):
        self.ageclasses.value = value


class Outgrid:
    def __init__(self):
        self._outlonleft = StaticArgument(
            type=float,
            dummyline="   #            OUTLONLEFT      geograhical longitude of lower left corner of output grid\n",
        )
        self._outlatlower = StaticArgument(
            type=float,
            dummyline="    #              OUTLATLOWER     geographical latitude of lower left corner of output grid\n",
        )
        self._numxgrid = StaticArgument(
            type=int,
            dummyline="    #               NUMXGRID        number of grid points in x direction (= # of cells )\n",
        )
        self._numygrid = StaticArgument(
            type=int,
            dummyline="    #               NUMYGRID        number of grid points in y direction (= # of cells )\n",
        )
        self._outgriddef = StaticArgument(
            type=int,
            dummyline="    #                OUTGRIDDEF      outgrid defined 0=using grid distance, 1=upperright corner coordinate\n",
        )
        self._dxoutlon = StaticArgument(
            type=float,
            dummyline="    #           DXOUTLON        grid distance in x direction or upper right corner of output grid\n",
        )
        self._dyoutlon = StaticArgument(
            type=float,
            dummyline="    #           DYOUTLON        grid distance in y direction or upper right corner of output grid\n",
        )
        self._numzgrid = StaticSpecifierArgument(
            dummyline="    #                NUMZGRID        number of vertical levels\n"
        )
        self._levels = DynamicSpecifierArgument(
            self._numzgrid, type=float, dummyline="height of level (upper boundary)\n"
        )

    def read(self, f: TextIO):
        f.readline()
        self.outlonleft.read(f)
        self.outlatlower.read(f)
        self.numxgrid.read(f)
        self.numygrid.read(f)
        self.outgriddef.read(f)
        self.dxoutlon.read(f)
        self.dyoutlon.read(f)
        self.numzgrid.read(f)
        self.levels.read(f)

    @property
    def outlonleft(self):
        return self._outlonleft

    @outlonleft.setter
    def outlonleft(self, value):
        self.outlonleft.value = value

    @property
    def outlatlower(self):
        return self._outlatlower

    @outlatlower.setter
    def outlatlower(self, value):
        self.outlatlower.value = value

    @property
    def numxgrid(self):
        return self._numxgrid

    @numxgrid.setter
    def numxgrid(self, value):
        self.numxgrid.value = value

    @property
    def numygrid(self):
        return self._numygrid

    @numygrid.setter
    def numygrid(self, value):
        self.numygrid.value = value

    @property
    def outgriddef(self):
        return self._outgriddef

    @outgriddef.setter
    def outgriddef(self, value):
        self.outgriddef.value = value

    @property
    def dxoutlon(self):
        return self._dxoutlon

    @dxoutlon.setter
    def dxoutlon(self, value):
        self.dxoutlon.value = value

    @property
    def dyoutlon(self):
        return self._dyoutlon

    @dyoutlon.setter
    def dyoutlon(self, value):
        self.dyoutlon.value = value

    @property
    def numzgrid(self):
        return self._numzgrid

    @numzgrid.setter
    def numzgrid(self, value):
        self.numzgrid.value = value

    @property
    def levels(self):
        return self._levels

    @levels.setter
    def levels(self, value):
        self.levels.value = value


class OutgridNest:
    def __init__(self):
        self._outlonleft = StaticArgument(
            type=float,
            dummyline="   #            OUTLONLEFT      geograhical longitude of lower left corner of output grid\n",
        )
        self._outlatlower = StaticArgument(
            type=float,
            dummyline="    #              OUTLATLOWER     geographical latitude of lower left corner of output grid\n",
        )
        self._numxgrid = StaticArgument(
            type=int,
            dummyline="    #               NUMXGRID        number of grid points in x direction (= # of cells )\n",
        )
        self._numygrid = StaticArgument(
            type=int,
            dummyline="    #               NUMYGRID        number of grid points in y direction (= # of cells )\n",
        )
        self._outgriddef = StaticArgument(
            type=int,
            dummyline="    #                OUTGRIDDEF      outgrid defined 0=using grid distance, 1=upperright corner coordinate\n",
        )
        self._dxoutlon = StaticArgument(
            type=float,
            dummyline="    #           DXOUTLON        grid distance in x direction or upper right corner of output grid\n",
        )
        self._dyoutlon = StaticArgument(
            type=float,
            dummyline="    #           DYOUTLON        grid distance in y direction or upper right corner of output grid\n",
        )

    def read(self, f: TextIO):
        f.readline()
        self.outlonleft.read(f)
        self.outlatlower.read(f)
        self.numxgrid.read(f)
        self.numygrid.read(f)
        self.outgriddef.read(f)
        self.dxoutlon.read(f)
        self.dyoutlon.read(f)

    @property
    def outlonleft(self):
        return self._outlonleft

    @outlonleft.setter
    def outlonleft(self, value):
        self.outlonleft.value = value

    @property
    def outlatlower(self):
        return self._outlatlower

    @outlatlower.setter
    def outlatlower(self, value):
        self.outlatlower.value = value

    @property
    def numxgrid(self):
        return self._numxgrid

    @numxgrid.setter
    def numxgrid(self, value):
        self.numxgrid.value = value

    @property
    def numygrid(self):
        return self._numygrid

    @numygrid.setter
    def numygrid(self, value):
        self.numygrid.value = value

    @property
    def outgriddef(self):
        return self._outgriddef

    @outgriddef.setter
    def outgriddef(self, value):
        self.outgriddef.value = value

    @property
    def dxoutlon(self):
        return self._dxoutlon

    @dxoutlon.setter
    def dxoutlon(self, value):
        self.dxoutlon.value = value

    @property
    def dyoutlon(self):
        return self._dyoutlon

    @dyoutlon.setter
    def dyoutlon(self, value):
        self.dyoutlon.value = value


class Receptor:
    def __init__(self):
        self._numreceptor = StaticSpecifierArgument(
            dummyline="    #                NUMRECEPTOR     number of receptors\n"
        )
        self._receptor = DynamicSpecifierArgument(
            self._numreceptor, type=str, dummyline="    #             RECEPTOR\n"
        )
        self._x = DynamicSpecifierArgument(
            self._numreceptor, type=float, dummyline="    #             X\n"
        )
        self._y = DynamicSpecifierArgument(
            self._numreceptor, type=float, dummyline="    #             y\n"
        )

    def read(self, f: TextIO):
        f.readline()
        self.numreceptor.read(f)
        for i in range(self.numreceptor.value):
            self.receptor.readline(f)
            self.x.readline(f)
            self.y.readline(f)

    @property
    def numreceptor(self):
        return self._numreceptor

    @numreceptor.setter
    def numreceptor(self, value):
        self.numreceptor.value = value

    @property
    def receptor(self):
        return self._receptor

    @receptor.setter
    def receptor(self, value):
        self.receptor.value = value

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self.x.value = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self.y.value = value


#####################################
##### Final FlexwrfInput Class ######
#####################################


class FlexwrfInput:
    def __init__(self):
        self._pathnames = Pathnames()
        self._command = Command()
        self._ageclasses = Ageclasses()
        self._outgrid = Outgrid()
        self._outgrid_nest = OutgridNest()
        self._receptor = Receptor()

    def read(self, file_path: Union[str, Path]):
        file_path = Path(file_path)
        with file_path.open("r") as f:
            self.pathnames.read(f)
            self.command.read(f)
            self.ageclasses.read(f)
            self.outgrid.read(f)
            self.outgrid_nest.read(f)
            self.receptor.read(f)

    @property
    def pathnames(self):
        return self._pathnames

    @property
    def command(self):
        return self._command

    @property
    def ageclasses(self):
        return self._ageclasses

    @property
    def outgrid(self):
        return self._outgrid

    @property
    def outgrid_nest(self):
        return self._outgrid_nest

    @property
    def receptor(self):
        return self._receptor
