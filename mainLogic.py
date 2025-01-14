import config.constant as c
import libs.pickle_itrk_opener as p_i_opener
from libs.debugging import debugmethods
from libs.loggingFuncs import print_and_log
import pandas as pd
import numpy as np
import os
import simplejson as json
from dataframe_collector import DfCollector
from lab_sig_counter import LabSigCounter
from tp_fp_frame_counters import TPFPCounter
from not_ready_check import NotReadyCheck
from cal_test import CalCheck
from event_counter import EventCounter
from datetime import datetime
import re
import sys
import math

cp60_spec_path = c.CP60_SPEC_PATH
pickles_f_list = c.CP_60_PICKLES_FILE_LIST
cp60_spec = c.CP60_SPEC
df_collector = DfCollector(c.SOP, c.A_STEP, c.PROJECT)  # -------------------------------------------------------------

@debugmethods(handle_static=False)
class MainLogic:

    def __init__(self, log, **kwargs):
        self.logger = log
        self._input = kwargs.get('input', False)
        self.file_list = self._find_pickles()
        self._output = kwargs.get('output_folder', False)
        self._rec_time = c.RECOGNITION_TIME
        self._path_itrk = c.PATH_ITRK
        # names for object instances
        self._sys = c.SYS
        self._lab = c.LAB
        # obj instances
        self.fail_safe_sys = {}
        self.fail_safe_lab = {}
        self.dt_str = re.sub(r"[:\-. ]", "", str(datetime.now()))
        self.name = f'{os.path.basename(self._input)}_{self.dt_str}.json'

        # SPI
        self.path_to_partials_any = os.path.join(self._output, 'spi_any')
        os.makedirs(self.path_to_partials_any, exist_ok=True)

        self.path_to_partials_backup = os.path.join(self._output, 'spi_backup')
        os.makedirs(self.path_to_partials_backup, exist_ok=True)

        self.path_to_partials_backup_up_down = os.path.join(self._output, 'spi_backup_up_down')
        os.makedirs(self.path_to_partials_backup_up_down, exist_ok=True)

        self.path_to_partials_backup_any = os.path.join(self._output, 'spi_backup_any')
        os.makedirs(self.path_to_partials_backup_any, exist_ok=True)

        self.path_to_partials_exact = os.path.join(self._output, 'spi_exact')
        os.makedirs(self.path_to_partials_exact, exist_ok=True)

        self.path_to_partials_exact_up_down = os.path.join(self._output, 'spi_exact_up_down')
        os.makedirs(self.path_to_partials_exact_up_down, exist_ok=True)

        self.path_to_partials_degrade = os.path.join(self._output, 'spi_degrade')
        os.makedirs(self.path_to_partials_degrade, exist_ok=True)
        # simulated flexray
        self.path_to_partials_flexray = os.path.join(self._output, 'flexray')
        os.makedirs(self.path_to_partials_flexray, exist_ok=True)

        self._partials_any = []
        self._partials_backup = []
        self._partials_backup_up_down = []
        self._partials_backup_any = []
        self._partials_exact = []
        self._partials_exact_up_down = []
        self._partials_degrade = []
        self._partials_flexray = []

    def run(self):
        self._main()

    def _main(self):
        self.itrks = self._find_itrks(self._path_itrk, list(self.file_list.keys())[0])
        if len(self.itrks) == 0:
            return None
        self.seq = Sequencer(files=self.file_list,
                             itrks=self.itrks,
                             dt_str=self.dt_str,
                             log=self.logger)
        msg = self.seq.run()
        if msg:
            spi_any = Sequencer.return_partials('any')
            spi_backup = Sequencer.return_partials('backup')
            spi_backup_up_down = Sequencer.return_partials('backup_up_down')
            spi_backup_any = Sequencer.return_partials('backup_any')
            spi_exact = Sequencer.return_partials('exact')
            spi_exact_up_down = Sequencer.return_partials('exact_up_down')
            spi_degrade = Sequencer.return_partials('degrade')
            flexray = Sequencer.return_partials('flexray')

            self._partials_any.append(spi_any)
            self._partials_backup.append(spi_backup)
            self._partials_backup_up_down.append(spi_backup_up_down)
            self._partials_backup_any.append(spi_backup_any)
            self._partials_exact.append(spi_exact)
            self._partials_exact_up_down.append(spi_exact_up_down)
            self._partials_degrade.append(spi_degrade)
            self._partials_flexray.append(flexray)

            self.name = os.path.basename(self.name)
            self.save_to_json(self.path_to_partials_any, self._partials_any, self.name)
            self.save_to_json(self.path_to_partials_backup, self._partials_backup, self.name)
            self.save_to_json(self.path_to_partials_backup_up_down, self._partials_backup_up_down, self.name)
            self.save_to_json(self.path_to_partials_backup_any, self._partials_backup_any, self.name)
            self.save_to_json(self.path_to_partials_exact, self._partials_exact, self.name)
            self.save_to_json(self.path_to_partials_exact_up_down, self._partials_exact_up_down, self.name)
            self.save_to_json(self.path_to_partials_degrade, self._partials_degrade, self.name)
            self.save_to_json(self.path_to_partials_flexray, self._partials_flexray, self.name)

            df_collector.divide_df_if_max_len()  # -------------------------------------------------------------------------
            df_collector.save_dfs()  # -------------------------------------------------------------------------------------

    def _find_itrks(self, path_itrk, measurement):
        _, v, d, hour, s = measurement.split('_')
        vin = v[-4:]
        date = d[2:]
        part_name_itrk = f'{vin}_{date}_{hour}'
        itrk_list = [x for x in os.listdir(path_itrk) if part_name_itrk in x]
        full_path_list = []
        for i in itrk_list:
            full_path_list.append(os.path.join(self._path_itrk, i))
        return sorted(set(full_path_list))

    def _find_pickles(self):
        pickles = {}
        pickles_found = []
        if cp60_spec:
            pickles_found = []  # cp60_spec
            with open(cp60_spec_path, 'r') as f:  # cp60_spec
                cp_60_list = json.load(f)  # cp60_spec
        for dirr, _, files in os.walk(self._input):
            for file in files:
                if file.endswith('pickle.xz'):
                    adcam, vin, date, hour, _, split = file.split('_')
                    if cp60_spec:
                        for elem in cp_60_list:  #
                            searched_pickle = f'{vin}_{date}_{hour}_v01_{split[:4]}.MF4'  # cp60_spec
                            if searched_pickle in elem:  # cp60_spec
                                pickles_found.append(searched_pickle)
                                pickles[f'{adcam}_{vin}_{date}_{hour}_{split[:4]}'] = os.path.join(dirr, file)
                    else:
                        pickles[f'{adcam}_{vin}_{date}_{hour}_{split[:4]}'] = os.path.join(dirr, file)
        if cp60_spec:
            with open(pickles_f_list, 'a') as f:  # cp60_spec
                json.dump(pickles_found, f, indent=2)  # cp60_spec
        pickles_to_remove = sorted(pickles.keys())
        if len(pickles_to_remove) > 3:  # cp60_spec
            del pickles[pickles_to_remove[0]]
            del pickles[pickles_to_remove[1]]
            del pickles[pickles_to_remove[-1]]
        return pickles

    @staticmethod
    def save_to_json(path, what, name):
        with open(os.path.join(path, name), 'w', encoding='utf-8') as f:
            json.dump(what, f, ensure_ascii=False, indent=2, ignore_nan=True)


@debugmethods(prefix='..')
class Sequencer:
    partials_any = []
    partials_backup = []
    partials_backup_up_down = []
    partials_backup_any = []
    partials_exact = []
    partials_exact_up_down = []
    partials_degrade = []
    partials_flexray = []

    def __init__(self, files, itrks, log, dt_str, filtering=None):
        self._logger = log
        self._file_list = files
        self._itrks = itrks
        self.dt_str = dt_str
        self.filtering = filtering
        self.data_lab = None
        self.data_sys = None
        self.project = c.PROJECT
        self.bad_label_dict = {}
        self.bad_label_frame_counters_dict = {}
        self.init_counter_dicts()
        self.not_ready_check = NotReadyCheck(self._file_list)
        self.lab_sig_counter = LabSigCounter(self._file_list, dt_str)
        self.tp_fp_counter = TPFPCounter(self._file_list, dt_str)
        self.cal_check = CalCheck(self._file_list)
        self.split_list = EventCounter(self._file_list, dt_str)
        self.day_time_dict = c.DAYTIME_DICT
        self.debounce_frames_fn = math.ceil(c.DEBOUNCE_TIME_FN_S / (16 / c.FREQUENCY))  # label is every 16th frame
        self.debounce_frames_fp = math.ceil(c.DEBOUNCE_TIME_FP_S / (16 / c.FREQUENCY))  # label is every 16th frame

    def run(self):
        print_and_log(self._logger, "....Start reading system data from - raw")
        self.data_sys = p_i_opener.read_from_raw(sorted(self._file_list.values()), logger=self._logger, fr=c.FLEXRAY)
        # read labeling
        print_and_log(self._logger, "....Start reading labeling data from - itrk files")
        self.data_lab = p_i_opener.read_from_itrk(sorted(self._itrks), logger=self._logger)

        # adding filename to DataFrame with labeling
        self.data_lab = self.data_lab.astype({'grabIndex': 'int64'})
        df_merged = pd.merge(self.data_sys, self.data_lab, right_on='grabIndex', left_on='COM_Cam_Frame_ID', how='left')
        # drop rows where grabIndex is null
        df_merged = df_merged.loc[df_merged['grabIndex'].notnull()]
        # df_fs = df_merged[['File_Name', 'partialBlockage', 'FS_Partial_Blockage_0', 'itrk_name']]

        self.split_list.get_pickle_list(df_merged)

        # fix velocity nan
        df_merged = self.fix_velocity_nan(df_merged)
        # if there is no column 'outOfFocus' add it filled with -1
        if c.LAB_OOF not in df_merged.columns.values:
            # insert new column before 'partialBlockage'
            # find 'partialBlockage' location
            if c.LAB_PARTIAL_BLOCKAGE in df_merged.columns.values:
                oof_lab_location = int(np.where(df_merged.columns.values == c.LAB_PARTIAL_BLOCKAGE)[0][0])
            else:
                oof_lab_location = int(len(df_merged.columns.values))
            # insert new column at oof_lab_location
            df_merged.insert(oof_lab_location, c.LAB_OOF, -1)
        df_merged.fillna(-1, inplace=True)
        df_merged = df_merged[c.BWD_COLUMNS]
        # CAL test
        if c.CAL_TEST:
            self.cal_check.check_cal(df_merged)
            if c.CAL_TEST_ONLY:
                sys.exit()

        # check for SPI = 0 (NOT_READY)
        self.not_ready_check.count_not_ready(df_merged)
        # convert ignore
        df_merged = self._convert_ignore(df_merged)
        # Get copy for fp
        df_merged_fp = df_merged.copy()
        if c.ZERO_SPEED_THRESHOLD > 0:
            df_merged = df_merged.loc[(df_merged['Velocity'] > c.ZERO_SPEED_THRESHOLD) | (df_merged['Velocity'] < -c.ZERO_SPEED_THRESHOLD) | (df_merged['Velocity'].isnull())]
        if c.REMOVE_TOGGLING_TP:
            df_smoothed = self._remove_toggling_tp(df_merged)
        else:
            df_smoothed = df_merged
        df_smoothed = self._map_day_time(df_smoothed)
        if c.REMOVE_TOGGLING_FP:
            df_smoothed_fp = self._remove_toggling_fp(df_merged_fp)
        else:
            df_smoothed_fp = df_merged_fp
        df_smoothed_fp = self._map_day_time(df_smoothed_fp)
        # Count all labels
        self.lab_sig_counter.count_lab(df_smoothed)  # Count all signals and labels
        # Count all signals
        self.lab_sig_counter.count_sig(df_smoothed_fp)  # Count all signals and labels
        # self.lab_sig_counter.save_results_df()
        # sys.exit()
        hole = 100  # number of frames when hole, sometimes there is a short gap of grab indexes
        if len(df_smoothed) == 0 or len(df_smoothed_fp) == 0:
            return None
        df_grouped_fp, number_of_frames, total_distance = self._separate_if_holes(hole=hole, dff=df_smoothed_fp)
        df_grouped, number_of_frames, total_distance = self._separate_if_holes(hole=hole, dff=df_smoothed)
        info = set(df_merged['File_Name'])

        spi_any_match = {"Processed": list(info),
                         "TotalNumberOfFrames": float(number_of_frames),
                         "DistanceDriven": total_distance,
                         "To_short_events": 0,
                         "LabeledFs": [],
                         "FalsePositive": []}
        spi_backup_match = {"Processed": list(info),
                            "TotalNumberOfFrames": float(number_of_frames),
                            "DistanceDriven": total_distance,
                            "To_short_events": 0,
                            "LabeledFs": [],
                            "FalsePositive": []}
        spi_backup_match_up_down = {"Processed": list(info),
                                    "TotalNumberOfFrames": float(number_of_frames),
                                    "DistanceDriven": total_distance,
                                    "To_short_events": 0,
                                    "LabeledFs": [],
                                    "FalsePositive": []}
        spi_backup_match_any = {"Processed": list(info),
                                "TotalNumberOfFrames": float(number_of_frames),
                                "DistanceDriven": total_distance,
                                "To_short_events": 0,
                                "LabeledFs": [],
                                "FalsePositive": []}
        spi_exact_match = {"Processed": list(info),
                           "TotalNumberOfFrames": float(number_of_frames),
                           "DistanceDriven": total_distance,
                           "To_short_events": 0,
                           "LabeledFs": [],
                           "FalsePositive": []}
        spi_exact_match_up_down = {"Processed": list(info),
                                   "TotalNumberOfFrames": float(number_of_frames),
                                   "DistanceDriven": total_distance,
                                   "To_short_events": 0,
                                   "LabeledFs": [],
                                   "FalsePositive": []}
        spi_degrade_match = {"Processed": list(info),
                             "TotalNumberOfFrames": float(number_of_frames),
                             "DistanceDriven": total_distance,
                             "To_short_events": 0,
                             "LabeledFs": [],
                             "FalsePositive": []}
        flexray_match = {"Processed": list(info),
                         "TotalNumberOfFrames": float(number_of_frames),
                         "DistanceDriven": total_distance,
                         "To_short_events": 0,
                         "LabeledFs": [],
                         "FalsePositive": []}
        # TPR
        if c.SPI_ANY:
            # match any failsafe, any severity
            self.tp_fp_counter.collect = True
            res_any_severity = self.calculate_tp(df_grouped, lab_sig_dict=c.LAB_TO_SPI_ALL, severities_to_check=c.SEVERITY_ANY, only_sys_severity=False)
            self.tp_fp_counter.collect = False
            spi_any_match.update(res_any_severity)
        if c.SPI_BACKUP:
            # match FS_Backup_Matrix
            res_backup_severity = self.calculate_tp(df_grouped, lab_sig_dict=c.LAB_TO_SPI_BACKUP, severities_to_check=c.SEVERITY_BACKUP)
            spi_backup_match.update(res_backup_severity)
        if c.SPI_DEGRADE:
            # match FS_Backup_Matrix but any severity that leads to degradation
            res_degrade_match = self.calculate_tp(df_grouped, lab_sig_dict=c.LAB_TO_SPI_BACKUP, severities_to_check=c.SEVERITY_DEGRADE)
            spi_degrade_match.update(res_degrade_match)
        if c.SPI_BACKUP_UP_DOWN:
            # match FS_Backup_Matrix +/- one level
            df_collector.collect = True  # -----------------------------------------------------------------------------
            res_backup_severity_up_down = self.calculate_tp(df_grouped, lab_sig_dict=c.LAB_TO_SPI_BACKUP, severities_to_check=c.SEVERITY_BACKUP_LEVEL_UP_DOWN)
            df_collector.collect = False
            spi_backup_match_up_down.update(res_backup_severity_up_down)
        if c.SPI_BACKUP_ANY:
            # match FS_Backup_Matrix any level
            self.not_ready_check.collect = True
            res_backup_severity_any = self.calculate_tp(df_grouped, lab_sig_dict=c.LAB_TO_SPI_BACKUP, severities_to_check=c.SEVERITY_ANY)
            self.not_ready_check.collect = False
            spi_backup_match_any.update(res_backup_severity_any)

        if c.SPI_EXACT:
            # match exact failsafe, exact severity
            res_exact_severity = self.calculate_tp(df_grouped, lab_sig_dict=c.LAB_TO_SYS, severities_to_check=c.SEVERITY_EXACT)
            spi_exact_match.update(res_exact_severity)
        if c.SPI_EXACT_UP_DOWN:
            # match exact failsafe, up down severity
            res_exact_severity_up_down = self.calculate_tp(df_grouped, lab_sig_dict=c.LAB_TO_SYS, severities_to_check=c.SEVERITY_LEVEL_UP_DOWN)
            spi_exact_match_up_down.update(res_exact_severity_up_down)
        if c.FLEXRAY:
            # match to verschmutzung
            res_flexray = self.calculate_tp(df_grouped, lab_sig_dict=c.LAB_TO_DEGRADE, severities_to_check=c.SEVERITY_VERSCHMUTZUNG)
            flexray_match.update(res_flexray)

        # FPR
        if c.SPI_EXACT:
            # No FP if same failsafe is labeled (same severity)
            self.tp_fp_counter.collect = True
            self.calculate_fp(df_grouped_fp, spi_exact_match, c.FP_SEVERITY_SPI_EXACT)
            self.tp_fp_counter.collect = False
        if c.SPI_BACKUP:
            # No FP if failsafe severity according to FS_Backup_Matrix is labelled
            self.calculate_fp(df_grouped_fp, spi_backup_match, c.FP_SEVERITY_SPI)
        if c.SPI_DEGRADE:
            # No FP if failsafe not activating Verschmutzung
            df_collector.collect = True  # -----------------------------------------------------------------------------
            self.calculate_fp(df_grouped_fp, spi_degrade_match, c.FP_SEVERITY_BACKUP_VERSCHMUTZUNG)
            df_collector.collect = False
        if c.SPI_EXACT_UP_DOWN:
            # No FP if same failsafe is labeled with severity up down one level
            self.calculate_fp(df_grouped_fp, spi_exact_match_up_down, c.FP_SEVERITY_SPI_ONE_LEVEL_UP_DOWN)
        if c.SPI_BACKUP_ANY:
            # No FP if backup failsafe is labeled (any severity)
            self.not_ready_check.collect = True
            self.calculate_fp(df_grouped_fp, spi_backup_match_any, c.SYS_TO_LAB2)
            self.not_ready_check.collect = False

        # SAVE BAD LABEL FRAME COUNTERS ----------------------------------------------
        # Get HILREPP name
        key = list(self._file_list.keys())[0]
        search_line = self._file_list[key]
        # search for HILREPP-7digits, force the engine to try matching at the furthest position
        search = re.search(r'(?s:.*).+(HILREPP-\d{7}).+', search_line)  # ex. HILREPP-2013288
        if search:
            hilrep_name = search.group(1)
            unique_name = f'bad_labeled_frame_counter_{hilrep_name}_{self.dt_str}.json'
        else:
            unique_name = f'bad_labeled_frame_counter_{self.dt_str}.json'

        bad_labeled_frame_counters_path = os.path.join(c.BAD_LABEL_DICT_FOLDER, 'bad_labeled_frame_counters')
        if not os.path.isdir(bad_labeled_frame_counters_path):
            os.makedirs(bad_labeled_frame_counters_path, exist_ok=True)
        self.save_to_json(bad_labeled_frame_counters_path, unique_name, self.bad_label_frame_counters_dict)
        # save not ready check dict
        self.not_ready_check.save_results()
        self.tp_fp_counter.save_results_df()
        self.lab_sig_counter.save_results_df()
        # ---------------------------------------------
        self.__class__.partials_any = spi_any_match
        self.__class__.partials_backup = spi_backup_match
        self.__class__.partials_backup_up_down = spi_backup_match_up_down
        self.__class__.partials_backup_any = spi_backup_match_any
        self.__class__.partials_exact = spi_exact_match
        self.__class__.partials_exact_up_down = spi_exact_match_up_down
        self.__class__.partials_degrade = spi_degrade_match
        self.__class__.partials_flexray = flexray_match
        return True

    @staticmethod
    def fix_velocity_nan(df):
        if len(df) > 0:
            not_null = len(df[df['Velocity'].notnull()])
            if not_null > 0:
                df.reset_index(inplace=True)
                df_first_index = df.index.values[0]
                df_last_index = df.index.values[-1]
                nan_indexes = df[df['Velocity'].isnull()].index.values
                if len(nan_indexes) > 0:
                    for index in nan_indexes:
                        if df_first_index < index < df_last_index:
                            down_val = 1
                            while True:
                                if (index - down_val) <= df_first_index:
                                    break
                                if df.loc[index - down_val, 'Velocity']:
                                    break
                                else:
                                    down_val += 1
                            up_val = 1
                            while True:
                                if (index + up_val) >= df_last_index:
                                    break
                                if df.loc[index + up_val, 'Velocity']:
                                    break
                                else:
                                    up_val += 1
                            if df.loc[index - down_val, 'Velocity'] and df.loc[index + up_val, 'Velocity']:
                                df.loc[index, 'Velocity'] = (df.loc[index - down_val, 'Velocity'] + df.loc[index + up_val, 'Velocity']) / 2
                            elif df.loc[index - down_val, 'Velocity']:
                                df.loc[index, 'Velocity'] = df.loc[index - down_val, 'Velocity']
                            elif df.loc[index + up_val, 'Velocity']:
                                df.loc[index, 'Velocity'] = df.loc[index + up_val, 'Velocity']
                            else:
                                pass
                df.set_index('index', inplace=True)
        return df

    def init_counter_dicts(self):
        # BAD LABEL DICT --------------------------------------------------------
        self.get_bad_label_dicts()
        # INIT FRAME COUNTERS ----------------------------------------------
        for fs in c.PARTIALS_NAMES_LAB.keys():
            self.bad_label_frame_counters_dict[fs] = 0
        for fs in c.PARTIALS_NAMES_SYS.keys():
            self.bad_label_frame_counters_dict[fs] = 0

    def _separate_if_holes(self, hole, dff):
        idx = np.where(np.diff(dff['grabIndex']) > hole)[0]
        idx = np.insert(idx, 0, -1)
        idx = np.append(idx, len(dff['grabIndex']))
        df_grouped = {}
        number_of_frames = 0
        total_distance = 0
        for i in range(len(idx) - 1):
            df = dff[idx[i] + 1: idx[i + 1]]
            if len(df) == 0:
                continue
            grab_index_first = df['COM_Cam_Frame_ID'].iloc[0]
            grab_index_last = df['COM_Cam_Frame_ID'].iloc[-1]
            df_grouped[f'{grab_index_first}_{grab_index_last}'] = {}
            df_grouped[f'{grab_index_first}_{grab_index_last}']['lab'] = df
            _sys = self.data_sys[self.data_sys['COM_Cam_Frame_ID'].between(grab_index_first, grab_index_last)]
            # To calculate distance in [km]
            temp_v = _sys['Velocity'].iloc[:-1] + np.abs(np.diff(_sys['Velocity'])) / 2
            temp_dt = np.diff(_sys['timestamp'])
            temp_ds = temp_v * temp_dt
            total_distance += np.sum(temp_ds) / 3600
            del _sys['Velocity']
            df_grouped[f'{grab_index_first}_{grab_index_last}']['sys'] = _sys
            number_of_frames += grab_index_last - grab_index_first
            pass
        return df_grouped, number_of_frames, total_distance

    def get_bad_label_dicts(self):
        if self.project == 'mid':
            bad_label_dict_fn = self.load_json(c.BAD_LABEL_DICT_FOLDER, 'bad_label_events_mid_fn.json')
            bad_label_dict_fp = self.load_json(c.BAD_LABEL_DICT_FOLDER, 'bad_label_events_mid_fp.json')
            self.bad_label_dict = {**bad_label_dict_fn, **bad_label_dict_fp}
        elif self.project == 'cp60':
            bad_label_dict_fn = self.load_json(c.BAD_LABEL_DICT_FOLDER, 'bad_label_events_cp60_fn.json')
            bad_label_dict_fp = self.load_json(c.BAD_LABEL_DICT_FOLDER, 'bad_label_events_cp60_fp.json')
            self.bad_label_dict = {**bad_label_dict_fn, **bad_label_dict_fp}
        else:
            print('get_bad_label_dicts: wrong project!!!')

    def Smatch_lab_fs(self, df, signals_to_check, label, labeled_severity, severities_to_check):
        """
        Matched True Positive based on severities_to_check
        :param df:
        :param signals_to_check:
        :param label:
        :param labeled_severity:
        :param severities_to_check:
        :return: matching_df (dataframe with TP), not_matching_df (dataframe wo TP)
        """
        matched_index_list = []
        severity_to_check = {}
        if severities_to_check != c.SEVERITY_ANY:
            # match severity according to FS_Backup_Matrix.xlsx
            if severities_to_check == c.SEVERITY_BACKUP:
                if signals_to_check[0] in c.SYS_ALL:
                    severity_to_check = c.SEVERITY_BACKUP_SPI[label][labeled_severity]
            # match severity according to FS_Backup_Matrix.xlsx but any severity causing degradation is ok
            elif severities_to_check == c.SEVERITY_DEGRADE:
                if signals_to_check[0] in c.SYS_ALL:
                    severity_to_check = c.SEVERITY_BACKUP_SPI_DEGRADE[label][labeled_severity]
            # match severity according to FS_Backup_Matrix.xlsx +- one level
            elif severities_to_check == c.SEVERITY_BACKUP_LEVEL_UP_DOWN:
                if signals_to_check[0] in c.SYS_ALL:
                    severity_to_check = c.SEVERITY_BACKUP_SPI_ONE_LEVEL_UP_DOWN[label][labeled_severity]
            # match severity according to FS_Backup_Matrix.xlsx +- one level, without backup signals
            elif severities_to_check == c.SEVERITY_LEVEL_UP_DOWN:
                if signals_to_check[0] in c.SYS_ALL:
                    severity_to_check = c.SEVERITY_SPI_ONE_LEVEL_UP_DOWN[label][labeled_severity]
            # match severity exact, without backup signals
            elif severities_to_check == c.SEVERITY_EXACT:
                if signals_to_check[0] in c.SYS_ALL:
                    severity_to_check = c.SEVERITY_SPI_EXACT[label][labeled_severity]
            # match verschmutzung
            elif severities_to_check == c.SEVERITY_VERSCHMUTZUNG:
                if signals_to_check[0] in c.DEGRADE:
                    severity_to_check = c.FLEXRAY_VERSCHMUTZUNG[label][labeled_severity]
            for signal, severity_list in severity_to_check.items():
                for severity in severity_list:
                    if signal in signals_to_check:
                        matched_df = df[df[signal] == severity]
                        if len(matched_df) > 0:
                            matched_df_indexes = matched_df.index.values.tolist()
                            for index in matched_df_indexes:
                                matched_index_list.append(index)
            index_list = list(set(matched_index_list))
            matching_df = df.loc[index_list]
            matching_df['to_match'] = True

        # match any severity
        else:  # severities_to_check == c.SEVERITY_ANY:
            df['to_match'] = df[signals_to_check].max(axis=1)
            matching_df = df.loc[df["to_match"] > 1]

        df_indexes = list(df['index'])
        matching_df_indexes = list(matching_df['index'])
        # get not matching indexes
        not_matching_indexes = list(set(df_indexes).difference(matching_df_indexes))
        # remove noise from not matched
        gap_list = self.get_gap_list(not_matching_indexes, self.debounce_frames_fn)
        diff_set = set(not_matching_indexes) - set(gap_list)
        not_matching_indexes_no_gap = list(diff_set)
        not_matching_indexes_no_gap.sort()
        not_matching_df = df[df['index'].isin(not_matching_indexes_no_gap)]
        # add removed to matched
        gap_df = df[df['index'].isin(gap_list)]
        matching_df = pd.concat([matching_df, gap_df], ignore_index=True)
        matching_df.sort_values(by=['index'],  inplace=True)
        # remove any match from not matching
        # not_matching_df['to_match'] = not_matching_df[signals_to_check].max(axis=1)
        # not_matching_df = not_matching_df[not_matching_df['to_match'] < 2]
        return matching_df, not_matching_df

    def match_sys_fs(self, df, signal, severity, severities_to_check):
        """
        Matched False Positive based on severities_to_check
        :param df:
        :param signal:
        :param severity:
        :param severities_to_check:
        :return: not_matching_df (dataframe with FP), matching_df (dataframe wo FP)
        """

        matched_index_list = []
        severity_to_check = {}

        if severities_to_check == c.FP_SEVERITY_SPI or severities_to_check == c.FP_SEVERITY_BACKUP_VERSCHMUTZUNG or \
                severities_to_check == c.FP_SEVERITY_SPI_EXACT or severities_to_check == c.FP_SEVERITY_SPI_ONE_LEVEL_UP_DOWN:
            if signal in severities_to_check.keys() and severity in severities_to_check[signal].keys():
                if severities_to_check == c.FP_SEVERITY_SPI_ONE_LEVEL_UP_DOWN:
                    severity_to_check = c.FP_SEVERITY_SPI_ONE_LEVEL_UP_DOWN[signal][severity]
                elif severities_to_check == c.FP_SEVERITY_SPI:
                    severity_to_check = c.FP_SEVERITY_SPI[signal][severity]
                elif severities_to_check == c.FP_SEVERITY_BACKUP_VERSCHMUTZUNG:
                    severity_to_check = c.FP_SEVERITY_BACKUP_VERSCHMUTZUNG[signal][severity]
                elif severities_to_check == c.FP_SEVERITY_SPI_EXACT:
                    severity_to_check = c.FP_SEVERITY_SPI_EXACT[signal][severity]
                for label, severity_list in severity_to_check.items():
                    for severity in severity_list:
                        matched_df = df[df[label] == severity]
                        if len(matched_df) > 0:
                            matched_df_indexes = matched_df.index.values.tolist()
                            for index in matched_df_indexes:
                                matched_index_list.append(index)
                index_list = list(set(matched_index_list))
                matching_df = df.loc[index_list]
                matching_df['to_match'] = True
            else:
                matching_df = pd.DataFrame(columns=df.columns.values)
                not_matching_df = pd.DataFrame(columns=df.columns.values)
                return not_matching_df, matching_df

        else:  # if severities_to_check == c.SYS_TO_LAB or severities_to_check == c.SYS_TO_LAB2:
            df['to_match2'] = df[severities_to_check[signal]].max(axis=1)
            matching_df = df.loc[df["to_match2"] > 1]

        df_indexes = list(df['index'])
        matching_df_indexes = list(matching_df['index'])
        # get not matching indexes
        not_matching_indexes = list(set(df_indexes).difference(matching_df_indexes))
        # remove noise from not matched
        gap_list = self.get_gap_list(not_matching_indexes, self.debounce_frames_fp)
        diff_set = set(not_matching_indexes) - set(gap_list)
        not_matching_indexes_no_gap = list(diff_set)
        not_matching_indexes_no_gap.sort()
        not_matching_df = df[df['index'].isin(not_matching_indexes_no_gap)]
        return not_matching_df, matching_df

    @staticmethod
    def get_gap_list(index_list, frames_to_debounce):
        if frames_to_debounce > 0:
            if index_list:
                index_list.sort()
                no_gap = 1
                gap_index_list = []
                gap_list = []
                last_index = index_list[0]
                for counter, index in enumerate(index_list):
                    if counter == 0:
                        gap_index_list.append(index)
                        continue
                    diff = index - last_index
                    last_index = index
                    if diff == 1:
                        no_gap += 1
                        gap_index_list.append(index)
                    else:
                        if no_gap < frames_to_debounce:
                            gap_list += gap_index_list
                        gap_index_list.clear()
                        gap_index_list.append(index)
                        no_gap = 1
                if no_gap < frames_to_debounce:
                    gap_list += gap_index_list
                return gap_list
            else:
                return []
        else:
            return []

    def check_bad_labels_fp(self, fs, df):
        if fs in self.bad_label_dict.keys():
            # if split in df is also in bad labeled splits list, remove row with that split from df
            df.reset_index(drop=True, inplace=True)
            bad_label_split_list = []
            # get list of splits in df
            split_list_all = list(df['File_Name'])
            split_list_unique = list(set(split_list_all))
            split_list_unique.sort()
            if split_list_unique:
                for split in split_list_unique:
                    if split in self.bad_label_dict[fs]:
                        if split in bad_label_split_list:
                            continue
                        bad_label_split_list.append(split)
                        # check up and down from split
                        search = re.search(r'(.+)_(\d{4})\.(.+)', split)
                        if search:
                            perf = search.group(1)
                            split_num = int(search.group(2))
                            post = search.group(3)
                            up_counter = split_num + 1
                            down_counter = split_num - 1
                            while True:
                                down_split = f'{perf}_{down_counter:04d}.{post}'
                                if down_split in split_list_unique:
                                    bad_label_split_list.append(down_split)
                                    down_counter -= 1
                                else:
                                    break
                            while True:
                                up_split = f'{perf}_{up_counter:04d}.{post}'
                                if up_split in split_list_unique:
                                    bad_label_split_list.append(up_split)
                                    up_counter += 1
                                else:
                                    break
            if bad_label_split_list:
                bad_label_split_list = list(set(bad_label_split_list))
                bad_label_split_list.sort()
                index_list = []
                for index, split in enumerate(split_list_all):
                    if split not in bad_label_split_list:
                        index_list.append(index)
                    else:
                        if df_collector.collect:
                            self.bad_label_frame_counters_dict[fs] += 1
                df = df.loc[index_list].reset_index(drop=True)
        return df

    def check_bad_labels_tp(self, fs, df_matched, df_not_matched):
        if fs in self.bad_label_dict.keys():
            # if split in df_not_matched is also in bad labeled splits list, move row with that split to df_matched
            if len(df_not_matched) > 0:
                df_not_matched.reset_index(inplace=True, drop=True)
                bad_label_split_list = []
                # get list of splits in df
                split_list_all = list(df_not_matched['File_Name'])
                split_list_unique = list(set(split_list_all))
                split_list_unique.sort()
                if split_list_unique:
                    for split in split_list_unique:
                        if split in self.bad_label_dict[fs]:
                            bad_label_split_list.append(split)
                if bad_label_split_list:
                    to_matched_index_list = []
                    keep_in_not_matched_index_list = []
                    for index, split in enumerate(split_list_all):
                        # if split is in bad labeled splits list get index, so it can be moved to df_matched
                        if split in bad_label_split_list:
                            to_matched_index_list.append(index)
                            if df_collector.collect:
                                self.bad_label_frame_counters_dict[fs] += 1
                        # else get index of rows to keep in df_matched
                        else:
                            keep_in_not_matched_index_list.append(index)
                    if to_matched_index_list:
                        # move to df_matched
                        df_to_matched = df_not_matched.loc[to_matched_index_list].reset_index(drop=True)
                        df_matched = pd.concat([df_matched, df_to_matched], ignore_index=True)
                        # sort by original index
                        df_matched.sort_values(by=['index'], inplace=True)
                        df_matched.reset_index(drop=True, inplace=True)
                        # new df_not_matched
                        df_not_matched = df_not_matched.loc[keep_in_not_matched_index_list].reset_index(drop=True)
        return df_matched, df_not_matched

    @staticmethod
    def check_backup_label(label, df_matched, df_not_matched, df_not_matched_backup_lab):
        if len(df_not_matched) > 0:
            matched_backup_index_list = []
            keep_im_not_matched_index_list = []
            # get signal from label
            if df_not_matched.columns.values[1] in c.SYS_ALL:
                signal_to_check = c.LAB_TO_SYS[label][0]
                for index in df_not_matched.index.values:
                    signal_to_check_value = df_not_matched.loc[index, signal_to_check]
                    if signal_to_check_value > 1:
                        not_matched_index = df_not_matched.loc[index, 'index']
                        backup_lab_values_set = set(df_not_matched_backup_lab.loc[not_matched_index, :].values)
                        if signal_to_check_value in backup_lab_values_set:
                            matched_backup_index_list.append(index)
                        else:
                            keep_im_not_matched_index_list.append(index)
            if matched_backup_index_list:
                # move to df_matched
                df_to_matched = df_not_matched.loc[matched_backup_index_list].reset_index(drop=True)
                df_matched = pd.concat([df_matched, df_to_matched], ignore_index=True)
                # sort by original index
                df_matched.sort_values(by=['index'], inplace=True)
                df_matched.reset_index(drop=True, inplace=True)
                # new df_not_matched
                df_not_matched = df_not_matched.loc[keep_im_not_matched_index_list].reset_index(drop=True)
        return df_matched, df_not_matched

    def calculate_fp(self, df_grouped, partials_dict, to_check_label_dict):
        # false positives
        for key, value in df_grouped.items():
            print('calculate_fp')
            _lab = value['lab'].reset_index()
            names = c.SYS_TO_LAB
            for signal, labels in names.items():
                if signal == 'freeview':
                    pass
                to_filter = []
                to_filter.extend(labels)
                to_filter.append(signal)
                _lab[to_filter] = _lab[to_filter].apply(pd.to_numeric)
                to_filter.extend(['grabIndex', 'File_Name', 'itrk_name', 'DayNight'])
                temp = _lab[to_filter]
                temp['max_lab'] = temp[labels].max(axis=1)
                freeview_df = temp[temp['max_lab'] < 2]
                self.not_ready_check.count_fv_not_ready(freeview_df, signal)
                # If zero is the length of the dataframe where detected failsafe is more than 1
                if len(temp.loc[temp[signal] > 1]) == 0:
                    continue
                for severity in [2, 4, 5]:
                    # dataframe where detected failsafe equals severity
                    sig_sev_df = temp.loc[temp[signal] == severity].reset_index()
                    if len(sig_sev_df) > 0:
                        matching, not_matching = self.match_sys_fs(sig_sev_df, signal, severity, to_check_label_dict)
                        if len(matching) > 0:
                            matching = self.check_bad_labels_fp(signal, matching)
                        if len(matching) > 0:
                            self.tp_fp_counter.count_fp(matching, signal, severity)
                            # check labeled ignore
                            self.not_ready_check.count_fp_ignore(matching, signal)
                            # list of all labels that are not backups for detected failsafe
                            xx = list(set(labels[1:]) - set(to_check_label_dict[signal]))
                            # list of all labeled failsafes from xx
                            x = list(sig_sev_df[xx].columns[sig_sev_df[xx].isin([2, 3, 4, 5]).any()])
                            xxx = []
                            for n, row in matching.iterrows():
                                # aa = self.data_lab.loc[self.data_lab.grabIndex == int(row.grabIndex), 'itrk_name']
                                # aaa = self.data_lab.loc[self.data_lab.grabIndex == int(row.grabIndex), 'itrk_name'].iloc[0]
                                xxx.append([row.File_Name, int(row.grabIndex),
                                            self.data_lab.loc[
                                                self.data_lab.grabIndex == int(row.grabIndex), 'itrk_name'].iloc[0], signal, severity,
                                            row.to_list()])
                            # ADD FP TO FAILED DATAFRAME -------------------------------------------------------------------
                            df_collector.add_df(matching, signal, self._file_list)
                            partials_dict["FalsePositive"].append({"FsName": signal,
                                                                   "LogNameEventStart": sig_sev_df['File_Name'].iloc[0],
                                                                   "LogNameEventStop": sig_sev_df['File_Name'].iloc[-1],
                                                                   "Severity": severity,
                                                                   "NumberOfFrames": len(matching) * 16,
                                                                   "Labeled": x,
                                                                   "Other": xxx,
                                                                   "DayNight": matching.loc[matching.index[0], 'DayNight']})

    def calculate_tp(self, df_grouped, lab_sig_dict, severities_to_check, only_sys_severity=True):
        # true positive
        label_names_dict = c.PARTIALS_NAMES_LAB
        template = {"To_short_events": 0, "LabeledFs": [], "FalsePositive": []}
        severity_sys = {2: '25', 3: '50', 4: '75', 5: '99'}
        for lab_sys_df_dict in df_grouped.values():
            _lab = lab_sys_df_dict['lab'].reset_index()
            # if df_collector.collect:
            #     lab_sig_counter.count(_lab)
            for label_name, signals_to_check in lab_sig_dict.items():
                if label_name == 'freeview':
                    kk = list(lab_sig_dict.keys())
                    kk.remove('freeview')
                    to_filter = []
                    to_filter.extend(kk)
                    to_filter.extend(signals_to_check)
                    _lab[to_filter] = _lab[to_filter].apply(pd.to_numeric)
                    to_filter.extend(['grabIndex', 'File_Name', 'DayNight'])
                    temp = _lab[to_filter]
                    temp['to_match'] = temp[kk].max(axis=1)
                    temp_2 = temp.loc[temp['to_match'] < 2].reset_index()
                    if len(temp_2) / 2 > c.RECOGNITION_TIME[c.LAB_TO_SYS[label_name][0]]:
                        temp_2['checking'] = temp_2[signals_to_check].max(axis=1)
                        matching = temp_2.loc[temp_2['checking'] < 2]
                        if len(matching) != 0:
                            template['LabeledFs'].append({"FsName": label_names_dict[label_name],
                                                          "LogNameEventStart": temp_2['File_Name'].iloc[0],
                                                          "LogNameEventStop": temp_2['File_Name'].iloc[-1],
                                                          "Severity": 99,
                                                          "IsRecognition": True,
                                                          "RecognitionTime": matching.index[0] * 16 / 36,
                                                          "FramesDetected": len(matching) * 16,
                                                          "FramesLabeled": len(temp_2) * 16,
                                                          "DayNight": matching.loc[matching.index[0], 'DayNight']})
                        else:
                            template['LabeledFs'].append({"FsName": label_names_dict[label_name],
                                                          "LogNameEventStart": temp_2['File_Name'].iloc[0],
                                                          "LogNameEventStop": temp_2['File_Name'].iloc[-1],
                                                          "Severity": 99,
                                                          "IsRecognition": False,
                                                          "RecognitionTime": np.nan,
                                                          "FramesDetected": 0,
                                                          "FramesLabeled": len(temp_2) * 16,
                                                          "DayNight": temp.loc[temp.index[0], 'DayNight']}, )
                    continue
                to_filter = []
                to_filter.extend(signals_to_check)
                to_filter.append(label_name)
                _lab[to_filter] = _lab[to_filter].apply(pd.to_numeric)
                to_filter.extend(['grabIndex', 'File_Name', 'itrk_name', 'DayNight', 'Velocity'])
                temp = _lab[to_filter]
                if only_sys_severity:
                    labeled_severity_list = c.VALID_SEVERITY_LAB[label_name]  # TPR shall only be calculated on failsafe levels that are a valid output
                else:
                    labeled_severity_list = [2, 4, 5]
                for labeled_severity in labeled_severity_list:
                    temp_2 = temp.loc[temp[label_name] == labeled_severity].reset_index()
                    if len(temp_2) != 0:
                        temps = []
                        diff = np.where(np.diff(temp_2['grabIndex']) > 64)[0]
                        diff = diff + 1
                        diff = np.append(diff, len(temp_2))
                        diff = np.append(0, diff)
                        for iii, jjj in zip(diff[:-1], diff[1:]):
                            temps.append(temp_2.iloc[iii:jjj])
                        for temp_3 in temps:
                            if len(temp_3) / 2 > c.RECOGNITION_TIME[c.LAB_TO_SYS[label_name][0]]:
                                temp_3['to_match'] = temp_3[signals_to_check].max(axis=1)
                                # matching = temp_3.loc[temp_3["to_match"] > 1]
                                matching, not_matching = self.match_lab_fs(temp_3, signals_to_check, label_name, labeled_severity, severities_to_check)
                                matching, not_matching = self.check_bad_labels_tp(label_name, matching, not_matching)
                                rows = list(not_matching['index'])
                                columns = c.LAB_BACKUP[label_name]
                                if rows and columns:
                                    lab_info_not_matching = _lab.loc[list(not_matching['index']), c.LAB_BACKUP[label_name]]
                                    matching, not_matching = self.check_backup_label(label_name, matching, not_matching, lab_info_not_matching)
                                if len(not_matching) > 0:
                                    self.not_ready_check.count_fn_not_ready(not_matching, label_name)
                                if label_name == c.LAB_SNOWFALL:
                                    fs_name = label_names_dict[c.LAB_RAIN]
                                    label_name_kpi = c.LAB_RAIN
                                else:
                                    fs_name = label_names_dict[label_name]
                                    label_name_kpi = label_name
                                if len(matching) != 0:
                                    self.tp_fp_counter.count_tp(matching, label_name_kpi, labeled_severity)
                                    # get event average velocity
                                    ave_speed = matching['Velocity'].mean()
                                    rec_time = (matching.loc[matching.index[0], 'index'] - temp_3.loc[temp_3.index[0], 'index']) * 16 / 36
                                    print(rec_time)
                                    template['LabeledFs'].append({"FsName": fs_name,
                                                                  "LogNameEventStart": temp_3['File_Name'].iloc[0],
                                                                  "LogNameEventStop": temp_3['File_Name'].iloc[-1],
                                                                  "Severity": severity_sys[labeled_severity],
                                                                  "IsRecognition": True,
                                                                  "RecognitionTime": rec_time,
                                                                  "FramesDetected": len(matching) * 16,
                                                                  "FramesLabeled": len(temp_3) * 16,
                                                                  "EventAveSpeed": ave_speed,
                                                                  "DayNight": matching.loc[matching.index[0], 'DayNight']})
                                elif len(not_matching) != 0:
                                    # get event average velocity
                                    ave_speed = not_matching['Velocity'].mean()
                                    template['LabeledFs'].append({"FsName": fs_name,
                                                                  "LogNameEventStart": temp_3['File_Name'].iloc[0],
                                                                  "LogNameEventStop": temp_3['File_Name'].iloc[-1],
                                                                  "Severity": severity_sys[labeled_severity],
                                                                  "IsRecognition": False,
                                                                  "RecognitionTime": np.nan,
                                                                  "FramesDetected": 0,
                                                                  "FramesLabeled": len(not_matching) * 16,
                                                                  "EventAveSpeed": ave_speed,
                                                                  "DayNight": not_matching.loc[not_matching.index[0], 'DayNight']})
                                # ADD FN TO FAILED DATAFRAME ----(df_collector handles empty df)---------------------------------
                                df_collector.add_df(not_matching, label_name, self._file_list)

                            else:
                                template['To_short_events'] += 1
        return template  # 2 tabs, but in calculate_tp_exact_match there are 3 tabs?

    @staticmethod
    def _convert_ignore(dataframe):
        df = dataframe.copy()
        for label in c.LAB_ALL:
            df.loc[df[label] == 0, label] = -1
            df.loc[df[label] == 9, label] = 1
        # if signal 25 is set, and label is ignore, set label to 25
        for signal, lab_list in c.SYS_TO_LAB2.items():
            lab = lab_list[0]
            sig_df = df[df[signal] == 2]
            sig_lab_ignore_df = sig_df[sig_df[lab] == 1]
            sig_lab_ignore_indexes = sig_lab_ignore_df.index.values
            if sig_lab_ignore_indexes.size > 0:
                df.loc[sig_lab_ignore_indexes, lab] = 2
        df.reset_index(drop=True, inplace=True)
        return df

    @staticmethod
    def _remove_toggling_tp(dataframe):
        df = dataframe.copy()
        seconds = 3
        valid_severity_per_fs = c.VALID_SEVERITY_LAB
        for label, valid_severity in valid_severity_per_fs.items():
            if label not in df.columns.values:
                continue
            # df.loc[df[k] == 9, k] = -2  # change ignore to -1
            try:
                df[label] = df[label].astype(int)
            except Exception as e:
                print(e)
            df_copy = df.copy()
            try:
                where_severity_change = np.where(np.diff(df[label]) != 0)[0]
                where_severity_change = np.append(where_severity_change, len(df))
                if len(where_severity_change) != 0:
                    first = where_severity_change[0]
                    flag = False
                    sec = 0
                    for i in range(len(where_severity_change) - 1):
                        diff = where_severity_change[i + 1] - where_severity_change[i]
                        if diff < seconds * 2:
                            if flag:
                                sec = where_severity_change[i + 1] + 2
                            else:
                                first = where_severity_change[i]
                                sec = where_severity_change[i + 1] + 2
                                flag = True
                        else:
                            if flag:
                                df[label].iloc[first:sec] = max(df[label].iloc[first:sec])
                                flag = False
                    if flag:
                        df[label].iloc[first:sec] = max(df[label].iloc[first:sec])
                # get the original label if its better
                fs_list = c.LAB_TO_SPI_BACKUP[label]
                df_fs = df[fs_list]
                df_fs[label] = df_copy[label]
                label_fixed = label + '_wo_toggling'
                df_fs[label_fixed] = df[label]
                df_fs.loc[df_fs[label] == -1, label] = 0
                df_fs.loc[df_fs[label_fixed] == -1, label_fixed] = 0
                df_fs['max_sig'] = df_fs[fs_list].max(axis=1)
                df_fs['final_label'] = df_fs[label]  # label_fixed
                for index in df_fs.index.values:
                    # All signals are zero ---------------------------------------------------------
                    if df_fs.loc[index, 'max_sig'] == 0:
                        # if signals are zero, and one of the labels original or corrected are zero, set final label = 0, go to next index
                        if df_fs.loc[index, label] == 0 or df_fs.loc[index, label_fixed] == 0:
                            df_fs.loc[index, 'final_label'] = 0
                            continue
                        # if signals are zero, and one of the labels original or corrected are none, set final label = 0, go to next index
                        if df_fs.loc[index, label] == 9 or df_fs.loc[index, label_fixed] == 9:
                            df_fs.loc[index, 'final_label'] = 9
                            continue
                        # if FN, use smaller label, go to next index
                        if df_fs.loc[index, label] != 0 and df_fs.loc[index, label_fixed] != 0:
                            # if original label is invalid, set final label to 0, go to next index
                            if df_fs.loc[index, label] not in valid_severity:
                                df_fs.loc[index, 'final_label'] = 0
                                continue
                            # if both labels are valid use smaller label
                            if df_fs.loc[index, label_fixed] in valid_severity:
                                if df_fs.loc[index, label] < df_fs.loc[index, label_fixed]:
                                    df_fs.loc[index, 'final_label'] = df_fs.loc[index, label]
                                else:
                                    df_fs.loc[index, 'final_label'] = df_fs.loc[index, label_fixed]
                            # if original label is valid use original
                            else:
                                df_fs.loc[index, 'final_label'] = df_fs.loc[index, label]
                            continue
                    # A signal is more than zero ---------------------------------------------------------
                    if df_fs.loc[index, 'max_sig'] > 0:
                        # if both labels are zero, set final label = 0
                        if df_fs.loc[index, label] == 0 and df_fs.loc[index, label_fixed] == 0:
                            df_fs.loc[index, 'final_label'] = 0
                            continue
                        if df_fs.loc[index, label] == 9 and df_fs.loc[index, label_fixed] == 9:
                            df_fs.loc[index, 'final_label'] = 9
                            continue
                        # if only none(0) or ignore(9), set final label to ignore
                        if (df_fs.loc[index, label] == 9 and df_fs.loc[index, label_fixed] == 0) or (df_fs.loc[index, label] == 0 and df_fs.loc[index, label_fixed] == 9):
                            if df_fs.loc[index, fs_list[0]] == 0:
                                df_fs.loc[index, 'final_label'] = 0
                            else:
                                df_fs.loc[index, 'final_label'] = 9
                            continue
                        # if one of the labels is 0 and fs is 0, set final label to 0
                        if (df_fs.loc[index, label] == 0 or df_fs.loc[index, label_fixed] == 0) and df_fs.loc[index, fs_list[0]] == 0:
                            df_fs.loc[index, 'final_label'] = 0
                            continue
                        # if one for the labels is 9 and fs is 0, set final label to 9
                        if df_fs.loc[index, label] == 9 or df_fs.loc[index, label_fixed] == 9 and df_fs.loc[index, fs_list[0]] == 0:
                            df_fs.loc[index, 'final_label'] = 9
                            continue
                        # if signal or backup signal is set and there is an invalid label
                        if (df_fs.loc[index, label] > 0 or df_fs.loc[index, label_fixed] > 0) and \
                                (df_fs.loc[index, label] not in c.VALID_SEVERITY_LAB[label] or df_fs.loc[index, label_fixed] not in c.VALID_SEVERITY_LAB[label]):
                            for fs in fs_list:
                                if df_fs.loc[index, fs] > 0:
                                    df_fs.loc[index, label] = df_fs.loc[index, fs]
                                    df_fs.loc[index, label_fixed] = df_fs.loc[index, fs]
                                    break
                        # check if the failsafe signal equals original label
                        if df_fs.loc[index, fs_list[0]] == df_fs.loc[index, label]:
                            df_fs.loc[index, 'final_label'] = df_fs.loc[index, label]
                        # check if the failsafe signal equals corrected label
                        elif df_fs.loc[index, fs_list[0]] == df_fs.loc[index, label_fixed]:
                            df_fs.loc[index, 'final_label'] = df_fs.loc[index, label_fixed]
                        # check if maximum signal equals original label
                        elif df_fs.loc[index, 'max_sig'] == df_fs.loc[index, label]:
                            df_fs.loc[index, 'final_label'] = df_fs.loc[index, label]
                        # check if maximum signal equals corrected label
                        elif df_fs.loc[index, 'max_sig'] == df_fs.loc[index, label_fixed]:
                            df_fs.loc[index, 'final_label'] = df_fs.loc[index, label_fixed]
                        # else try to use label that is in signal severity backup
                        else:
                            try:
                                for fs in fs_list:
                                    # k_list = c.SEVERITY_BACKUP[k][df_fs.loc[index, k]][fs]
                                    # k_fixed_list = c.SEVERITY_BACKUP[k][df_fs.loc[index, k_fixed]][fs]
                                    if df_fs.loc[index, label_fixed] in c.SEVERITY_BACKUP[label].keys():
                                        if df_fs.loc[index, fs] in c.SEVERITY_BACKUP[label][df_fs.loc[index, label_fixed]][fs]:
                                            df_fs.loc[index, 'final_label'] = df_fs.loc[index, label_fixed]
                                            break
                                        else:
                                            if abs(df_fs.loc[index, label_fixed] - df_fs.loc[index, fs]) < abs(df_fs.loc[index, label] - df_fs.loc[index, fs]):
                                                df_fs.loc[index, 'final_label'] = df_fs.loc[index, label_fixed]
                                            else:
                                                df_fs.loc[index, 'final_label'] = df_fs.loc[index, label]
                                    elif df_fs.loc[index, label] in c.SEVERITY_BACKUP[label].keys():
                                        if df_fs.loc[index, fs] in c.SEVERITY_BACKUP[label][df_fs.loc[index, label]][fs]:
                                            df_fs.loc[index, 'final_label'] = df_fs.loc[index, label]
                                            break
                                        else:
                                            if abs(df_fs.loc[index, label] - df_fs.loc[index, fs]) < abs(df_fs.loc[index, label_fixed] - df_fs.loc[index, fs]):
                                                df_fs.loc[index, 'final_label'] = df_fs.loc[index, label]
                                            else:
                                                df_fs.loc[index, 'final_label'] = df_fs.loc[index, label_fixed]
                            except:
                                pass
                df_fs['final_label'] = df_fs['final_label'].astype(int)
                df[label] = df_fs['final_label']
                df.loc[df[label] == 0, label] = -1
                df.loc[df[label] == 9, label] = 1
                # print()
            except:
                pass
        df.reset_index(drop=True, inplace=True)
        return df

    @staticmethod
    def _remove_toggling_fp(df):
        seconds = 3
        valid_severity_per_fs = c.VALID_SEVERITY_LAB
        for label, valid_severity in valid_severity_per_fs.items():
            if label not in df.columns.values:
                continue
            df[label] = df[label].astype(int)
            df_copy = df.copy()
            try:
                where_severity_change = np.where(np.diff(df[label]) != 0)[0]
                where_severity_change = np.append(where_severity_change, len(df))
                if len(where_severity_change) != 0:
                    first = where_severity_change[0]
                    flag = False
                    sec = 0
                    for i in range(len(where_severity_change) - 1):
                        diff = where_severity_change[i + 1] - where_severity_change[i]
                        if diff < seconds * 2:
                            if flag:
                                sec = where_severity_change[i + 1] + 2
                            else:
                                first = where_severity_change[i]
                                sec = where_severity_change[i + 1] + 2
                                flag = True
                        else:
                            if flag:
                                df[label].iloc[first:sec] = max(df[label].iloc[first:sec])
                                flag = False
                    if flag:
                        df[label].iloc[first:sec] = max(df[label].iloc[first:sec])
                # get the original label if its better
                fs_list = c.LAB_TO_SPI_BACKUP[label]
                df_fs = df[fs_list]
                df_fs[label] = df_copy[label]
                label_fixed = label + '_wo_toggling'
                df_fs[label_fixed] = df[label]
                df_fs.loc[df_fs[label] == -1, label] = 0
                df_fs.loc[df_fs[label_fixed] == -1, label_fixed] = 0
                df_fs['max_sig'] = df_fs[fs_list].max(axis=1)
                df_fs['final_label'] = df_fs[label]  # label_fixed
                for index in df_fs.index.values:
                    # if signal or backup signal is set
                    if df_fs.loc[index, 'max_sig'] > 0:
                        # if original label is invalid (labeled but not a valid label), set to signal
                        if 0 < df_fs.loc[index, label] > 6 and df_fs.loc[index, label] not in c.VALID_SEVERITY_LAB[label]:
                            for fs in fs_list:
                                if df_fs.loc[index, fs] > 0:
                                    df_fs.loc[index, 'final_label'] = df_fs.loc[index, fs]
                                    break
                            continue
                        if 0 < df_fs.loc[index, label] < 6 and 2 > df_fs.loc[index, label_fixed] > 5:
                            df_fs.loc[index, 'final_label'] = df_fs.loc[index, label]
                            continue
                        if 0 < df_fs.loc[index, label_fixed] < 6 and 2 > df_fs.loc[index, label] > 5:
                            df_fs.loc[index, 'final_label'] = df_fs.loc[index, label_fixed]
                            continue
                        # check if the failsafe signal equals original label
                        if df_fs.loc[index, fs_list[0]] == df_fs.loc[index, label]:
                            df_fs.loc[index, 'final_label'] = df_fs.loc[index, label]
                        # check if the failsafe signal equals corrected label
                        elif df_fs.loc[index, fs_list[0]] == df_fs.loc[index, label_fixed]:
                            df_fs.loc[index, 'final_label'] = df_fs.loc[index, label_fixed]
                        # check if maximum signal equals original label
                        elif df_fs.loc[index, 'max_sig'] == df_fs.loc[index, label]:
                            df_fs.loc[index, 'final_label'] = df_fs.loc[index, label]
                        # check if maximum signal equals corrected label
                        elif df_fs.loc[index, 'max_sig'] == df_fs.loc[index, label_fixed]:
                            df_fs.loc[index, 'final_label'] = df_fs.loc[index, label_fixed]
                df_fs['final_label'] = df_fs['final_label'].astype(int)
                df[label] = df_fs['final_label']
                df.loc[df[label] == 0, label] = -1
                df.loc[df[label] == 9, label] = 1
                # print()
            except:
                pass
        df.reset_index(drop=True, inplace=True)
        return df

    def _map_day_time(self, df):
        df.reset_index(drop=True, inplace=True)
        if len(df) > 0:
            df['DayNight'] = 'Day'
            file_names = df['File_Name'].tolist()
            for index, file_name in enumerate(file_names):
                if file_name in self.day_time_dict.keys():
                    df.loc[index, 'DayNight'] = self.day_time_dict[file_name]
        return df

    @classmethod
    def return_partials(cls, n):
        if n == 'eth_any':
            return cls.partials_eth_any
        elif n == 'eth_backup':
            return cls.partials_eth_backup
        elif n == 'eth_backup_up_down':
            return cls.partials_eth_backup_up_down
        elif n == 'eth_backup_any':
            return cls.partials_eth_backup_any
        elif n == 'eth_exact':
            return cls.partials_eth_exact
        elif n == 'any':
            return cls.partials_any
        elif n == 'backup':
            return cls.partials_backup
        elif n == 'backup_up_down':
            return cls.partials_backup_up_down
        elif n == 'backup_any':
            return cls.partials_backup_any
        elif n == 'exact':
            return cls.partials_exact
        elif n == 'exact_up_down':
            return cls.partials_exact_up_down
        elif n == 'degrade':
            return cls.partials_degrade
        elif n == 'flexray':
            return cls.partials_flexray

    @staticmethod
    def save_to_json(path, name, what):
        with open(os.path.join(path, name), 'w') as f:
            json.dump(what, f, indent=2)

    @staticmethod
    def load_json(path, file=None):
        """
        Load object
        :param path: path to folder
        :param file: json file name
        :return:
        """
        if file:
            if '.json' not in file:
                filename = file + '.json'
            else:
                filename = file
            path = os.path.join(path, filename)
        try:
            with open(path, 'r') as f:
                print(f'loading json: {path}')
                return json.load(f)
        except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
            print(f'failed to load json: {path}')
            print(e)
            raise e
