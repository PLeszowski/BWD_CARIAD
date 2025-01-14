"""
Script searches logs for a specific failsafe with specific severity and lists: Start Split, Stop Split:, start frame, stop frame
Patryk Leszowski
APTIV
BWD
"""

from file_list import FileList
import serializer
import config.constant as c
import pandas as pd


class FSFinder:

    def __init__(self):

        self.pickle_path = r'f:\CARIAD\BHE\VCOT\D065\look_for_rain\BHE\pickles'
        self.dataframe_path = r'f:\CARIAD\BHE\VCOT\D065\look_for_rain\BHE\pickles\dataframe'
        self.dataframe_file_name = r'BHE_DF_RAIN.pickle'
        self.xz_file_list = FileList(self.pickle_path, 'xz')
        self.pickle_file_list = FileList(self.pickle_path, 'pickle')
        self.xz_file_list.get_file_list()
        self.pickle_file_list.get_file_list()
        self.file_list = self.xz_file_list.files + self.pickle_file_list.files
        self.df = pd.DataFrame()
        self.timestamp = 'timestamp'
        self.grab_index = 'COM_Cam_Frame_ID'
        self.file_name = 'file_name'

    def get_dataframe(self):

        df_list = []
        for file in self.file_list:

            bhe_dict = {}
            com_dict = {}
            pickle = serializer.load_pkl(self.pickle_path, file)

            try:
                if 'EYEQ_TO_HOST' in pickle['SPI'] and 'Core_Failsafe_protocol' in pickle['SPI']['EYEQ_TO_HOST']:
                    bhe_dict[self.timestamp] = pickle['SPI']['EYEQ_TO_HOST']['Core_Failsafe_protocol'][self.timestamp]
                    bhe_dict[self.file_name] = [file[0:48] + '.MF4']*len(bhe_dict[self.timestamp])
                    bhe_dict[c.SYS_RAIN] = pickle['SPI']['EYEQ_TO_HOST']['Core_Failsafe_protocol'][c.SYS_RAIN]
                else:
                    print(f'No Core_Failsafe_protocol in {file}')
                    continue
            except KeyError as e:
                print('error in Core_Failsafe_protocol')
            try:
                if 'EYEQ_TO_HOST' in pickle['SPI'] and 'Core_Common_protocol' in pickle['SPI']['EYEQ_TO_HOST']:
                    com_dict[self.timestamp] = pickle['SPI']['EYEQ_TO_HOST']['Core_Common_protocol'][self.timestamp]
                    # com_dict['COM_EyeQ_Frame_ID'] = pickle['SPI']['EYEQ_TO_HOST']['Core_Common_protocol']['COM_EyeQ_Frame_ID']
                    com_dict['COM_Cam_Frame_ID'] = pickle['SPI']['EYEQ_TO_HOST']['Core_Common_protocol'][self.grab_index]
                else:
                    print(f'No Core_Common_protocol in {file}')
                    continue
            except KeyError as e:
                print('error in Core_Common_protocol')

            # make dataframes from dictionaries
            bhe_df = pd.DataFrame(bhe_dict)
            com_df = pd.DataFrame(com_dict)
            # merge dataframes by timestamp
            df = pd.merge_asof(bhe_df.sort_values(self.timestamp), com_df, on=self.timestamp, direction='nearest')
            # append merged dataframe to list
            df_list.append(df)

        self.df = pd.concat(df_list, ignore_index=True)
        serializer.save_pkl(self.df, self.dataframe_path, self.dataframe_file_name)

    def load_df(self):
        if len(self.df) == 0:
            self.df = serializer.load_pkl(self.dataframe_path, self.dataframe_file_name)

    def print_fs_severity_events(self, fs, severity):
        start_split = ''
        start_frame = ''
        df_severities = self.df[self.df[fs] >= severity]
        fs_severity_list = set(df_severities[fs].to_list())
        if fs_severity_list:
            for fs_severity in fs_severity_list:
                df_severity = self.df[self.df[fs] == fs_severity]
                df_severity_boundary = self.copy_rows__index_boundary_val_df(df_severity).reset_index(drop=True)
                index_list = list(df_severity_boundary.index.values)
                if index_list:
                    for index in index_list:
                        if index % 2 == 0:
                            start_split = df_severity_boundary.loc[index, self.file_name]
                            start_frame = str(df_severity_boundary.loc[index, self.grab_index])
                        else:
                            stop_split = df_severity_boundary.loc[index, self.file_name]
                            stop_frame = str(df_severity_boundary.loc[index, self.grab_index])

                            print(f'{fs} {fs_severity} - Start Split: {start_split}, Stop Split: {stop_split}, start_frame: {start_frame}, stop_frame: {stop_frame}')

        pass

    @staticmethod
    def copy_rows__index_boundary_val_df(dataframe):
        """
        :param dataframe: Dataframe
        :return: df: Dataframe
        Function searches data_frame for consecutive indexes with a difference of more than 1
        Copies to df rows where this difference occurs
        Includes first row, last row, and both rows where the difference occurs
        Returns Dataframe df with selected rows
        """
        try:
            col = list(dataframe.index.values)
        except KeyError as e:
            print(e)
            raise e
        else:
            prev_val = col[0]
            index_list = []

            for index, val in enumerate(col):

                if index == 0:
                    index_list.append(val)  # first index
                elif val != prev_val + 1:
                    index_list.append(prev_val)  # last consecutive index
                    index_list.append(val)  # new index value

                prev_val = val

            index_list.append(prev_val)  # last index value
            df = dataframe.loc[index_list]  # .reset_index(drop=True)
            return df

def main():
    fs_finder = FSFinder()
    # fs_finder.get_dataframe()
    fs_finder.load_df()
    fs_finder.print_fs_severity_events(c.SYS_RAIN, 4)


if __name__ == "__main__":
    main()


