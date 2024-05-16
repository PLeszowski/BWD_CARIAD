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
parse arguments from input

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                                History

date            author          version       Comment
11 Sep 2020     Dudek Michał    0.1.0         Initial Release

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                                ToDo
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
import argparse
import json


def arguments_parsing():
    parser = argparse.ArgumentParser()

    # INPUT/OUTPUT
    parser.add_argument('-i', '--input', help='dictionary with all required information', required=True)

    args = parser.parse_args().__dict__
    args_acceptable = args['input'].replace("'", "\"")
    args_converted_to_dict = json.loads(args_acceptable)

    return args_converted_to_dict
