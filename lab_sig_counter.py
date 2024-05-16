"""
Module counts number of occurrences (frames) for labels, spi, eth for each severity level
Patryk Leszowski
APTIV
BWD
"""
import pandas as pd
import config.constant as c
import pickle
import os
import re


class LabSigCounter:

    def __init__(self, file_dict, dt_str):

        self.function = 'BWD'
        self.sop = c.SOP
        self.a_step = c.A_STEP
        self.severity_list = [0, 1, 2, 3, 4, 5]
        self.results_df = pd.DataFrame(index=self.severity_list, columns=c.LAB_SIG_COUNTER_COLUMNS)
        self.results_df.fillna(0, inplace=True)
        self.dt_str = dt_str
        self.file_dict = file_dict
        self.new_folder = f'{self.function}_{self.sop}_{self.a_step}_LAB_COUNT_DFS'
        self.new_path = os.path.join(c.PATH_FAILED_KPI_DFS, self.new_folder)

    def count_lab(self, df):

        for col in c.FAILED_KPI_FN_EVENTS:
            df_columns = df.columns.values.tolist()
            if col in df_columns:
                for severity in self.severity_list:
                    fs_count = len(df[df[col] == severity])
                    self.results_df.loc[severity, col] += fs_count
            else:
                print(f'col {col} not in {df_columns}')

    def count_sig(self, df):

        for col in c.FAILED_KPI_FP_EVENTS:
            df_columns = df.columns.values.tolist()
            if col in df_columns:
                for severity in self.severity_list:
                    fs_count = len(df[df[col] == severity])
                    self.results_df.loc[severity, col] += fs_count
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

    def save_results_df(self):
        if self.results_df.shape[0] > 0:
            if not os.path.isdir(self.new_path):
                os.makedirs(self.new_path, exist_ok=True)

            key = list(self.file_dict.keys())[0]
            search_line = self.file_dict[key]
            # search for HILREPP-7digits, force the engine to try matching at the furthest position
            search = re.search(r'(?s:.*).+(\d{4}_\d{4}).+', search_line)   # ex. HILREPP-2013288
            if search:
                unique_name = search.group(1) + "_" + self.dt_str
            else:
                unique_name = self.dt_str

            file_name = f'{self.function}_{self.sop}_{self.a_step}_{unique_name}.pickle'
            self.save_pkl(self.results_df, self.new_path, file_name)


class LabSigDfBinder(LabSigCounter):

    def __init__(self):

        self.ext = '.pickle'
        self.file_name = ''
        self.files = []
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
    def load_pkl(path, file):
        """
        Load pickle to object
        :param path: path to folder
        :param file: pickle file name
        :return:
        Load object
        """
        pickle_path = os.path.join(path, file)
        try:
            with open(pickle_path, 'rb') as f:
                return pickle.load(f)
        except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
            print(f'LabSigDfBinder: ERROR: Cant open {file}')
            print(e)

    def bind_dfs(self):
        if self.files:
            num_of_files = len(self.files)
            for i, file in enumerate(self.files):
                print(f'LabSigDfBinder: INFO: Calculating {i + 1}/{num_of_files}: {file}')
                df = self.load_pkl(self.new_path, file)
                for column in c.LAB_SIG_COUNTER_COLUMNS:
                    for severity in self.severity_list:
                        self.results_df.loc[severity, column] += df.loc[severity, column]

    def save_df(self):
        file_name = f'{self.function}_{self.sop}_{self.a_step}_LAB_SIG_COUNT.pickle'
        self.save_pkl(self.results_df, self.new_path, file_name)
        self.save_df_to_excel()

    def save_df_to_excel(self):
        file_name = f'{self.function}_{self.sop}_{self.a_step}_LAB_SIG_COUNT.xlsx'
        wb_name = os.path.join(self.new_path, file_name)
        with pd.ExcelWriter(wb_name) as writer:
            self.results_df.to_excel(writer, sheet_name='Counters')


def main():
    lab_sig_df_binder = LabSigDfBinder()
    lab_sig_df_binder.get_df_files()
    lab_sig_df_binder.bind_dfs()
    lab_sig_df_binder.save_df()

    # lab_sig_df_binder.results_df = lab_sig_df_binder.load_pkl(r'c:\Users\wjjymc\PycharmProjects\BWD\FAILED_KPI_DFS\BWD_SOP8_A360_LAB_COUNT_DFS', 'BWD_SOP8_A360_LAB_SIG_COUNT.pickle')
    # lab_sig_df_binder.save_df_to_excel()


if __name__ == "__main__":
    main()
