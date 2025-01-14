# join all pickle path lists to one list. Copy output file directly to
# /net/8k3/e0fs01/irods/PLKRA-PROJECTS/ADCAM/7-Tools/ADCAM/BWD/LISTS/

import os
from file_list import FileList

lists_folder = r"F:\CARIAD\BHE\REPRO\X110\lists"
new_file_name_text = "CARIAD_X110.txt"
all_file_list = []

file_list = FileList(lists_folder, 'txt')
file_list.get_file_list()

for file_list in file_list.files:
    file_path = os.path.join(lists_folder, file_list)
    with open(file_path, 'r') as f:
        line = f.readline()
        while line:
            source_path = line.strip()
            all_file_list.append(source_path)
            line = f.readline()

txt_file = os.path.join(lists_folder, new_file_name_text)
with open(txt_file, 'w', newline='') as file:
    for line in all_file_list:
        file.write(line)
        file.write("\n")







