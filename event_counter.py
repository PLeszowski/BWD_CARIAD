"""
Module counts the amount of PICKLES used in test loop
Saves partial results for each measurement
Saves one unique sorted list when run outside
Patryk Leszowski
APTIV
BWD
"""
import os
import json
import re
import config.constant as c
import serializer


class EventCounter:

    def __init__(self, file_dict, dt_str):
        self.file_dict = file_dict
        self.pickle_list = []
        self.ext = 'json'
        self.function = 'BWD'
        self.sop = c.SOP
        self.a_step = c.A_STEP
        self.dt_str = dt_str
        self.new_folder = f'{self.function}_{self.sop}_{self.a_step}_FILE_LISTS'
        self.new_path = os.path.join(c.PATH_FAILED_KPI_DFS, self.new_folder)

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
        except(FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
            print(f'failed to save json: {file}')
            print(e)
            pass

    def get_hilrep(self):
        key = list(self.file_dict.keys())[0]
        search_line = self.file_dict[key]
        # search for HILREPP-7digits, force the engine to try matching at the furthest position
        search = re.search(r'(?s:.*).+\W(\d{4}_\d{4})\W.+', search_line)  # ex. HILREPP-2013288
        if search:
            return search.group(1)
        else:
            return None

    def save_results(self):
        try:
            if not os.path.isdir(self.new_path):
                os.makedirs(self.new_path, exist_ok=True)
            hilrep = self.get_hilrep()
            if hilrep:
                unique_name = hilrep + "_" + self.dt_str
            else:
                unique_name = self.dt_str
            file_name = f'{self.function}_{self.sop}_{self.a_step}_{unique_name}.{self.ext}'
            self.save_json(self.pickle_list, self.new_path, file_name)
        except(FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
            print(f'Cant save: {e}')
            pass

    def get_pickle_list(self, df):
        file_list = df['File_Name'].values.tolist()
        self.pickle_list = list(set(file_list))
        self.save_results()

class FileListConcat(EventCounter):

    def __init__(self):
        self.files = []
        self.file_list = []
        super().__init__(None, None)

    @staticmethod
    def open_json_file(path, file):
        try:
            with open(os.path.join(path, file), 'rb') as f:
                return json.load(f)
        except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
            print(f'LabSigDfBinder: ERROR: Cant open {file}')
            print(e)

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

    def concat_lists(self):
        all_file_list = []
        if self.files:
            for file in self.files:
                print(file)
                file_list = self.open_json_file(self.new_path, file)
                if file_list:
                    all_file_list += file_list
            for file in all_file_list:
                if isinstance(file, str):
                    self.file_list.append(file)
            self.file_list = list(set(self.file_list))
            self.file_list.sort()
            self.save_json(self.file_list, self.new_path, 'all_split_list.json')

def main():
    nr_df_binder = FileListConcat()
    nr_df_binder.get_df_files()
    nr_df_binder.concat_lists()


if __name__ == "__main__":
    main()
