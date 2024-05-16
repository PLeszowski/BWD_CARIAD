import os
import pickle
import pandas as pd


class DfEditor:

    def __init__(self):
        self.df_location = r'c:\Users\wjjymc\PycharmProjects\BWD\FAILED_KPI_DFS\SOP1_A440\MID_DATASET\BWD_SOP1_A440_BIND_DFS\BWD_SOP1_A440_BIND_DFS_PARTIAL\one_per_split\separate_fn'
        self.df_name = 'BWD_SOP1_A440_fn_one_per_split_outOfFocus.pickle'

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

    def change_col(self, col, new_val):
        df = self.load_pkl(self.df_location, self.df_name)
        df[col] = new_val
        new_df_names = self.df_name.split('.')
        new_df_name = f'{new_df_names[0]}_new.pickle'
        self.save_pkl(df, self.df_location, new_df_name)


def main():
    editor = DfEditor()
    editor.change_col('Project', 'cp60')


if __name__ == "__main__":
    main()


