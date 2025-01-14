"""
Module selects failed frames for review
Patryk Leszowski
APTIV
BWD
"""
import config.constant as c
import pandas as pd
import numpy as np
import pickle
import os
import json


class DfFailedSelector:

    def __init__(self):
        self.filelist = []
        self.input_folder = r'f:\CARIAD\BHE\REPRO\X110\failed_dfs\NEW_ALL_WITH_SEVERITIES\ALL'
        self.output_folder = r'f:\CARIAD\BHE\REPRO\X110\failed_dfs\NEW_ALL_WITH_SEVERITIES\ALL_ONE_PER_SPLIT'

    @staticmethod
    def load_pkl(path, file=None):
        """
        Load pickle to object
        :param path: path to folder
        :param file: pickle file name
        :return:
        Load object
        """
        if file:
            pickle_path = os.path.join(path, file)
        else:
            pickle_path = path
        try:
            with open(pickle_path, 'rb') as f:
                return pickle.load(f)
        except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
            print(f'DfFailedSelector: ERROR: Cant open {file}')
            print(e)

    @staticmethod
    def save_pkl(obj, path, file=None):
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
        obj.to_pickle(path_file, protocol=4)

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
    def copy_rows_where_col_changed_to_new_val_df(dataframe, col_name):
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
            print(f'DfFailedSelector: copy_rows_where_col_changed_to_new_val_df: KeyError {col_name}')
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

    @staticmethod
    def copy_rows_where_list_col_contains_text_df(df, col_name, text):
        try:
            df.reset_index(drop=True, inplace=True)
            col = list(df[col_name])
        except KeyError as e:
            print(f'DfFailedSelector: copy_rows_where_list_col_contains_text_df: KeyError {col_name}')
            raise e
        else:
            index_list = []
            for index, col_list in enumerate(col):
                if text in col_list:
                    index_list.append(index)
            df = df.loc[index_list].reset_index(drop=True)
            return df

    def get_pickles(self):

        try:
            allfiles = os.listdir(self.input_folder)
        except (FileNotFoundError, PermissionError, NotADirectoryError) as e:
            print(f'DfBinder: ERROR: Cant open {self.input_folder}')
            print(e)
            raise e
        else:
            if allfiles:
                for file in allfiles:
                    if file.endswith('pickle'):
                        self.filelist.append(file)
            else:
                print(f'DfBinder: No pickles in {self.input_folder}')
                print(FileNotFoundError)
                raise FileNotFoundError

    def select_data_fp(self):
        df_list = []
        for file in self.filelist:
            file_path = os.path.join(self.input_folder, file)
            df = self.load_pkl(file_path)
            df_list.append(df)
        df = pd.concat(df_list, ignore_index=True)
        df_filtered = self.copy_rows_where_list_col_contains_text_df(df, 'FailureType', 'FP')
        df_dict = {}
        for fs in c.SYS_ALL:
            df_sig = self.copy_rows_where_list_col_contains_text_df(df_filtered, 'Id', fs)
            df_dict[fs] = df_sig
        for fs, df_fs in df_dict.items():
            if len(df_fs) > 0:
                diff = np.where(abs(np.diff(df_fs['Gid'])) > 64)[0]
                diff = diff + 1
                diff = np.append(diff, len(df_fs))
                diff = np.append(0, diff)
                diff_mid = []
                for i in range(1, len(diff)):
                    mid_val = np.median([diff[i], diff[i-1]])
                    diff_mid.append(int(mid_val))
                df_selected = df_fs.loc[diff_mid].reset_index(drop=True)
                # Add column with measurement name
                # add Split Name column
                df_selected['Measurement'] = np.nan
                df_selected['Measurement'] = df_selected['Path'].str.extract(r'.+(ADCAM_.+_\d{8}_\d{6}).+', expand=False)
                # sort by split name
                df_selected.sort_values('Measurement', inplace=True)
                # leave only first row for each same path - different split in each row
                df_selected = self.copy_rows_where_col_changed_to_new_val_df(df_selected, 'Measurement')
                if len(df_selected) > 0:
                    pickle_name = f'BHE_X060_FP_{fs}_measurement.pickle'
                    output_pickle = os.path.join(self.output_folder, pickle_name)
                    if not os.path.isdir(self.output_folder):
                        os.makedirs(self.output_folder, exist_ok=True)
                    self.save_pkl(df_selected, output_pickle)
                    print(f'Saved pickle{pickle_name}')
                else:
                    print(f'Empty pickle for {fs}')

    def select_data_split(self):
        # one frame per split
        df_list = []
        plk = self.filelist[0][0:13]
        for file in self.filelist:
            file_path = os.path.join(self.input_folder, file)
            df = self.load_pkl(file_path)
            df_list.append(df)
        df = pd.concat(df_list, ignore_index=True)
        # Add column with pickle name
        # add Split Name column
        df['Split'] = np.nan
        df['Split'] = df['Path'].str.extract(r'.+(ADCAM_.+_\d{8}_\d{6}_pic_\d{4}).+', expand=False)
        # sort by split name
        df.sort_values('Split', inplace=True)
        df_dict = {}
        df_selected = self.copy_rows_where_col_changed_to_new_val_df(df, 'Split')
        df_dict['fn_fp'] = df_selected
        df_dict['fp'] = self.copy_rows_where_list_col_contains_text_df(df_selected, 'FailureType', 'FP')
        df_dict['fn'] = self.copy_rows_where_list_col_contains_text_df(df_selected, 'FailureType', 'FN')
        for df_type, df_s in df_dict.items():
            if len(df_s) > 0:
                pickle_name = f'{plk}_{df_type}_one_per_split.pickle'
                output_pickle = os.path.join(self.output_folder, pickle_name)
                if not os.path.isdir(self.output_folder):
                    os.makedirs(self.output_folder, exist_ok=True)
                self.save_pkl(df_s, output_pickle)
                print(f'Saved pickle {pickle_name}')
            else:
                print(f'Empty pickle {df_type}')

    def select_data_split_for_each(self):
        # one frame per split for each pickle in folder
        for file in self.filelist:
            file_path = os.path.join(self.input_folder, file)
            df = self.load_pkl(file_path)
            # New name
            file_new = file.split('.')[0]
            # Add column with pickle name
            # add Split Name column
            df['Split'] = np.nan
            df['Split'] = df['Path'].str.extract(r'.+(ADCAM_.+_\d{8}_\d{6}_pic_\d{4}).+', expand=False)
            # sort by split name
            df.sort_values('Split', inplace=True)
            df_selected = self.copy_rows_where_col_changed_to_new_val_df(df, 'Split')
            if len(df_selected) > 0:
                pickle_name = f'{file_new}_one_per_split.pickle'
                output_pickle = os.path.join(self.output_folder, pickle_name)
                if not os.path.isdir(self.output_folder):
                    os.makedirs(self.output_folder, exist_ok=True)
                self.save_pkl(df_selected, output_pickle)
                print(f'Saved pickle {pickle_name}')
            else:
                print(f'Empty pickle {file}')

    def select_one_per_measurement(self):
        for file in self.filelist:
            file_path = os.path.join(self.input_folder, file)
            df = self.load_pkl(file_path)
            df['Measurement'] = np.nan
            df['Measurement'] = df['Path'].str.extract(r'.+(ADCAM_.+_\d{8}_\d{6}).+', expand=False)
            df['split_num'] = df['Path'].str.extract(r'.+ADCAM_.+_\d{8}_\d{6}_pic_(\d{4}).+', expand=False).apply(pd.to_numeric)
            # # sort by split name
            # df.sort_values('Measurement', inplace=True)
            # leave only first row for each same path - different split in each row
            df_selected = self.copy_rows_where_col_changed_to_new_val_df(df, 'Measurement')
            if len(df_selected) > 0:
                part_name = file[:-7]
                pickle_name = f'{part_name}_measurement.pickle'
                output_pickle = os.path.join(self.output_folder, pickle_name)
                if not os.path.isdir(self.output_folder):
                    os.makedirs(self.output_folder, exist_ok=True)
                self.save_pkl(df_selected, output_pickle)
                print(f'Saved pickle{pickle_name}')
            else:
                print(f'Empty pickle for {file}')

    def select_if_gap_in_split_num(self):
        for file in self.filelist:
            index_list = []
            file_path = os.path.join(self.input_folder, file)
            df = self.load_pkl(file_path)
            try:
                df.reset_index(drop=True, inplace=True)
                split_num_list = list(df['split_num'])
                measurement_list = list(df['Measurement'])
                old_value = split_num_list[0]
                old_measurement = measurement_list[0]
                index_list.append(0)
                for index, value in enumerate(split_num_list):
                    if abs(value - old_value) > 10 or old_measurement != measurement_list[index]:
                        index_list.append(index)
                        old_value = value
                        old_measurement = measurement_list[index]
                df_new = df.loc[index_list].reset_index(drop=True)
                part_name = file[:-7]
                pickle_name = f'{part_name}_event.pickle'
                if not os.path.isdir(self.output_folder):
                    os.makedirs(self.output_folder, exist_ok=True)
                self.save_pkl(df_new, pickle_name)

            except KeyError as e:
                print(f'DfFailedSelector: select_if_gap_in_split_num: KeyError: split_num')
                raise e

    def select_fs_from_one_fp_pickle(self, pickle_path, plk):
        df_dict = {}
        df = self.load_pkl(pickle_path, plk)
        for fs in c.SYS_ALL:
            df_sig = self.copy_rows_where_list_col_contains_text_df(df, 'Id', fs)
            df_dict[fs] = df_sig
        for fs, fs_df in df_dict.items():
            pkl_names = plk.split(".")
            pkl_name = f'{pkl_names[0]}_{fs}.pickle'
            self.save_pkl(fs_df, pickle_path, pkl_name)

    def select_fs_from_one_fn_pickle(self, pickle_path, plk):
        df_dict = {}
        df = self.load_pkl(pickle_path, plk)
        for fs in c.VALID_SEVERITY_LAB.keys():
            df_sig = self.copy_rows_where_list_col_contains_text_df(df, 'Id', fs)
            df_dict[fs] = df_sig
        for fs, fs_df in df_dict.items():
            pkl_names = plk.split(".")
            pkl_name = f'{pkl_names[0]}_{fs}.pickle'
            self.save_pkl(fs_df, pickle_path, pkl_name)

    def select_fs_from_all_fp_pickle(self):
        df_dict = {}
        df_list = []
        plk = self.filelist[0][0:13]
        for file in self.filelist:
            file_path = os.path.join(self.input_folder, file)
            df = self.load_pkl(file_path)
            df_list.append(df)
        df = pd.concat(df_list, ignore_index=True)
        for fs in c.SYS_ALL:
            df_sig = self.copy_rows_where_list_col_contains_text_df(df, 'Id', fs)
            df_dict[fs] = df_sig
        for fs, fs_df in df_dict.items():
            pkl_name = f'{plk}_all_fp_{fs}.pickle'
            self.save_pkl(fs_df, self.output_folder, pkl_name)

    def select_fs_from_all_fn_pickle(self):
        df_dict = {}
        df_list = []
        plk = self.filelist[0][0:13]
        for file in self.filelist:
            file_path = os.path.join(self.input_folder, file)
            df = self.load_pkl(file_path)
            df_list.append(df)
        df = pd.concat(df_list, ignore_index=True)
        for fs in c.VALID_SEVERITY_LAB.keys():
            df_sig = self.copy_rows_where_list_col_contains_text_df(df, 'Id', fs)
            df_dict[fs] = df_sig
        for fs, fs_df in df_dict.items():
            pkl_name = f'{plk}_all_fn_{fs}.pickle'
            self.save_pkl(fs_df, self.output_folder, pkl_name)

    def select_from_split_list(self, failed_kpi_df_pickle, split_list_json):
        # get pickle path and name
        path_file = os.path.split(failed_kpi_df_pickle)
        pickle_path = path_file[0]
        pickle_name = path_file[1]
        split_list = self.load_json(split_list_json)
        df = self.load_pkl(failed_kpi_df_pickle)
        # add split name column to df
        df['split_name'] = np.nan
        df['split_name'] = df['Path'].str.extract(r'.+(ADCAM_.+_\d{8}_\d{6}_pic_\d{4}.pickle.xz)', expand=False)
        df = self.copy_rows_where_col_changed_to_new_val_df(df, 'split_name')
        df.reset_index(drop=True, inplace=True)
        split_name_list = list(df['split_name'])
        index_list = []
        for index, split in enumerate(split_name_list):
            if split in split_list:
                index_list.append(index)
        df_selected = df.loc[index_list].reset_index(drop=True)
        new_names = pickle_name.split('.')
        new_name = f'{new_names[0]}_selected.pickle'
        self.save_pkl(df_selected, pickle_path, new_name)

    #  makes dataframes per fs per severity for FN events
    def select_fs_severity_from_one_fn_pickle(self, pickle_path, plk):
        df_dict = {}
        df = self.load_pkl(pickle_path, plk)
        for fs, severity_list in c.VALID_SEVERITY_LAB.items():
            if fs in df.columns:
                for severity in severity_list:
                    df_sig = df[df[fs] == severity]
                    fs_severity = f'{fs}_{severity}'
                    df_dict[fs_severity] = df_sig
        for fs_severity, fs_df in df_dict.items():
            fs_df = fs_df[c.FAILED_KPI_DF_COLUMNS].reset_index(drop=True)
            new_name = f'FN_{fs_severity}.pickle'
            self.save_pkl(fs_df, pickle_path, new_name)

    #  makes dataframes per fs per severity for FP events
    def select_fs_severity_from_one_fp_pickle(self, pickle_path, plk):
        df_dict = {}
        df = self.load_pkl(pickle_path, plk)
        for fs, severity_list in c.VALID_SEVERITY_SYS.items():
            if fs in df.columns:
                for severity in severity_list:
                    df_sig = df[df[fs] == severity]
                    fs_severity = f'{fs}_{severity}'
                    df_dict[fs_severity] = df_sig
        for fs_severity, fs_df in df_dict.items():
            fs_df = fs_df[c.FAILED_KPI_DF_COLUMNS].reset_index(drop=True)
            new_name = f'FP_{fs_severity}.pickle'
            self.save_pkl(fs_df, pickle_path, new_name)

    def change_project(self):

        for root, d_names, f_names in os.walk(self.input_folder):
            print(f'searching: {root}')
            for f_name in f_names:
                if f_name.endswith('pickle'):
                    file_path = os.path.join(root, f_name)
                    df = self.load_pkl(file_path)
                    df['Project'] = 'mid'
                    if 'Split' in df.columns:
                        df.drop(columns='Split', inplace=True)
                    if 'Measurement' in df.columns:
                        df.drop(columns='Measurement', inplace=True)
                    if 'split_num' in df.columns:
                        df.drop(columns='split_num', inplace=True)
                    self.save_pkl(df, root, f_name)

def main():
    frame_selector = DfFailedSelector()
    frame_selector.change_project()
    frame_selector.get_pickles()
    # frame_selector.select_fs_from_all_fn_pickle()
    # frame_selector.select_fs_from_all_fp_pickle()
    # frame_selector.select_data_split()
    # frame_selector.select_data_split_for_each()
    # frame_selector.select_data_fp()
    # frame_selector.select_one_per_measurement()
    # frame_selector.select_if_gap_in_split_num()
    frame_selector.select_fs_severity_from_one_fn_pickle(r'f:\CARIAD\BHE\REPRO\X110\failed_dfs\NEW_ALL_WITH_SEVERITIES\ALL_ONE_PER_SPLIT', 'BWD_SOP1_X110_fn_one_per_split.pickle')
    frame_selector.select_fs_severity_from_one_fp_pickle(r'f:\CARIAD\BHE\REPRO\X110\failed_dfs\NEW_ALL_WITH_SEVERITIES\ALL_ONE_PER_SPLIT', 'BWD_SOP1_X110_fp_one_per_split.pickle')

    #path = r'c:\Users\wjjymc\PycharmProjects\BWD\FAILED_KPI_DFS\SOP1_A480_CP60_01\BWD_SOP1_A480_BIND_DFS\partials'
    #pkl = r'BWD_SOP1_A480_fn_one_per_split.pickle'
    # frame_selector.select_fs_from_one_fp_pickle(path, pkl)
    # frame_selector.select_fs_from_one_fn_pickle(path, pkl)

    # frame_selector.select_fs_from_all_fp_pickle()
    # frame_selector.select_fs_from_all_fn_pickle()

    # failed_kpi_df_pickle = r'C:\Users\wjjymc\PycharmProjects\BWD\FAILED_KPI_DFS\SOP1_A440\MID_DATASET\BWD_SOP1_A440_BIND_DFS\BWD_SOP1_A440_BIND_DFS_PARTIAL\all\separate_fp\BWD_SOP1_A440_all_fp_FS_Low_Sun_0.pickle'
    # split_list_json = r'f:\BWD\CP60\TR\SOP1_A440\spi_any\00_fp_split_list_low_sun_99.json'
    # frame_selector.select_from_split_list(failed_kpi_df_pickle, split_list_json)


if __name__ == "__main__":
    main()
