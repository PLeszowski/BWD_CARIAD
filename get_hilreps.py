import lzma
import pickle
import os


def load_pickle(path):
    ret = None
    if path.endswith('.pickle') or path.endswith('.jsz'):
        with open(path, 'rb') as f:
            ret = pickle.load(f)
    if path.endswith('.xz'):
        with lzma.open(path, 'rb') as file:
            ret = pickle.load(file)
    return ret


def main(path, path_to_save):
    r = []
    for dir, sub, files in os.walk(path):
        for file in files:
            if 'BWD' in file:
                print(file)
                x = load_pickle(os.path.join(dir, file))
                r += list(x['Valid_data'])
    rr = [os.path.dirname(os.path.dirname(z)) for z in r]
    rr = sorted(set(rr))
    print(len(rr))
    with open(path_to_save, 'w') as f:
        for line in rr:
            f.write(f'{line}\n')


if __name__ == '__main__':
    valid_path = "/net/8k3/e0fs01/irods/PLKRA-PROJECTS/ADCAM-VST/8-Users/pickle_verification/data/SBV6155/CP60/20230508/"
    path_to_save = "/net/8k3/e0fs01/irods/PLKRA-PROJECTS/ADCAM/7-Tools/ADCAM/BWD/LISTS/CP60_SBV6155_RBS.txt"
    main(valid_path, path_to_save)