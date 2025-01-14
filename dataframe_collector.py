"""
Module collects failed KPI frames and stores info in dataframes
Patryk Leszowski
APTIV
BWD
"""
from libs.debugging import logger
from datetime import datetime
import config.constant as c
import pandas as pd
import numpy as np
import re
import os


class DfCollector:
    def __init__(self, sop, a_step, project):

        self.master_df_list = []
        self.df_row_counter = 0
        self.df_max_len = 50000
        self.collect = False
        self.sop = sop
        self.a_step = a_step
        self.function = 'BWD'
        self.project = project
        self.event_counter_dict = dict.fromkeys(c.FAILED_KPI_EVENTS, 0)
        self.master_df = pd.DataFrame(columns=c.FAILED_KPI_MASTER_DF_COLUMNS)
        self.dt_str = re.sub(r"[:\-. ]", "", str(datetime.now()))
        self.unique_name = self.dt_str

    def add_df(self, df, falisafe, file_dict):
        """
        Method gets dataframe and data from mainLogic.py and makes failed kpi dataframes with event counters
        :param df: df from mainLogic
        :param falisafe: falisafe from mainLogic
        :param file_dict: file_dict from mainLogic
        :return: True/False
        """
        if self.collect:
            num_of_rows = df.shape[0]
            if num_of_rows < 1:
                print(f'DfCollector: {self.dt_str}: ERROR: passed empty dataframe into add_df')
                return False

            # increment event counters
            # self.event_counter_dict[falisafe] += 1

            # adapt file_dict so that keys have full file names
            if not file_dict:
                print(f'DfCollector: {self.dt_str}: ERROR: passed empty file dictionary into add_df')
                return False
            file_dict = self.adapt_file_dict(file_dict)
            if not file_dict:
                print(f'DfCollector: {self.dt_str}: ERROR: got empty file dictionary from adapt_file_dict()')
                return False

            # Get HILREPP name
            key = list(file_dict.keys())[0]
            search_line = file_dict[key]
            # search for HILREPP-7digits, force the engine to try matching at the furthest position
            search = re.search(r'(?s:.*).+\W(\d{4}_\d{4})\W.+', search_line)   # ex. HILREPP-2013288
            if search:
                self.unique_name = search.group(1)

            # reset indexes
            df.reset_index(drop=True, inplace=True)

            # make temporary dataframe
            temp_df = pd.DataFrame(index=np.arange(num_of_rows), columns=c.FAILED_KPI_MASTER_DF_COLUMNS)
            # Fill info
            temp_df[c.FAILED_KPI_FUNC] = self.function
            temp_df[c.FAILED_KPI_SOP] = self.sop
            temp_df[c.FAILED_KPI_PROJECT] = self.project
            temp_df[c.FAILED_KPI_ASTEP] = self.a_step

            # insert Type lists to Type column
            t_list = self.get_type(df, falisafe)
            if len(t_list) == num_of_rows:
                temp_df[c.FAILED_KPI_TYPE] = t_list
            else:
                print(f'DfCollector: {self.dt_str}: ERROR: type list length unequal to num_of_rows')
                return False

            # insert failure type lists to FailureType column
            # make fs a list
            ft_list = []
            ft_column_list = []
            # get failure type, FN, or FP
            fail_type = self.get_failure_type(falisafe)
            ft_list.append(fail_type)
            # make list of falisafe type lists
            for i in range(num_of_rows):
                ft_column_list.append(ft_list)
            if len(ft_column_list) == num_of_rows:
                temp_df[c.FAILED_KPI_FAILURE_TYPE] = ft_column_list
            else:
                print(f'DfCollector: {self.dt_str}: ERROR: failure type list length unequal to num_of_rows')
                return False

            # Get and fill id lists to id column
            id_list = []
            id_column_list = []
            # make id_name a list
            id_list.append(falisafe)
            # make list of id lists
            for i in range(num_of_rows):
                id_column_list.append(id_list)
            if len(id_column_list) == num_of_rows:
                temp_df[c.FAILED_KPI_ID] = id_column_list
            else:
                print(f'DfCollector: {self.dt_str}: ERROR: id list length unequal to num_of_rows')
                return False

            # Copy grab index
            temp_df[c.FAILED_KPI_GID] = list(df['grabIndex'].astype(int))

            # Copy filename (temp column)
            temp_df[c.FAILED_KPI_FILENAME] = df['File_Name']

            # Fill Path column
            for i in range(num_of_rows):
                file = temp_df.loc[i, c.FAILED_KPI_FILENAME]
                temp_df.at[i, c.FAILED_KPI_PATH] = file_dict[file]

            # Copy itrk_name
            temp_df[c.FAILED_KPI_ITRK] = df['itrk_name']

            # make split + grabindex column (temp column)
            split_gid_list = []
            split_list = list(df['File_Name'])
            grab_index_list = list(df['grabIndex'].astype(int))
            # get rid of .pickle.xz
            for i in range(num_of_rows):
                split_name = split_list[i].split('.')[0]
                split_gid_list.append(split_name + '_' + str(grab_index_list[i]))
            if len(split_gid_list) == num_of_rows:
                temp_df[c.FAILED_KPI_SPLIT_GID] = split_gid_list
            else:
                print(f'DfCollector: {self.dt_str}: ERROR: split_gid_list length unequal to num_of_rows')
                return False

            try:
                # Add event counter to dataframe
                # temp_df.loc[:, falisafe] = self.event_counter_dict[falisafe]
                temp_df.fillna(0, inplace=True)
            except Exception as e:
                print(f'DfCollector: {self.dt_str}: ERROR: adding failsafe counter')
                logger.exception(e)
                return False

            # copy label and signal values from df to temp_df
            try:
                for kpi_event in c.FAILED_KPI_EVENTS:
                    if kpi_event in df.columns:
                        temp_df[kpi_event] = df[kpi_event]
            except Exception as e:
                print(f'DfCollector: {self.dt_str}: ERROR: copy label and signal values from df to temp_df')
                logger.exception(e)
                return False

            # Merge to master_df dataframes
            # if master_df contains data
            if self.master_df.shape[0] > 0:
                try:
                    # find common split_gid in dataframes
                    common_split_gid_df = pd.merge(self.master_df, temp_df, how='inner', left_on=c.FAILED_KPI_SPLIT_GID, right_on=c.FAILED_KPI_SPLIT_GID)
                except Exception as e:
                    print(f'DfCollector: {self.dt_str}: ERROR: merging master_df and temp_df')
                    logger.exception(e)
                    return False
                # if frames are already in masted_df
                if common_split_gid_df.shape[0] > 0:
                    # get splits from temp_df that are not in common_split_gid_df
                    unique_split_gid_df = temp_df[~temp_df[c.FAILED_KPI_SPLIT_GID].isin(common_split_gid_df[c.FAILED_KPI_SPLIT_GID])]
                    # add Type lists
                    try:
                        type_list = common_split_gid_df[c.FAILED_KPI_TYPE + '_x'] + common_split_gid_df[c.FAILED_KPI_TYPE + '_y']
                        common_split_gid_df.insert(0, c.FAILED_KPI_TYPE, type_list, True)
                        common_split_gid_df.drop([c.FAILED_KPI_TYPE + '_x', c.FAILED_KPI_TYPE + '_y'], axis=1, inplace=True)
                    except Exception as e:
                        print(f'DfCollector: {self.dt_str}: ERROR: in add Type lists')
                        logger.exception(e)
                        return False
                    # add FailureType lists
                    try:
                        failure_type_list = common_split_gid_df[c.FAILED_KPI_FAILURE_TYPE + '_x'] + common_split_gid_df[c.FAILED_KPI_FAILURE_TYPE + '_y']
                        common_split_gid_df.insert(1, c.FAILED_KPI_FAILURE_TYPE, failure_type_list, True)
                        common_split_gid_df.drop([c.FAILED_KPI_FAILURE_TYPE + '_x', c.FAILED_KPI_FAILURE_TYPE + '_y'], axis=1, inplace=True)
                    except Exception as e:
                        print(f'DfCollector: {self.dt_str}: ERROR: in add FailureType lists')
                        logger.exception(e)
                        return False
                    # add Id lists
                    try:
                        id_list = common_split_gid_df[c.FAILED_KPI_ID + '_x'] + common_split_gid_df[c.FAILED_KPI_ID + '_y']
                        common_split_gid_df.insert(2, c.FAILED_KPI_ID, id_list, True)
                        common_split_gid_df.drop([c.FAILED_KPI_ID + '_x', c.FAILED_KPI_ID + '_y'], axis=1, inplace=True)
                    except Exception as e:
                        print(f'DfCollector: {self.dt_str}: ERROR: in add Id lists')
                        logger.exception(e)
                        return False
                    try:
                        # get dataframe slice from master_df where Split_Gid is also in common_split_gid_df
                        temp_split_gid_df = self.master_df.loc[self.master_df[c.FAILED_KPI_SPLIT_GID].isin(common_split_gid_df[c.FAILED_KPI_SPLIT_GID])].copy()
                        # copy values from common_split_gid_df
                        temp_split_gid_df.loc[:, c.FAILED_KPI_TYPE] = common_split_gid_df.Type.values  # column of str lists
                        temp_split_gid_df.loc[:, c.FAILED_KPI_FAILURE_TYPE] = common_split_gid_df.FailureType.values  # column of str lists
                        temp_split_gid_df.loc[:, c.FAILED_KPI_ID] = common_split_gid_df.Id.values  # column of str lists
                        # for event in c.FAILED_KPI_EVENTS:
                        temp_split_gid_df.loc[:, falisafe] = common_split_gid_df[falisafe + '_y'].values
                        # replace rows in master_df with rows from temp_split_gid_df
                        self.master_df.loc[temp_split_gid_df.index, :] = temp_split_gid_df[:]
                    except Exception as e:
                        print(f'DfCollector: {self.dt_str}: ERROR: in temp_split_gid_df')
                        logger.exception(e)
                        return False
                    # add splits from temp_df that are not in common_split_gid_df
                    try:
                        if unique_split_gid_df.shape[0] > 0:
                            self.master_df = pd.concat([self.master_df, unique_split_gid_df]).reset_index(drop=True)
                    except Exception as e:
                        print(f'DfCollector: {self.dt_str}: ERROR: concat unique_split_gid_df to master_df')
                        logger.exception(e)
                        return False
                # if frames are not already in masted_df, concat whole dataframe
                else:
                    try:
                        self.master_df = pd.concat([self.master_df, temp_df]).reset_index(drop=True)
                    except Exception as e:
                        print(f'DfCollector: {self.dt_str}: ERROR: concat temp_df to master_df')
                        logger.exception(e)
                        return False
            # if master_df does not contain data, concat first data
            else:
                try:
                    self.master_df = pd.concat([self.master_df, temp_df]).reset_index(drop=True)
                except Exception as e:
                    print(f'DfCollector: {self.dt_str}: ERROR: concat temp_df to empty master_df')
                    logger.exception(e)
                    return False
            # sort by Split_Gid
            self.master_df.sort_values(by=[c.FAILED_KPI_SPLIT_GID], axis=0, inplace=True, ignore_index=True)
            return True

        else:
            return False

    def append_to_master_df_list(self, df_to_append):
        """
        Append master dataframes to list with rows
        :param df_to_append:
        :return:
        """
        try:
            df = df_to_append[c.FAILED_KPI_MASTER_DF_COLUMNS].reset_index(drop=True)
            self.master_df_list.append(df)
        except Exception as e:
            print(f'DfCollector: {self.dt_str}: ERROR: cannot append with specified rows')
            logger.exception(e)

    def save_dfs(self):
        if self.master_df_list:
            new_folder = f'{self.function}_{self.sop}_{self.a_step}_HILREPP_DFS'
            new_path = os.path.join(c.PATH_FAILED_KPI_DFS, new_folder)
            if not os.path.isdir(new_path):
                os.makedirs(new_path, exist_ok=True)
            counter = 0
            for df in self.master_df_list:
                if len(df) > 0:
                    counter += 1
                    file_name = f'{self.function}_{self.sop}_{self.a_step}_{self.unique_name}_{counter:04d}.pickle'
                    self.save_pkl(df, new_path, file_name)
        else:
            print(f'DfCollector: {self.dt_str}: WARNING: No Dataframes to save')
        df_count = len(self.master_df_list)
        print(f'DfCollector: {self.dt_str}: INFO: Number of dataframes: {df_count}')

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

    def get_failure_type(self, failsafe):
        """
        Gets failure type
        :param failsafe:
        :return: failure_type
        """
        if failsafe in c.FAILED_KPI_FP_EVENTS:
            failure_type = 'FP'
        elif failsafe in c.FAILED_KPI_FN_EVENTS:
            failure_type = 'FN'
        else:
            print(f'DfCollector: {self.dt_str}: WARNING: Cant get failure_type in get_failure_type()')
            failure_type = 'NA'
        return failure_type

    def get_type(self, df, failsafe):
        """
        Gets type, attribute that failed
        :param df:
        :param failsafe:
        :return: type_column_list
        """
        type_column_list = []
        failure_type = self.get_failure_type(failsafe)
        if failure_type == 'FN':
            signal_list = c.LAB_TO_SPI_BACKUP[failsafe]
            for index in range(len(df)):
                type_list = []
                detection_type = c.FAILED_KPI_NO_DETECTION
                for signal in signal_list:
                    if signal not in df.columns:
                        continue
                    if df.loc[index, signal] > 1:
                        detection_type = c.FAILED_KPI_WRONG_SEVERITY
                type_list.append(detection_type)
                type_column_list.append(type_list)
        elif failure_type == 'FP':
            signal_list = c.SYS_TO_LAB[failsafe]
            for index in range(len(df)):
                type_list = []
                detection_type = c.FAILED_KPI_FALSE_DETECTION
                for signal in signal_list:
                    if df.loc[index, signal] > -1:
                        detection_type = c.FAILED_KPI_WRONG_DETECTION
                type_list.append(detection_type)
                type_column_list.append(type_list)
        else:
            print(f'DfCollector: {self.dt_str}: WARNING: wrong failure_type in get_type()')
        return type_column_list

    def adapt_file_dict(self, file_dict):
        """
        Adapt keys, so they are full filenames
        :param file_dict:
        :return:
        """
        new_file_dict = {}
        for file, path in file_dict.items():
            search_file_name = re.search(r'.+(AD(CAM|MCP)_.+_\d{8}_\d{6}_.+)', path)
            if search_file_name:
                filename = search_file_name.group(1)
                new_file_dict[filename] = path
            else:
                print(f'DfCollector: {self.dt_str}: WARNING: cant find full file name in {path}')
        return new_file_dict

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
                self.append_to_master_df_list(df)
        elif master_df_len > 0:
            self.append_to_master_df_list(self.master_df)
