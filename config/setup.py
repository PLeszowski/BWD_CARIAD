A_STEP = 'X100'
SOP = 'SOP1'
CP60_SPEC = False  # True for 0km/h events (always false for CARIAD)
PROJECT = 'mid'  # cp60 or mid (always mid for CARIAD)
CAL_TEST = False  # checks for deviations in pitch in BWD dataset and during failsafe activations, and also for height 0.5m
CAL_TEST_ONLY = False  # don't calculate KPIs, exit after cal check


# use only valid system severity
ONLY_SYS_SEVERITY = True
# calculate KPIs comparing "same signal same severity" (TP only if label = signal severity, FP if signal != label severity)
SPI_EXACT = True
# calculate KPIs comparing "same signal severity +/- 1" (TP if label = signal severity +/- one level, FP if signal != label severity +/- one level)
SPI_EXACT_UP_DOWN = True
# calculate KPIs comparing "backup signal same severity" (TP if label = any backup signal with same severity, FP if signal != any backup label with same severity)
SPI_BACKUP = True
# calculate KPIs comparing "backup signal severity +/-1" (TP if label = any backup signal with severity +/- one level, FP if signal != any backup label with severity +/- one level)
SPI_BACKUP_UP_DOWN = True
# calculate KPIs comparing "backup signal any severity" (TP if label = any backup signal with any severity, FP if signal != any backup label with any severity)
SPI_BACKUP_ANY = True
# calculate KPIs comparing "any signal any severity" (TP if label = any signal with any severity, FP if signal != any label with any severity)
SPI_ANY = True
# calculate KPIs comparing "backup signal any severity that causes degradation" (TP if label that would cause degradation = any signal/backup signal with any severity that would cause degradation)
SPI_DEGRADE = True
# calculate KPIs analyzing simulated flexray verschmutzung signals
FLEXRAY = True
# TPR don't use data below this speed (km/h), 0 = don't use speed threshold
ZERO_SPEED_THRESHOLD = 5
# debounce time (s) for FN noise, 0 = don't use debouncing
DEBOUNCE_TIME_FN_S = 5
# debounce time (s) for FP noise, 0 = don't use debouncing
DEBOUNCE_TIME_FP_S = 2
# Use remove toggling for TP
REMOVE_TOGGLING_TP = True
# Use remove toggling for FP
REMOVE_TOGGLING_FP = True
# KPI report generator
J_NAME = "CARIAD_X110_005"  # same as in start_BWD.sh
KPI_RECOG_TIME = True  # use recognition time in TPR
KPI_GENERATE_DAY = True
KPI_GENERATE_NIGHT = True

