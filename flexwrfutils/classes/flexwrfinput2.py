from typing import TextIO, Any, List, Union
from pathlib import Path
import numpy as np
from datetime import datetime
import pandas as pd


class BaseArgument:
    def __init__(self):
        self._type = None
        self._value = None
        self._dummyline = None

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
    def __init__(self):
        super().__init__()
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
    def __init__(self):
        self._type = str
        self._value = None
        self._dummyline = "    #  YYYYMMDD HHMISS   "

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
    def __init__(self):
        super().__init__()
        self._type = int
        self.children = []


class DynamicSpecifierArgument(BaseArgument):
    def __init__(self, specifier: StaticSpecifierArgument):
        super().__init__()
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
        self.specifier.value += 1

    def remove(self, index):
        self._value.remove(self.value[-1])
        self.specifier.value -= 1


#####################################
##### Actual Argument Classes #######
#####################################

#####################################
############# PATHNAMES #############
#####################################


class OutputPath(StaticArgument):
    def __init__(self):
        self._type = Path
        self._value = None
        self._dummyline = "#/\n"


class InputPath(DynamicArgument):
    def __init__(self):
        super().__init__()
        self._type = Path
        self._dummyline = "#/\n"


#####################################
############## COMMAND ##############
#####################################


class Ldirect(StaticArgument):
    def __init__(self):
        super().__init__()
        self._type = int
        self._dummyline = "    #                LDIRECT:          1 for forward simulation, -1 for backward simulation\n"


class RunStart(DatetimeArgument):
    def __init__(self):
        super().__init__()
        self._dummyline = "    #  YYYYMMDD HHMISS   beginning date of simulation\n"


class RunStop(DatetimeArgument):
    def __init__(self):
        super().__init__()
        self._dummyline = "    #  YYYYMMDD HHMISS   ending date of simulation\n"


class OutputRate(StaticArgument):
    def __init__(self):
        super().__init__()
        self._type = int
        self._dummyline = (
            "    #             SSSSS  (int)      output every SSSSS seconds"
        )


class AverageRate(StaticArgument):
    def __init__(self):
        super().__init__()
        self._type = int
        self._dummyline = "    #             SSSSS  (int)      time average of output (in SSSSS seconds)"


class SamplingRate(StaticArgument):
    def __init__(self):
        super().__init__()
        self._type = int
        self._dummyline = "    #              SSSSS  (int)      sampling rate of output (in SSSSS seconds)"


class SplittingTime(StaticArgument):
    def __init__(self):
        super().__init__()
        self._type = int
        self._dummyline = "    #        SSSSS  (int)      time constant for particle splitting (in seconds)"


class SyncronizationInterval(StaticArgument):
    def __init__(self):
        super().__init__()
        self._type = int
        self._dummyline = "    #              SSSSS  (int)      synchronisation interval of flexpart (in seconds)"


class Ctl(StaticArgument):
    def __init__(self):
        super().__init__()
        self._type = float
        self._dummyline = "    #.              CTL    (real)     factor by which time step must be smaller than tl"


class Ifine(StaticArgument):
    def __init__(self):
        super().__init__()
        self._type = int
        self._dummyline = "    #               IFINE  (int)      decrease of time step for vertical motion by factor ifine"


class Iout(StaticArgument):
    def __init__(self):
        super().__init__()
        self._type = int
        self._dummyline = "    #                IOUT              1 concentration, 2 mixing ratio, 3 both, 4 plume traject, 5=1+4"


class Ipout(StaticArgument):
    def __init__(self):
        super().__init__()
        self._type = int
        self._dummyline = "    #                IPOUT             particle dump: 0 no, 1 every output interval, 2 only at end"


class Lsubgrid(StaticArgument):
    def __init__(self):
        super().__init__()
        self._type = int
        self._dummyline = "    #                LSUBGRID          subgrid terrain effect parameterization: 1 yes, 0 no"


class Lconvection(StaticArgument):
    def __init__(self):
        super().__init__()
        self._type = int
        self._dummyline = (
            "    #                LCONVECTION       convection: 3 yes, 0 no"
        )


class DtConv(StaticArgument):
    def __init__(self):
        super().__init__()
        self._type = float
        self._dummyline = "    #.            DT_CONV  (real)   time interval to call convection, seconds"


class Lagespectra(StaticArgument):
    def __init__(self):
        super().__init__()
        self._type = int
        self._dummyline = (
            "    #                LAGESPECTRA       age spectra: 1 yes, 0 no"
        )


class Ipin(StaticArgument):
    def __init__(self):
        super().__init__()
        self._type = int
        self._dummyline = "    #                IPIN              continue simulation with dumped particle data: 1 yes, 0 no"


class Iflux(StaticArgument):
    def __init__(self):
        super().__init__()
        self._type = int
        self._dummyline = (
            "    #                IFLUX             calculate fluxes: 1 yes, 0 no"
        )


class Ioutputforeachrel(StaticArgument):
    def __init__(self):
        super().__init__()
        self._type = int
        self._dummyline = "    #                IOUTPUTFOREACHREL CREATE AN OUPUT FILE FOR EACH RELEASE LOCATION: 1 YES, 0 NO"


class Mdomainfill(StaticArgument):
    def __init__(self):
        super().__init__()
        self._type = int
        self._dummyline = "    #                MDOMAINFILL       domain-filling trajectory option: 1 yes, 0 no, 2 strat. o3 tracer"


class IndSource(StaticArgument):
    def __init__(self):
        super().__init__()
        self._type = int
        self._dummyline = "    #                IND_SOURCE        1=mass unit , 2=mass mixing ratio unit"


class IndReceptor(StaticArgument):
    def __init__(self):
        super().__init__()
        self._type = int
        self._dummyline = "    #                IND_RECEPTOR      1=mass unit , 2=mass mixing ratio unit"


class NestedOutput(StaticArgument):
    def __init__(self):
        super().__init__()
        self._type = int
        self._dummyline = "    #                NESTED_OUTPUT     shall nested output be used? 1 yes, 0 no"


class LinitCond(StaticArgument):
    def __init__(self):
        super().__init__()
        self._type = int
        self._dummyline = "    #                LINIT_COND   INITIAL COND. FOR BW RUNS: 0=NO,1=MASS UNIT,2=MASS MIXING RATIO UNIT"


class TurbOption(StaticArgument):
    def __init__(self):
        super().__init__()
        self._type = int
        self._dummyline = "    #                TURB_OPTION       0=no turbulence; 1=diagnosed as in flexpart_ecmwf; 2 and 3=from tke."


class LuOption(StaticArgument):
    def __init__(self):
        super().__init__()
        self._type = int
        self._dummyline = "    #                LU_OPTION         0=old landuse (IGBP.dat); 1=landuse from WRF"


class CblScheme(StaticArgument):
    def __init__(self):
        super().__init__()
        self._type = int
        self._dummyline = (
            "    #                CBL SCHEME        0=no, 1=yes. works if TURB_OPTION=1"
        )


class SfcOption(StaticArgument):
    def __init__(self):
        super().__init__()
        self._type = int
        self._dummyline = "    #                SFC_OPTION        0=default computation of u*, hflux, pblh, 1=from wrf"


class WindOption(StaticArgument):
    def __init__(self):
        super().__init__()
        self._type = int
        self._dummyline = "    #                WIND_OPTION       0=snapshot winds, 1=mean winds,2=snapshot eta-dot,-1=w based on divergence"


class TimeOption(StaticArgument):
    def __init__(self):
        super().__init__()
        self._type = int
        self._dummyline = "    #                TIME_OPTION       1=correction of time validity for time-average wind,  0=no need"


class OutgridCoord(StaticArgument):
    def __init__(self):
        super().__init__()
        self._type = int
        self._dummyline = "    #                OUTGRID_COORD     0=wrf grid(meters), 1=regular lat/lon grid"


class ReleaseCoord(StaticArgument):
    def __init__(self):
        super().__init__()
        self._type = int
        self._dummyline = "    #                RELEASE_COORD     0=wrf grid(meters), 1=regular lat/lon grid"


class Iouttype(StaticArgument):
    def __init__(self):
        super().__init__()
        self._type = int
        self._dummyline = "    #                IOUTTYPE          0=default binary, 1=ascii (for particle dump only),2=netcdf"


class Nctimerec(StaticArgument):
    def __init__(self):
        super().__init__()
        self._type = int
        self._dummyline = "    #                NCTIMEREC (int)   Time frames per output file, only used for netcdf"


class Verbose(StaticArgument):
    def __init__(self):
        super().__init__()
        self._type = int
        self._dummyline = (
            "    #                VERBOSE           VERBOSE MODE,0=minimum, 100=maximum"
        )


#####################################
############# Ageclasses #############
#####################################


class Nageclasses(StaticSpecifierArgument):
    def __init__(self):
        super().__init__()
        self._dummyline = (
            "    #                NAGECLASS        number of age classes\n"
        )


class AgeclassesInstance(DynamicSpecifierArgument):
    def __init__(self, specifier):
        super().__init__(specifier)
        self._type = int
        self._dummyline = (
            "    #             SSSSSS  (int)    age class in SSSSS seconds\n"
        )


#####################################
####### Actual Option Classes #######
#####################################


class Pathnames:
    def __init__(self):
        self._outputpath = OutputPath()
        self._inputpath = InputPath()
        self._availablepath = InputPath()

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
        self._ldirect = Ldirect()
        self._runstart = RunStart()
        self._runstop = RunStop()
        self._outputrate = OutputRate()
        self._averagerate = AverageRate()
        self._samplingrate = SamplingRate()
        self._splittingtime = SplittingTime()
        self._syncronizationinterval = SyncronizationInterval()
        self._ctl = Ctl()
        self._ifine = Ifine()
        self._iout = Iout()
        self._ipout = Ipout()
        self._lsubgrid = Lsubgrid()
        self._lconvection = Lconvection()
        self._dtconv = DtConv()
        self._lagespectra = Lagespectra()
        self._ipin = Ipin()
        self._iflux = Iflux()
        self._ioutputforeachrel = Ioutputforeachrel()
        self._mdomainfill = Mdomainfill()
        self._indsource = IndSource()
        self._indreceptor = IndReceptor()
        self._nestedoutput = NestedOutput()
        self._linitcond = LinitCond()
        self._turboption = TurbOption()
        self._luoption = LuOption()
        self._cblscheme = CblScheme()
        self._sfcoption = SfcOption()
        self._windoption = WindOption()
        self._timeoption = TimeOption()
        self._outgridcoord = OutgridCoord()
        self._releasecoord = ReleaseCoord()
        self._iouttype = Iouttype()
        self._nctimerec = Nctimerec()
        self._verbose = Verbose()

    def read(self, f: TextIO):
        f.readline()
        self.ldirect.read(f)
        self.runstart.read(f)
        self.runstop.read(f)
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
    def runstart(self):
        return self._runstart

    @runstart.setter
    def runstart(self, value):
        self.runstart.value = value

    @property
    def runstop(self):
        return self._runstop

    @runstop.setter
    def runstop(self, value):
        self.runstop.value = value

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


class FlexwrfInput:
    def __init__(self):
        self._pathnames = Pathnames()
        self._command = Command()
        self._ageclasses = None

    def read(self, file_path: Union[str, Path]):
        file_path = Path(file_path)
        with file_path.open("r") as f:
            self.pathnames.read(f)
            self.command.read(f)

    @property
    def pathnames(self):
        return self._pathnames

    @property
    def command(self):
        return self._command

    @property
    def ageclasses(self):
        return self._ageclasses
