from config import constant as c
import json
import os
root_dir = c.KPI_GENERATOR_OUTPUT_FOLDER
ext = 'json'
bad_file_list = []

def open_json_file(json_path):
    try:
        with open(json_path, 'rb') as f:
            return json.load(f)
    except Exception as e:
        print(f'CANT OPEN {json_path}')
        print(f'Exception {e}')
        raise e

def main():
    print(f'ROOT: {root_dir}')
    for root, d_names, f_names in os.walk(root_dir, topdown=True):
        for file in f_names:
            if file.endswith(ext):
                file_path = os.path.join(root, file)
                # print(file_path)
                try:
                    open_json_file(file_path)
                except:
                    print(f'BAD FILE: {file_path}')
                    bad_file_list.append(file_path)
                    continue
    print('---------------------------------------------')
    if bad_file_list:
        for file in bad_file_list:
            print(file)
    else:
        print('ALL FILES GOOOOD')


if __name__ == "__main__":
    main()



