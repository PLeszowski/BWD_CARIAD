# -*- coding: utf-8 -*-
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
Script for decoding MobileEye Lablling

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                                History

date            author          version       Comment

22 Feb 2019     Szymon Maj      0.1.0         Initial Release
10 Sep 2019     Jan Fyda        0.2.0         Exception handling and verification mode added


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                                ToDo

- Check if it is working for all labelling files
- Support mapping (18-09-27_AB-ME_1400_20180927_173000_0030.irtk)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
import re
import os
import pickle


class LabellingExtractor:
    """
    call decode with filepath to retriece decoded dictionary
    """
    _core_re_ex = r'[a-z0-9-_.,+/\ ]'
    _line_re_ex = r'^(?P<indexMain>[0-9_]+)( )(?P<headerMain>{})( )(?P<headerSec>{})(?P<values>{}+)$'
    _format_re_ex = r'^(?P<format>format:)(?P<headers>{}+)$'.format(_core_re_ex)

    def __init__(self, file_path='', print_not_matched=True, verify_correctness=True, print_result=False):
        self.print_not_matched = print_not_matched
        self.verify_correctness = verify_correctness
        self._format_re_ex_comp = re.compile(self._format_re_ex, re.IGNORECASE)
        self.file_path = file_path
        self.print_result = print_result
        self._formats = [
            {'header_main': 'MetaData', 'header_secondary': 'cameraInstance', 'values': ['info1', 'info2']}]
        self._return_dict = {}
        self._file_lines_sum = 0
        self._decoded_sum = 0
        self._not_matched_lines = 0
        self._values_mapping = []

    def get_formats(self):
        formatFound = False
        with open(self.file_path, 'r') as file:
            line = file.readline()
            while line:
                decode_line = self._format_re_ex_comp.search(line)
                if decode_line is not None:
                    formatFound = True
                if formatFound and decode_line is None:
                    break
                if formatFound:
                    headers = [ele for ele in decode_line.group('headers').split(' ') if ele]
                    if len(headers) < 3:
                        raise IndexError("Invalid encoding for format header")
                    self._formats.append(
                        {'header_main': headers[0], 'header_secondary': headers[1], 'values': headers[2:]})
                    self._decoded_sum += 1
                line = file.readline()
        self._reformat_formats()

    def _reformat_formats(self):
        for format_dict in self._formats:
            reg_ex_str = self._line_re_ex.format(format_dict['header_main'], format_dict['header_secondary'],
                                                 self._core_re_ex)
            format_dict['reg_ex'] = re.compile(reg_ex_str, re.IGNORECASE)

    def get_values(self):
        with open(self.file_path, 'r') as file:
            line = file.readline()
            while line:
                if line.startswith('_'):
                    line = file.readline()
                    continue
                if line.strip():
                    self._file_lines_sum += 1
                match_found = False
                for format_dict in self._formats:
                    decode_line = format_dict['reg_ex'].search(line)
                    if decode_line is None:
                        continue
                    if format_dict['header_main'] not in self._return_dict.keys():
                        self._return_dict[format_dict['header_main']] = {}
                    if format_dict['header_secondary'] not in self._return_dict[format_dict['header_main']].keys() and \
                            format_dict['header_secondary'] != '-':
                        self._return_dict[format_dict['header_main']][format_dict['header_secondary']] = {}
                    if format_dict['header_secondary'] == '-':
                        working_dict = self._return_dict[format_dict['header_main']]
                    else:
                        working_dict = self._return_dict[format_dict['header_main']][format_dict['header_secondary']]
                    # 'indexMain'
                    if 'indexMain' not in working_dict.keys():
                        working_dict['indexMain'] = []
                    working_dict['indexMain'].append(decode_line.group('indexMain'))
                    # values
                    values = [ele for ele in decode_line.group('values').split(' ') if ele]
                    if len(values) != len(format_dict['values']):
                        raise IndexError(f"Number of columns for index {decode_line.group('indexMain')} does not match format")
                    for idx, header in enumerate(format_dict['values']):
                        if header not in working_dict.keys():
                            working_dict[header] = []
                        working_dict[header].append(values[idx])
                    self._decoded_sum += 1
                    match_found = True
                    break
                if not match_found and not line.startswith('format') and not line.strip().startswith('_') and not line.startswith(r'/mobileye'):
                    self._not_matched_lines += 1
                    if self.print_not_matched:
                        print('Cant\'t match line: {}'.format(line))
                line = file.readline()

    def get_values_mapping(self):
        with open(self.file_path, 'r') as file:
            line = file.readline()
            while line:
                if line.startswith('_'):
                    self._values_mapping.append(line)
                    line = file.readline()
                else:
                    line = file.readline()

    def decode(self, filepath=''):
        self._file_lines_sum = 0
        self._decoded_sum = 0
        if filepath:
            self.file_path = filepath
        if not self.file_path or not os.path.isfile(self.file_path):
            raise FileNotFoundError('No file: {}'.format(self.file_path))
        self.get_formats()
        self.get_values()
        self.get_values_mapping()
        if self._not_matched_lines >= 1:
            self.overall_result = 2
        else:
            self.overall_result = 0
        if self._decoded_sum + 1 != self._file_lines_sum:
            if self.print_result:
                print('Some lines not decoded, check')
            if self.verify_correctness:
                return self._return_dict, 1
        else:
            if self.print_result:
                print('OK')
            if self.verify_correctness:
                return self._return_dict, self.overall_result, self._values_mapping
        return self._return_dict  # This return after if/else statement, doing nothing


if __name__ == '__main__':
    def save_df(data, column_names, DIRECTORY, file):
        df = DataFrame(data)
        df = df.transpose()
        df.columns = column_names

        out = file.split('.')[0]

        if not os.path.exists(os.path.join(DIRECTORY, out)):
            os.mkdir(os.path.join(DIRECTORY, out))

        # df.to_excel(os.path.join(DIRECTORY, out, f"{out}_{key}_{arg}.xlsx"), index=False)


    from pandas import DataFrame

    DIRECTORY = r"C:\Users\zj2j7c\Desktop\NEW_ITRK"
    for file in [ele for ele in os.listdir(DIRECTORY) if os.path.isfile(os.path.join(DIRECTORY, ele))]:
        print(file)
        decoded = LabellingExtractor(print_not_matched=True).decode(os.path.join(DIRECTORY, file))
        pickle.dump(decoded, open('{}.pickle'.format(file), 'wb'))

        # for key in decoded.keys():
        #     for arg in decoded[key].keys():
        #         if isinstance(decoded[key][arg], list):
        #             data = [decoded[key][x] for x in decoded[key].keys()]
        #             column_names = [x for x in decoded[key].keys()]
        #             save_df(data, column_names, DIRECTORY, file)
        #             break
        #         else:
        #             data = [decoded[key][arg][x] for x in decoded[key][arg].keys()]
        #             column_names = [x for x in decoded[key][arg].keys()]
        #             save_df(data, column_names, DIRECTORY, file)

        # a = 1