import os
import pickle
import numpy as np


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


df = load_pkl(r'c:\Users\wjjymc\PycharmProjects\BWD\FAILED_KPI_DFS\SOP1_A440\CP60_DATASET\SOP1_A440_CP60\BWD_SOP1_A440_BIND_DFS\one_per_split', 'BWD_SOP1_A440_partial_fp_one_per_split_FS_Low_Sun_0.pickle')
# add split name column to df
if 'split_name' not in df.columns.values:
    df['split_name'] = np.nan
    df['split_name'] = df['Path'].str.extract(r'.+(ADCAM_.+_\d{8}_\d{6}_pic_\d{4}.pickle.xz)', expand=False)
df.sort_values(by=['split_name'])
save_pkl(df, r'c:\Users\wjjymc\PycharmProjects\BWD\FAILED_KPI_DFS\SOP1_A440\CP60_DATASET\SOP1_A440_CP60\BWD_SOP1_A440_BIND_DFS\one_per_split', 'BWD_SOP1_A440_partial_fp_one_per_split_FS_Low_Sun_1.pickle')
