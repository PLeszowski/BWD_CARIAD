import os
import json
import pandas as pd
import numpy as np
import pickle


class OutputDiffTable:

    def __init__(self):
        self.hilrep_output_normal_path = r'c:\Users\wjjymc\PycharmProjects\BWD\FAILED_KPI_DFS\BWD_SOP7_A420_OUTPUT\SPI\NORMAL_RUN'
        self.hilrep_output_prio1_path = r'c:\Users\wjjymc\PycharmProjects\BWD\FAILED_KPI_DFS\BWD_SOP7_A420_OUTPUT\SPI\PRIO1_RUN_NEW'
        self.hilrep_output_prio2_path = r'c:\Users\wjjymc\PycharmProjects\BWD\FAILED_KPI_DFS\BWD_SOP7_A420_OUTPUT\SPI\PRIO2_RUN_NEW'
        self.results_normal_path = r'c:\Users\wjjymc\PycharmProjects\BWD\FAILED_KPI_DFS\BWD_SOP7_A420_BIND_DFS_01\NORMAL_RUN'
        self.results_prio1_path = r'c:\Users\wjjymc\PycharmProjects\BWD\FAILED_KPI_DFS\BWD_SOP7_A420_BIND_DFS_01\PRIO1_RUN_NEW'
        self.results_prio2_path = r'c:\Users\wjjymc\PycharmProjects\BWD\FAILED_KPI_DFS\BWD_SOP7_A420_BIND_DFS_01\PRIO2_RUN_NEW'
        self.file_list = []
        self.pickle_list_normal = []
        self.pickle_list_prio1 = []
        self.pickle_list_prio2 = []
        self.pickle_list_all = []
        self.final_df_path = r'c:\Users\wjjymc\PycharmProjects\BWD\FAILED_KPI_DFS\BWD_SOP7_A420_OUTPUT\SPI\SOP7_A420_DIFF_DF_02.pickle'
        self.df_columns = ['Split Name', 'Normal Result', 'Prio1 Result', 'Prio2 Result']
        self.master_df = pd.DataFrame(columns=self.df_columns)

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
            print(f'OutputDiffTable: ERROR: Cant open {file}')
            print(e)

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
    def save_pkl(obj, path, file=None):
        """
        Save object to pickle
        :param obj: object to be serialized
        :param path: path to folder
        :param file: file name
        :return:
        """
        if file:
            pickle_path = os.path.join(path, file)
        else:
            pickle_path = path
        filename = os.path.join(pickle_path)
        obj.to_pickle(filename, protocol=4)

    @staticmethod
    def generate_event_split_list(start, stop):
        event_split_list = []
        pre = start[:44]
        post = start[48:]
        start_event = start[44:48]
        stop_event = stop[44:48]
        start_log_int = int(start_event)
        stop_log_int = int(stop_event)
        for split_count in range(start_log_int, stop_log_int + 1):
            event_split_list.append(f'{pre}{split_count:04d}{post}')
        return event_split_list

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
            print(f'OutputDiffTable: copy_rows_where_col_changed_to_new_val_df: KeyError {col_name}')
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
            df = dataframe.loc[index_list].reset_index(drop=True)
            return df

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

    def get_used_splits_list(self, path):
        counter = 0
        used_splits_list = []
        all_file_count = len(self.file_list)
        for file in self.file_list:
            counter += 1
            print(f'get_used_splits_list: {counter}/{all_file_count}: {file}')
            hilrep_output = self.load_json(path, file)
            if hilrep_output:
                for data_dict in hilrep_output:
                    if data_dict:
                        if "Processed" in data_dict:
                            pickle_list = data_dict["Processed"]
                            try:
                                if None in pickle_list:
                                    pickle_list = list(filter(lambda x: x is not None, pickle_list))
                                pickle_list.sort()
                                used_splits_list += pickle_list
                            except TypeError as e:
                                print(e)

        used_splits_list = list(set(used_splits_list))
        used_splits_list.sort()
        return used_splits_list

    def add_passed_to_master_df(self, column, split_list):
        # put PASS in column
        # get df indexes by split_list
        temp_df = self.master_df[self.master_df['Split Name'].isin(split_list)]
        indexes = temp_df.index.values
        # put PASS in column at indexes
        self.master_df.loc[indexes, column] = 'PASS'

    def add_failed_to_master_df(self, column, results_path):
        failed_df_list = []
        run_name_keep_column_list = ['Type', 'FailureType', 'Id', 'Gid', 'Path']
        run_name_drop_column_list = ['SOP', 'Astep', 'Function', 'Project', 'Itrkname']
        run_name = column.split(' ')[0]
        for file in self.file_list:
            # load failed kpi dataframe
            failed_df = self.load_pkl(results_path, file)
            failed_df_list.append(failed_df)

        all_failed_df = pd.concat(failed_df_list, ignore_index=True)
        # add Split Name column
        all_failed_df['Split Name'] = np.nan
        all_failed_df['Split Name'] = all_failed_df['Path'].str.extract(r'.+(ADCAM_.+_\d{8}_\d{6}_pic_\d{4}.+)', expand=False)
        # sort by split name
        all_failed_df.sort_values('Split Name', inplace=True)
        # leave only first row for each same path - different split in each row
        all_failed_df = self.copy_rows_where_col_changed_to_new_val_df(all_failed_df, 'Split Name')
        # get all failed splits list
        split_list = list(all_failed_df['Split Name'])
        # get df indexes by split_list - master_df contains all used splits, get indexes of the failed ones
        failed_from_master_df = self.master_df[self.master_df['Split Name'].isin(split_list)]
        failed_from_master_indexes = failed_from_master_df.index.values
        # put FAIL in column at indexes
        self.master_df.loc[failed_from_master_indexes, column] = 'FAIL'
        # rename columns in failed_df
        for col in all_failed_df.columns.values:
            if col in run_name_keep_column_list:
                all_failed_df.rename(columns={col: run_name + ' ' + col}, inplace=True)
        if run_name != 'Normal':
            all_failed_df.drop(run_name_drop_column_list, axis=1, inplace=True)
            print()
        # put columns from failed_df_ to master
        self.master_df = self.master_df.merge(all_failed_df, on='Split Name', how='left')

    def get_output_table(self):
        # get normal pickle list
        self.get_df_files(self.hilrep_output_normal_path, '.json')
        self.pickle_list_normal = self.get_used_splits_list(self.hilrep_output_normal_path)
        self.pickle_list_all += self.pickle_list_normal
        # get prio1 pickle list
        self.get_df_files(self.hilrep_output_prio1_path, '.json')
        self.pickle_list_prio1 += self.get_used_splits_list(self.hilrep_output_prio1_path)
        self.pickle_list_all += self.pickle_list_prio1
        # get prio2 pickle list
        self.get_df_files(self.hilrep_output_prio2_path, '.json')
        self.pickle_list_prio2 += self.get_used_splits_list(self.hilrep_output_prio2_path)
        self.pickle_list_all += self.pickle_list_prio2

        # make all pickle dataframe
        self.pickle_list_all = list(set(self.pickle_list_all))
        self.pickle_list_all.sort()
        self.master_df.loc[:, 'Split Name'] = self.pickle_list_all

        # put PASS in Normal Result
        self.add_passed_to_master_df('Normal Result', self.pickle_list_normal)
        # put PASS in Prio1 Result
        self.add_passed_to_master_df('Prio1 Result', self.pickle_list_prio1)
        # put PASS in Prio2 Result
        self.add_passed_to_master_df('Prio2 Result', self.pickle_list_prio2)

        # put FAIL in Normal Result
        self.get_df_files(self.results_normal_path, '.pickle')
        self.add_failed_to_master_df('Normal Result', self.results_normal_path)
        # put FAIL in Prio1 Result
        self.get_df_files(self.results_prio1_path, '.pickle')
        self.add_failed_to_master_df('Prio1 Result', self.results_prio1_path)
        # put FAIL in Prio2 Result
        self.get_df_files(self.results_prio2_path, '.pickle')
        self.add_failed_to_master_df('Prio2 Result', self.results_prio2_path)

        # Leave only rows that failed
        self.master_df['Diff'] = self.master_df[self.master_df[['Normal Result', 'Prio1 Result', 'Prio2 Result']] == 'FAIL'].any(axis=1)
        any_fail_df = self.master_df.loc[self.master_df['Diff']]
        any_fail_df.drop(['Diff'], axis=1, inplace=True)
        # get rid of all rows where Normal Result and Prio1 Result and Prio2 Result all equal FAIL
        final_df = any_fail_df.loc[~((any_fail_df['Normal Result'] == 'FAIL') & (any_fail_df['Prio1 Result'] == 'FAIL') & (any_fail_df['Prio2 Result'] == 'FAIL'))]
        # get rid of nans
        final_df = final_df[pd.notnull(final_df['Normal Result'])]
        final_df = final_df[pd.notnull(final_df['Prio1 Result'])]
        final_df = final_df[pd.notnull(final_df['Prio2 Result'])]
        final_df.reset_index(drop=True, inplace=True)
        self.save_pkl(final_df, self.final_df_path)
        new_path = os.path.splitext(self.final_df_path)[0]
        wb_name = new_path + '.xlsx'
        with pd.ExcelWriter(wb_name) as writer:
            final_df.to_excel(writer, sheet_name='Diff')


def main():
    table = OutputDiffTable()
    table.get_output_table()


if __name__ == "__main__":
    main()
