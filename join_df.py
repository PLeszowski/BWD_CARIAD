import os
import pickle
import pandas as pd


class DfJoiner:

    def __init__(self):
        self.df_location = r'c:\Users\wjjymc\PycharmProjects\BWD\FAILED_KPI_DFS\BWD_SOP8_A360_NEW_LOGIC_DAY_NIGHT_INVALID_LABEL_FIX_08\MID_DATASET\BWD_SOP8_A-360_v1_BIND_DFS'
        self.df_destination = r'c:\Users\wjjymc\PycharmProjects\BWD\FAILED_KPI_DFS\BWD_SOP8_A360_NEW_LOGIC_DAY_NIGHT_INVALID_LABEL_FIX_08\MID_DATASET\BWD_SOP8_A-360_v1_BIND_DFS\one'
        self.ext = '.pickle'
        self.file_list = []

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

    def get_df_files(self):
        try:
            allfiles = os.listdir(self.df_location)
        except (FileNotFoundError, PermissionError, NotADirectoryError) as e:
            print(f'DfBinder: ERROR: Cant open {self.df_location}')
            print(e)
            raise e
        else:
            if allfiles:
                for file in allfiles:
                    if file.endswith(self.ext):
                        self.file_list.append(file)
            else:
                print(f'DfBinder: No pickles in {self.df_location}')
                print(FileNotFoundError)
                raise FileNotFoundError

    def bind_to_one_dfs(self):
        pickle_name = 'all_in_one.pickle'
        df_list = []
        if self.file_list:
            num_of_files = len(self.file_list)
            for i, file in enumerate(self.file_list):
                if i == 0:
                    name = file[0:-11]
                    pickle_name = name + pickle_name
                    print(pickle_name)
                print(f'DfJoiner: INFO: Foining {i + 1}/{num_of_files}: {file}')
                df = self.load_pkl(self.df_location, file)
                if len(df) > 0:
                    df_list.append(df)
            try:
                # Concatenate df_list list one dataframe
                master_df = pd.concat(df_list, ignore_index=True)
                self.save_pkl(master_df, self.df_destination, pickle_name)
                print(f'Saved {pickle_name}')
            except ValueError as e:
                print('DfBinder: bind_dfs: Cant concat master_df_list')
                print(e)
                raise e


def main():
    joiner = DfJoiner()
    joiner.get_df_files()
    joiner.bind_to_one_dfs()


if __name__ == "__main__":
    main()