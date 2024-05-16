import pandas as pd
import config.constant as c
from datetime import datetime
import os
import re
import json


class NRCounter:

    def __init__(self):

        self.function = 'BWD'
        self.sop = c.SOP
        self.a_step = c.A_STEP
        self.counter_list = c.NR_COUNTER_ROWS
        self.results_df = pd.DataFrame(index=self.counter_list, columns=c.FAILED_KPI_FP_EVENTS)
        self.results_df.fillna(0, inplace=True)
        self.dt_str = re.sub(r"[:\-. ]", "", str(datetime.now()))
        self.unique_name = self.dt_str
        self.new_folder = f'{self.function}_{self.sop}_{self.a_step}_NOT_READY_CHECK'
        self.new_path = os.path.join(c.PATH_FAILED_KPI_DFS, self.new_folder)

    def count(self, df):

        for col in c.NR_COUNTER_ROWS:
            df_columns = df.columns.values.tolist()
            if col in df_columns:
                for countr in self.counter_list:
                    fs_count = len(df[df[col] == countr])
                    self.results_df.loc[countr, col] += fs_count
            else:
                print(f'col {col} not in {df_columns}')

    @staticmethod
    def save_pkl(obj, path, file):
        """
        Save object to pickle
        :param obj: object to be serialized
        :param path: path to folder
        :param file: file name
        :return:
        """
        filename = os.path.join(path, file)
        obj.to_pickle(filename, protocol=4)

    def save_results_df(self, file_dict):
        if self.results_df.shape[0] > 0:
            if not os.path.isdir(self.new_path):
                os.makedirs(self.new_path, exist_ok=True)

            key = list(file_dict.keys())[0]
            search_line = file_dict[key]
            # search for HILREPP-7digits, force the engine to try matching at the furthest position
            search = re.search(r'(?s:.*).+(HILREPP-\d{7}).+', search_line)   # ex. HILREPP-2013288
            if search:
                self.unique_name = search.group(1)

            file_name = f'{self.function}_{self.sop}_{self.a_step}_{self.unique_name}.pickle'
            self.save_pkl(self.results_df, self.new_path, file_name)


class NRDfBinder(NRCounter):

    def __init__(self):

        self.ext = '.json'
        self.file_name = ''
        self.files = []
        super().__init__()

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
                df = self.open_json_file(self.new_path, file)
                for column in c.FAILED_KPI_FP_EVENTS:
                    if df[column]:
                        for countr in self.counter_list:
                            self.results_df.loc[countr, column] += int(df[column][countr])
                    else:
                        print(f'{column} is empty')

    def save_df(self):
        file_name = f'{self.function}_{self.sop}_{self.a_step}_NR_COUNT.pickle'
        self.save_pkl(self.results_df, self.new_path, file_name)
        self.save_df_to_excel()

    def save_df_to_excel(self):
        file_name = f'{self.function}_{self.sop}_{self.a_step}_NR_COUNT.xlsx'
        wb_name = os.path.join(self.new_path, file_name)
        with pd.ExcelWriter(wb_name) as writer:
            self.results_df.to_excel(writer, sheet_name='Counters')


def main():
    nr_df_binder = NRDfBinder()
    nr_df_binder.get_df_files()
    nr_df_binder.bind_dfs()
    nr_df_binder.save_df()


if __name__ == "__main__":
    main()
