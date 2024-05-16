import os
import sys
import argparse
from mainLogic import MainLogic
from libs.debugging import logger

conf_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(conf_path))

def arguments_parsing():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='input to pickles', required=True)
    parser.add_argument('-o', '--output_folder', help='output_folder', required=True)
    args = parser.parse_args()
    return vars(args)


def main():
    args = arguments_parsing()
    main_inst = MainLogic(logger, **args)
    main_inst.run()


if __name__ == "__main__":
    main()
