"""
Module reads BWD_testcases.xlsx, opens pickles from start trial to end trial, and tests based on TC-X in tc_map_dict
Outputs BWD_testcases_results.xlsx, a similar workbook as BWD_testcases.xlsx but with test result column
Patryk Leszowski
APTIV
BWD
"""
import pandas as pd
import numpy as np
import pickle
import json
import lzma
import os
import config.constant as c


class BwdTestcases:
    def __init__(self):
        self.tc_df = pd.DataFrame()
        self.bwd_testcases_info = r'c:\Users\wjjymc\PycharmProjects\BWD\BWD_Testcases\BWD_testcases.xlsx'
        self.bwd_testcases_pickle_folder = r'c:\Users\wjjymc\PycharmProjects\BWD\BWD_Testcases\pickles'
        self.bwd_testcases_output_folder = r'c:\Users\wjjymc\PycharmProjects\BWD\BWD_Testcases\output'
        self.bwd_tc_cyfro_paths_folder = r'c:\Users\wjjymc\PycharmProjects\BWD\BWD_Testcases\cyfro_paths\MID'
        self.bwd_tc_cyfro_paths_pickle_list = []
        self.bwd_tc_cyfro_paths_list = []
        self.bad_file_list = []
        self.all_pickle_list = []
        self.tc_map_dict = {'TC-1': {'signals': [c.SYS_PARTIAL_BLOCKAGE, c.SYS_FULL_BLOCKAGE, c.SYS_FROZEN_WINDSHIELD], 'detect': True},  # PDD_2103
                            'TC-2': {'signals': [c.SYS_FOG], 'detect': False},  # PDD_2104
                            'TC-3': {'signals': c.SYS_ALL, 'detect': True},  # PDD_2105
                            'TC-4': {'signals': [c.SYS_FOG], 'detect': False},  # PDD_2113
                            'TC-5': {'signals': [c.SYS_SUN_RAY], 'detect': False},  # PDD_2114
                            'TC-6': {'signals': c.SYS_ALL, 'detect': False}  # PDD_2115
                            }

    def get_bwd_tc_info_to_df(self):
        self.tc_df = pd.read_excel(self.bwd_testcases_info)
        # add test result column, fill with nan
        self.tc_df['test result'] = np.nan

    def get_cyfro_paths_pickle_list(self):

        try:
            allfiles = os.listdir(self.bwd_tc_cyfro_paths_folder)
        except (FileNotFoundError, PermissionError, NotADirectoryError) as e:
            print(f'DfBinder: ERROR: Cant open {self.bwd_tc_cyfro_paths_folder}')
            print(e)
            raise e
        else:
            if allfiles:
                for file in allfiles:
                    if file.endswith('.pickle.xz'):
                        self.bwd_tc_cyfro_paths_pickle_list.append(file)
            else:
                print(f'DfBinder: No pickles in {self.bwd_tc_cyfro_paths_folder}')
                print(FileNotFoundError)
                raise FileNotFoundError

    @staticmethod
    def get_split_list(start_split, end_split):
        split_list = []
        log_name = start_split[0:40]
        start_log_int = int(start_split[44:48])
        stop_log_int = int(end_split[44:48])
        for i in range(start_log_int, stop_log_int + 1):
            i_string = f'{log_name}pic_{i:04d}.pickle.xz'
            split_list.append(i_string)
        return split_list

    @staticmethod
    def load_pkl(path, file):
        """
        Function opens pickle file, whether it is packed with 'xz'
        :param path: path to folder
        :param file: pickle file name
        :return: extracted data from pickle to dictionary
        """
        input_file = os.path.join(path, file)
        ext = input_file.split('.')[-1]
        if ext == 'pickle' or ext == 'pkl':
            with open(input_file, 'rb') as tab:
                data = pickle.load(tab)
        if ext == 'xz':
            with lzma.open(input_file, 'rb') as tab:
                data = pickle.load(tab)
        if ext == 'json':
            with open(input_file, 'rb') as tab:
                data = json.load(tab)
        return data

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

    def save_pickle_list_to_json(self):
        self.save_json(self.all_pickle_list, self.bwd_testcases_output_folder, 'bwd_tc_pickle_list.json')

    def save_bad_file_list_to_json(self):
        self.save_json(self.bad_file_list, self.bwd_testcases_output_folder, 'bad_file_list.json')

    def save_result_excel(self):
        with pd.ExcelWriter(f'{self.bwd_testcases_output_folder}/BWD_testcases_results.xlsx') as writer:
            self.tc_df.to_excel(writer, sheet_name='TPR_results')

    def get_pickle_data_df(self, pickle_list):
        df_list = []
        for file in pickle_list:
            try:
                plk = self.load_pkl(self.bwd_testcases_pickle_folder, file)
            except Exception as e:
                print(f'Cant open: {file}')
                print(e)
                self.bad_file_list.append(file)
                continue

            split_dict = {}
            # BWD ---------------------------------------------------------------
            try:
                if 'EYEQ_TO_HOST' in plk['SPI'] and 'Core_Failsafe_protocol' in plk['SPI']['EYEQ_TO_HOST']:
                    split_dict['timestamp'] = list(plk['SPI']['EYEQ_TO_HOST']['Core_Failsafe_protocol']['timestamp'])
                    split_dict[c.SYS_SUN_RAY] = list(plk['SPI']['EYEQ_TO_HOST']['Core_Failsafe_protocol'][c.SYS_SUN_RAY])
                    split_dict[c.SYS_FADING_BY_SUN] = list(plk['SPI']['EYEQ_TO_HOST']['Core_Failsafe_protocol'][c.SYS_FADING_BY_SUN])
                    split_dict[c.SYS_RAIN] = list(plk['SPI']['EYEQ_TO_HOST']['Core_Failsafe_protocol'][c.SYS_RAIN])
                    split_dict[c.SYS_FULL_BLOCKAGE] = list(plk['SPI']['EYEQ_TO_HOST']['Core_Failsafe_protocol'][c.SYS_FULL_BLOCKAGE])
                    split_dict[c.SYS_FROZEN_WINDSHIELD] = list(plk['SPI']['EYEQ_TO_HOST']['Core_Failsafe_protocol'][c.SYS_FROZEN_WINDSHIELD])
                    split_dict[c.SYS_FOG] = list(plk['SPI']['EYEQ_TO_HOST']['Core_Failsafe_protocol'][c.SYS_FOG])
                    split_dict[c.SYS_PARTIAL_BLOCKAGE] = list(plk['SPI']['EYEQ_TO_HOST']['Core_Failsafe_protocol'][c.SYS_PARTIAL_BLOCKAGE])
                    split_dict[c.SYS_BLUR] = list(plk['SPI']['EYEQ_TO_HOST']['Core_Failsafe_protocol'][c.SYS_BLUR])
                    split_dict[c.SYS_OUT_OF_FOCUS] = list(plk['SPI']['EYEQ_TO_HOST']['Core_Failsafe_protocol'][c.SYS_OUT_OF_FOCUS])
                    split_dict[c.SYS_ROAD_SPRAY] = list(plk['SPI']['EYEQ_TO_HOST']['Core_Failsafe_protocol'][c.SYS_ROAD_SPRAY])
                else:
                    split_dict['timestamp'] = []
                    split_dict[c.SYS_SUN_RAY] = []
                    split_dict[c.SYS_FADING_BY_SUN] = []
                    split_dict[c.SYS_RAIN] = []
                    split_dict[c.SYS_FULL_BLOCKAGE] = []
                    split_dict[c.SYS_FROZEN_WINDSHIELD] = []
                    split_dict[c.SYS_FOG] = []
                    split_dict[c.SYS_PARTIAL_BLOCKAGE] = []
                    split_dict[c.SYS_BLUR] = []
                    split_dict[c.SYS_OUT_OF_FOCUS] = []
                    split_dict[c.SYS_ROAD_SPRAY] = []
                    print(f'No Core_Failsafe_protocol: {file}')

            except KeyError as e:
                self.bad_file_list.append(file)
                print(f'KeyError in Core_Failsafe_protocol: {file}')
                print(e)
                continue

            pickle_data_df = pd.DataFrame.from_dict(split_dict)
            df_list.append(pickle_data_df)

        if df_list:
            trial_df = pd.concat(df_list, ignore_index=True, sort=True)
        else:
            trial_df = pd.DataFrame()
        return trial_df

    def test_trial(self, tc, trial_df):
        result = 'NONE'
        for signal in self.tc_map_dict[tc]['signals']:
            signal_values = trial_df[signal]
            max_value = signal_values.max()
            if self.tc_map_dict[tc]['detect']:
                if max_value > 1:
                    result = 'PASS'
                    break
                else:
                    result = 'FAIL'
            else:
                if max_value > 1:
                    result = 'FAIL'
                    break
                else:
                    result = 'PASS'
        return result

    def get_pickle_lists(self):
        # get pickle list from BWD_testcases.xlsx dataframe
        for index in self.tc_df.index.values:
            start_split = self.tc_df.loc[index, 'start trial']
            stop_split = self.tc_df.loc[index, 'end trial']
            self.all_pickle_list += self.get_split_list(start_split, stop_split)
        # get cyfro paths
        # get list of cyfro path pickles
        self.get_cyfro_paths_pickle_list()
        for pkl in self.bwd_tc_cyfro_paths_pickle_list:
            cyfro_paths_dict = self.load_pkl(self.bwd_tc_cyfro_paths_folder, pkl)
            cyfro_paths_list = list(cyfro_paths_dict['Valid_data'])
            for cyfro_path in cyfro_paths_list:
                split = cyfro_path.split('/')[-1]
                if split in self.all_pickle_list:
                    self.bwd_tc_cyfro_paths_list.append(cyfro_path)
        self.save_json(self.bwd_tc_cyfro_paths_list, self.bwd_tc_cyfro_paths_folder, 'bwd_tc_cyfro_paths.json')

    def run_bwd_testcases(self):
        for index in self.tc_df.index.values:
            tc = self.tc_df.loc[index, 'test case number']
            start_split = self.tc_df.loc[index, 'start trial']
            stop_split = self.tc_df.loc[index, 'end trial']
            pickle_list = self.get_split_list(start_split, stop_split)
            trial_df = self.get_pickle_data_df(pickle_list)
            if len(trial_df) > 0:
                test_result = self.test_trial(tc, trial_df)
                self.tc_df.loc[index, 'test result'] = test_result
        self.save_result_excel()
        if self.bad_file_list:
            self.save_bad_file_list_to_json()


def main():
    bwd_tc = BwdTestcases()
    bwd_tc.get_bwd_tc_info_to_df()
    # bwd_tc.get_pickle_lists()
    bwd_tc.run_bwd_testcases()
    print()


if __name__ == "__main__":
    main()
