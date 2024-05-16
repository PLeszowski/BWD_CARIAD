"""
Module concatenates dataframes from dataframe_collector, counts stats, leaves only relevant columns
Patryk Leszowski
APTIV
BWD
"""
import config.constant as c
import pandas as pd
import numpy as np
import pickle
import os


class DfSplitter:

    def __init__(self, path, sop, a_step):
        self.path = path
        self.ext = '.pickle'
        self.df_max_len = 880
        self.sop = sop
        self.a_step = a_step
        self.function = 'BWD'
        self.files = []
        self.master_df_list = []
        self.master_df = pd.DataFrame(columns=c.FAILED_KPI_DF_COLUMNS)
        self.event_stats_df = pd.DataFrame(index=c.FAILED_KPI_TYPES, columns=c.FAILED_KPI_EVENTS)
        self.event_stats_df.fillna(0, inplace=True)
        self.frame_stats_df = pd.DataFrame(index=c.FAILED_KPI_TYPES, columns=c.FAILED_KPI_EVENTS)
        self.frame_stats_df.fillna(0, inplace=True)
        self.hilrepp_dfs_path = self.path

    def get_df_files(self):

        try:
            allfiles = os.listdir(self.hilrepp_dfs_path)
        except (FileNotFoundError, PermissionError, NotADirectoryError) as e:
            print(f'DfBinder: ERROR: Cant open {self.hilrepp_dfs_path}')
            print(e)
            raise e
        else:
            if allfiles:
                for file in allfiles:
                    if file.endswith(self.ext):
                        self.files.append(file)
            else:
                print(f'DfBinder: No pickles in {self.hilrepp_dfs_path}')
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
            print(f'DfBinder: ERROR: Cant open {file}')
            print(e)

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

    def divide_df_if_max_len(self):
        """
        Divide dataframe if it is bigger than df_max_len
        :return:
        """
        # Check if master_df is bigger than df_max_len
        master_df_len = len(self.master_df)
        # get the number of dataframes to split
        number_of_dfs_float = master_df_len/self.df_max_len
        number_of_dfs = int(number_of_dfs_float) + 1
        if master_df_len > self.df_max_len:
            # divide master_df to number_of_dfs dfs
            split_dfs_list = np.array_split(self.master_df, number_of_dfs)
            # append each df to master_df_list
            for df in split_dfs_list:
                self.master_df_list.append(df)
        elif master_df_len > 0:
            self.master_df_list.append(self.master_df)

    def save_dfs(self):
        if self.master_df_list:
            new_folder = f'{self.function}_{self.sop}_{self.a_step}_BIND_DFS'
            new_path = os.path.join(c.PATH_FAILED_KPI_DFS, new_folder)
            if not os.path.isdir(new_path):
                os.makedirs(new_path, exist_ok=True)
            counter = 0
            for df in self.master_df_list:
                if len(df) > 0:
                    counter += 1
                    file_name = f'{self.function}_{self.sop}_{self.a_step}_{counter:04d}.pickle'
                    self.save_pkl(df, new_path, file_name)
            wb_name = os.path.join(new_path, 'stats_output.xlsx')
            with pd.ExcelWriter(wb_name) as writer:
                self.frame_stats_df.to_excel(writer, sheet_name='Frames')
                self.event_stats_df.to_excel(writer, sheet_name='Events')
        else:
            print('DfBinder: : WARNING: No Dataframes to save')
        df_count = len(self.master_df_list)
        print(f'DfBinder: INFO: Number of dataframes: {df_count}, saved: {new_path}')

    def bind_dfs(self):
        df_list = []
        if self.files:
            num_of_files = len(self.files)
            for i, file in enumerate(self.files):
                print(f'DfBinder: INFO: Calculating {i+1}/{num_of_files}: {file}')
                df = self.load_pkl(self.hilrepp_dfs_path, file)
                df['Astep'] = self.a_step
                df['Project'] = c.PROJECT
                # df_to_append = df[c.FAILED_KPI_DF_COLUMNS].reset_index(drop=True)
                df_list.append(df)
            try:
                # Concatenate master_df_list list to master_df
                self.master_df = pd.concat(df_list, ignore_index=True)
            except ValueError as e:
                print('DfBinder: bind_dfs: Cant concat master_df_list')
                print(e)
                raise e


def main():
    path = c.PATH_FAILED_KPI_DFS
    path = r'c:\Users\wjjymc\PycharmProjects\BWD\FAILED_KPI_DFS\SOP1_A440\MID_DATASET\08_FP_LOWSUN\BWD_SOP1_A440_BIND_DFS\one_per_split\lowsun'
    sop = c.SOP
    a_step = c.A_STEP
    df_binder = DfSplitter(path, sop, a_step)
    df_binder.get_df_files()
    df_binder.bind_dfs()
    df_binder.divide_df_if_max_len()
    df_binder.save_dfs()


if __name__ == "__main__":
    main()
