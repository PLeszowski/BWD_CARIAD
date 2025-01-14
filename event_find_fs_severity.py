"""
Script finds eventy with given severity in partial results
"""
import serializer
import config.constant as c
from file_list import FileList


class EventFindFsSeverity:

    def __init__(self):

        self.failsafe_tp = c.PARTIALS_NAMES_LAB[c.LAB_LOWSUN]
        self.failsafe_fp = c.SYS_FADING_BY_SUN
        self.severity_tp = "25"
        self.severity_fp = 5
        self.path_to_partial_results = r'f:\CARIAD\BHE\REPRO\X071\TR\raw_16\spi_exact_up_down'
        self.path_to_output = r'f:\CARIAD\BHE\REPRO\X071\TR\raw_16\spi_backup\event_finder'
        self.output_file_tp = f'{self.failsafe_tp}_{self.severity_tp}.json'
        self.ext = '.json'
        self.json_file_list = FileList(self.path_to_partial_results, 'json')
        self.json_file_list.get_file_list()
        self.file_list = self.json_file_list.files
        print()

    def find_tp(self):
        if self.file_list:
            for file in self.file_list:
                hilrep = serializer.load_json(self.path_to_partial_results, file)
                if hilrep:
                    for main_dict in hilrep:
                        if main_dict:
                            if "LabeledFs" in main_dict.keys():
                                for event_dict in main_dict["LabeledFs"]:
                                    # severity = int(self.severity_tp)
                                    if event_dict["FsName"] == self.failsafe_tp and event_dict["Severity"] == self.severity_tp and not event_dict["IsRecognition"]:
                                        print(f'Start split: {event_dict["LogNameEventStart"]}, stop split: {event_dict["LogNameEventStop"]}')

    def find_fp(self):
        if self.file_list:
            for file in self.file_list:
                hilrep = serializer.load_json(self.path_to_partial_results, file)
                if hilrep:
                    for main_dict in hilrep:
                        if main_dict:
                            if "FalsePositive" in main_dict.keys():
                                for event_dict in main_dict["FalsePositive"]:
                                    if event_dict["FsName"] == self.failsafe_fp and event_dict["Severity"] == self.severity_fp:
                                        print(f'Start split: {event_dict["LogNameEventStart"]}, stop split: {event_dict["LogNameEventStop"]}')

def main():
    fs_finder = EventFindFsSeverity()
    fs_finder.find_fp()

if __name__ == "__main__":
    main()



