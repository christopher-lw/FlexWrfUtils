from typing import TextIO, Any, List, Union
from pathlib import Path
import numpy as np
from datetime import datetime
import pandas as pd


def peek_line(f: TextIO):
    pos = f.tell()
    line = f.readline()
    f.seek(pos)
    return line


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
    def __init__(self, type=None, dummyline=None):
        super().__init__(type, dummyline)

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

    @BaseArgument.value.setter
    def value(self, value):
        new_values = [self._type(new_value) for new_value in value]
        self._value = new_values

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

    def __getitem__(self, index):
        return self.value[index]

    def __setitem__(self, index, value):
        self.value[index] = self._type(value)


class DatetimeArgument(StaticArgument):
    def __init__(self, dummyline=None):
        super().__init__(dummyline=dummyline)

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

    @BaseArgument.value.setter
    def value(self, value):
        new_values = [self._type(new_value) for new_value in value]
        self._value = new_values

    def __len__(self):
        return len(self._value)

    def __getitem__(self, index):
        return self.value[index]

    def __setitem__(self, index, value):
        self.value[index] = self._type(value)

    def readline(self, file: TextIO):
        line = file.readline()
        self.append(self.linecaster(line))

    def read(self, file: TextIO):
        n_values = self.specifier.value
        for i in range(n_values):
            line = file.readline()
            self.append(self.linecaster(line))

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


class DynamicDatetimeArgument(DynamicSpecifierArgument):
    def __init__(
        self,
        specifier: StaticSpecifierArgument,
        type=None,
        dummyline=None,
    ):
        super().__init__(specifier, type, dummyline)

    def __setitem__(self, index, value):
        if isinstance(value, np.datetime64):
            value = pd.to_datetime(value)
            value = value.strftime("%Y%m%d %H%M%S")
        elif isinstance(value, datetime):
            value = value.strftime("%Y%m%d %H%M%S")
        self.value[index] = self._type(value)

    def linecaster(self, line: str) -> str:
        decoded_line = line.strip().split(" ")[:2]
        decoded_line = f"{decoded_line[0]} {decoded_line[1]}"
        return decoded_line

    @DynamicSpecifierArgument.value.setter
    def value(self, value: List[Union[str, np.datetime64, datetime]]) -> str:
        new_values = []
        for new_value in value:
            if isinstance(new_value, np.datetime64):
                new_value = pd.to_datetime(new_value)
                new_value = new_value.strftime("%Y%m%d %H%M%S")
            elif isinstance(new_value, datetime):
                new_value = new_value.strftime("%Y%m%d %H%M%S")
            new_values.append(new_value)
        self._value = new_values


class SpeciesArgument(DynamicSpecifierArgument):
    def __init__(
        self,
        specifier: StaticSpecifierArgument,
        formatter: str,
        start_position: int,
        end_position: int,
        type=float,
    ):
        super().__init__(specifier, type)
        self.formatter = formatter
        self.start_position = start_position
        self.end_position = end_position

    def read(self, file: TextIO):
        start_line_index = file.tell()
        for i in range(self.specifier.value):
            line = file.readline()
            line_snippet = line[self.start_position : self.end_position]
            if line_snippet.strip() == "":
                new_value = None
            else:
                new_value = self._type(line_snippet)
            self.append(new_value)
        file.seek(start_line_index)

    def as_strings(self):
        strings = []
        for value in self.value:
            if value is None:
                string = " " * (self.end_position - self.start_position)
            else:
                string = self.formatter.format(value)
            strings.append(string)
        return strings


class DynamicTableArgument(DynamicSpecifierArgument):
    def __init__(
        self,
        specifier: StaticSpecifierArgument,
        length: int,
        start_position: int,
        end_position: int,
        formatter: str,
        type=float,
    ):
        super().__init__(specifier, type)
        self.length = length
        self.start_position = start_position
        self.end_position = end_position
        self.formatter = formatter
        self._value: List[List[self._type]] = []

    @DynamicSpecifierArgument.value.setter
    def value(self, value):
        casted_new_values = []
        for new_value_list in value:
            casted_new_value_list = [
                self._type(new_value) for new_value in new_value_list
            ]
            casted_new_values.append(casted_new_value_list)
        self._value = casted_new_values

    def readcolumn(self, f):
        start_line_index = f.tell()
        new_values = []
        for i in range(self.length):
            line = f.readline()
            line_snippet = line[self.start_position : self.end_position]
            new_values.append(self._type(line_snippet))
        self._value.append(new_values)
        f.seek(start_line_index)

    def as_strings(self):
        strings = []
        for values in self._value:
            new_strings = [self.formatter.format(value) for value in values]
            strings.append(new_strings)
        return strings

    def line(self):
        raise NotImplementedError

    def lines(self):
        raise NotImplementedError

    def linecaster(self, line: str) -> Any:
        raise NotImplementedError


class NestedSpecifierArgument:
    def __init__(
        self,
        specifier1: StaticSpecifierArgument,
        specifier2: StaticSpecifierArgument,
        type,
        dummyline: str,
        formatter: str = None,
    ):
        self.specifier1 = specifier1
        self.specifier2 = specifier2
        self.formatter = formatter
        self._type = type
        self._dummyline = dummyline
        self._value: List[List[self._type]] = []

    def __getitem__(self, index):
        return self.value[index]

    def __setitem__(self, index, value):
        value = [self._type(v) for v in value]
        self.value[index] = value

    def readblock(self, f: TextIO):
        new_values = []
        for i in range(self.specifier2.value):
            line = f.readline()
            new_values.append(self.linecaster(line))
        self.value.append(new_values)

    def as_string(self):
        strings = []
        for values in self._value:
            new_strings = [self.formatter.format(value) for value in values]
            strings.append(new_strings)
        return strings

    @property
    def lines(self):
        lines = []
        for strings in self.as_string():
            new_lines = [self._dummyline.replace("#", string) for string in strings]
            lines.append(new_lines)
        return lines

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        casted_new_values = []
        for new_value_list in value:
            casted_new_value_list = [
                self._type(new_value) for new_value in new_value_list
            ]
            casted_new_values.append(casted_new_value_list)
        self._value = casted_new_values

    def read(self, file: TextIO):
        line = file.readline()
        self.value = self.linecaster(line)

    def linecaster(self, line: str) -> Any:
        decoded_line = self._type(line.strip().split(" ")[0])
        return decoded_line

    def append(self, value):
        self._value.append(value)
        self.specifier1.value = len(self._value)

    def remove(self, index):
        self._value.remove(self.value[index])
        self.specifier1.value = len(self._value)


####################################
###### Actual Option Classes #######
####################################


class Pathnames:
    def __init__(self):
        self._header = "=====================FORMER PATHNAMES FILE===================\n"
        self._footer = "=============================================================\n"
        self._outputpath = StaticArgument(type=Path, dummyline="#/\n")
        self._inputpath = DynamicArgument(type=Path, dummyline="#/\n")
        self._availablepath = DynamicArgument(type=Path, dummyline="#\n")

    def read(self, f: TextIO):
        f.readline()
        self.outputpath.read(f)
        while "====" not in peek_line(f):
            self.inputpath.readline(f)
            self.availablepath.readline(f)
        f.readline()

    @property
    def lines(self):
        lines = []
        lines.append(self._header)
        lines.append(self.outputpath.line)
        for input_line, available_line in zip(
            self.inputpath.lines, self.availablepath.lines
        ):
            lines.append(input_line)
            lines.append(available_line)
        lines.append(self._footer)
        return lines

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
        self._header = "=====================FORMER COMMAND FILE=====================\n"
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
            dummyline="    #              CTL    (real)     factor by which time step must be smaller than tl\n",
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
            dummyline="    #            DT_CONV  (real)   time interval to call convection, seconds\n",
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
    def lines(self):
        lines = [
            self._header,
            self.ldirect.line,
            self.start.line,
            self.stop.line,
            self.outputrate.line,
            self.averagerate.line,
            self.samplingrate.line,
            self.splittingtime.line,
            self.syncronizationinterval.line,
            self.ctl.line,
            self.ifine.line,
            self.iout.line,
            self.ipout.line,
            self.lsubgrid.line,
            self.lconvection.line,
            self.dtconv.line,
            self.lagespectra.line,
            self.ipin.line,
            self.iflux.line,
            self.ioutputforeachrel.line,
            self.mdomainfill.line,
            self.indsource.line,
            self.indreceptor.line,
            self.nestedoutput.line,
            self.linitcond.line,
            self.turboption.line,
            self.luoption.line,
            self.cblscheme.line,
            self.sfcoption.line,
            self.windoption.line,
            self.timeoption.line,
            self.outgridcoord.line,
            self.releasecoord.line,
            self.iouttype.line,
            self.nctimerec.line,
            self.verbose.line,
        ]
        return lines

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
        self._header = "=====================FORMER AGECLASESS FILE==================\n"
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
    def lines(self):
        lines = [self._header, self.nageclasses.line]
        lines.extend(self.ageclasses.lines)
        return lines

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
        self._header = "=====================FORMER OUTGRID FILE=====================\n"
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
            self._numzgrid,
            type=float,
            dummyline="    #            LEVEL           height of level (upper boundary)\n",
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
    def lines(self):
        lines = [
            self._header,
            self.outlonleft.line,
            self.outlatlower.line,
            self.numxgrid.line,
            self.numygrid.line,
            self.outgriddef.line,
            self.dxoutlon.line,
            self.dyoutlon.line,
            self.numzgrid.line,
        ]
        lines.extend(self.levels.lines)
        return lines

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
        self._header = "================OUTGRID_NEST==========================\n"
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

    def is_in_file(self, f: TextIO) -> bool:
        current_line = f.tell()
        [f.readline() for i in range(8)]
        expected_end_line = f.readline()
        f.seek(current_line)
        return "=====" in expected_end_line

    def read(self, f: TextIO):
        if self.is_in_file(f):
            f.readline()
            self.outlonleft.read(f)
            self.outlatlower.read(f)
            self.numxgrid.read(f)
            self.numygrid.read(f)
            self.outgriddef.read(f)
            self.dxoutlon.read(f)
            self.dyoutlon.read(f)
        else:
            pass

    @property
    def lines(self):
        if self.outlonleft.value is None:
            lines = []
        else:
            lines = [
                self._header,
                self.outlonleft.line,
                self.outlatlower.line,
                self.numxgrid.line,
                self.numygrid.line,
                self.outgriddef.line,
                self.dxoutlon.line,
                self.dyoutlon.line,
            ]
        return lines

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
        self._header = "=====================FORMER RECEPTOR FILE====================\n"
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
    def lines(self):
        lines = [self._header, self.numreceptor.line]
        for receptor_line, x_line, y_line in zip(
            self.receptor.lines, self.x.lines, self.y.lines
        ):
            lines.append(receptor_line)
            lines.append(x_line)
            lines.append(y_line)
        return lines

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


class Species:
    def __init__(self):
        self._header = "=====================FORMER SPECIES FILE=====================\n"
        self._legend = "XXXX|NAME    |decaytime |wetscava  |wetsb|drydif|dryhenry|drya|partrho  |parmean|partsig|dryvelo|weight |\n"
        self._numtable = StaticSpecifierArgument(
            dummyline="    #               NUMTABLE        number of variable properties. The following lines are fixed format\n"
        )

        self._name = SpeciesArgument(
            specifier=self._numtable,
            formatter="{:10}",
            start_position=4,
            end_position=14,
            type=str,
        )

        self._decaytime = SpeciesArgument(
            specifier=self._numtable,
            formatter="{:10.1f}",
            start_position=14,
            end_position=24,
        )

        self._wetscava = SpeciesArgument(
            specifier=self._numtable,
            formatter="{:11.1E}",
            start_position=24,
            end_position=35,
        )

        self._wetsb = SpeciesArgument(
            specifier=self._numtable,
            formatter="{:6.2f}",
            start_position=35,
            end_position=41,
        )

        self._drydif = SpeciesArgument(
            specifier=self._numtable,
            formatter="{:7.1f}",
            start_position=41,
            end_position=48,
        )

        self._dryhenry = SpeciesArgument(
            specifier=self._numtable,
            formatter="{:9.1E}",
            start_position=48,
            end_position=57,
        )
        self._drya = SpeciesArgument(
            specifier=self._numtable,
            formatter="{:5.1f}",
            start_position=57,
            end_position=62,
        )
        self._partrho = SpeciesArgument(
            specifier=self._numtable,
            formatter="{:10.1E}",
            start_position=62,
            end_position=72,
        )
        self._parmean = SpeciesArgument(
            specifier=self._numtable,
            formatter="{:8.1E}",
            start_position=72,
            end_position=80,
        )
        self._partsig = SpeciesArgument(
            specifier=self._numtable,
            formatter="{:8.1E}",
            start_position=80,
            end_position=88,
        )
        self._dryvelo = SpeciesArgument(
            specifier=self._numtable,
            formatter="{:8.2f}",
            start_position=88,
            end_position=96,
        )
        self._weight = SpeciesArgument(
            specifier=self._numtable,
            formatter="{:8.2f}",
            start_position=96,
            end_position=104,
        )

    def read(self, f: TextIO):
        f.readline()
        self.numtable.read(f)
        f.readline()
        self.name.read(f)
        self.decaytime.read(f)
        self.wetscava.read(f)
        self.wetsb.read(f)
        self.drydif.read(f)
        self.dryhenry.read(f)
        self.drya.read(f)
        self.partrho.read(f)
        self.parmean.read(f)
        self.partsig.read(f)
        self.dryvelo.read(f)
        self.weight.read(f)
        [f.readline() for i in range(self.numtable.value)]

    @property
    def lines(self):
        lines = [self._header, self.numtable.line, self._legend]
        for argument_strings in zip(
            self.name.as_strings(),
            self.decaytime.as_strings(),
            self.wetscava.as_strings(),
            self.wetsb.as_strings(),
            self.drydif.as_strings(),
            self.dryhenry.as_strings(),
            self.drya.as_strings(),
            self.partrho.as_strings(),
            self.parmean.as_strings(),
            self.partsig.as_strings(),
            self.dryvelo.as_strings(),
            self.weight.as_strings(),
        ):
            line = "    "
            for string in argument_strings:
                line += string
            lines.append(line + "\n")
        return lines

    @property
    def numtable(self):
        return self._numtable

    @numtable.setter
    def numtable(self, value):
        self._numtable.value = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name.value = value

    @property
    def decaytime(self):
        return self._decaytime

    @decaytime.setter
    def decaytime(self, value):
        self._decaytime.value = value

    @property
    def wetscava(self):
        return self._wetscava

    @wetscava.setter
    def wetscava(self, value):
        self._wetscava.value = value

    @property
    def wetsb(self):
        return self._wetsb

    @wetsb.setter
    def wetsb(self, value):
        self._wetsb.value = value

    @property
    def drydif(self):
        return self._drydif

    @drydif.setter
    def drydif(self, value):
        self._drydif.value = value

    @property
    def dryhenry(self):
        return self._dryhenry

    @dryhenry.setter
    def dryhenry(self, value):
        self._dryhenry.value = value

    @property
    def drya(self):
        return self._drya

    @drya.setter
    def drya(self, value):
        self._drya.value = value

    @property
    def partrho(self):
        return self._partrho

    @partrho.setter
    def partrho(self, value):
        self._partrho.value = value

    @property
    def parmean(self):
        return self._parmean

    @parmean.setter
    def parmean(self, value):
        self._parmean.value = value

    @property
    def partsig(self):
        return self._partsig

    @partsig.setter
    def partsig(self, value):
        self._partsig.value = value

    @property
    def dryvelo(self):
        return self._dryvelo

    @dryvelo.setter
    def dryvelo(self, value):
        self._dryvelo.value = value

    @property
    def weight(self):
        return self._weight

    @weight.setter
    def weight(self, value):
        self._weight.value = value


class Releases:
    def __init__(self):
        self._header = "=====================FORMER RELEEASES FILE===================\n"
        self._nspec = StaticSpecifierArgument(
            dummyline="   #                NSPEC           total number of species emitted\n"
        )
        self._emitvar = StaticArgument(
            type=int,
            dummyline="   #                EMITVAR         1 for emission variation\n",
        )
        self._link = DynamicSpecifierArgument(
            self._nspec,
            type=int,
            dummyline="   #                LINK            index of species in file SPECIES\n",
        )
        self._ihour = DynamicTableArgument(
            specifier=self._nspec,
            length=24,
            start_position=3,
            end_position=5,
            formatter="{:2}",
            type=int,
        )

        self._area_hour = DynamicTableArgument(
            specifier=self._nspec,
            length=24,
            start_position=5,
            end_position=12,
            formatter="{:7.3f}",
            type=float,
        )

        self._point_hour = DynamicTableArgument(
            specifier=self._nspec,
            length=24,
            start_position=12,
            end_position=19,
            formatter="{:7.3f}",
            type=float,
        )
        self._idow = DynamicTableArgument(
            specifier=self._nspec,
            length=7,
            start_position=3,
            end_position=4,
            formatter="{:1}",
            type=int,
        )

        self._area_dow = DynamicTableArgument(
            specifier=self._nspec,
            length=7,
            start_position=5,
            end_position=17,
            formatter="{:12.3f}",
            type=float,
        )

        self._point_dow = DynamicTableArgument(
            specifier=self._nspec,
            length=7,
            start_position=17,
            end_position=29,
            formatter="{:12.3f}",
            type=float,
        )

        self._numpoint = StaticSpecifierArgument(
            dummyline="#                 NUMPOINT        number of releases\n"
        )

        self._start = DynamicDatetimeArgument(
            specifier=self._numpoint,
            type=str,
            dummyline="#   ID1, IT1        beginning date and time of release\n",
        )

        self._stop = DynamicDatetimeArgument(
            specifier=self._numpoint,
            type=str,
            dummyline="#   ID1, IT1        ending date and time of release\n",
        )

        self._xpoint1 = DynamicSpecifierArgument(
            specifier=self._numpoint,
            type=float,
            dummyline="#         XPOINT1 (real)  longitude [deg] of lower left corner\n",
        )
        self._ypoint1 = DynamicSpecifierArgument(
            specifier=self._numpoint,
            type=float,
            dummyline="#         YPOINT1 (real)  latitude [deg] of lower left corner\n",
        )
        self._xpoint2 = DynamicSpecifierArgument(
            specifier=self._numpoint,
            type=float,
            dummyline="#         XPOINT2 (real)  longitude [deg] of upper right corner\n",
        )
        self._ypoint2 = DynamicSpecifierArgument(
            specifier=self._numpoint,
            type=float,
            dummyline="#         YPOINT2 (real)  latitude [DEG] of upper right corner\n",
        )
        self._kindz = DynamicSpecifierArgument(
            specifier=self._numpoint,
            type=int,
            dummyline="#         KINDZ  (int)  1 for m above ground, 2 for m above sea level, 3 pressure\n",
        )
        self._zpoint1 = DynamicSpecifierArgument(
            specifier=self._numpoint,
            type=float,
            dummyline="#        ZPOINT1 (real)  lower z-level\n",
        )
        self._zpoint2 = DynamicSpecifierArgument(
            specifier=self._numpoint,
            type=float,
            dummyline="#        ZPOINT2 (real)  upper z-level \n",
        )
        self._npart = DynamicSpecifierArgument(
            specifier=self._numpoint,
            type=int,
            dummyline="#          NPART (int)     total number of particles to be released\n",
        )
        self._xmass = NestedSpecifierArgument(
            specifier1=self._numpoint,
            specifier2=self._nspec,
            type=float,
            dummyline="#         XMASS (real)    total mass emitted\n",
            formatter="{:.4E}",
        )
        self._name = DynamicSpecifierArgument(
            specifier=self._numpoint,
            type=str,
            dummyline="#  NAME OF RELEASE LOCATION\n",
        )

    def read(self, f: TextIO):
        f.readline()
        self.nspec.read(f)
        self.emitvar.read(f)
        for i in range(self.nspec.value):
            self.link.readline(f)
            if self.emitvar.value == 1:
                self.ihour.readcolumn(f)
                self.area_hour.readcolumn(f)
                self.point_hour.readcolumn(f)
                [f.readline() for j in range(24)]
                self.idow.readcolumn(f)
                self.area_dow.readcolumn(f)
                self.point_dow.readcolumn(f)
                [f.readline() for j in range(7)]
        self.numpoint.read(f)
        for i in range(self.numpoint.value):
            self.start.readline(f)
            self.stop.readline(f)
            self.xpoint1.readline(f)
            self.ypoint1.readline(f)
            self.xpoint2.readline(f)
            self.ypoint2.readline(f)
            self.kindz.readline(f)
            self.zpoint1.readline(f)
            self.zpoint2.readline(f)
            self.npart.readline(f)
            self.xmass.readblock(f)
            self.name.readline(f)

    @property
    def lines(self):
        lines = [self._header, self.nspec.line, self.emitvar.line]

        if self.emitvar.value == 0:
            lines.extend(self.link.lines)

        else:
            for (
                link_line,
                ihour,
                area_hour,
                point_hour,
                idow,
                area_dow,
                point_dow,
            ) in zip(
                self.link.lines,
                self.ihour.as_strings(),
                self.area_hour.as_strings(),
                self.point_hour.as_strings(),
                self.idow.as_strings(),
                self.area_dow.as_strings(),
                self.point_dow.as_strings(),
            ):
                lines.append(link_line)
                line_start = "   "
                line_end = "\n"
                for i, a, p in zip(ihour, area_hour, point_hour):
                    lines.append(line_start + i + a + p + line_end)
                for i, a, p in zip(idow, area_dow, point_dow):
                    lines.append(line_start + i + a + p + line_end)
        lines.append(self.numpoint.line)
        for (
            start_line,
            stop_line,
            xpoint1_line,
            ypoint1_line,
            xpoint2_line,
            ypoint2_line,
            kindz_line,
            zpoint1_line,
            zpoint2_line,
            npart_line,
            xmass_lines,
            name_line,
        ) in zip(
            self.start.lines,
            self.stop.lines,
            self.xpoint1.lines,
            self.ypoint1.lines,
            self.xpoint2.lines,
            self.ypoint2.lines,
            self.kindz.lines,
            self.zpoint1.lines,
            self.zpoint2.lines,
            self.npart.lines,
            self.xmass.lines,
            self.name.lines,
        ):
            lines.append(start_line)
            lines.append(stop_line)
            lines.append(xpoint1_line)
            lines.append(ypoint1_line)
            lines.append(xpoint2_line)
            lines.append(ypoint2_line)
            lines.append(kindz_line)
            lines.append(zpoint1_line)
            lines.append(zpoint2_line)
            lines.append(npart_line)
            lines.extend(xmass_lines)
            lines.append(name_line)
        return lines

    def add_copy(self, release_index: int):
        release_arguments = [
            self.start,
            self.stop,
            self.xpoint1,
            self.ypoint1,
            self.xpoint2,
            self.ypoint2,
            self.kindz,
            self.zpoint1,
            self.zpoint2,
            self.npart,
            self.xmass,
            self.name,
        ]
        for release_argument in release_arguments:
            release_argument.append(release_argument.value[release_index])

    @property
    def nspec(self):
        return self._nspec

    @nspec.setter
    def nspec(self, value):
        self.nspec.value = value

    @property
    def emitvar(self):
        return self._emitvar

    @emitvar.setter
    def emitvar(self, value):
        self.emitvar.value = value

    @property
    def link(self):
        return self._link

    @link.setter
    def link(self, value):
        self.link.value = value

    @property
    def ihour(self):
        return self._ihour

    @ihour.setter
    def ihour(self, value):
        self.ihour.value = value

    @property
    def area_hour(self):
        return self._area_hour

    @area_hour.setter
    def area_hour(self, value):
        self.area_hour.value = value

    @property
    def point_hour(self):
        return self._point_hour

    @point_hour.setter
    def point_hour(self, value):
        self.point_hour.value = value

    @property
    def idow(self):
        return self._idow

    @idow.setter
    def idow(self, value):
        self.idow.value = value

    @property
    def area_dow(self):
        return self._area_dow

    @area_dow.setter
    def area_dow(self, value):
        self.area_dow.value = value

    @property
    def point_dow(self):
        return self._point_dow

    @point_dow.setter
    def point_dow(self, value):
        self.point_dow.value = value

    @property
    def numpoint(self):
        return self._numpoint

    @numpoint.setter
    def numpoint(self, value):
        self.numpoint.value = value

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
    def xpoint1(self):
        return self._xpoint1

    @xpoint1.setter
    def xpoint1(self, value):
        self.xpoint1.value = value

    @property
    def ypoint1(self):
        return self._ypoint1

    @ypoint1.setter
    def ypoint1(self, value):
        self.ypoint1.value = value

    @property
    def xpoint2(self):
        return self._xpoint2

    @xpoint2.setter
    def xpoint2(self, value):
        self.xpoint2.value = value

    @property
    def ypoint2(self):
        return self._ypoint2

    @ypoint2.setter
    def ypoint2(self, value):
        self.ypoint2.value = value

    @property
    def kindz(self):
        return self._kindz

    @kindz.setter
    def kindz(self, value):
        self.kindz.value = value

    @property
    def zpoint1(self):
        return self._zpoint1

    @zpoint1.setter
    def zpoint1(self, value):
        self.zpoint1.value = value

    @property
    def zpoint2(self):
        return self._zpoint2

    @zpoint2.setter
    def zpoint2(self, value):
        self.zpoint2.value = value

    @property
    def npart(self):
        return self._npart

    @npart.setter
    def npart(self, value):
        self.npart.value = value

    @property
    def xmass(self):
        return self._xmass

    @xmass.setter
    def xmass(self, value):
        self.xmass.value = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self.name.value = value


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
        self._species = Species()
        self._releases = Releases()
        self.options = [
            self._pathnames,
            self._command,
            self._ageclasses,
            self._outgrid,
            self._outgrid_nest,
            self._receptor,
            self._species,
            self._releases,
        ]

    def read(self, file_path: Union[str, Path]):
        file_path = Path(file_path)
        with file_path.open("r") as f:
            for option in self.options:
                option.read(f)

    def write(self, file_path: Union[str, Path]):
        file_path = Path(file_path)
        with file_path.open("w") as f:
            for line in self.lines:
                f.write(line)

    @property
    def lines(self) -> str:
        lines = []
        for option in self.options:
            lines.extend(option.lines)
        return lines

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

    @property
    def species(self):
        return self._species

    @property
    def releases(self):
        return self._releases
