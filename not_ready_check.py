"""
Module counts the amount of NOT_READY and NONE states for each failsafe and severity, freeview, false positive, false negative events
Counts other NOT_READY and NONE related events
Counts IGNORE labels
Saves partial results for each measurement
Counts and makes excel with stats
Patryk Leszowski
APTIV
BWD
"""
import pandas as pd
import config.constant as c
from datetime import datetime
import json
import os
import re
import copy


class NotReadyCheck:

    def __init__(self, file_dict):

        self.file_dict = file_dict
        self.function = 'BWD'
        self.sop = c.SOP
        self.a_step = c.A_STEP
        self.collect = False
        self.dt_str = re.sub(r"[:\-. ]", "", str(datetime.now()))
        self.unique_name = self.dt_str
        self.new_folder = f'{self.function}_{self.sop}_{self.a_step}_NOT_READY_CHECK'
        self.new_path = os.path.join(c.PATH_FAILED_KPI_DFS, self.new_folder)
        self.signal_list = c.FAILED_KPI_FP_EVENTS
        self.event_counter_dict = {}
        self.count_dict = {"NOT_READY_in_Event": False,
                           "Only_NOT_READY_in_Event": False,
                           "FS_After_NOT_READY": False,
                           "FS_After_NOT_READY_Counter": 0,
                           "NONE_After_NOT_READY": False,
                           "NONE_After_NOT_READY_Counter": 0,
                           "NONE_in_Event": False,
                           "Only_NONE_in_Event": False,
                           "FS_After_NONE": False,
                           "FS_After_NONE_Counter": 0,
                           "NOT_READY_After_NONE": False,
                           "NOT_READY_After_NONE_Counter": 0,
                           "FN_NOT_READY_Counter": 0,
                           "FN_NONE_Counter": 0,
                           "FN_NOT_READY_Severity_Counter": {'2': 0, '3': 0, '4': 0, '5': 0},  # per labeled severity
                           "FN_NONE_Severity_Counter": {'2': 0, '3': 0, '4': 0, '5': 0},  # per labeled severity
                           "FN_Total_Counter": 0,
                           "FP_IGNORE_LABEL_Counter": 0,
                           "FP_Total_Counter": 0,
                           "FV_NOT_READY_Counter": 0,
                           "FV_NONE_Counter": 0,
                           "FV_FS_Counter": 0,
                           "FV_IGNORE_LABEL_Counter": 0,
                           "FV_NO_LABEL_Counter": 0,
                           "FV_Total_Counter": 0}
        self.init_event_counter_dict()

    def init_event_counter_dict(self):
        self.event_counter_dict["Start_Split"] = ""
        self.event_counter_dict["Stop_Split"] = ""
        self.event_counter_dict["Split_Count"] = 0
        for signal in self.signal_list:
            self.event_counter_dict[signal] = copy.deepcopy(self.count_dict)

    @staticmethod
    def drop_null_df(df, col):
        # drop rows if column value is nan
        df = df.loc[df[col].notnull()]
        return df

    @staticmethod
    def save_json(obj, path, file=None):
        """
        :param obj: object to be serialized
        :param path: path to folder
        :param file: file name
        :return:
        Save object to json
        """
        print(f'saving json: {file}')
        if file:
            if '.json' not in file:
                filename = file + '.json'
            else:
                filename = file
            path = os.path.join(path, filename)
        try:
            with open(path, 'w') as f:
                json.dump(obj, f, indent=2)
        except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
            print(f'failed to save json: {path}')
            print(e)
            raise e

    def get_hilrep(self):
        key = list(self.file_dict.keys())[0]
        search_line = self.file_dict[key]
        # search for HILREPP-7digits, force the engine to try matching at the furthest position
        search = re.search(r'(?s:.*).+(HILREPP-\d{7}).+', search_line)  # ex. HILREPP-2013288
        if search:
            return search.group(1)
        else:
            return None

    def save_results(self):
        if self.event_counter_dict:
            if not os.path.isdir(self.new_path):
                os.makedirs(self.new_path, exist_ok=True)
            hilrep = self.get_hilrep()
            if hilrep:
                self.unique_name = hilrep
            file_name = f'{self.function}_{self.sop}_{self.a_step}_{self.unique_name}.pickle'
            self.save_json(self.event_counter_dict, self.new_path, file_name)
        else:
            print(f'Cant save, collect is off')

    @staticmethod
    def copy_rows__col_changed_to_new_val_df(dataframe, col_name):
        """
        :param dataframe:
        :param col_name:
        :return: Dataframe
        Function searches dataframe column col_name for value changes
        Copies to df row where the change to the new value occurs (includes first row and only rows after change)
        Includes first row, and the rows where the changes to new value occurs
        Returns Dataframe df with selected rows
        """
        param_value = -1
        try:
            dataframe.reset_index(drop=True, inplace=True)
            col = list(dataframe[col_name])
        except KeyError as e:
            print(e)
            raise e
        else:
            prev_index = 0
            index_list = []
            for index, val in enumerate(col):
                if index == prev_index:
                    index_list.append(index)
                    param_value = col[index]
                elif col[index] != param_value:
                    index_list.append(index)
                    param_value = col[index]
                prev_index = index
            df = dataframe.loc[index_list]  # .reset_index(drop=True)
            return df

    def count_not_ready(self, df):
        for signal in self.signal_list:
            try:
                df = self.drop_null_df(df, signal)
                if len(df) < 1:
                    continue
                signal_df = self.copy_rows__col_changed_to_new_val_df(df, signal)
                signal_df.reset_index(drop=True, inplace=True)
                signal_list = list(signal_df[signal])
                signal_set = list(set(signal_list))
                signal_set.sort()
                split_list = list(set(df.loc[:, "File_Name"]))
                split_list.sort()
                split_count = len(split_list)
                start_split = split_list[0]
                stop_split = split_list[-1]
                self.event_counter_dict["Start_Split"] = start_split
                self.event_counter_dict["Stop_Split"] = stop_split
                self.event_counter_dict["Split_Count"] = split_count
                if 0 in signal_set:
                    if len(signal_set) == 1:
                        self.event_counter_dict[signal]["Only_NOT_READY_in_Event"] = True
                        continue
                    # check if after 0 (NOT_READY) there is a failsafe
                    found_zero = False
                    for value in signal_list:
                        if value == 0 and not found_zero:
                            found_zero = True
                            if not self.event_counter_dict[signal]["NOT_READY_in_Event"]:
                                self.event_counter_dict[signal]["NOT_READY_in_Event"] = True
                        if found_zero:
                            if value > 1:
                                found_zero = False
                                self.event_counter_dict[signal]["FS_After_NOT_READY_Counter"] += 1
                                if not self.event_counter_dict[signal]["FS_After_NOT_READY"]:
                                    self.event_counter_dict[signal]["FS_After_NOT_READY"] = True
                            if value == 1:
                                found_zero = False
                                self.event_counter_dict[signal]["NONE_After_NOT_READY_Counter"] += 1
                                if not self.event_counter_dict[signal]["NONE_After_NOT_READY"]:
                                    self.event_counter_dict[signal]["NONE_After_NOT_READY"] = True
                if 1 in signal_set:
                    if len(signal_set) == 1:
                        self.event_counter_dict[signal]["Only_NONE_in_Event"] = True
                        continue
                    found_one = False
                    for value in signal_list:
                        if value == 1 and not found_one:
                            found_one = True
                            if not self.event_counter_dict[signal]["NONE_in_Event"]:
                                self.event_counter_dict[signal]["NONE_in_Event"] = True
                        if found_one:
                            if value > 1:
                                found_one = False
                                self.event_counter_dict[signal]["FS_After_NONE_Counter"] += 1
                                if not self.event_counter_dict[signal]["FS_After_NONE"]:
                                    self.event_counter_dict[signal]["FS_After_NONE"] = True
                            if value == 0:
                                found_one = False
                                self.event_counter_dict[signal]["NOT_READY_After_NONE_Counter"] += 1
                                if not self.event_counter_dict[signal]["NOT_READY_After_NONE"]:
                                    self.event_counter_dict[signal]["NOT_READY_After_NONE"] = True
            except Exception as e:
                print(e)
                return False
        return True

    def count_fn_not_ready(self, df, label_name):
        if self.collect:
            try:
                df = self.drop_null_df(df, label_name)
                if len(df) < 1:
                    return False
                severity = str(df.loc[df.index[0], label_name])
                df_not_ready = df[df[c.LAB_TO_SYS[label_name][0]] == 0]
                df_none = df[df[c.LAB_TO_SYS[label_name][0]] == 1]
                self.event_counter_dict[c.LAB_TO_SYS[label_name][0]]["FN_NOT_READY_Counter"] += len(df_not_ready)
                self.event_counter_dict[c.LAB_TO_SYS[label_name][0]]["FN_NONE_Counter"] += len(df_none)
                self.event_counter_dict[c.LAB_TO_SYS[label_name][0]]["FN_Total_Counter"] += len(df)
                self.event_counter_dict[c.LAB_TO_SYS[label_name][0]]["FN_NOT_READY_Severity_Counter"][severity] += len(df_not_ready)
                self.event_counter_dict[c.LAB_TO_SYS[label_name][0]]["FN_NONE_Severity_Counter"][severity] += len(df_none)
                return True
            except Exception as e:
                print(f'label_name: {label_name}, count_fn_not_ready error: {e}')
                pass

    def count_fp_ignore(self, df, sig_name):
        if self.collect:
            try:
                df = self.drop_null_df(df, sig_name)
                if len(df) < 1:
                    return False
                df_ignore = df[df[c.SYS_TO_LAB[sig_name][0]] == 1]
                self.event_counter_dict[sig_name]["FP_IGNORE_LABEL_Counter"] += len(df_ignore)
                self.event_counter_dict[sig_name]["FP_Total_Counter"] += len(df)
                return True
            except Exception as e:
                print(f'count_fp_ignore error: {e}')
                pass

    def count_fv_not_ready(self, df, sig_name):
        if self.collect:
            try:
                df = self.drop_null_df(df, sig_name)
                if len(df) < 1:
                    return False
                df_not_ready = df[df[sig_name] == 0]
                df_none = df[df[sig_name] == 1]
                df_fs = df[df[sig_name] > 1]
                df_ignore = df[df[c.SYS_TO_LAB[sig_name][0]] == 1]
                df_no_label = df[df[c.SYS_TO_LAB[sig_name][0]] < 1]
                self.event_counter_dict[sig_name]["FV_NOT_READY_Counter"] += len(df_not_ready)
                self.event_counter_dict[sig_name]["FV_NONE_Counter"] += len(df_none)
                self.event_counter_dict[sig_name]["FV_FS_Counter"] += len(df_fs)
                self.event_counter_dict[sig_name]["FV_IGNORE_LABEL_Counter"] += len(df_ignore)
                self.event_counter_dict[sig_name]["FV_NO_LABEL_Counter"] += len(df_no_label)
                self.event_counter_dict[sig_name]["FV_Total_Counter"] += len(df)
                return True
            except Exception as e:
                print(f'count_fv_not_ready error: {e}')
                pass


class NotReadyBinder(NotReadyCheck):

    def __init__(self):

        self.ext = '.json'
        self.file_name = ''
        self.files = []
        super().__init__(None)
        self.counter_list = list(self.count_dict.keys())
        self.results_df = pd.DataFrame(0, index=self.count_dict.keys(), columns=c.FAILED_KPI_FP_EVENTS)
        self.results_severity_df_dict = {}
        self.split_count_df = pd.DataFrame(0, index=[0], columns=["Split_Count"])
        self.init_dfs()

    def init_dfs(self):
        # remove rows that are nested dictionaries from self.results_df
        nested = []
        counters = []
        for key, value in self.count_dict.items():
            if type(value) == bool or type(value) == int:
                counters.append(key)
            else:
                nested.append(key)
        self.results_df = self.results_df.loc[counters]
        # make results_severity_dfs with severity index names and signal rows
        for name in nested:
            indexes = self.count_dict[name].keys()
            self.results_severity_df_dict[name] = pd.DataFrame(0, indexes, columns=c.FAILED_KPI_FP_EVENTS)
        print()

    def get_df_files(self):
        try:
            allfiles = os.listdir(self.new_path)
        except (FileNotFoundError, PermissionError, NotADirectoryError) as e:
            print(f'DfBinder: ERROR: Cant open {self.new_path}')
            print(e)
            raise e
        else:
            if allfiles:
                for file in allfiles:
                    if file.endswith(self.ext):
                        self.files.append(file)
            else:
                print(f'DfBinder: No pickles in {self.new_path}')
                print(FileNotFoundError)
                raise FileNotFoundError

    @staticmethod
    def open_json_file(path, file):
        try:
            with open(os.path.join(path, file), 'rb') as f:
                return json.load(f)
        except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
            print(f'LabSigDfBinder: ERROR: Cant open {file}')
            print(e)

    def bind_dfs(self):
        if self.files:
            num_of_files = len(self.files)
            for i, file in enumerate(self.files):
                print(f'NRDfBinder: INFO: Calculating {i + 1}/{num_of_files}: {file}')
                data_dict = self.open_json_file(self.new_path, file)
                if "Split_Count" in data_dict.keys():
                    self.split_count_df.loc[0, "Split_Count"] += data_dict["Split_Count"]
                for column in c.FAILED_KPI_FP_EVENTS:
                    if data_dict[column]:
                        for counter in self.results_df.index.values:
                            self.results_df.loc[counter, column] += int(data_dict[column][counter])
                        for df_name, df in self.results_severity_df_dict.items():
                            for severity, count in data_dict[column][df_name].items():
                                df.loc[severity, column] += count
                    else:
                        print(f'{column} is empty')

    def save_df_to_excel(self):
        file_name = f'{self.function}_{self.sop}_{self.a_step}_NR_COUNT.xlsx'
        wb_name = os.path.join(self.new_path, file_name)
        with pd.ExcelWriter(wb_name) as writer:
            self.results_df.to_excel(writer, sheet_name='Counters')
            for df_name, df in self.results_severity_df_dict.items():
                df.to_excel(writer, sheet_name=df_name)
            self.split_count_df.to_excel(writer, sheet_name='Split_Count')


def main():
    nr_df_binder = NotReadyBinder()
    nr_df_binder.get_df_files()
    nr_df_binder.bind_dfs()
    nr_df_binder.save_df_to_excel()


if __name__ == "__main__":
    main()
