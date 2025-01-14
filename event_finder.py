import os
import json
import time
import pandas as pd
import config.constant as c


class EventFinder:

    def __init__(self):

        self.path_to_partial_results = r'f:\CARIAD\BHE\REPRO\X071\spi_exact'
        self.path_to_output_excel = r'f:\CARIAD\BHE\REPRO\X071\spi_exact\event_finder'
        self.ext = '.json'
        self.file_list = []
        self.severity_tp_list = [0, 25, 50, 75, 99]
        self.severity_fp_list = [0, 1, 2, 3, 4, 5]

        self.columns = c.KPI_NAMES_INIT + c.FAILED_KPI_FP_EVENTS

        self.event_counter_tp_day_df = pd.DataFrame(index=self.severity_tp_list, columns=c.KPI_NAMES_INIT)
        self.event_counter_fn_day_df = pd.DataFrame(index=self.severity_tp_list, columns=c.KPI_NAMES_INIT)
        self.event_counter_fp_day_df = pd.DataFrame(index=self.severity_fp_list, columns=c.FAILED_KPI_FP_EVENTS)
        self.event_counter_tp_night_df = pd.DataFrame(index=self.severity_tp_list, columns=c.KPI_NAMES_INIT)
        self.event_counter_fn_night_df = pd.DataFrame(index=self.severity_tp_list, columns=c.KPI_NAMES_INIT)
        self.event_counter_fp_night_df = pd.DataFrame(index=self.severity_fp_list, columns=c.FAILED_KPI_FP_EVENTS)
        self.event_counter_tp_na_df = pd.DataFrame(index=self.severity_tp_list, columns=c.KPI_NAMES_INIT)
        self.event_counter_fn_na_df = pd.DataFrame(index=self.severity_tp_list, columns=c.KPI_NAMES_INIT)
        self.event_counter_fp_na_df = pd.DataFrame(index=self.severity_fp_list, columns=c.FAILED_KPI_FP_EVENTS)
        self.event_counter_tp_total_df = pd.DataFrame(index=self.severity_tp_list, columns=c.KPI_NAMES_INIT)
        self.event_counter_fn_total_df = pd.DataFrame(index=self.severity_tp_list, columns=c.KPI_NAMES_INIT)
        self.event_counter_fp_total_df = pd.DataFrame(index=self.severity_fp_list, columns=c.FAILED_KPI_FP_EVENTS)
        self.event_counter_tp_day_df.fillna(0, inplace=True)
        self.event_counter_fn_day_df.fillna(0, inplace=True)
        self.event_counter_fp_day_df.fillna(0, inplace=True)
        self.event_counter_tp_night_df.fillna(0, inplace=True)
        self.event_counter_fn_night_df.fillna(0, inplace=True)
        self.event_counter_fp_night_df.fillna(0, inplace=True)
        self.event_counter_tp_na_df.fillna(0, inplace=True)
        self.event_counter_fn_na_df.fillna(0, inplace=True)
        self.event_counter_fp_na_df.fillna(0, inplace=True)
        self.event_counter_tp_total_df.fillna(0, inplace=True)
        self.event_counter_fn_total_df.fillna(0, inplace=True)
        self.event_counter_fp_total_df.fillna(0, inplace=True)
        self.error_tp_dict = {k: [] for k in c.KPI_NAMES_INIT}
        self.error_fp_dict = {k: [] for k in c.FAILED_KPI_FP_EVENTS}
        self.frame_counter_tp_total_df = pd.DataFrame(index=self.severity_tp_list, columns=c.KPI_NAMES_INIT)
        self.frame_counter_tp_fn_total_df = pd.DataFrame(index=self.severity_tp_list, columns=c.KPI_NAMES_INIT)
        self.frame_counter_tp_total_df.fillna(0, inplace=True)
        self.frame_counter_tp_fn_total_df.fillna(0, inplace=True)


    @staticmethod
    def load_json(path, file=None):
        """
        Load json file
        :param path: path to folder
        :param file: json file name
        :return: object
        """
        if file:
            json_path = os.path.join(path, file)
        else:
            json_path = path
        try:
            with open(json_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
            print(f'OutputDiffTable: ERROR: Cant open {file}')
            print(e)

    @staticmethod
    def save_json(obj, path, file=None):
        """
        Save object to pickle
        :param obj: object to be serialized
        :param path: path to folder
        :param file: file name
        :return:
        """
        if file:
            path_file = os.path.join(path, file)
        else:
            path_file = path
        try:
            with open(path_file, 'w') as f:
                json.dump(obj, f, indent=2)
        except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
            print(f'failed to save json: {file}')
            print(e)
            raise e

    def get_df_files(self, path, ext):

        try:
            self.file_list.clear()
            allfiles = os.listdir(path)
        except (FileNotFoundError, PermissionError, NotADirectoryError) as e:
            print(f'OutputDiffTable: ERROR: Cant open {path}')
            print(e)
            raise e
        else:
            if allfiles:
                for file in allfiles:
                    if file.endswith(ext):
                        self.file_list.append(file)
            else:
                print(f'OutputDiffTable: No {ext} in {path}')
                print(FileNotFoundError)
                raise FileNotFoundError

    @staticmethod
    def get_splits(start_split, stop_split):
        split_list = []
        log_name = start_split[0:44]
        start_log_int = int(start_split[44:48])
        stop_log_int = int(stop_split[44:48])
        for i in range(start_log_int, stop_log_int + 1):
            i_string = f'{log_name}{i:04d}.pickle.xz'
            split_list.append(i_string)
        return split_list

    def find_event(self):
        self.get_df_files(self.path_to_partial_results, self.ext)
        print('TP/FN --------------------------------------------------------')
        # TP/FN
        tp_counter = 0
        for file in self.file_list:
            hilrep = self.load_json(self.path_to_partial_results, file)
            if hilrep:
                for main_dict in hilrep:
                    if main_dict:
                        if "LabeledFs" in main_dict.keys():
                            if main_dict["LabeledFs"]:
                                for event_dict in main_dict["LabeledFs"]:
                                    if "FsName" in event_dict and "DayNight" in event_dict and "IsRecognition" in event_dict:
                                        if event_dict["FsName"] == "Low Sun" and event_dict["Severity"] == "99": #or event_dict["FsName"] == "Sun Ray") and event_dict["DayNight"] == "NIGHT":
                                            tp_counter += 1
                                            if event_dict["IsRecognition"]:
                                                fs_type = 'TP'
                                            else:
                                                fs_type = 'FN'
                                            print(f'{tp_counter} {fs_type} {event_dict["FsName"]}: {file}')
                                        if event_dict["DayNight"] == "DAY":
                                            if event_dict["IsRecognition"]:
                                                self.event_counter_tp_day_df.loc[int(event_dict["Severity"]), event_dict["FsName"]] += 1
                                            else:
                                                self.event_counter_fn_day_df.loc[int(event_dict["Severity"]), event_dict["FsName"]] += 1
                                        elif event_dict["DayNight"] == "NIGHT":
                                            if event_dict["IsRecognition"]:
                                                self.event_counter_tp_night_df.loc[int(event_dict["Severity"]), event_dict["FsName"]] += 1
                                            else:
                                                self.event_counter_fn_night_df.loc[int(event_dict["Severity"]), event_dict["FsName"]] += 1
                                        else:
                                            if event_dict["IsRecognition"]:
                                                self.event_counter_tp_na_df.loc[int(event_dict["Severity"]), event_dict["FsName"]] += 1
                                            else:
                                                self.event_counter_fn_na_df.loc[int(event_dict["Severity"]), event_dict["FsName"]] += 1
                                            self.error_tp_dict[event_dict["FsName"]].append(file)
                                        if event_dict["IsRecognition"]:
                                            self.event_counter_tp_total_df.loc[int(event_dict["Severity"]), event_dict["FsName"]] += 1
                                        else:
                                            self.event_counter_fn_total_df.loc[int(event_dict["Severity"]), event_dict["FsName"]] += 1
                                        self.frame_counter_tp_total_df.loc[int(event_dict["Severity"]), event_dict["FsName"]] += event_dict["FramesDetected"]
                                        self.frame_counter_tp_fn_total_df.loc[int(event_dict["Severity"]), event_dict["FsName"]] += event_dict["FramesLabeled"]
        print('FP -----------------------------------------------------------')
        # FP
        pf_counter = 0
        fp_split_list = []
        for file in self.file_list:
            hilrep = self.load_json(self.path_to_partial_results, file)
            if hilrep:
                for main_dict in hilrep:
                    if main_dict:
                        if "FalsePositive" in main_dict.keys():
                            if main_dict["FalsePositive"]:
                                for event_dict in main_dict["FalsePositive"]:
                                    if "FsName" in event_dict and "DayNight" in event_dict:
                                        # if (event_dict["FsName"] == "FS_Low_Sun_0" or event_dict["FsName"] == "FS_Sun_Ray_0") and event_dict["DayNight"] == "NIGHT":
                                        if event_dict["FsName"] == "FS_Low_Sun_0" and event_dict["Severity"] == 5:
                                            pf_counter += 1
                                            # get splits
                                            start_split = event_dict["LogNameEventStart"]
                                            stop_split = event_dict["LogNameEventStop"]
                                            fp_split_list += self.get_splits(start_split, stop_split)
                                            print(f'{pf_counter} FP {event_dict["FsName"]}: {file}')
                                        if event_dict["DayNight"] == "DAY":
                                            self.event_counter_fp_day_df.loc[int(event_dict["Severity"]), event_dict["FsName"]] += 1
                                        elif event_dict["DayNight"] == "NIGHT":
                                            self.event_counter_fp_night_df.loc[int(event_dict["Severity"]), event_dict["FsName"]] += 1
                                        else:
                                            self.event_counter_fp_na_df.loc[int(event_dict["Severity"]), event_dict["FsName"]] += 1
                                            self.error_fp_dict[event_dict["FsName"]].append(file)
                                        self.event_counter_fp_total_df.loc[int(event_dict["Severity"]), event_dict["FsName"]] += 1
        self.save_json(fp_split_list, self.path_to_output_excel, 'split_list.json')
        print('--------------------------------------------------------------')
        timestr = time.strftime("%Y%m%d%H%M%S")
        df_tpr_frame = pd.DataFrame(index=self.severity_tp_list, columns=c.KPI_NAMES_INIT)
        for index in self.severity_tp_list:
            for column in c.KPI_NAMES_INIT:
                df_tpr_frame.loc[index, column] = (self.frame_counter_tp_total_df.loc[index, column] / self.frame_counter_tp_fn_total_df.loc[index, column]) * 100
        df_tpr_event = pd.DataFrame(index=self.severity_tp_list, columns=c.KPI_NAMES_INIT)
        for index in self.severity_tp_list:
            for column in c.KPI_NAMES_INIT:
                tp = self.event_counter_tp_total_df.loc[index, column]
                fn = self.event_counter_fn_total_df.loc[index, column]
                total = tp + fn
                df_tpr_event.loc[index, column] = (tp/total) * 100

        with pd.ExcelWriter(f'{self.path_to_output_excel}/event_finder_counters_{timestr}.xlsx') as writer:
            df_tpr_frame.to_excel(writer, sheet_name='TOTAL FRAME BASED TPR')
            df_tpr_event.to_excel(writer, sheet_name='TOTAL EVENT BASED TPR')
            self.event_counter_tp_total_df.to_excel(writer, sheet_name='TOTAL TP')
            self.event_counter_fn_total_df.to_excel(writer, sheet_name='TOTAL FN')
            self.event_counter_fp_total_df.to_excel(writer, sheet_name='TOTAL FP')
            self.event_counter_tp_day_df.to_excel(writer, sheet_name='TP DAY')
            self.event_counter_tp_night_df.to_excel(writer, sheet_name='TP NIGHT')
            self.event_counter_tp_na_df.to_excel(writer, sheet_name='TP NA')
            self.event_counter_fn_day_df.to_excel(writer, sheet_name='FN DAY')
            self.event_counter_fn_night_df.to_excel(writer, sheet_name='FN NIGHT')
            self.event_counter_fn_na_df.to_excel(writer, sheet_name='FN NA')
            self.event_counter_fp_day_df.to_excel(writer, sheet_name='FP DAY')
            self.event_counter_fp_night_df.to_excel(writer, sheet_name='FP NIGHT')
            self.event_counter_fp_na_df.to_excel(writer, sheet_name='FP NA')


def main():
    event_finder = EventFinder()
    event_finder.find_event()


if __name__ == "__main__":
    main()
