from libs.listAndSegregate import GetAdcamFilelist
import lzma
import pickle
import json
import os
import pandas as pd


class FilesChecking:

    def __init__(self, path_for_hil_output, path_for_json):
        self._path_for_hil_output = path_for_hil_output
        self._path_for_json = path_for_json

        self._statistic = {
            'good_pickle': [],
            'no_fs_protocol': [],
            'no_sync_protocol': [],
            'cant_open_pickle': [],
            'not_bwd_pickle': []
        }

    def main(self):
        # get grouped list of files
        validHILRuns = ['']
        #validHILRuns = ['SBV-0014', 'SBV-0015']  # if you want to accept all hil runs swap with above line
        self._file_list_from_hil = GetAdcamFilelist.get_full_dict_with_filenames(self._path_for_hil_output, validHILRuns)
        # get list of files by json.
        self._file_list_for_hil = self._get_file_list_from_json()
        self._check_files(from_hil=self._file_list_from_hil, for_hil=self._file_list_for_hil)
        print('--------------------')
        print(f'number of files to HiL: {len(self._file_list_for_hil)}')
        print('--------------------')
        self._print_statistic('Before removing duplicates', self._statistic)
        df = self._prepare_data()
        self._print_statistic('After removing duplicates', self._statistic_final)
        df.to_excel(r'D:\A370\20200507\110520FileLists\BWD\BWD_High_RWUP\Valid_invalid\BWD_not_usable_pickles.xlsx')
        self.save_json(r'D:\A370\20200507\110520FileLists\BWD\BWD_High_RWUP\Valid_invalid\good_pickle', self._statistic_final['good_pickle'])
        print('end')

    def _get_file_list_from_json(self):
        files = [f for f in os.listdir(self._path_for_json) if f.endswith('.json')]
        combained = []
        for file in files:
            combained.extend(self.read_json(os.path.join(self._path_for_json, file)))
        corrected = [f.replace(f[40:43], 'pic').replace(f[49:], 'pickle.xz') for f in combained]
        return corrected

    def _check_files(self, for_hil, from_hil):

        for measurement, l in from_hil.items():
            print(f'checking files in {measurement}')
            for pic in l['pickles_list']:
                pic_name = os.path.basename(pic)
                if pic_name in for_hil:
                    print(pic_name)
                    data = self.read_pickle(pic)
                    if data == 'EOFError':
                        self._statistic['cant_open_pickle'].append(pic_name)
                        continue
                    try:
                        temp = data['SPI']['EYEQ_TO_HOST']['Core_Failsafe_protocol']
                    except KeyError:
                        self._statistic['no_fs_protocol'].append(pic_name)
                        continue

                    try:
                        sync = {'COM_Sync_Frame_ID': data['SPI']['EYEQ_TO_HOST']['Core_Common_protocol']['COM_Sync_Frame_ID'],
                                'COM_Cam_Frame_ID': data['SPI']['EYEQ_TO_HOST']['Core_Common_protocol']['COM_Cam_Frame_ID']}
                    except KeyError:
                        self._statistic['no_sync_protocol'].append(pic_name)
                        continue

                    self._statistic['good_pickle'].append(pic_name)
                else:
                    self._statistic['not_bwd_pickle'].append(pic_name)

    def _prepare_data(self):
        data = self._statistic.copy()
        for k, v in data.items():
            data[k] = set(v)

        z1 = data['good_pickle'].intersection(data['no_fs_protocol'])
        data['no_fs_protocol'] -= z1
        z2 = data['good_pickle'].intersection(data['no_sync_protocol'])
        data['no_sync_protocol'] -= z2
        z3 = data['good_pickle'].intersection(data['cant_open_pickle'])
        data['cant_open_pickle'] -= z3

        for k, v in data.items():
            data[k] = sorted(list(v))
        self._statistic_final = data

        not_usable_dict = {}
        for n1 in data['no_fs_protocol']:
            not_usable_dict[n1] = 'no_fs_protocol'
        for n2 in data['no_sync_protocol']:
            not_usable_dict[n2] = 'no_sync_protocol'
        for n3 in data['cant_open_pickle']:
            not_usable_dict[n3] = 'cant_open_pickle'

        df_not_usable = pd.DataFrame(data=not_usable_dict, index=[0])
        df_not_usable = df_not_usable.T
        return df_not_usable

    # HELPERS
    @staticmethod
    def _print_statistic(msg, data):
        print(msg)
        for k, v in data.items():
            print(k, len(v))
        print('--------------------')

    @staticmethod
    def read_pickle(path):
        try:
            if path.endswith('.xz'):
                with lzma.open(path, 'rb') as f:
                    return pickle.load(f)
            with open(path, 'rb') as f:
                return pickle.load(f)
        except EOFError:
            return 'EOFError'

    @staticmethod
    def read_json(path):
        with open(path) as f:
            return json.load(f)

    @staticmethod
    def save_json(name, data):
        with open(f'{name}.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


def main():
    path_to_hil_files = r'D:\A370\20200507\110520FileLists\BWD\BWD_High_RWUP\added_pickles'
    path_to_json = r'C:\Users\hj5vm8\Desktop\Repo\vtv.snf\bwdKPI\FileListForHiL\BWD_A370'
    inst = FilesChecking(path_to_hil_files, path_to_json)
    inst.main()


if __name__ == '__main__':
    main()
