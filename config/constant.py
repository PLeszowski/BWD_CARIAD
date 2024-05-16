import copy
import json

DAYTIME_DICT_FILE = r'C:\Users\wjjymc\PycharmProjects\BWD_CARIAD\config\BWD_daytime.json'
with open(DAYTIME_DICT_FILE, 'r') as f:
    DAYTIME_DICT = json.load(f)


PATH_ITRK = r"c:/Users/wjjymc/PycharmProjects/BWD/BWD_MID_itrks_20220706"
PATH_RESULT = r'c:/Users/wjjymc/PycharmProjects/BWD_CARIAD/logs'
PATH_FAILED_KPI_DFS = r'c:/Users/wjjymc/PycharmProjects/BWD_CARIAD/FAILED_KPI_DFS'

CP60_SPEC_PATH = "c:/Users/wjjymc/PycharmProjects/BWD/cp60_staged_lists/pb_list.json"
CP_60_PICKLES_FILE_LIST = "c:/Users/wjjymc/PycharmProjects/BWD/cp60_staged_lists/f_pb2_list.json"

BAD_LABEL_DICT_FOLDER = r'c:/Users/wjjymc/PycharmProjects/BWD_CARIAD/BWD_BAD_LABELS'
BAD_LABELS_PATH_TO_PARTIAL_RESULTS_CP60 = r'c:\Users\wjjymc\PycharmProjects\BWD_CARIAD\output\spi_backup_any'
BAD_LABELS_PATH_TO_PARTIAL_RESULTS_MID = r'c:\Users\wjjymc\PycharmProjects\BWD_CARIAD\output\spi_backup_any'

A_STEP = 'X060'
SOP = 'SOP1'
CP60_SPEC = False  # True for 0km/h events
PROJECT = 'mid'  # cp60 or mid

if PROJECT == 'cp60':
    DONT_CHECK_ZERO_SPEED = False
else:
    DONT_CHECK_ZERO_SPEED = True

CAL_TEST = False
CAL_TEST_ONLY = False
NO_VALUE = 0
CALIBRATED = 64273
UNVALIDATED = 43923
SUSPECTED = 48290
OOR = 2422

ONLY_SYS_SEVERITY = True
SEVERITY_ANY = 0  # match any failsafe, any severity
SEVERITY_BACKUP = 1  # match FS_Backup_Matrix
SEVERITY_BACKUP_LEVEL_UP_DOWN = 2  # match FS_Backup_Matrix +/- one level
SEVERITY_EXACT = 3  # match exact failsafe, exact severity
SEVERITY_LEVEL_UP_DOWN = 5  # match FS_Backup_Matrix +/- one level without backup signal
SEVERITY_FP_VERSCHMUTZUNG = 6

FREQUENCY = 36
SPI_EXACT = True
SPI_EXACT_UP_DOWN = True
SPI_BACKUP = True
SPI_BACKUP_UP_DOWN = True
SPI_ANY = True
SPI_BACKUP_ANY = True

KPI_GENERATOR_OUTPUT_FOLDER = r"c:\Users\wjjymc\PycharmProjects\BWD_CARIAD\output"
KPI_GENERATE_DAY = True
KPI_GENERATE_NIGHT = True
KPI_RECOG_TIME = False

SYS_BLUR = 'FS_Blur_Image_0'  # CoreProtocol_v4.19.5
SYS_FROZEN_WINDSHIELD = 'FS_Frozen_Windshield_Lens_0'  # CoreProtocol_v4.19.5
SYS_FULL_BLOCKAGE = 'FS_Full_Blockage_0'  # CoreProtocol_v4.19.5
SYS_PARTIAL_BLOCKAGE = 'FS_Partial_Blockage_0'  # CoreProtocol_v4.19.5
SYS_FADING_BY_SUN = 'FS_Low_Sun_0'  # CoreProtocol_v4.19.5
SYS_LIGHT_SWORD = ''
SYS_SUN_RAY = 'FS_Sun_Ray_0'  # CoreProtocol_v4.19.5
SYS_OUT_OF_CALIBRATION = 'FS_Out_Of_Calib_0'  # CoreProtocol_v4.19.5
SYS_OUT_OF_FOCUS = 'FS_Out_Of_Focus_0'  # CoreProtocol_v4.19.5
SYS_RAIN = 'FS_Rain'  # CoreProtocol_v4.19.5
SYS_SNOWFALL = 'FS_Rain'  # ''
SYS_ROAD_SPRAY = 'FS_Splashes_0'  # CoreProtocol_v4.19.5
SYS_FOG = 'FS_Fog'  # CoreProtocol_v4.19.5
SYS_FREEVIEW = 'FS_Free_Sight_0'  # CoreProtocol_v4.19.5
SYS_IMPACTED_TECHNOLOGIES = 'FS_Impacted_Technologies'
# FS_Calibration_Misalignment ???
# FS_Camera_to_Camera_Calib_XX ???

LAB_BLOCKAGE = 'blockage'
LAB_BLUR_IMAGE = 'blurImage'
LAB_FOG = 'fog'
LAB_FROZEN_WINDSHIELD = 'frozenWindshield'
LAB_FULL_BLOCKAGE = 'fullBlockage'
LAB_LOWSUN = 'lowSun'
LAB_PARTIAL_BLOCKAGE = 'partialBlockage'
LAB_SNOWFALL = 'snowfall'
LAB_RAIN = 'rain'
LAB_SPLASHES = 'splashes'
LAB_SUNRAY = 'sunRay'
LAB_OOF = 'outOfFocus'
LAB_FREEVIEW = 'freeview'

CAL_STATE = 'CO_main_safetyState'
CAL_PITCH = 'CO_main2road_euler_pitch'
CAL_YAW = 'CO_main2road_euler_yaw'
CAL_ROLL = 'CO_main2road_euler_roll'
CAL_HEIGHT = 'CO_main_camH'

VALID_SEVERITY_LAB = {LAB_BLUR_IMAGE: [4, 5],
                      LAB_FOG: [2, 5],
                      LAB_FROZEN_WINDSHIELD: [2, 4, 5],
                      LAB_FULL_BLOCKAGE: [5],
                      LAB_LOWSUN: [2, 4, 5],
                      LAB_PARTIAL_BLOCKAGE: [2, 4, 5],
                      LAB_SNOWFALL: [2, 4, 5],
                      LAB_RAIN: [2, 4, 5],
                      LAB_SPLASHES: [2, 4, 5],
                      LAB_OOF: [4, 5],
                      LAB_SUNRAY: [2, 4, 5]}

RECOGNITION_TIME = {
    SYS_BLUR: 5,
    SYS_FROZEN_WINDSHIELD: 5,
    SYS_FULL_BLOCKAGE: 4,
    SYS_PARTIAL_BLOCKAGE: 60,
    SYS_FADING_BY_SUN: 5,
    SYS_SUN_RAY: 7,
    SYS_OUT_OF_CALIBRATION: 0,
    SYS_OUT_OF_FOCUS: 0,
    SYS_RAIN: 7,
    SYS_SNOWFALL: 5,
    SYS_ROAD_SPRAY: 5,
    SYS_FOG: 5,
    SYS_FREEVIEW: 5,
    SYS_IMPACTED_TECHNOLOGIES: 0
}

SEVERITY_LAB = {LAB_BLOCKAGE: {0: '25', 1: '99'},
                LAB_BLUR_IMAGE: {2: '25', 3: '50', 4: '75', 5: '99'},
                LAB_FOG: {2: '25', 3: '50', 4: '75', 5: '99'},
                LAB_FROZEN_WINDSHIELD: {2: '25', 3: '50', 4: '75', 5: '99'},
                LAB_FULL_BLOCKAGE: {2: '25', 3: '50', 4: '75', 5: '99'},
                LAB_LOWSUN: {2: '25', 3: '50', 4: '75', 5: '99'},
                LAB_PARTIAL_BLOCKAGE: {2: '25', 3: '50', 4: '75', 5: '99'},
                LAB_SNOWFALL: {2: '25', 3: '50', 4: '75', 5: '99'},
                LAB_RAIN: {2: '25', 3: '50', 4: '75', 5: '99'},
                LAB_SPLASHES: {2: '25', 3: '50', 4: '75', 5: '99'},
                LAB_SUNRAY: {2: '25', 3: '50', 4: '75', 5: '99'},
                LAB_OOF: {4: '75', 5: '99'},
                LAB_FREEVIEW: {5: '99'}}

SEVERITY_SYS = {'25': 2,
                '75': 4,
                '99': 5}

SEVERITY_MAP = {2: '25',
                4: '75',
                5: '99'}

SEVERITY_SYS_LIST = [2, 4, 5]

SYS_AVAILABLE_SEVERITY = {
    LAB_BLUR_IMAGE: [4, 5],
    LAB_FOG: [2, 5],
    LAB_FROZEN_WINDSHIELD: [2, 4, 5],
    LAB_FULL_BLOCKAGE: [5],
    LAB_LOWSUN: [2, 4, 5],
    LAB_PARTIAL_BLOCKAGE: [2, 4, 5],
    LAB_SNOWFALL: [2, 4, 5],
    LAB_RAIN: [2, 4, 5],
    LAB_SPLASHES: [2, 4, 5],
    LAB_SUNRAY: [2, 4, 5],
    LAB_OOF: [4, 5],
    LAB_FREEVIEW: [0]
}

SYS_ALL = [SYS_BLUR, SYS_FROZEN_WINDSHIELD, SYS_FULL_BLOCKAGE, SYS_PARTIAL_BLOCKAGE, SYS_FADING_BY_SUN, SYS_SUN_RAY,
           SYS_RAIN, SYS_ROAD_SPRAY, SYS_FOG, SYS_OUT_OF_FOCUS]
CAL_ALL = [CAL_STATE, CAL_PITCH, CAL_YAW, CAL_ROLL, CAL_HEIGHT]

LAB_ALL = [LAB_BLUR_IMAGE, LAB_FOG, LAB_FROZEN_WINDSHIELD, LAB_FULL_BLOCKAGE, LAB_LOWSUN, LAB_PARTIAL_BLOCKAGE, LAB_RAIN, LAB_SPLASHES, LAB_SUNRAY, LAB_OOF]

LAB_TO_SYS = {LAB_BLUR_IMAGE: [SYS_BLUR],
              LAB_FOG: [SYS_FOG],
              LAB_FROZEN_WINDSHIELD: [SYS_FROZEN_WINDSHIELD],
              LAB_FULL_BLOCKAGE: [SYS_FULL_BLOCKAGE],
              LAB_LOWSUN: [SYS_FADING_BY_SUN],
              LAB_PARTIAL_BLOCKAGE: [SYS_PARTIAL_BLOCKAGE],
              LAB_SNOWFALL: [SYS_SNOWFALL],
              LAB_RAIN: [SYS_RAIN],
              LAB_SPLASHES: [SYS_ROAD_SPRAY],
              LAB_SUNRAY: [SYS_SUN_RAY],
              LAB_OOF: [SYS_OUT_OF_FOCUS],
              LAB_FREEVIEW: SYS_ALL}

LAB_TO_SPI_BACKUP = {
    LAB_BLUR_IMAGE: [SYS_BLUR, SYS_FOG, SYS_FADING_BY_SUN, SYS_RAIN, SYS_ROAD_SPRAY, SYS_FROZEN_WINDSHIELD],
    LAB_FOG: [SYS_FOG, SYS_BLUR],
    LAB_FROZEN_WINDSHIELD: [SYS_FROZEN_WINDSHIELD, SYS_FULL_BLOCKAGE, SYS_PARTIAL_BLOCKAGE, SYS_BLUR,
                            SYS_FOG],
    LAB_FULL_BLOCKAGE: [SYS_FULL_BLOCKAGE, SYS_PARTIAL_BLOCKAGE, SYS_FROZEN_WINDSHIELD],
    LAB_LOWSUN: [SYS_FADING_BY_SUN, SYS_SUN_RAY],
    LAB_PARTIAL_BLOCKAGE: [SYS_PARTIAL_BLOCKAGE, SYS_FROZEN_WINDSHIELD, SYS_FULL_BLOCKAGE],
    LAB_SNOWFALL: [SYS_RAIN, SYS_ROAD_SPRAY, SYS_BLUR],
    LAB_RAIN: [SYS_RAIN, SYS_ROAD_SPRAY, SYS_BLUR],
    LAB_SPLASHES: [SYS_ROAD_SPRAY, SYS_RAIN, SYS_BLUR],
    LAB_SUNRAY: [SYS_SUN_RAY, SYS_FADING_BY_SUN],
    LAB_OOF: [SYS_OUT_OF_FOCUS],
    LAB_FREEVIEW: SYS_ALL}

SYS_TO_LAB2 = {
    SYS_BLUR: [LAB_BLUR_IMAGE, LAB_FOG, LAB_FROZEN_WINDSHIELD, LAB_SNOWFALL, LAB_RAIN, LAB_SPLASHES],
    SYS_FOG: [LAB_FOG, LAB_BLUR_IMAGE],
    SYS_FROZEN_WINDSHIELD: [LAB_FROZEN_WINDSHIELD, LAB_BLUR_IMAGE, LAB_FOG, LAB_PARTIAL_BLOCKAGE],
    SYS_FULL_BLOCKAGE: [LAB_FULL_BLOCKAGE, LAB_FROZEN_WINDSHIELD, LAB_PARTIAL_BLOCKAGE],
    SYS_FADING_BY_SUN: [LAB_LOWSUN, LAB_SUNRAY],
    SYS_PARTIAL_BLOCKAGE: [LAB_PARTIAL_BLOCKAGE, LAB_FROZEN_WINDSHIELD, LAB_FULL_BLOCKAGE],
    SYS_SNOWFALL: [LAB_SNOWFALL, LAB_BLUR_IMAGE, LAB_RAIN, LAB_SPLASHES],
    SYS_RAIN: [LAB_RAIN, LAB_BLUR_IMAGE, LAB_SNOWFALL, LAB_SPLASHES],
    SYS_ROAD_SPRAY: [LAB_SPLASHES, LAB_BLUR_IMAGE, LAB_SNOWFALL, LAB_RAIN],
    SYS_OUT_OF_FOCUS: [LAB_OOF],
    SYS_SUN_RAY: [LAB_SUNRAY, LAB_LOWSUN]
}

LAB_TO_SPI_ALL = {LAB_BLUR_IMAGE: SYS_ALL,
                  LAB_FOG: SYS_ALL,
                  LAB_FROZEN_WINDSHIELD: SYS_ALL,
                  LAB_FULL_BLOCKAGE: SYS_ALL,
                  LAB_LOWSUN: SYS_ALL,
                  LAB_PARTIAL_BLOCKAGE: SYS_ALL,
                  LAB_SNOWFALL: SYS_ALL,
                  LAB_RAIN: SYS_ALL,
                  LAB_SPLASHES: SYS_ALL,
                  LAB_SUNRAY: SYS_ALL,
                  LAB_OOF: SYS_ALL,
                  LAB_FREEVIEW: SYS_ALL}

SYS_TO_LAB = {
    SYS_BLUR: [LAB_BLUR_IMAGE, LAB_FOG, LAB_FROZEN_WINDSHIELD, LAB_FULL_BLOCKAGE, LAB_LOWSUN, LAB_PARTIAL_BLOCKAGE, LAB_SNOWFALL, LAB_RAIN, LAB_SPLASHES, LAB_OOF, LAB_SUNRAY],
    SYS_FOG: [LAB_FOG, LAB_BLUR_IMAGE, LAB_FROZEN_WINDSHIELD, LAB_FULL_BLOCKAGE, LAB_LOWSUN, LAB_PARTIAL_BLOCKAGE, LAB_SNOWFALL, LAB_RAIN, LAB_SPLASHES, LAB_OOF, LAB_SUNRAY],
    SYS_FROZEN_WINDSHIELD: [LAB_FROZEN_WINDSHIELD, LAB_BLUR_IMAGE, LAB_FOG, LAB_FULL_BLOCKAGE, LAB_LOWSUN, LAB_PARTIAL_BLOCKAGE, LAB_SNOWFALL, LAB_RAIN, LAB_SPLASHES, LAB_OOF, LAB_SUNRAY],
    SYS_FULL_BLOCKAGE: [LAB_FULL_BLOCKAGE, LAB_BLUR_IMAGE, LAB_FOG, LAB_FROZEN_WINDSHIELD, LAB_LOWSUN, LAB_PARTIAL_BLOCKAGE, LAB_SNOWFALL, LAB_RAIN, LAB_SPLASHES, LAB_OOF, LAB_SUNRAY],
    SYS_FADING_BY_SUN: [LAB_LOWSUN, LAB_BLUR_IMAGE, LAB_FOG, LAB_FROZEN_WINDSHIELD, LAB_FULL_BLOCKAGE, LAB_PARTIAL_BLOCKAGE, LAB_SNOWFALL, LAB_RAIN, LAB_SPLASHES, LAB_OOF, LAB_SUNRAY],
    SYS_PARTIAL_BLOCKAGE: [LAB_PARTIAL_BLOCKAGE, LAB_BLUR_IMAGE, LAB_FOG, LAB_FROZEN_WINDSHIELD, LAB_FULL_BLOCKAGE, LAB_LOWSUN, LAB_SNOWFALL, LAB_RAIN, LAB_SPLASHES, LAB_OOF, LAB_SUNRAY],
    SYS_SNOWFALL: [LAB_SNOWFALL, LAB_BLUR_IMAGE, LAB_FOG, LAB_FROZEN_WINDSHIELD, LAB_FULL_BLOCKAGE, LAB_LOWSUN, LAB_PARTIAL_BLOCKAGE, LAB_RAIN, LAB_SPLASHES, LAB_OOF, LAB_SUNRAY],
    SYS_RAIN: [LAB_RAIN, LAB_BLUR_IMAGE, LAB_FOG, LAB_FROZEN_WINDSHIELD, LAB_FULL_BLOCKAGE, LAB_LOWSUN, LAB_PARTIAL_BLOCKAGE, LAB_SNOWFALL, LAB_SPLASHES, LAB_OOF, LAB_SUNRAY],
    SYS_ROAD_SPRAY: [LAB_SPLASHES, LAB_BLUR_IMAGE, LAB_FOG, LAB_FROZEN_WINDSHIELD, LAB_FULL_BLOCKAGE, LAB_LOWSUN, LAB_PARTIAL_BLOCKAGE, LAB_SNOWFALL, LAB_RAIN, LAB_OOF, LAB_SUNRAY],
    SYS_OUT_OF_FOCUS: [LAB_OOF, LAB_SUNRAY, LAB_BLUR_IMAGE, LAB_FOG, LAB_FROZEN_WINDSHIELD, LAB_FULL_BLOCKAGE, LAB_LOWSUN, LAB_PARTIAL_BLOCKAGE, LAB_SNOWFALL, LAB_RAIN, LAB_SPLASHES],
    SYS_SUN_RAY: [LAB_SUNRAY, LAB_BLUR_IMAGE, LAB_FOG, LAB_FROZEN_WINDSHIELD, LAB_FULL_BLOCKAGE, LAB_LOWSUN, LAB_PARTIAL_BLOCKAGE, LAB_SNOWFALL, LAB_RAIN, LAB_SPLASHES, LAB_OOF]
}

LAB_BACKUP = {
    LAB_BLUR_IMAGE: [LAB_FOG, LAB_FROZEN_WINDSHIELD, LAB_LOWSUN, LAB_SNOWFALL, LAB_RAIN, LAB_SPLASHES],
    LAB_FOG: [LAB_BLUR_IMAGE],
    LAB_FROZEN_WINDSHIELD: [LAB_BLUR_IMAGE, LAB_FOG, LAB_FULL_BLOCKAGE, LAB_PARTIAL_BLOCKAGE],
    LAB_FULL_BLOCKAGE: [LAB_FROZEN_WINDSHIELD, LAB_PARTIAL_BLOCKAGE],
    LAB_LOWSUN: [LAB_SUNRAY],
    LAB_PARTIAL_BLOCKAGE: [LAB_FROZEN_WINDSHIELD, LAB_FULL_BLOCKAGE],
    LAB_SNOWFALL: [LAB_BLUR_IMAGE, LAB_RAIN, LAB_SPLASHES],
    LAB_RAIN: [LAB_BLUR_IMAGE, LAB_SNOWFALL, LAB_SPLASHES],
    LAB_SPLASHES: [LAB_BLUR_IMAGE, LAB_SNOWFALL, LAB_RAIN],
    LAB_OOF: [],
    LAB_SUNRAY: [LAB_LOWSUN]
}

TO_CHECK_FOR_FALSE_POSITIVES = [LAB_BLUR_IMAGE, LAB_FOG, LAB_FROZEN_WINDSHIELD, LAB_FULL_BLOCKAGE, LAB_LOWSUN,
                                LAB_PARTIAL_BLOCKAGE, LAB_SNOWFALL, LAB_RAIN, LAB_SPLASHES, LAB_OOF, LAB_SUNRAY, LAB_FREEVIEW]

TO_CHECK_FOR_TRUE_POSITIVES = [LAB_BLUR_IMAGE, LAB_FOG, LAB_FROZEN_WINDSHIELD, LAB_FULL_BLOCKAGE, LAB_LOWSUN,
                               LAB_PARTIAL_BLOCKAGE, LAB_SNOWFALL, LAB_RAIN, LAB_SPLASHES, LAB_OOF, LAB_SUNRAY, LAB_FREEVIEW]

SYS = [SYS_FROZEN_WINDSHIELD, SYS_FULL_BLOCKAGE, SYS_PARTIAL_BLOCKAGE, SYS_FADING_BY_SUN, SYS_BLUR,
       SYS_SUN_RAY, SYS_OUT_OF_CALIBRATION, SYS_OUT_OF_FOCUS, SYS_RAIN, SYS_ROAD_SPRAY, SYS_FOG,
       SYS_FREEVIEW, SYS_IMPACTED_TECHNOLOGIES]

LAB = [LAB_BLUR_IMAGE, LAB_FOG, LAB_FROZEN_WINDSHIELD, LAB_FULL_BLOCKAGE, LAB_LOWSUN,  # LAB_FREEVIEW,#LAB_BLOCKAGE,
       LAB_PARTIAL_BLOCKAGE, LAB_SNOWFALL, LAB_RAIN, LAB_SPLASHES, LAB_OOF, LAB_SUNRAY]

KPI_NAMES_INIT = ['Blur', 'Frozen Windshield', 'Full Blockage', 'Partial Blockage', 'Fading by Sun', 'Sun Ray', 'Rain',
                  'Snowfall', 'Road Spray', 'Fog', 'Out of Focus', 'Free View']

KPI_NAMES_VSPEED_INIT = ['Total', 'Blur', 'Frozen Windshield', 'Full Blockage', 'Partial Blockage', 'Fading by Sun', 'Sun Ray', 'Rain',
                         'Snowfall', 'Road Spray', 'Fog', 'Out of Focus']

KPI_NAMES_INIT_25 = ['Partial Blockage', 'Fading by Sun', 'Sun Ray', 'Rain',
                     'Snowfall', 'Road Spray', 'Fog', 'Free View']

KPI_NAMES_INIT_75 = ['Blur', 'Partial Blockage', 'Rain',
                     'Snowfall', 'Out of Focus', 'Free View']

KPI_NAMES_INIT_99 = ['Blur', 'Frozen Windshield', 'Full Blockage', 'Partial Blockage', 'Fading by Sun', 'Sun Ray', 'Rain',
                     'Snowfall', 'Road Spray', 'Fog', 'Out of Focus', 'Free View']

PARTIALS_NAMES_LAB = {
    LAB_BLUR_IMAGE: 'Blur',
    LAB_FOG: 'Fog',
    LAB_FROZEN_WINDSHIELD: 'Frozen Windshield',
    LAB_FULL_BLOCKAGE: 'Full Blockage',
    LAB_LOWSUN: 'Fading by Sun',
    LAB_PARTIAL_BLOCKAGE: 'Partial Blockage',
    LAB_SNOWFALL: 'Snowfall',
    LAB_RAIN: 'Rain',
    LAB_SPLASHES: 'Road Spray',
    LAB_OOF: 'Out of Focus',
    LAB_SUNRAY: 'Sun Ray',
    LAB_FREEVIEW: 'Free View'
}

DETECTION_THRESHOLD = {PARTIALS_NAMES_LAB[LAB_BLUR_IMAGE]: 5,
                       PARTIALS_NAMES_LAB[LAB_FROZEN_WINDSHIELD]: 5,
                       PARTIALS_NAMES_LAB[LAB_FULL_BLOCKAGE]: 4,
                       PARTIALS_NAMES_LAB[LAB_PARTIAL_BLOCKAGE]: 60,
                       PARTIALS_NAMES_LAB[LAB_LOWSUN]: 5,
                       PARTIALS_NAMES_LAB[LAB_SUNRAY]: 7,
                       PARTIALS_NAMES_LAB[LAB_RAIN]: 7,
                       PARTIALS_NAMES_LAB[LAB_SNOWFALL]: 5,
                       PARTIALS_NAMES_LAB[LAB_SPLASHES]: 5,
                       PARTIALS_NAMES_LAB[LAB_OOF]: 5,
                       PARTIALS_NAMES_LAB[LAB_FOG]: 5,
                       PARTIALS_NAMES_LAB[LAB_FREEVIEW]: 5
                       }

PARTIALS_NAMES_SYS = {
    SYS_BLUR: 'Blur',
    SYS_FOG: 'Fog',
    SYS_FROZEN_WINDSHIELD: 'Frozen Windshield',
    SYS_FULL_BLOCKAGE: 'Full Blockage',
    SYS_FADING_BY_SUN: 'Fading by Sun',
    SYS_PARTIAL_BLOCKAGE: 'Partial Blockage',
    SYS_RAIN: 'Rain',
    SYS_ROAD_SPRAY: 'Road Spray',
    SYS_SUN_RAY: 'Sun Ray',
    SYS_OUT_OF_FOCUS: 'Out of Focus',
    SYS_FREEVIEW: 'Free View'
}

CP_NOT_READY = 'NOT_READY'
CP_NONE = "NONE"
CP_25 = "low"
CP_50 = "50"
CP_75 = "mid"
CP_99 = "high"
CP_IGNORE = 'ignore'
CP_CAMERA_ID_MAIN = "main"
CP_CAMERA_ID_FRONT_NARROW = "narrow"
CP_CAMERA_ID_FRONT_FISHEYE = "fisheye"
CP_CAMERA_ID_REAR = "rear"
CP_CAMERA_ID_REAR_CORNER_LEFT = "rearCornerLeft"
CP_CAMERA_ID_REAR_CORNER_RIGHT = "rearCornerRight"
CP_CAMERA_ID_FRONT_CORNER_LEFT = "frontCornerLeft"
CP_CAMERA_ID_FRONT_CORNER_RIGHT = "frontCornerRight"
CP_CAMERA_ID_PARKING_FRONT = "parking_front"
CP_CAMERA_ID_PARKING_REAR = "parking_rear"
CP_CAMERA_ID_PARKING_LEFT = "parking_left"
CP_CAMERA_ID_PARKING_RIGHT = "parking_right"

CORE_PROTOCOL_MAPPING = {
    CP_NOT_READY: 10,
    CP_NONE: 1,
    CP_25: 2,
    CP_50: 3,
    CP_75: 4,
    CP_99: 5,
    CP_IGNORE: 9,
    CP_CAMERA_ID_MAIN: 100,
    CP_CAMERA_ID_FRONT_NARROW: 101,
    CP_CAMERA_ID_FRONT_FISHEYE: 102,
    CP_CAMERA_ID_REAR: 103,
    CP_CAMERA_ID_REAR_CORNER_LEFT: 104,
    CP_CAMERA_ID_REAR_CORNER_RIGHT: 105,
    CP_CAMERA_ID_FRONT_CORNER_LEFT: 106,
    CP_CAMERA_ID_FRONT_CORNER_RIGHT: 107,
    CP_CAMERA_ID_PARKING_FRONT: 108,
    CP_CAMERA_ID_PARKING_REAR: 109,
    CP_CAMERA_ID_PARKING_LEFT: 110,
    CP_CAMERA_ID_PARKING_RIGHT: 111
}

FILE_NAME_PATTERN = re_filename = r'^(?P<project>adcam|hpad|conti{1})(_{1})(?P<comment>[a-z0-9]*)(_?)(?P<vin>[a-z0-9]{17})(_{1})(?P<date>[0-9]{8})(_{1})(?P<time>[0-9]{6})(_{1})(?P<extension>oth|dlt|eth|bus|tap|deb|tcd|ref|v01|v02|v03|v04|v05|v06|v07|v08|pic){0,1}(_?)(?P<number>[0-9]+)'

BWD_COLUMNS = ['File_Name', 'itrk_name', 'timestamp', 'grabIndex', 'COM_Cam_Frame_ID', 'Velocity'] + LAB + SYS_ALL + CAL_ALL

# FAILED KPI DATAFRAME NAMES -------------------------------------------------------------------------------------------
# New failed kpi dataframe constants
FAILED_KPI_NO_DETECTION = 'No Detection'  # False negative - no detection on signal and backup signals in whole event
FAILED_KPI_WRONG_SEVERITY = 'Wrong Severity'  # False negative - detected severity doesn't match labeled severity*
FAILED_KPI_FALSE_DETECTION = 'False Detection'  # False positive - system detected a failsafe but no failsafe was labeled
FAILED_KPI_WRONG_DETECTION = 'Wrong Detection'  # False positive - system detected a failsafe but a different failsafe was labeled*
# *severity level mismatch and backup signals depend on input dataframe to df_collector add_df method
FAILED_KPI_TYPES = [FAILED_KPI_NO_DETECTION, FAILED_KPI_WRONG_SEVERITY, FAILED_KPI_FALSE_DETECTION, FAILED_KPI_WRONG_DETECTION]

FAILED_KPI_TYPE = 'Type'
FAILED_KPI_FAILURE_TYPE = 'FailureType'
FAILED_KPI_ID = 'Id'
FAILED_KPI_GID = 'Gid'
FAILED_KPI_SOP = 'SOP'
FAILED_KPI_ASTEP = 'Astep'
FAILED_KPI_PATH = 'Path'
FAILED_KPI_ITRK = 'Itrkname'
FAILED_KPI_FUNC = 'Function'
FAILED_KPI_PROJECT = 'Project'
FAILED_KPI_FILENAME = 'File_Name'
FAILED_KPI_SPLIT_GID = 'Split_Gid'
FAILED_KPI_FN_EVENTS = [LAB_BLUR_IMAGE, LAB_FOG, LAB_FROZEN_WINDSHIELD, LAB_FULL_BLOCKAGE, LAB_LOWSUN,
                        LAB_PARTIAL_BLOCKAGE, LAB_SNOWFALL, LAB_RAIN, LAB_SPLASHES, LAB_SUNRAY, LAB_OOF]
FAILED_KPI_FP_EVENTS = [SYS_BLUR, SYS_FROZEN_WINDSHIELD, SYS_FULL_BLOCKAGE, SYS_PARTIAL_BLOCKAGE, SYS_FADING_BY_SUN,
                        SYS_SUN_RAY, SYS_RAIN, SYS_ROAD_SPRAY, SYS_FOG, SYS_OUT_OF_FOCUS]
FAILED_KPI_EVENTS = FAILED_KPI_FN_EVENTS + FAILED_KPI_FP_EVENTS
FAILED_KPI_DF_COLUMNS = [FAILED_KPI_TYPE, FAILED_KPI_FAILURE_TYPE, FAILED_KPI_ID, FAILED_KPI_GID, FAILED_KPI_SOP,
                         FAILED_KPI_ASTEP, FAILED_KPI_PATH, FAILED_KPI_ITRK, FAILED_KPI_FUNC, FAILED_KPI_PROJECT]
FAILED_KPI_MASTER_DF_COLUMNS = FAILED_KPI_DF_COLUMNS + FAILED_KPI_EVENTS
PERCENTILE_RECOG_TIME_COL = [i for i in range(0, 105, 5)]
ITRK_LAB_NAMES = [LAB_BLUR_IMAGE, LAB_FOG, LAB_FROZEN_WINDSHIELD, LAB_FULL_BLOCKAGE, LAB_LOWSUN, LAB_PARTIAL_BLOCKAGE,
                  LAB_SNOWFALL, LAB_RAIN, LAB_SPLASHES, LAB_SUNRAY, LAB_OOF]

LAB_SIG_COUNTER_COLUMNS = FAILED_KPI_FN_EVENTS + FAILED_KPI_FP_EVENTS

SEVERITY_BACKUP_SPI = {
    LAB_BLUR_IMAGE: {4: {SYS_BLUR: [4], SYS_FOG: [2, 5], SYS_FROZEN_WINDSHIELD: [5], SYS_FADING_BY_SUN: [2, 5], SYS_RAIN: [4], SYS_ROAD_SPRAY: [4]},
                     5: {SYS_BLUR: [5], SYS_FOG: [5], SYS_FROZEN_WINDSHIELD: [5], SYS_FADING_BY_SUN: [5], SYS_RAIN: [5], SYS_ROAD_SPRAY: [5]}},
    LAB_FOG: {2: {SYS_FOG: [2], SYS_BLUR: [4]},
              5: {SYS_FOG: [5], SYS_BLUR: [5]}},
    LAB_FROZEN_WINDSHIELD: {2: {SYS_FROZEN_WINDSHIELD: [2], SYS_BLUR: [4], SYS_FOG: [2, 5], SYS_FULL_BLOCKAGE: [5], SYS_PARTIAL_BLOCKAGE: [2]},
                            4: {SYS_FROZEN_WINDSHIELD: [4], SYS_BLUR: [4], SYS_FOG: [2, 5], SYS_FULL_BLOCKAGE: [5], SYS_PARTIAL_BLOCKAGE: [4]},
                            5: {SYS_FROZEN_WINDSHIELD: [5], SYS_BLUR: [5], SYS_FOG: [5], SYS_FULL_BLOCKAGE: [5], SYS_PARTIAL_BLOCKAGE: [5]}},
    LAB_FULL_BLOCKAGE: {5: {SYS_FULL_BLOCKAGE: [5], SYS_FROZEN_WINDSHIELD: [5], SYS_PARTIAL_BLOCKAGE: [5]}},
    LAB_LOWSUN: {2: {SYS_FADING_BY_SUN: [2], SYS_SUN_RAY: [2]},
                 4: {SYS_FADING_BY_SUN: [4], SYS_SUN_RAY: [4]},
                 5: {SYS_FADING_BY_SUN: [5], SYS_SUN_RAY: [5]}},
    LAB_SUNRAY: {2: {SYS_SUN_RAY: [2], SYS_FADING_BY_SUN: [2]},
                 4: {SYS_SUN_RAY: [4], SYS_FADING_BY_SUN: [4]},
                 5: {SYS_SUN_RAY: [5], SYS_FADING_BY_SUN: [5]}},
    LAB_RAIN: {2: {SYS_RAIN: [2], SYS_BLUR: [4], SYS_ROAD_SPRAY: [2]},
               4: {SYS_RAIN: [4], SYS_BLUR: [4], SYS_ROAD_SPRAY: [4]},
               5: {SYS_RAIN: [5], SYS_BLUR: [5], SYS_ROAD_SPRAY: [5]}},
    LAB_SNOWFALL: {2: {SYS_SNOWFALL: [2], SYS_BLUR: [4], SYS_ROAD_SPRAY: [2]},
                   4: {SYS_SNOWFALL: [4], SYS_BLUR: [4], SYS_ROAD_SPRAY: [4]},
                   5: {SYS_SNOWFALL: [5], SYS_BLUR: [5], SYS_ROAD_SPRAY: [5]}},
    LAB_PARTIAL_BLOCKAGE: {2: {SYS_PARTIAL_BLOCKAGE: [2], SYS_FROZEN_WINDSHIELD: [2]},
                           4: {SYS_PARTIAL_BLOCKAGE: [4], SYS_FROZEN_WINDSHIELD: [4], SYS_FULL_BLOCKAGE: [5]},
                           5: {SYS_PARTIAL_BLOCKAGE: [5], SYS_FROZEN_WINDSHIELD: [5], SYS_FULL_BLOCKAGE: [5]}},
    LAB_SPLASHES: {2: {SYS_ROAD_SPRAY: [2], SYS_BLUR: [4], SYS_RAIN: [2]},
                   4: {SYS_ROAD_SPRAY: [4], SYS_BLUR: [4], SYS_RAIN: [4]},
                   5: {SYS_ROAD_SPRAY: [5], SYS_BLUR: [5], SYS_RAIN: [5]}},
    LAB_OOF: {4: {SYS_OUT_OF_FOCUS: [4]},
              5: {SYS_OUT_OF_FOCUS: [5]}}
}

SEVERITY_BACKUP_SPI_ONE_LEVEL_UP_DOWN = {
    LAB_BLUR_IMAGE: {4: {SYS_BLUR: [4, 5], SYS_FOG: [2, 5], SYS_FROZEN_WINDSHIELD: [4, 5], SYS_FADING_BY_SUN: [2, 4, 5], SYS_RAIN: [2, 4, 5], SYS_ROAD_SPRAY: [2, 4, 5]},
                     5: {SYS_BLUR: [4, 5], SYS_FOG: [2, 5], SYS_FROZEN_WINDSHIELD: [4, 5], SYS_FADING_BY_SUN: [4, 5], SYS_RAIN: [4, 5], SYS_ROAD_SPRAY: [4, 5]}},
    LAB_FOG: {2: {SYS_FOG: [2, 5], SYS_BLUR: [4]},
              5: {SYS_FOG: [2, 5], SYS_BLUR: [4, 5]}},
    LAB_FROZEN_WINDSHIELD: {2: {SYS_FROZEN_WINDSHIELD: [2, 4], SYS_BLUR: [4], SYS_FOG: [2, 5], SYS_FULL_BLOCKAGE: [5], SYS_PARTIAL_BLOCKAGE: [4]},
                            4: {SYS_FROZEN_WINDSHIELD: [2, 4, 5], SYS_BLUR: [4, 5], SYS_FOG: [2, 5], SYS_FULL_BLOCKAGE: [5], SYS_PARTIAL_BLOCKAGE: [2, 4, 5]},
                            5: {SYS_FROZEN_WINDSHIELD: [4, 5], SYS_BLUR: [4, 5], SYS_FOG: [2, 5], SYS_FULL_BLOCKAGE: [5], SYS_PARTIAL_BLOCKAGE: [4, 5]}},
    LAB_FULL_BLOCKAGE: {5: {SYS_FULL_BLOCKAGE: [5], SYS_FROZEN_WINDSHIELD: [5], SYS_PARTIAL_BLOCKAGE: [4, 5]}},
    LAB_LOWSUN: {2: {SYS_FADING_BY_SUN: [2, 5], SYS_SUN_RAY: [2, 4]},
                 4: {SYS_FADING_BY_SUN: [2, 4, 5], SYS_SUN_RAY: [2, 4, 5]},
                 5: {SYS_FADING_BY_SUN: [4, 5], SYS_SUN_RAY: [4, 5]}},
    LAB_SUNRAY: {2: {SYS_SUN_RAY: [2, 4], SYS_FADING_BY_SUN: [2, 5]},
                 4: {SYS_SUN_RAY: [2, 4, 5], SYS_FADING_BY_SUN: [2, 4, 5]},
                 5: {SYS_SUN_RAY: [4, 5], SYS_FADING_BY_SUN: [4, 5]}},
    LAB_RAIN: {2: {SYS_RAIN: [2, 4], SYS_BLUR: [4], SYS_ROAD_SPRAY: [2, 4]},
               4: {SYS_RAIN: [2, 4, 5], SYS_BLUR: [4, 5], SYS_ROAD_SPRAY: [2, 4, 5]},
               5: {SYS_RAIN: [4, 5], SYS_BLUR: [4, 5], SYS_ROAD_SPRAY: [4, 5]}},
    LAB_SNOWFALL: {2: {SYS_SNOWFALL: [2, 4], SYS_BLUR: [4], SYS_ROAD_SPRAY: [2, 4]},
                   4: {SYS_SNOWFALL: [2, 4, 5], SYS_BLUR: [4, 5], SYS_ROAD_SPRAY: [2, 4, 5]},
                   5: {SYS_SNOWFALL: [4, 5], SYS_BLUR: [4, 5], SYS_ROAD_SPRAY: [4, 5]}},
    LAB_PARTIAL_BLOCKAGE: {2: {SYS_PARTIAL_BLOCKAGE: [2, 4], SYS_FROZEN_WINDSHIELD: [2, 4]},
                           4: {SYS_PARTIAL_BLOCKAGE: [2, 4, 5], SYS_FROZEN_WINDSHIELD: [2, 4, 5], SYS_FULL_BLOCKAGE: [5]},
                           5: {SYS_PARTIAL_BLOCKAGE: [4, 5], SYS_FROZEN_WINDSHIELD: [4, 5], SYS_FULL_BLOCKAGE: [5]}},
    LAB_SPLASHES: {2: {SYS_ROAD_SPRAY: [2, 4], SYS_BLUR: [4], SYS_RAIN: [2, 4]},
                   4: {SYS_ROAD_SPRAY: [2, 4, 5], SYS_BLUR: [4, 5], SYS_RAIN: [2, 4, 5]},
                   5: {SYS_ROAD_SPRAY: [4, 5], SYS_BLUR: [4, 5], SYS_RAIN: [4, 5]}},
    LAB_OOF: {4: {SYS_OUT_OF_FOCUS: [4, 5]},
              5: {SYS_OUT_OF_FOCUS: [4, 5]}}
}

# SPI severity +- 1 available level (no backup signals)-> according to FS_Backup_Matrix.xlsx
SEVERITY_SPI_ONE_LEVEL_UP_DOWN = {
    LAB_BLUR_IMAGE: {4: {SYS_BLUR: [4, 5]},
                     5: {SYS_BLUR: [4, 5]}},
    LAB_FOG: {2: {SYS_FOG: [2, 5]},
              5: {SYS_FOG: [2, 5]}},
    LAB_FROZEN_WINDSHIELD: {2: {SYS_FROZEN_WINDSHIELD: [2, 4]},
                            4: {SYS_FROZEN_WINDSHIELD: [2, 4, 5]},
                            5: {SYS_FROZEN_WINDSHIELD: [4, 5]}},
    LAB_FULL_BLOCKAGE: {5: {SYS_FULL_BLOCKAGE: [5]}},
    LAB_LOWSUN: {2: {SYS_FADING_BY_SUN: [2, 4]},
                 4: {SYS_FADING_BY_SUN: [2, 4, 5]},
                 5: {SYS_FADING_BY_SUN: [2, 5]}},
    LAB_SUNRAY: {2: {SYS_SUN_RAY: [2, 4]},
                 4: {SYS_SUN_RAY: [2, 4, 5]},
                 5: {SYS_SUN_RAY: [4, 5]}},
    LAB_RAIN: {2: {SYS_RAIN: [2, 4]},
               4: {SYS_RAIN: [2, 4, 5]},
               5: {SYS_RAIN: [4, 5]}},
    LAB_SNOWFALL: {2: {SYS_SNOWFALL: [2, 4]},
                   4: {SYS_SNOWFALL: [2, 4, 5]},
                   5: {SYS_SNOWFALL: [4, 5]}},
    LAB_PARTIAL_BLOCKAGE: {2: {SYS_PARTIAL_BLOCKAGE: [2, 4]},
                           4: {SYS_PARTIAL_BLOCKAGE: [2, 4, 5]},
                           5: {SYS_PARTIAL_BLOCKAGE: [4, 5]}},
    LAB_SPLASHES: {2: {SYS_ROAD_SPRAY: [2, 4]},
                   4: {SYS_ROAD_SPRAY: [2, 4, 5]},
                   5: {SYS_ROAD_SPRAY: [4, 5]}},
    LAB_OOF: {4: {SYS_OUT_OF_FOCUS: [4, 5]},
              5: {SYS_OUT_OF_FOCUS: [4, 5]}}
}

# SPI same severity (no backup signals)-
SEVERITY_SPI_EXACT = {
    LAB_BLUR_IMAGE: {4: {SYS_BLUR: [4]},
                     5: {SYS_BLUR: [5]}},
    LAB_FOG: {2: {SYS_FOG: [2]},
              5: {SYS_FOG: [5]}},
    LAB_FROZEN_WINDSHIELD: {2: {SYS_FROZEN_WINDSHIELD: [2]},
                            3: {SYS_FROZEN_WINDSHIELD: [4]},
                            5: {SYS_FROZEN_WINDSHIELD: [5]}},
    LAB_FULL_BLOCKAGE: {5: {SYS_FULL_BLOCKAGE: [5]}},
    LAB_LOWSUN: {2: {SYS_FADING_BY_SUN: [2]},
                 4: {SYS_FADING_BY_SUN: [4]},
                 5: {SYS_FADING_BY_SUN: [5]}},
    LAB_SUNRAY: {2: {SYS_SUN_RAY: [2]},
                 4: {SYS_SUN_RAY: [4]},
                 5: {SYS_SUN_RAY: [5]}},
    LAB_RAIN: {2: {SYS_RAIN: [2]},
               4: {SYS_RAIN: [4]},
               5: {SYS_RAIN: [5]}},
    LAB_SNOWFALL: {2: {SYS_SNOWFALL: [2]},
                   4: {SYS_SNOWFALL: [4]},
                   5: {SYS_SNOWFALL: [5]}},
    LAB_PARTIAL_BLOCKAGE: {2: {SYS_PARTIAL_BLOCKAGE: [2]},
                           4: {SYS_PARTIAL_BLOCKAGE: [4]},
                           5: {SYS_PARTIAL_BLOCKAGE: [5]}},
    LAB_SPLASHES: {2: {SYS_ROAD_SPRAY: [2]},
                   4: {SYS_ROAD_SPRAY: [4]},
                   5: {SYS_ROAD_SPRAY: [5]}},
    LAB_OOF: {4: {SYS_OUT_OF_FOCUS: [4]},
              5: {SYS_OUT_OF_FOCUS: [5]}}
}

CAUSES_VERSCHMUTZUNG = {LAB_BLUR_IMAGE: [4, 5],
                        LAB_FOG: [4, 5],
                        LAB_FROZEN_WINDSHIELD: [5],
                        LAB_FULL_BLOCKAGE: [2, 3, 5],
                        LAB_LOWSUN: [5],
                        LAB_SUNRAY: [5],
                        LAB_RAIN: [4, 5],
                        LAB_SNOWFALL: [4, 5],
                        LAB_PARTIAL_BLOCKAGE: [2, 3, 5],
                        LAB_SPLASHES: [2, 3, 5],
                        LAB_OOF: [4, 5]
                        }

FP_SEVERITY_BACKUP_VERSCHMUTZUNG = {
    SYS_BLUR: {4: CAUSES_VERSCHMUTZUNG,
               5: CAUSES_VERSCHMUTZUNG},
    SYS_FOG: {5: CAUSES_VERSCHMUTZUNG},
    SYS_FROZEN_WINDSHIELD: {5: CAUSES_VERSCHMUTZUNG},
    SYS_FULL_BLOCKAGE: {5: CAUSES_VERSCHMUTZUNG},
    SYS_FADING_BY_SUN: {5: CAUSES_VERSCHMUTZUNG},
    SYS_SUN_RAY: {5: CAUSES_VERSCHMUTZUNG},
    SYS_RAIN: {5: CAUSES_VERSCHMUTZUNG},
    SYS_PARTIAL_BLOCKAGE: {2: CAUSES_VERSCHMUTZUNG,
                           4: CAUSES_VERSCHMUTZUNG,
                           5: CAUSES_VERSCHMUTZUNG},
    SYS_ROAD_SPRAY: {2: CAUSES_VERSCHMUTZUNG,
                     4: CAUSES_VERSCHMUTZUNG,
                     5: CAUSES_VERSCHMUTZUNG},
    SYS_OUT_OF_FOCUS: {4: CAUSES_VERSCHMUTZUNG,
                       5: CAUSES_VERSCHMUTZUNG}
}

# SPI severity +- 1 available level (no backup signals)-> according to FS_Backup_Matrix.xlsx
FP_SEVERITY_SPI_ONE_LEVEL_UP_DOWN = {
    SYS_BLUR: {4: {LAB_BLUR_IMAGE: [4, 5]},
               5: {LAB_BLUR_IMAGE: [4, 5]}},
    SYS_FOG: {2: {LAB_FOG: [2, 5]},
              5: {LAB_FOG: [2, 5]}},
    SYS_FROZEN_WINDSHIELD: {2: {LAB_FROZEN_WINDSHIELD: [2, 4]},
                            4: {LAB_FROZEN_WINDSHIELD: [2, 4, 5]},
                            5: {LAB_FROZEN_WINDSHIELD: [4, 5]}},
    SYS_FULL_BLOCKAGE: {5: {LAB_FULL_BLOCKAGE: [5]}},
    SYS_FADING_BY_SUN: {2: {LAB_LOWSUN: [2, 5]},
                        4: {LAB_LOWSUN: [2, 4, 5]},
                        5: {LAB_LOWSUN: [2, 5]}},
    SYS_SUN_RAY: {2: {LAB_SUNRAY: [2, 4]},
                  4: {LAB_SUNRAY: [2, 4, 5]},
                  5: {LAB_SUNRAY: [4, 5]}},
    SYS_RAIN: {2: {LAB_RAIN: [2, 4], LAB_SNOWFALL: [2, 4]},
               4: {LAB_RAIN: [2, 4, 5], LAB_SNOWFALL: [2, 4, 5]},
               5: {LAB_RAIN: [4, 5], LAB_SNOWFALL: [4, 5]}},
    SYS_PARTIAL_BLOCKAGE: {2: {LAB_PARTIAL_BLOCKAGE: [2, 4]},
                           4: {LAB_PARTIAL_BLOCKAGE: [2, 4, 5]},
                           5: {LAB_PARTIAL_BLOCKAGE: [4, 5]}},
    SYS_ROAD_SPRAY: {2: {LAB_SPLASHES: [2, 4]},
                     4: {LAB_SPLASHES: [2, 4, 5]},
                     5: {LAB_SPLASHES: [4, 5]}},
    SYS_OUT_OF_FOCUS: {4: {LAB_OOF: [4, 5]},
                       5: {LAB_OOF: [4, 5]}}
}

# SPI exact (no backup signals)-> according to FS_Backup_Matrix.xlsx
FP_SEVERITY_SPI_EXACT = {
    SYS_BLUR: {4: {LAB_BLUR_IMAGE: [4]},
               5: {LAB_BLUR_IMAGE: [5]}},
    SYS_FOG: {2: {LAB_FOG: [2]},
              5: {LAB_FOG: [5]}},
    SYS_FROZEN_WINDSHIELD: {2: {LAB_FROZEN_WINDSHIELD: [2]},
                            4: {LAB_FROZEN_WINDSHIELD: [4]},
                            5: {LAB_FROZEN_WINDSHIELD: [5]}},
    SYS_FULL_BLOCKAGE: {5: {LAB_FULL_BLOCKAGE: [5]}},
    SYS_FADING_BY_SUN: {2: {LAB_LOWSUN: [2]},
                        4: {LAB_LOWSUN: [4]},
                        5: {LAB_LOWSUN: [5]}},
    SYS_SUN_RAY: {2: {LAB_SUNRAY: [2]},
                  4: {LAB_SUNRAY: [4]},
                  5: {LAB_SUNRAY: [5]}},
    SYS_RAIN: {2: {LAB_RAIN: [2], LAB_SNOWFALL: [2]},
               4: {LAB_RAIN: [4], LAB_SNOWFALL: [4]},
               5: {LAB_RAIN: [5], LAB_SNOWFALL: [5]}},
    SYS_PARTIAL_BLOCKAGE: {2: {LAB_PARTIAL_BLOCKAGE: [2]},
                           4: {LAB_PARTIAL_BLOCKAGE: [4]},
                           5: {LAB_PARTIAL_BLOCKAGE: [5]}},
    SYS_ROAD_SPRAY: {2: {LAB_SPLASHES: [2]},
                     4: {LAB_SPLASHES: [4]},
                     5: {LAB_SPLASHES: [45]}},
    SYS_OUT_OF_FOCUS: {4: {LAB_OOF: [4]},
                       5: {LAB_OOF: [5]}}
}

SEVERITY_COUNTERS = {2: 0, 4: 0, 5: 0}
SYS_SEVERITY_COUNTERS = {SYS_BLUR: copy.deepcopy(SEVERITY_COUNTERS),
                         SYS_FOG: copy.deepcopy(SEVERITY_COUNTERS),
                         SYS_FROZEN_WINDSHIELD: copy.deepcopy(SEVERITY_COUNTERS),
                         SYS_FULL_BLOCKAGE: copy.deepcopy(SEVERITY_COUNTERS),
                         SYS_FADING_BY_SUN: copy.deepcopy(SEVERITY_COUNTERS),
                         SYS_SUN_RAY: copy.deepcopy(SEVERITY_COUNTERS),
                         SYS_RAIN: copy.deepcopy(SEVERITY_COUNTERS),
                         SYS_PARTIAL_BLOCKAGE: copy.deepcopy(SEVERITY_COUNTERS),
                         SYS_ROAD_SPRAY: copy.deepcopy(SEVERITY_COUNTERS),
                         SYS_OUT_OF_FOCUS: copy.deepcopy(SEVERITY_COUNTERS)
                         }
LAB_SEVERITY_COUNTERS = {LAB_BLUR_IMAGE: copy.deepcopy(SEVERITY_COUNTERS),
                         LAB_FOG: copy.deepcopy(SEVERITY_COUNTERS),
                         LAB_FROZEN_WINDSHIELD: copy.deepcopy(SEVERITY_COUNTERS),
                         LAB_FULL_BLOCKAGE: copy.deepcopy(SEVERITY_COUNTERS),
                         LAB_LOWSUN: copy.deepcopy(SEVERITY_COUNTERS),
                         LAB_SUNRAY: copy.deepcopy(SEVERITY_COUNTERS),
                         LAB_RAIN: copy.deepcopy(SEVERITY_COUNTERS),
                         LAB_PARTIAL_BLOCKAGE: copy.deepcopy(SEVERITY_COUNTERS),
                         LAB_SPLASHES: copy.deepcopy(SEVERITY_COUNTERS),
                         LAB_OOF: copy.deepcopy(SEVERITY_COUNTERS)
                         }

TP_COUNTERS = {LAB_BLUR_IMAGE: {2: copy.deepcopy(SYS_SEVERITY_COUNTERS), 4: copy.deepcopy(SYS_SEVERITY_COUNTERS), 5: copy.deepcopy(SYS_SEVERITY_COUNTERS)},
               LAB_FOG: {2: copy.deepcopy(SYS_SEVERITY_COUNTERS), 4: copy.deepcopy(SYS_SEVERITY_COUNTERS), 5: copy.deepcopy(SYS_SEVERITY_COUNTERS)},
               LAB_FROZEN_WINDSHIELD: {2: copy.deepcopy(SYS_SEVERITY_COUNTERS), 4: copy.deepcopy(SYS_SEVERITY_COUNTERS), 5: copy.deepcopy(SYS_SEVERITY_COUNTERS)},
               LAB_FULL_BLOCKAGE: {2: copy.deepcopy(SYS_SEVERITY_COUNTERS), 4: copy.deepcopy(SYS_SEVERITY_COUNTERS), 5: copy.deepcopy(SYS_SEVERITY_COUNTERS)},
               LAB_LOWSUN: {2: copy.deepcopy(SYS_SEVERITY_COUNTERS), 4: copy.deepcopy(SYS_SEVERITY_COUNTERS), 5: copy.deepcopy(SYS_SEVERITY_COUNTERS)},
               LAB_SUNRAY: {2: copy.deepcopy(SYS_SEVERITY_COUNTERS), 4: copy.deepcopy(SYS_SEVERITY_COUNTERS), 5: copy.deepcopy(SYS_SEVERITY_COUNTERS)},
               LAB_RAIN: {2: copy.deepcopy(SYS_SEVERITY_COUNTERS), 4: copy.deepcopy(SYS_SEVERITY_COUNTERS), 5: copy.deepcopy(SYS_SEVERITY_COUNTERS)},
               LAB_PARTIAL_BLOCKAGE: {2: copy.deepcopy(SYS_SEVERITY_COUNTERS), 4: copy.deepcopy(SYS_SEVERITY_COUNTERS), 5: copy.deepcopy(SYS_SEVERITY_COUNTERS)},
               LAB_SPLASHES: {2: copy.deepcopy(SYS_SEVERITY_COUNTERS), 4: copy.deepcopy(SYS_SEVERITY_COUNTERS), 5: copy.deepcopy(SYS_SEVERITY_COUNTERS)},
               LAB_OOF: {2: copy.deepcopy(SYS_SEVERITY_COUNTERS), 4: copy.deepcopy(SYS_SEVERITY_COUNTERS), 5: copy.deepcopy(SYS_SEVERITY_COUNTERS)}
               }

FP_COUNTERS = {SYS_BLUR: {2: copy.deepcopy(LAB_SEVERITY_COUNTERS), 4: copy.deepcopy(LAB_SEVERITY_COUNTERS), 5: copy.deepcopy(LAB_SEVERITY_COUNTERS)},
               SYS_FOG: {2: copy.deepcopy(LAB_SEVERITY_COUNTERS), 4: copy.deepcopy(LAB_SEVERITY_COUNTERS), 5: copy.deepcopy(LAB_SEVERITY_COUNTERS)},
               SYS_FROZEN_WINDSHIELD: {2: copy.deepcopy(LAB_SEVERITY_COUNTERS), 4: copy.deepcopy(LAB_SEVERITY_COUNTERS), 5: copy.deepcopy(LAB_SEVERITY_COUNTERS)},
               SYS_FULL_BLOCKAGE: {2: copy.deepcopy(LAB_SEVERITY_COUNTERS), 4: copy.deepcopy(LAB_SEVERITY_COUNTERS), 5: copy.deepcopy(LAB_SEVERITY_COUNTERS)},
               SYS_FADING_BY_SUN: {2: copy.deepcopy(LAB_SEVERITY_COUNTERS), 4: copy.deepcopy(LAB_SEVERITY_COUNTERS), 5: copy.deepcopy(LAB_SEVERITY_COUNTERS)},
               SYS_SUN_RAY: {2: copy.deepcopy(LAB_SEVERITY_COUNTERS), 4: copy.deepcopy(LAB_SEVERITY_COUNTERS), 5: copy.deepcopy(LAB_SEVERITY_COUNTERS)},
               SYS_RAIN: {2: copy.deepcopy(LAB_SEVERITY_COUNTERS), 4: copy.deepcopy(LAB_SEVERITY_COUNTERS), 5: copy.deepcopy(LAB_SEVERITY_COUNTERS)},
               SYS_PARTIAL_BLOCKAGE: {2: copy.deepcopy(LAB_SEVERITY_COUNTERS), 4: copy.deepcopy(LAB_SEVERITY_COUNTERS), 5: copy.deepcopy(LAB_SEVERITY_COUNTERS)},
               SYS_ROAD_SPRAY: {2: copy.deepcopy(LAB_SEVERITY_COUNTERS), 4: copy.deepcopy(LAB_SEVERITY_COUNTERS), 5: copy.deepcopy(LAB_SEVERITY_COUNTERS)},
               SYS_OUT_OF_FOCUS: {2: copy.deepcopy(LAB_SEVERITY_COUNTERS), 4: copy.deepcopy(LAB_SEVERITY_COUNTERS), 5: copy.deepcopy(LAB_SEVERITY_COUNTERS)}
               }
