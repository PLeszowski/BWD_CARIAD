"""
Module checks for deviations in pitch in BWD dataset and during failsafe activations
Checks also for height 0.5m
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
from cal_test_plot import CalPlot


class CalCheck(CalPlot):

    def __init__(self, file_dict):
        self.file_dict = file_dict
        self.function = 'BWD'
        self.sop = c.SOP
        self.a_step = c.A_STEP
        self.collect = False
        self.dt_str = re.sub(r"[:\-. ]", "", str(datetime.now()))
        self.unique_name = self.dt_str
        self.new_folder = f'{self.function}_{self.sop}_{self.a_step}_CAL_CHECK'
        self.new_folder_plots = f'{self.function}_{self.sop}_{self.a_step}_CAL_CHECK_PLOTS'
        self.new_path = os.path.join(c.PATH_FAILED_KPI_DFS, self.new_folder)
        self.new_path_plots = os.path.join(c.PATH_FAILED_KPI_DFS, self.new_folder_plots)
        super().__init__(self.new_path_plots)
        self.label_list = c.LAB
        self.signal_list = c.SYS_ALL
        self.max_pitch_dev = 2  # degrees
        self.c2w_state_dict = {c.NO_VALUE: "NO_VALUE",
                               c.CALIBRATED: "CALIBRATED",
                               c.UNVALIDATED: "UNVALIDATED",
                               c.SUSPECTED: "SUSPECTED",
                               c.OOR: "OOR"}
        self.event_dict = {"Measurement": "",
                           "Hilrep": "",
                           "Start split": "",
                           "End split": "",
                           "Script status": "OK",
                           "Total frames": 0,
                           "Height MIN": 0,
                           "Height 0.5 frames": 0,
                           "Height 0.5 frame%": 0,
                           "Pitch OK": True,
                           "Pitch NOK from AVE frames": 0,
                           "Pitch NOK from CODED frames": 0,
                           "Pitch MIN ETH": 0,
                           "Pitch MAX ETH": 0,
                           "Pitch MIN": 0,
                           "Pitch MAX": 0,
                           "Pitch AVE": 0,
                           "Pitch CODED": 0,
                           "Pitch MAX MIN DIFF": 0,
                           "Pitch MAX DEV from AVE": 0,
                           "Pitch MAX DEV from CODED": 0,
                           "Pitch MAX DEV from AVE deg": 0,
                           "Pitch MAX DEV from CODED deg": 0,
                           "C2W States": [],
                           "OOR": False,
                           "OOR Split": "",
                           "FS Activated in session": False,
                           "FS Labeled in session": False,
                           "FS Activated": [],
                           "FS Labeled": [],
                           "FS at MAX DEV AVE": [],
                           "FS at MAX DEV CODED": [],
                           "Label at MAX DEV AVE": [],
                           "Label at MAX DEV CODED": []
                           }
        self.vin_pitch_tac_dict = {"5UXTR9C51KLE21663": -190,
                                   "WBA7F21060B236144": -200,
                                   "WBA7F21070B235942": -192,
                                   "WBA7F21080B235965": -206,
                                   "WBA7F21080B236145": -188,
                                   "WBA7F21090B235683": -208,
                                   "WBA7F21090B235800": -198,
                                   "WBA7F210X0B235966": -200,
                                   "WBA7G81020B248890": -202,
                                   "WBA7G81060B248889": -198,
                                   "WBA7G81080G784732": -190,
                                   "WBA7H01000B267498": -212,
                                   "WBA7H01020B267499": -200,
                                   "WBA7H01030B267513": -196,
                                   "WBA7H01070B267515": -210,
                                   "WBATR95030NC87773": -192,
                                   "WBATR95050NC87113": -202,
                                   "WBATR950X0NC87723": -192}

    def get_hilrep(self):
        key = list(self.file_dict.keys())[0]
        search_line = self.file_dict[key]
        # search for HILREPP-7digits, force the engine to try matching at the furthest position
        search = re.search(r'(?s:.*).+(HILREPP-\d{7}).+', search_line)  # ex. HILREPP-2013288
        if search:
            return search.group(1)
        else:
            return None

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

    def save_results(self):
        if self.event_dict:
            if not os.path.isdir(self.new_path):
                os.makedirs(self.new_path, exist_ok=True)
            hilrep = self.get_hilrep()
            if hilrep:
                self.unique_name = hilrep
            file_name = f'{self.function}_{self.sop}_{self.a_step}_{self.unique_name}'
            self.save_json(self.event_dict, self.new_path, file_name)
        else:
            print(f'Cant save, collect is off')

    @staticmethod
    def get_fs_s(fs_s):
        fs_s_list = fs_s.split(": ")
        fs = fs_s_list[0]
        severity = c.SEVERITY_SYS[fs_s_list[1]]
        return fs, severity

    @staticmethod
    def px_to_deg_level2(px):
        return px / 20.75

    @staticmethod
    def deg_to_px_level2(deg):
        return deg * 20.75

    def check_cal(self, df):
        # if empty dataframe passed, exit
        if len(df) < 1:
            self.event_dict["Script status"] = "NOK - empty df"
            self.save_results()
        try:
            # get total frames
            self.event_dict["Total frames"] = len(df)
            # Check height for 0.5m
            self.event_dict["Height MIN"] = df[c.CAL_HEIGHT].min()
            total_frames = len(df)
            df_h_0_5 = df[df[c.CAL_HEIGHT] < 0.6]
            h_0_5_frames = len(df_h_0_5)
            if h_0_5_frames > 0:
                self.event_dict["Height 0.5 frames"] = h_0_5_frames
                self.event_dict["Height 0.5 frame%"] = h_0_5_frames/total_frames * 100

            # Get Max, Min and, Average pitch
            self.event_dict["Pitch MIN ETH"] = str(df[c.ETH_PITCH].min())
            self.event_dict["Pitch MAX ETH"] = str(df[c.ETH_PITCH].max())
            self.event_dict["Pitch MIN"] = int(df[c.CAL_PITCH].min())
            self.event_dict["Pitch MAX"] = int(df[c.CAL_PITCH].max())
            self.event_dict["Pitch AVE"] = int(df[c.CAL_PITCH].mean())

            # get max dev min to max
            self.event_dict["Pitch MAX MIN DIFF"] = abs(self.event_dict["Pitch MAX"] - self.event_dict["Pitch MIN"])

            # get dataframe first index
            idx = df.index.tolist()[0]
            idx_last = df.index.tolist()[-1]
            # get file name
            file_name = df.loc[idx, "File_Name"]
            file_name_last = df.loc[idx_last, "File_Name"]
            file_name_split = file_name.split("_")
            file_name_last_split = file_name_last.split("_")
            # get vin datestamp, timestamp from file name
            vin = file_name_split[1]
            date_stamp = file_name_split[2]
            time_stamp = file_name_split[3]
            # get measurement
            self.event_dict["Measurement"] = f'{file_name_split[0]}_{vin}_{date_stamp}_{time_stamp}'
            # get hilrep
            self.event_dict["Hilrep"] = self.get_hilrep()
            # get first split
            first_split = file_name_split[-1].split(".")[0]
            self.event_dict["Start split"] = first_split
            # get last split
            last_split = file_name_last_split[-1].split(".")[0]
            self.event_dict["End split"] = last_split
            # get pitch coded value
            self.event_dict["Pitch CODED"] = self.vin_pitch_tac_dict[vin]
            # get deviations
            ave_to_min = int(abs(self.event_dict["Pitch AVE"] - self.event_dict["Pitch MIN"]))
            ave_to_max = int(abs(self.event_dict["Pitch AVE"] - self.event_dict["Pitch MAX"]))
            coded_to_min = int(abs(self.event_dict["Pitch CODED"] - self.event_dict["Pitch MIN"]))
            coded_to_max = int(abs(self.event_dict["Pitch CODED"] - self.event_dict["Pitch MAX"]))
            if ave_to_min > ave_to_max:
                self.event_dict["Pitch MAX DEV from AVE"] = ave_to_min
            else:
                self.event_dict["Pitch MAX DEV from AVE"] = ave_to_max
            self.event_dict["Pitch MAX DEV from AVE deg"] = self.px_to_deg_level2(self.event_dict["Pitch MAX DEV from AVE"])
            if coded_to_min > coded_to_max:
                self.event_dict["Pitch MAX DEV from CODED"] = coded_to_min
            else:
                self.event_dict["Pitch MAX DEV from CODED"] = coded_to_max
            self.event_dict["Pitch MAX DEV from CODED deg"] = self.px_to_deg_level2(self.event_dict["Pitch MAX DEV from CODED"])
            # check if pitch nok
            max_dev_px = self.deg_to_px_level2(self.max_pitch_dev)
            if self.event_dict["Pitch MAX DEV from AVE"] > max_dev_px or self.event_dict["Pitch MAX DEV from CODED"] > max_dev_px:
                self.event_dict["Pitch OK"] = False
                # get pitch NOK frame count
                df_ave_max = df[df[c.CAL_PITCH] > self.event_dict["Pitch AVE"] + max_dev_px]
                df_ave_min = df[df[c.CAL_PITCH] < self.event_dict["Pitch AVE"] - max_dev_px]
                df_cod_max = df[df[c.CAL_PITCH] > self.event_dict["Pitch CODED"] + max_dev_px]
                df_cod_min = df[df[c.CAL_PITCH] < self.event_dict["Pitch CODED"] - max_dev_px]
                self.event_dict["Pitch NOK from AVE frames"] = len(df_ave_max) + len(df_ave_min)
                self.event_dict["Pitch NOK from CODED frames"] = len(df_cod_max) + len(df_cod_min)
            # get C2W states
            c2w_states = set(df["CLB_C2W_State"].tolist())
            if c.OOR in c2w_states:
                self.event_dict["OOR"] = True
            if c2w_states:
                for state in c2w_states:
                    if state in self.c2w_state_dict.keys():
                        self.event_dict["C2W States"].append(self.c2w_state_dict[state])
            df_oor = df[df["CLB_C2W_State"] == c.OOR]
            if len(df_oor) > 0:
                # get first index
                idx = df_oor.index.tolist()[0]
                # get file name
                file_name = df_oor.loc[idx, "File_Name"]
                search = re.search(r".*_(\d{4})\.*", file_name)
                if search:
                    oor_split = search.group(1)
                    self.event_dict["OOR Split"] = oor_split
            # check if FS in session
            for signal in self.signal_list:
                if df[signal].max() > 1:
                    self.event_dict["FS Activated in session"] = True
                    break
            for label in self.label_list:
                values = set(df[label].to_list())
                if 2 in values or 4 in values or 5 in values:
                    self.event_dict["FS Labeled in session"] = True
                    break
            # check activated FS in session
            for signal in self.signal_list:
                df_temp = df[df[signal] > 1]
                if len(df_temp) > 0:
                    severity_set = set(df_temp[signal].to_list())
                    for severity in severity_set:
                        severity_mapped = c.SEVERITY_MAP[severity]
                        fs_severity = f'{signal}: {severity_mapped}'
                        if fs_severity not in self.event_dict["FS Activated"]:
                            self.event_dict["FS Activated"].append(fs_severity)
            # check labeled FS in session
            for label in self.label_list:
                severity_set = set(df[label].to_list())
                if severity_set:
                    for severity in severity_set:
                        if severity == 2 or severity == 4 or severity == 5:
                            severity_mapped = c.SEVERITY_MAP[severity]
                            fs_severity = f'{label}: {severity_mapped}'
                            if fs_severity not in self.event_dict["FS Labeled"]:
                                self.event_dict["FS Labeled"].append(fs_severity)
            # check if max dev occurs during fs or label
            pitch_ave = self.event_dict["Pitch AVE"]
            pitch_cod = self.event_dict["Pitch CODED"]
            pitch_ave_max_dev = self.event_dict["Pitch MAX DEV from AVE"]
            pitch_cod_max_dev = self.event_dict["Pitch MAX DEV from CODED"]
            # check if FS at max dev
            if self.event_dict["FS Activated"]:
                for fs_s in self.event_dict["FS Activated"]:
                    fs, severity = self.get_fs_s(fs_s)
                    if fs in self.signal_list and (severity == 2 or severity == 4 or severity == 5):
                        df_temp = df[df[fs] == severity]
                        pitch_set = set(df_temp[c.CAL_PITCH].to_list())
                        if pitch_ave + pitch_ave_max_dev in pitch_set or pitch_ave - pitch_ave_max_dev:
                            self.event_dict["FS at MAX DEV AVE"].append(fs_s)
                        if pitch_cod + pitch_cod_max_dev in pitch_set or pitch_cod - pitch_cod_max_dev:
                            self.event_dict["FS at MAX DEV CODED"].append(fs_s)
            # check if Label at max dev
            if self.event_dict["FS Labeled"]:
                for lab_s in self.event_dict["FS Labeled"]:
                    lab, severity = self.get_fs_s(lab_s)
                    if lab in self.label_list and (severity == 2 or severity == 4 or severity == 5):
                        df_temp = df[df[lab] == severity]
                        pitch_set = set(df_temp[c.CAL_PITCH].to_list())
                        if pitch_ave + pitch_ave_max_dev in pitch_set or pitch_ave - pitch_ave_max_dev:
                            self.event_dict["Label at MAX DEV AVE"].append(lab_s)
                        if pitch_cod + pitch_cod_max_dev in pitch_set or pitch_cod - pitch_cod_max_dev:
                            self.event_dict["Label at MAX DEV CODED"].append(lab_s)
            self.save_results()
            # if not self.event_dict["Pitch OK"]:
            self.make_plot(df, self.event_dict["Measurement"], self.event_dict["Hilrep"])
        except Exception as e:
            self.event_dict["Script status"] = f"NOK - {e}"
            self.save_results()


class CALtoDF(CalCheck):

    def __init__(self):
        self.ext = '.json'
        self.files = []
        self.results_dict = {}
        self.results_df = pd.DataFrame()
        super().__init__(None)
        self.new_path = os.path.join(c.PATH_FAILED_KPI_DFS, self.new_folder)

    def get_json_files(self):
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

    def bind_cal_test(self):
        if self.files:
            num_of_files = len(self.files)
            for i, file in enumerate(self.files):
                cal_dict = self.open_json_file(self.new_path, file)
                self.results_dict[i] = cal_dict
            self.results_df = pd.DataFrame.from_dict(self.results_dict).T
            print(num_of_files)

    def save_df_to_excel(self):
        file_name = f'{self.function}_{self.sop}_{self.a_step}_CAL_TEST.xlsx'
        wb_name = os.path.join(self.new_path, file_name)
        with pd.ExcelWriter(wb_name) as writer:
            self.results_df.to_excel(writer, sheet_name='CAL_TEST')


def main():
    cal_binder = CALtoDF()
    cal_binder.get_json_files()
    cal_binder.bind_cal_test()
    cal_binder.save_df_to_excel()


if __name__ == "__main__":
    main()
