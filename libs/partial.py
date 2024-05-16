import numpy as np
from config.constant import PARTIALS_NAMES_LAB
from config.constant import PARTIALS_NAMES_SYS


lab_mapping = {'blockage': {2: '25', 4: '75', 5: '99'},
               'blurImage': {2: '25', 4: '75', 5: '99'},
               'fog': {2: '25', 4: '75', 5: '99'},
               'frozenWindshield': {2: '25', 4: '75', 5: '99'},
               'fullBlockage': {2: '25', 4: '75', 5: '99'},
               'lowSun': {2: '25', 4: '75', 5: '99'},
               'partialBlockage': {2: '25', 4: '75', 5: '99'},
               'snowfall': {2: '25', 4: '75', 5: '99'},
               'rain': {2: '25', 4: '75', 5: '99'},
               'splashes': {2: '25', 4: '75', 5: '99'},
               'sunRay': {2: '25', 4: '75', 5: '99'},
               'freeview': {5: '99'}
               }
sys_mapping = {2: '25', 4: '75', 5: '99'}


def create_partial(_sys, _lab, _filt, frames, distance):

    def without_keys(d, keys):
        return {x: d[x] for x in d if x not in keys}

    k = ['LogNameStart', 'LogNameEnd']
    labeled_fs = {}
    false_positive = {}
    partials = {}
    list_of_tp = []
    list_of_fp = []
    if _filt is not None:
        partials['LogInfo'] = without_keys(_filt, k)
    partials['TotalNumberOfFrames'] = int(frames)
    # TODO measure distance
    partials['DistanceDriven'] = distance
    partials['MTBF'] = None
    # iterating over every labeled FS to search for True Positives
    to_short = 0
    for lab_keys, lab_values in _lab.items():
        try:
            to_short += lab_values.description.count('Event to short')
        except:
            pass
        # Finding where was recognition other than nan (0 or 1)
        idx = np.where(~np.isnan(_lab[lab_keys].recognition))[0]
        if idx.size != 0:
            # Creating partial table for every detected FS
            for i in idx:
                labeled_fs['LogNameEventStart'] = lab_values.start_pic[i]
                labeled_fs['LogNameEventStop'] = lab_values.stop_pic[i]
                labeled_fs['FsName'] = PARTIALS_NAMES_LAB[lab_values.name]
                labeled_fs['Severity'] = lab_mapping[lab_values.name][lab_values.severity[i]]
                labeled_fs['IsRecognition'] = bool(lab_values.recognition[i])
                labeled_fs['RecognitionTime'] = lab_values.recognition_time[i]
                labeled_fs['FramesDetected'] = int(lab_values.frames_detected[i])
                labeled_fs['FramesLabeled'] = int(lab_values.frames_labeled[i])
                labeled_fs['ErrorType'] = None
                labeled_fs['ErrorDescription'] = lab_values.description[i]
                list_of_tp.append(labeled_fs.copy())
    partials['To_short_events'] = to_short
    # iterating over every system FS to search for False Positives
    # for sys_keys, sys_values in _sys.items():
    #     for severity_name, severity_value in sys_values.fpr.items():
    #         if severity_value[0] != 0:
    #             key_name = f"FP_frames_{sys_values.name}_{sys_mapping[severity_name]}"
    #             partials[key_name] = int(severity_value[0])

    for sys_keys, sys_values in _sys.items():
        for severity, frames in sys_values.fpr.items():
            if frames[0] != 0:
                # false_positive['LogNameEventStart'] = sys_values.start_pic[i]
                # false_positive['LogNameEventStop'] = sys_values.stop_pic[i]
                false_positive['FsName'] = PARTIALS_NAMES_SYS[sys_values.name]
                false_positive['Severity'] = sys_mapping[severity]
                false_positive['NumberOfFrames'] = int(frames[0])
                false_positive['Labeled'] = frames[2]
                list_of_fp.append(false_positive.copy())

    partials['LabeledFs'] = list_of_tp
    partials['FalsePositive'] = list_of_fp
    return partials
