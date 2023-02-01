from enum import Enum


class FlexWrfEnum(Enum):
    pass


class PathnamesArgs(FlexWrfEnum):
    START_DELIMITER = (
        start_delimiter
    ) = "=====================FORMER PATHNAMES FILE==================="
    OUTPUT_PATH = output_path = "#"
    INPUT_PATH = input_path = "# "
    AVAILABLE_PATH = available_path = "#  "
    END_DELIMITER = (
        end_delimiter
    ) = "============================================================="


class CommandArgs(FlexWrfEnum):
    START_DELIMITER = (
        start_delimiter
    ) = "=====================FORMER COMMAND FILE==================="
    LDIRECT = (
        ldirect
    ) = "    #                LDIRECT:          1 for forward simulation, -1 for backward simulation"
    START = start = "    #  YYYYMMDD HHMISS   beginning date of simulation"
    STOP = stop = "    #  YYYYMMDD HHMISS   ending date of simulation"
    OUTPUT_RATE = (
        output_rate
    ) = "    #             SSSSS  (int)      output every SSSSS seconds"
    AVERAGE_RATE = (
        average_rate
    ) = "    #             SSSSS  (int)      time average of output (in SSSSS seconds)"
    SAMPLING_RATE = (
        sampling_rate
    ) = "    #              SSSSS  (int)      sampling rate of output (in SSSSS seconds)"
    SPLITTING_TIME = (
        splitting_time
    ) = "    #        SSSSS  (int)      time constant for particle splitting (in seconds)"
    SYNCRONIZATION_INTERVAL = (
        syncronization_interval
    ) = "    #              SSSSS  (int)      synchronisation interval of flexpart (in seconds)"
    CTL = (
        ctl
    ) = "    #              CTL    (real)     factor by which time step must be smaller than tl"
    IFINE = (
        ifine
    ) = "    #               IFINE  (int)      decrease of time step for vertical motion by factor ifine"
    IOUT = (
        iout
    ) = "    #                IOUT              1 concentration, 2 mixing ratio, 3 both, 4 plume traject, 5=1+4"
    IPOUT = (
        ipout
    ) = "    #                IPOUT             particle dump: 0 no, 1 every output interval, 2 only at end"
    LSUBGRID = (
        lsubgrid
    ) = "    #                LSUBGRID          subgrid terrain effect parameterization: 1 yes, 0 no"
    LCONVECTION = (
        lconvection
    ) = "    #                LCONVECTION       convection: 3 yes, 0 no"
    DT_CONV = (
        dt_conv
    ) = "    #            DT_CONV  (real)   time interval to call convection, seconds"
    LAGESPECTRA = (
        lagespectra
    ) = "    #                LAGESPECTRA       age spectra: 1 yes, 0 no"
    IPIN = (
        ipin
    ) = "    #                IPIN              continue simulation with dumped particle data: 1 yes, 0 no"
    IFLUX = (
        iflux
    ) = "    #                IFLUX             calculate fluxes: 1 yes, 0 no"
    IOUTPUTFOREACHREL = (
        ioutputforeachrel
    ) = "    #                IOUTPUTFOREACHREL CREATE AN OUPUT FILE FOR EACH RELEASE LOCATION: 1 YES, 0 NO"
    MDOMAINFILL = (
        mdomainfill
    ) = "    #                MDOMAINFILL       domain-filling trajectory option: 1 yes, 0 no, 2 strat. o3 tracer"
    IND_SOURCE = (
        ind_source
    ) = "    #                IND_SOURCE        1=mass unit , 2=mass mixing ratio unit"
    IND_RECEPTOR = (
        ind_receptor
    ) = "    #                IND_RECEPTOR      1=mass unit , 2=mass mixing ratio unit"
    NESTED_OUTPUT = (
        nested_output
    ) = "    #                NESTED_OUTPUT     shall nested output be used? 1 yes, 0 no"
    LINIT_COND = (
        linit_cond
    ) = "    #                LINIT_COND   INITIAL COND. FOR BW RUNS: 0=NO,1=MASS UNIT,2=MASS MIXING RATIO UNIT"
    TURB_OPTION = (
        turb_option
    ) = "    #                TURB_OPTION       0=no turbulence; 1=diagnosed as in flexpart_ecmwf; 2 and 3=from tke."
    LU_OPTION = (
        lu_option
    ) = "    #                LU_OPTION         0=old landuse (IGBP.dat); 1=landuse from WRF"
    CBL = (
        cbl
    ) = "    #                CBL SCHEME        0=no, 1=yes. works if TURB_OPTION=1"
    SFC_OPTION = (
        sfc_option
    ) = "    #                SFC_OPTION        0=default computation of u*, hflux, pblh, 1=from wrf"
    WIND_OPTION = (
        wind_option
    ) = "    #                WIND_OPTION       0=snapshot winds, 1=mean winds,2=snapshot eta-dot,-1=w based on divergence"
    TIME_OPTION = (
        time_option
    ) = "    #                TIME_OPTION       1=correction of time validity for time-average wind,  0=no need"
    OUTGRID_COORD = (
        outgrid_coord
    ) = "    #                OUTGRID_COORD     0=wrf grid(meters), 1=regular lat/lon grid"
    RELEASE_COORD = (
        release_coord
    ) = "    #                RELEASE_COORD     0=wrf grid(meters), 1=regular lat/lon grid"
    IOUTTYPE = (
        iouttype
    ) = "    #                IOUTTYPE          0=default binary, 1=ascii (for particle dump only),2=netcdf"
    NCTIMEREC = (
        nctimerec
    ) = "    #                NCTIMEREC (int)   Time frames per output file, only used for netcdf"
    VERBOSE = (
        verbose
    ) = "    #                VERBOSE           VERBOSE MODE,0=minimum, 100=maximum    "


class AgeclassheaderArgs(FlexWrfEnum):
    START_DELIMITER = (
        start_delimiter
    ) = "=====================FORMER AGECLASS FILE==================="
    NAGECLASS = (
        nageclass
    ) = "    #                NAGECLASS        number of age classes"


class AgeclassinstanceArgs(FlexWrfEnum):
    AGECLASS = (
        ageclass
    ) = "    #             SSSSSS  (int)    age class in SSSSS seconds"


class OutgridheaderArgs(FlexWrfEnum):
    START_DELIMITER = (
        start_delimiter
    ) = "=====================FORMER OUTGRID FILE==================="
    OUTLONLEFT = (
        outlonleft
    ) = "  #            OUTLONLEFT      geograhical longitude of lower left corner of output grid"
    OUTLATLOWER = (
        outlatlower
    ) = "  #              OUTLATLOWER     geographical latitude of lower left corner of output grid"
    NUMXGRID = (
        numxgrid
    ) = "  #               NUMXGRID        number of grid points in x direction (= # of cells )"
    NUMYGRID = (
        numygrid
    ) = "  #             NUMYGRID        number of grid points in y direction (= # of cells )"
    OUTGRIDDEF = (
        outgriddef
    ) = "  #              OUTGRIDDEF      outgrid defined 0=using grid distance, 1=upperright corner coordinate"
    DXOUTLON = (
        dxoutlon
    ) = "  #           DXOUTLON        grid distance in x direction or upper right corner of output grid"
    DYOUTLON = (
        dyoutlon
    ) = "  #           DYOUTLON        grid distance in y direction or upper right corner of output grid"
    NUMZGRID = numzgrid = "  #             NUMZGRID        number of vertical levels"


class OutgridinstanceArgs(FlexWrfEnum):
    LEVEL = level = "  #            LEVEL           height of level (upper boundary)"


class OutgridnestArgs(FlexWrfEnum):
    START_DELIMITER = (
        start_delimiter
    ) = "=====================FORMER OUTGRID_NEST FILE==================="
    OUTLONLEFT = (
        outlonleft
    ) = "   #             OUTLONLEFT      geograhical longitude of lower left corner of output grid"
    OUTLATLOWER = (
        outlatlower
    ) = "    #             OUTLATLOWER     geographical latitude of lower left corner of output grid"
    NUMXGRID = (
        numxgrid
    ) = "    #               NUMXGRID        number of grid points in x direction (= # of cells )"
    NUMYGRID = (
        numygrid
    ) = "    #               NUMYGRID        number of grid points in y direction (= # of cells )"
    OUTGRIDDEF = (
        outgriddef
    ) = "    #                OUTGRIDDEF      outgrid defined 0=using grid distance, 1=upperright corner coordinate"
    DXOUTLON = (
        dxoutlon
    ) = "    #            DXOUTLON        grid distance in x direction or upper right corner of output grid"
    DYOUTLON = (
        dyoutlon
    ) = "    #            DYOUTLON        grid distance in y direction or upper right corner of output grid"


class ReceptorheaderArgs(FlexWrfEnum):
    START_DELIMITER = (
        start_delimiter
    ) = "=====================FORMER RECEPTOR FILE==================="
    NUMRECEPTOR = (
        numreceptor
    ) = "    #                NUMRECEPTOR     number of receptors"


class SpeciesheaderArgs(FlexWrfEnum):
    START_DELIMITER = (
        start_delimiter
    ) = "=====================FORMER SPECIES FILE==================="
    NUMTABLE = (
        numtable
    ) = "     #               NUMTABLE        number of variable properties. The following lines are fixed format"
    LEGEND = (
        legend
    ) = "XXXX|NAME    |decaytime |wetscava  |wetsb|drydif|dryhenry|drya|partrho  |parmean|partsig|dryvelo|weight |"


class SpeciesinstanceArgs(FlexWrfEnum):
    SPECIES = species = "     #"


class ReleasesheaderArgs(FlexWrfEnum):
    START_DELIMITER = (
        start_delimiter
    ) = "=====================FORMER RELEASES FILE==================="
    NSPEC = nspec = "#                NSPEC           total number of species emitted"
    EMITVAR = emitvar = "#                EMITVAR         1 for emission variation "


class ReleaseslinkArgs(FlexWrfEnum):
    LINK = link = "#                LINK            index of species in file SPECIES"


class ReleasesnumpointArgs(FlexWrfEnum):
    NUMPOINT = numpoint = "#                 NUMPOINT        number of releases"


class ReleasesinstanceArgs(FlexWrfEnum):
    START = start = "#   ID1, IT1        beginning date and time of release"
    STOP = stop = "#   ID2, IT2        ending date and time of release"
    XPOINT1 = (
        xpoint1
    ) = "    #         XPOINT1 (real)  longitude [deg] of lower left corner"
    YPOINT1 = (
        ypoint1
    ) = "    #         YPOINT1 (real)  latitude [deg] of lower left corner"
    XPOINT2 = (
        xpoint2
    ) = "    #         XPOINT2 (real)  longitude [deg] of upper right corner"
    YPOINT2 = (
        ypoint2
    ) = "    #         YPOINT2 (real)  latitude [DEG] of upper right corner"
    KINDZ = (
        kindz
    ) = "    #         KINDZ  (int)  1 for m above ground, 2 for m above sea level, 3 pressure"
    ZPOINT1 = zpoint1 = "    #        ZPOINT1 (real)  lower z-level"
    ZPOINT2 = zpoint2 = "    #        ZPOINT2 (real)  upper z-level"
    NPART = (
        npart
    ) = "    #          NPART (int)     total number of particles to be released"


class ReleasesinstancexmassArgs(FlexWrfEnum):
    XMASS = xmass = "    #         XMASS (real)    total mass emitted"


class ReleasesinstancenameArgs(FlexWrfEnum):
    NAME = name = "    #              NAME OF RELEASE LOCATION"


####### META OPTIONS #########

# class Option(Enum):
#     PATHNAMES = pathnames = [PathnamesArgs]
#     COMMAND = command = [CommandArgs]
#     AGECLASS = ageclass = [AgeclassheaderArgs, AgeclassinstanceArgs]
#     OUTGRID = outgrid = [OutgridArgs, OutgridlevelArgs]
#     OUTGRID_NEST = outgrid_nest = [OutgridnestArgs]
#     RECEPTOR = receptor = [ReceptorheaderArgs]
#     SPECIES = species = [SpeciesheaderArgs, SpeciesinstanceArgs]
#     RELEASES = releases = [ReleasesheaderArgs, ReleaseslinkArgs, ReleasesnumpointArgs, ReleasesinstanceArgs, ReleasesinstancexmassArgs, ReleasesinstancenameArgs]
