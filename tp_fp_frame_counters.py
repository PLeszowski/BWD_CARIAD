"""
Module counts number of occurrences (frames) for TP and FP
Patryk Leszowski
APTIV
BWD
"""
import pandas as pd
import config.constant as c
import os
import re
import json


class TPFPCounter:

    def __init__(self, file_list, dt_str):

        self.function = 'BWD'
        self.sop = c.SOP
        self.a_step = c.A_STEP
        self.collect = False
        self.file_list = file_list
        self.tp_counters = c.TP_COUNTERS
        self.fp_counters = c.FP_COUNTERS
        self.counters_dict = {'TP': self.tp_counters, 'FP': self.fp_counters}
        self.dt_str = dt_str
        self.new_folder = f'{self.function}_{self.sop}_{self.a_step}_TP_FP_COUNT'
        self.new_path = os.path.join(c.PATH_FAILED_KPI_DFS, self.new_folder)

    def count_tp(self, df, label, severity):
        if self.collect:
            signals = c.SYS_ALL
            for signal in signals:
                for sig_val in [2, 4, 5]:
                    value = len(df[df[signal] == sig_val])
                    self.tp_counters[label][severity][signal][sig_val] += value

    def count_fp(self, df, signal, severity):
        if self.collect:
            labels = c.LAB_ALL
            for label in labels:
                for lab_val in [2, 4, 5]:
                    value = len(df[df[label] == lab_val])
                    self.fp_counters[signal][severity][label][lab_val] += value

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

    def save_results_df(self):
        if not os.path.isdir(self.new_path):
            os.makedirs(self.new_path, exist_ok=True)
        key = list(self.file_list.keys())[0]
        search_line = self.file_list[key]
        # search for _1234_1234_, force the engine to try matching at the furthest position
        search = re.search(r'(?s:.*).+\W(\d{4}_\d{4})\W.+', search_line)
        if search:
            unique_name = search.group(1) + "_" + self.dt_str
        else:
            unique_name = self.dt_str
        file_name = f'{self.function}_{self.sop}_{self.a_step}_{unique_name}.json'
        self.save_json(self.counters_dict, self.new_path, file_name)


class TPFPCountBinder(TPFPCounter):

    def __init__(self):

        self.ext = '.json'
        self.file_name = ''
        self.files = []
        self.tp_df = pd.DataFrame()
        self.fp_df = pd.DataFrame()
        super().__init__(None, None)

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

    def bind_dicts(self):
        if self.files:
            num_of_files = len(self.files)
            for i, file in enumerate(self.files):
                print(f'TPFPCountBinder: INFO: Calculating {i + 1}/{num_of_files}: {file}')
                counters_dict = self.open_json_file(self.new_path, file)
                # TP
                for lab, lab_sig_sev_dict in counters_dict['TP'].items():
                    for lab_sev, sys_sev_dict in lab_sig_sev_dict.items():
                        for sig, sev_dict in sys_sev_dict.items():
                            for sev, value in sev_dict.items():
                                self.tp_counters[lab][int(lab_sev)][sig][int(sev)] += value
                # FP
                for sig, sig_lab_sev_dict in counters_dict['FP'].items():
                    for sig_sev, lab_sev_dict in sig_lab_sev_dict.items():
                        for lab, sev_dict in lab_sev_dict.items():
                            for sev, value in sev_dict.items():
                                self.fp_counters[sig][int(sig_sev)][lab][int(sev)] += value

    def dict_to_df(self):
        tp_dict = {}
        fp_dict = {}
        # TP
        for lab, lab_sig_sev_dict in self.tp_counters.items():
            for lab_sev, sys_sev_dict in lab_sig_sev_dict.items():
                lab_sev_str = f'{lab}_{lab_sev}'
                tp_dict[lab_sev_str] = {}
                for sig, sev_dict in sys_sev_dict.items():
                    for sev, value in sev_dict.items():
                        sig_sev_str = f'{sig}_{sev}'
                        tp_dict[lab_sev_str][sig_sev_str] = value
        print()
        # FP
        for sig, sig_lab_sev_dict in self.fp_counters.items():
            for sig_sev, lab_sev_dict in sig_lab_sev_dict.items():
                sig_sev_str = f'{sig}_{sig_sev}'
                fp_dict[sig_sev_str] = {}
                for lab, sev_dict in lab_sev_dict.items():
                    for sev, value in sev_dict.items():
                        lab_sev_str = f'{lab}_{sev}'
                        fp_dict[sig_sev_str][lab_sev_str] = value

        self.tp_df = pd.DataFrame.from_dict(tp_dict)
        self.fp_df = pd.DataFrame.from_dict(fp_dict)
        print()

    def save_df_to_excel(self):
        file_name = f'{self.function}_{self.sop}_{self.a_step}_TP_FP_COUNT.xlsx'
        wb_name = os.path.join(self.new_path, file_name)
        with pd.ExcelWriter(wb_name) as writer:
            self.tp_df.to_excel(writer, sheet_name='TP_counters')
            self.fp_df.to_excel(writer, sheet_name='FP_counters')

def main():
    tp_fp_df_binder = TPFPCountBinder()
    tp_fp_df_binder.get_df_files()
    tp_fp_df_binder.bind_dicts()
    tp_fp_df_binder.dict_to_df()
    tp_fp_df_binder.save_df_to_excel()

if __name__ == "__main__":
    main()