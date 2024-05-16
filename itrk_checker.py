"""
Module checks itrk files and reports amount of failsafes
Patryk Leszowski
APTIV
BWD
"""
import config.constant as c
import pandas as pd
import re
import os
import time
import datetime
import json


class ItrkChecker:

    def __init__(self, path):
        self.path = path
        self.ext = '.itrk'
        self.itrk_files = []
        self.master_df_list = []
        self.file_counter = 0
        self.file_count = 0
        self.master_df = pd.DataFrame()

    def get_ikrk_files(self):

        try:
            allfiles = os.listdir(self.path)
        except (FileNotFoundError, PermissionError, NotADirectoryError) as e:
            print(f'ItrkChecker: ERROR: Cant open {self.path}')
            print(e)
            raise e
        else:
            if allfiles:
                for file in allfiles:
                    if file.endswith(self.ext):
                        self.itrk_files.append(file)
                self.file_count = len(self.itrk_files)
            else:
                print(f'ItrkChecker: No pickles in {self.path}')
                print(FileNotFoundError)
                raise FileNotFoundError

    def check_itrk(self):
        df = pd.DataFrame()
        for itrk_file in self.itrk_files:
            self.file_counter += 1
            print(f'Checking {self.file_counter}/{self.file_count}: {itrk_file}')
            got_signals = False
            file_path = os.path.join(self.path, itrk_file)
            with open(file_path, 'r') as f:
                line = f.readline()
                while line:
                    if not got_signals:
                        search = re.search(r'^format: Perfect FrameTag.+', line)
                        if search:
                            signal_list = line.split(" ")
                            df = pd.DataFrame(columns=signal_list)
                            got_signals = True
                    search = re.search(r'^\d+ Perfect.+', line)
                    if search:
                        line_list = line.split(" ")
                        df.loc[len(df)] = line_list
                        pass
                    else:
                        pass
                    line = f.readline()
        df_col_names = df.columns.values.tolist()
        itrk_names = []
        for fs_name in c.ITRK_LAB_NAMES:
            if fs_name in df_col_names:
                itrk_names.append(fs_name)
        self.master_df = df[itrk_names].reset_index(drop=True)
        self.master_df = self.master_df.astype(int)
        severity_list = [1, 3, 4, 5]
        results_df = pd.DataFrame(index=severity_list, columns=itrk_names)

        for col in itrk_names:
            for severity in severity_list:
                fs_count = len(self.master_df[self.master_df[col] == severity])
                results_df.loc[severity, col] = fs_count

        if c.PATH_ITRK.split("/")[-1] == '':
            file = c.PATH_ITRK.split("/")[-2] + '.xlsx'
        else:
            file = c.PATH_ITRK.split("/")[-1] + '.xlsx'
        wb_name = os.path.join(c.PATH_FAILED_KPI_DFS, file)
        with pd.ExcelWriter(wb_name) as writer:
            results_df.to_excel(writer, sheet_name='label_count')

    def find_pb_itrk(self):
        label_index = None
        file_list = []
        for itrk_file in self.itrk_files:
            self.file_counter += 1
            print(f'Checking {self.file_counter}/{self.file_count}: {itrk_file}')
            got_label_names = False
            file_path = os.path.join(self.path, itrk_file)
            with open(file_path, 'r') as f:
                line = f.readline()
                while line:
                    if not got_label_names:
                        search = re.search(r'^format: Perfect FrameTag.+', line)
                        if search:
                            label_list = line.split(" ")
                            if 'partialBlockage' in label_list:
                                label_index = label_list.index("partialBlockage")
                            got_label_names = True
                    search = re.search(r'^\d+ Perfect.+', line)
                    if search:
                        line_list = line.split(" ")
                        if label_index and line_list[label_index] == '0':
                            file_list.append(itrk_file)
                            break
                    line = f.readline()
        self.save_json(file_list, self.path, 'aaa_itrk_search.json')

    @staticmethod
    def save_json(obj, path, file):
        """
        :param obj: object to be serialized
        :param path: path to folder
        :param file: file name
        :return:
        Save object to json
        """
        try:
            with open(path + file, 'w') as f:
                json.dump(obj, f, indent=2)
        except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
            raise e


def main():
    path = c.PATH_ITRK
    itrk_checker = ItrkChecker(path)
    itrk_checker.get_ikrk_files()
    # itrk_checker.check_itrk()
    itrk_checker.find_pb_itrk()


if __name__ == "__main__":
    _start_time = time.time()
    print('Script start time: ' + str(datetime.datetime.now().time()))
    main()
    _script_time = time.time() - _start_time
    print('Script end time: ' + str(datetime.datetime.now().time()))
    print('Total script time: ' + str(datetime.timedelta(seconds=_script_time)))