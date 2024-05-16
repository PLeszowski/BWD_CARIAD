"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                    Copyright 2019 All Rights Reserved.
            APTIV ADVANCED SAFETY & USER EXPERIENCE PROPRIETARY

           THIS SOFTWARE IS ADVANCED SAFETY & USER EXPERIENCE PROPRIETARY.
            IT MUST NOT BE DISTRIBUTED TO ANYBODY OUTSIDE OF APTIV.

        THIS SOFTWARE INCLUDES NO WARRANTIES, EXPRESS OR IMPLIED, WHETHER
        ORAL, OR WRITTEN WITH RESPECT TO THE SOFTWARE OR OTHER MATERIAL,
            INCLUDING BUT NOT LIMITED TO ANY IMPLIED WARRANTIES OF
       MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE, OR ARISING FROM
           A COURSE OF PERFORMANCE OR DEALING, OR FROM USAGE OR TRADE, OR OF
                   NON-INFRINGEMENT OF ANY PATENTS OF THIRD PARTIES.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                            Author: Szymon Maj
Find all pickle, jsz an segregate them into series and etc.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                                History

date            author          version       Comment

04 Apr 2019     Szymon Maj      0.1.0         Initial Release
30 Jan 2020     Michal Dudek    0.2.0         Adjusted to BWD

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                                To Do

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""

import os
import re
import numpy as np


class GetAdcamFilelist:

    re_filename = r'^(?P<project>adcam|hpad|conti{1})(_{1})(?P<comment>[a-z0-9]*)(_?)(?P<vin>[a-z0-9]{17})(_{1})(?P<date>[0-9]{8})(_{1})(?P<time>[0-9]{6})(_{1})(?P<extension>oth|dlt|eth|bus|tap|deb|tcd|ref|v01|v02|v03|v04|v05|v06|v07|v08|pic){0,1}(_?)(?P<number>[0-9]+)'

    @classmethod
    def get_full_dict_with_filenames(cls, path, validHILRuns, logger=None, file_ends=('.pickle', '.xz'), splits_to_skip=[], skip_last_split=False) -> dict:
        """
        List all files on self.search path with real size in bytes information and assigned to logs

        :return: dict with logname as key and info of each file
        """
        if not os.path.exists(path):
            raise FileExistsError("File/Folder: {} doesn't exist".format(path))
        full_dict = {}
        return_dict = {}
        # list all files in folder
        for path, subdirs, files in os.walk(path):
            for name in files:
                # get formatted name
                formatted_file_name = cls._get_formatted_filename(name, logger)
                # exclude bad filename format
                if formatted_file_name is None:
                    continue
                # get full path to file
                full_file_path = os.path.join(path, name)
                if os.path.splitext(full_file_path.lower().strip())[1] not in file_ends:
                    continue
                if formatted_file_name not in full_dict.keys():
                    full_dict[formatted_file_name] = []
                # append informations
                if any(validRun in full_file_path for validRun in validHILRuns):
                    full_dict[formatted_file_name].append(full_file_path)
        # split for series
        for key in full_dict.keys():
            series_name = cls._get_series_name(key)
            if series_name not in return_dict.keys():
                return_dict[series_name] = {
                    'pickles': {}, 'pickles_list': [], 'split_numbers': []
                }
            cls._distribute_single_files(key, full_dict[key], return_dict[series_name], splits_to_skip)
        if skip_last_split:
            for key in return_dict.keys():
                cls._delete_last_split(return_dict[key])
        return cls._segragate_splits(return_dict)

    @classmethod
    def _get_series_name(cls, name):
        regexp_compiled = re.compile(cls.re_filename, re.IGNORECASE)
        re_match = regexp_compiled.search(name)
        if re_match is None:
            return None
        ret_list = [re_match.group('project'), re_match.group('comment'), re_match.group('vin'), re_match.group('date'), re_match.group('time')]
        return '_'.join([part for part in ret_list if part])

    @classmethod
    def _distribute_single_files(cls, key, in_dict, out_series, splits_to_skip):
        regexp_compiled = re.compile(cls.re_filename, re.IGNORECASE)
        re_match = regexp_compiled.search(key)
        if re_match is None:
            return None
        split_num = int(re_match.group('number'))
        if split_num in splits_to_skip:
            return None
        for full_path in in_dict:
            if full_path.endswith('.pickle') or full_path.endswith('.pickle.xz'):
                if full_path not in out_series['pickles_list']:
                    if key not in out_series['pickles'].keys():
                        out_series['pickles'][key] = []
                    out_series['pickles'][key].append(full_path)
                    out_series['pickles_list'].append(full_path)
                    out_series['split_numbers'].append(split_num)


    @classmethod
    def _segragate_splits(cls, return_dict):
        final_return = {}
        regexp_compiled = re.compile(cls.re_filename, re.IGNORECASE)
        for key in return_dict.keys():
            current_dict = return_dict[key]
            indexes = np.where(np.diff(np.array(current_dict['split_numbers'])) > 1)[0]
            if len(indexes) > 0:
                indexes = np.insert(indexes, 0, -1)
                indexes = np.append(indexes, len(current_dict['split_numbers']) - 1)
                for idx in range(len(indexes)-1):
                    start = current_dict['split_numbers'][indexes[idx] + 1]
                    stop = current_dict['split_numbers'][indexes[idx + 1]]
                    main_key = f"{key}_{start:04}_{stop:04}"
                    if main_key not in final_return.keys():
                        final_return[main_key] = {}
                    selected_dict = final_return[main_key]
                    selected_dict['split_numbers'] = current_dict['split_numbers'][indexes[idx] + 1:indexes[idx + 1] + 1]
                    #
                    temp = []
                    for file in current_dict['pickles_list']:
                        re_match = regexp_compiled.search(os.path.basename(file))
                        if re_match is None:
                            return None
                        if int(re_match.group('number')) >= start and int(re_match.group('number')) <= stop:
                            temp.append(file)
                    selected_dict['pickles_list'] = temp
                    #
                    temp = {}
                    for file in current_dict['pickles'].keys():
                        re_match = regexp_compiled.search(os.path.basename(file))
                        if re_match is None:
                            return None
                        if int(re_match.group('number')) >= start and int(re_match.group('number')) <= stop:
                            temp[file] = current_dict['pickles'][file]
                    selected_dict['pickles'] = temp

            else:
                final_return[f"{key}_{current_dict['split_numbers'][0]:04}_{current_dict['split_numbers'][-1]:04}"] = return_dict[key]
        return final_return

    @classmethod
    def _delete_last_split(cls, series_dict):
        regexp_compiled = re.compile(cls.re_filename, re.IGNORECASE)
        if series_dict['max_split'] < 1:
            return
        split_to_skip = series_dict['max_split']
        series_dict['max_split'] -= 1
        #
        idxs_to_pop = []
        for idx, file in enumerate(series_dict['jszs_list']):
            re_match = regexp_compiled.search(os.path.basename(file))
            if re_match is None:
                return None
            if int(re_match.group('number')) == split_to_skip:
                idxs_to_pop.append(idx)
        for idx in reversed(sorted(idxs_to_pop)):
            series_dict['jszs_list'].pop(idx)
        #
        idxs_to_pop = []
        for idx, file in enumerate(series_dict['pickles_list']):
            re_match = regexp_compiled.search(os.path.basename(file))
            if re_match is None:
                return None
            if int(re_match.group('number')) == split_to_skip:
                idxs_to_pop.append(idx)
        for idx in reversed(sorted(idxs_to_pop)):
            series_dict['pickles_list'].pop(idx)
        #
        keys_to_pop = []
        for file in series_dict['pickles'].keys():
            re_match = regexp_compiled.search(os.path.basename(file))
            if re_match is None:
                return None
            if int(re_match.group('number')) == split_to_skip:
                keys_to_pop.append(file)
        for key1 in reversed(sorted(keys_to_pop)):
            del series_dict['pickles'][key1]
        #
        keys_to_pop = []
        for file in series_dict['jszs'].keys():
            re_match = regexp_compiled.search(os.path.basename(file))
            if re_match is None:
                return None
            if int(re_match.group('number')) == split_to_skip:
                keys_to_pop.append(file)
        for key1 in reversed(sorted(keys_to_pop)):
            del series_dict['jszs'][key1]

    #HELPERS
    @classmethod
    def _get_formatted_filename(cls, filename: str, logger=None) -> (str, None):
        """
        Return formatted filename

        :param filename: input filename
        :return: formatted filename if filename is correct, None if filename is incorrect
        """

        # path name
        filename = os.path.splitext(os.path.basename(filename))[0]
        # validation
        splitted_filename = cls._validate_and_split(filename)
        if splitted_filename is None:
            #print( "Skipped file: {}".format(filename))
            return
        # get formatted Path
        return '_'.join(splitted_filename)

    @classmethod
    def _validate_and_split(cls, filename: str) -> (tuple, None):
        """
        Check if splitted filename is correct adcam/hPad name

        :param splitted_filename: filename splitted by '_'
        :return: True if filename is correct, False if incorrect

        >>> cls._validate_and_split("ADCAM_RWUPTSR_WBANA31020B020501_20180823_220816_v01_0000")
        True
        >>> cls._validate_and_split("ADCAM_RWUPTSR_WBANA31020B0220501_20180823_220816_v01_0000")
        False
        >>> cls._validate_and_split("ADCAM_RWUPTSR_WBANA31020B0220501_2018082a_220816_v01_0000")
        False
        >>> cls._validate_and_split("ADCAM_RWUPTSR_WBANA31020B0220501_20180823_22081a_v01_0000")
        False
        >>> cls._validate_and_split("ADCAM_RWUPTSR_WSANA32020B020501_20180823_220816_0905")
        True
        >>> cls._validate_and_split("ADCAM_RWUPTSR_WSANA32020B020501_20180823_220816")
        False
        >>> cls._validate_and_split("ADCAM_RWUPTSR_WBANA31020B020501_201808232_220816_v01_0000")
        False
        >>> cls._validate_and_split("ADCAM_RWUPTSR_WBANA31020B020501_20180823_2208162_v01_0000")
        False
        """
        regexp_compiled = re.compile(cls.re_filename, re.IGNORECASE)
        re_match = regexp_compiled.search(filename)
        if re_match is None:
            return None
        ret_list = [re_match.group('project'), re_match.group('comment'), re_match.group('vin'), re_match.group('date'), re_match.group('time'), re_match.group('number')]
        return [part for part in ret_list if part]
