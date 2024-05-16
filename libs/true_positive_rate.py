import config.constant as c
import numpy as np
from libs.loggingFuncs import print_and_log
from libs.debugging import wrapping


# import generate_excel as ge

def prep(fs_sys_objects, fs_lab_objects, logger):

    failsafe_to_check = {}
    what_to_check = c.TO_CHECK_FOR_TRUE_POSITIVES

    # find every labeled failsafe
    for k, v in fs_lab_objects.items():
        if k in what_to_check:
            to_check = v.check_fs()
            if to_check is not None:
                failsafe_to_check[k] = to_check
                print_and_log(logger, f"......Labeled events  founded for: {k}")
            else:
                print_and_log(logger, f"......No labeled events for: {k}")
        else:
            print_and_log(logger, f"......SKPIPPING: {k}")
    for key, value in failsafe_to_check.items():
        print_and_log(logger, f"........{key} - {value}")
        sys_name = fs_lab_objects[key].get_sys_name()
        if key == 'blurImage':
            kk = ['FS_Blur_Image_0', 'FS_Splashes_0', 'FS_Fog', 'FS_Low_Sun_0', 'FS_Rain']
        if key == 'fog':
            kk = ['FS_Blur_Image_0', 'FS_Fog']
        if key == 'frozenWindshield':
            kk = ['FS_Blur_Image_0', 'FS_Fog', 'FS_Frozen_Windshield', 'FS_Full_Blockage_0', 'FS_Partial_Blockage_0']
        if key == 'fullBlockage':
            kk = ['FS_Frozen_Windshield', 'FS_Full_Blockage_0', 'FS_Partial_Blockage_0']
        if key == 'lowSun':
            kk = ['FS_Low_Sun_0', 'FS_Sun_Ray_0']
        if key == 'partialBlockage':
            kk = ['FS_Frozen_Windshield', 'FS_Full_Blockage_0', 'FS_Partial_Blockage_0']
        if key == 'snowfall':
            kk = ['FS_Blur_Image_0', 'FS_Splashes_0', 'FS_Rain']
        if key == 'rain':
            kk = ['FS_Blur_Image_0', 'FS_Splashes_0', 'FS_Rain']
        if key == 'splashes':
            kk = ['FS_Blur_Image_0', 'FS_Splashes_0', 'FS_Rain']
        if key == 'sunRay':
            kk = ['FS_Low_Sun_0', 'FS_Sun_Ray_0']
        if key == 'freeview':
            kk = ['FS_Free_Sight_0']
        filtered_d = dict((k, fs_sys_objects[k]) for k in kk if k in fs_sys_objects)
        for severit in value:
            get_info(fs_lab_objects[key], filtered_d, severit, logger=logger, sys_name=sys_name)


def slice_and_dice(cake, knife, fs_lab_obj):
    for c in cake:
        sliced = False
        for k in knife:
            if c[0] < k < c[1]:
                fs_lab_obj.insert(k)
                sliced = True
                break
    return False


def get_info(fs_lab_obj, fs_sys_objs, severity, logger, sys_name):
    # get system severity for label severity
    repeat = True
    flag = True
    while repeat:
        s = False
        if fs_lab_obj.name == 'freeview':
            s = fs_lab_obj.get_sys_severity(severity, freeview=True)
        # else:
        #     s = fs_lab_obj.get_sys_severity(severity)
        # get start - stop for labeled event
        label_starts, label_stops, idx_lab = fs_lab_obj.get_timers_for_specific_severity(lvl=severity)
        # get start - stop for system
        if s:
            fs_sys_obj = fs_sys_objs['FS_Free_Sight_0']
            system_starts, system_stops, idx_sys = fs_sys_obj.get_timers_for_specific_severity(lvl=s)
        else:
            system_starts = []
            system_stops = []
            for fs_sys_obj in fs_sys_objs.values():
                for s in [2, 4, 5]:
                    system_start, system_stop, idx_sys = fs_sys_obj.get_timers_for_specific_severity(lvl=s)
                    system_starts.extend(list(system_start))
                    system_stops.extend(list(system_stop))
            system_starts = np.asarray(sorted(system_starts))
            system_stops = np.asarray(sorted(system_stops))
        # get max rec time
        fs_sys_obj = fs_sys_objs[sys_name]
        max_rec_time = fs_sys_obj.max_recognition_time
        # get first and last frames available from system
        first, last = fs_sys_obj.get_first_last()
        # slice
        if flag:
            if not system_stops.size == 0:
                flag = slice_and_dice(list(zip(label_starts, label_stops)), system_stops, fs_lab_obj)
            else:
                repeat = False
        else:
            repeat = False
    # calculate recognitions
    recognitions = positive_recognition(system_starts=system_starts, system_stops=system_stops,
                                        label_starts=label_starts, label_stops=label_stops,
                                        max_rec_time=max_rec_time,
                                        first=first, last=last,
                                        logger=logger)
    if recognitions is not None:
        fs_lab_obj.setup_recognition(idx_lab, recognitions)


@wrapping(prefix='......', kind='not_class')
def positive_recognition(system_starts, system_stops, label_starts, label_stops, max_rec_time, first, last, logger):

    frequency = c.FREQUENCY
    labeled_frames = []
    detected_frames = []
    is_recognition = []
    recognition_time = []
    description = []
    if len(label_starts) != len(label_stops):
        return print_and_log(logger, f'........length of label_start = {len(label_starts)} != length of label_stop = {len(label_stops)}')
    if len(system_starts) != len(system_stops):
        return print_and_log(logger, f'........length of system_start = {len(system_starts)} != length of system_stop = {len(system_stops)}')
    if len(label_starts) == 0:
        return print_and_log(logger, f'........No label data provided')

    for lab_start, lab_stop in zip(label_starts, label_stops):
        labeled_frames.append(lab_stop - lab_start)
        duration = (lab_stop - lab_start) / frequency
        if duration < max_rec_time:     # checking event duration
            print_and_log(logger, "........Duration is too short")
            detected_frames.append(None)
            is_recognition.append(None)
            recognition_time.append(None)
            description.append("Event to short")
            continue
        # if first > lab_start or last < lab_stop:    # checking if there we have data from system
        #     print_and_log(logger, "........No data from system")
        #     detected_frames.append(None)
        #     is_recognition.append(None)
        #     recognition_time.append(None)
        #     description.append("No data from system")
        #     continue
        if len(system_starts) == 0:     # Checking if system detect this FS
            is_recognition.append(False)
            detected_frames.append(0)
            recognition_time.append(np.nan)
            description.append('No Recognition')
            continue
        for sys_start, sys_stop in zip(system_starts, system_stops):
            if sys_start > lab_stop:  # if interval from system starts after interval from label ends
                is_recognition.append(False)  # adding no recognition
                detected_frames.append(0)
                recognition_time.append(np.nan)  # recognition time = nan
                description.append('No Recognition')
                break  # if 1st start system was to late, next one will be to late too so we break system looping
            elif sys_stop <= lab_start:  # if end of interval from system is before start for labeling
                if sys_stop == system_stops[-1]:  # have to check if this is last interval if YES
                    is_recognition.append(False)  # no recognition
                    detected_frames.append(0)
                    recognition_time.append(np.nan)
                    description.append('No Recognition')
                continue  # if no we check next interval from system
            else:  # start from system is before label ends, stop from system is after label starts, we good
                rec_time = (sys_start - lab_start) / frequency
                recognition_time.append(rec_time)  # there is recognition time
                # Should never be case
                if sys_stop < lab_stop:  # if stops to early
                    is_recognition.append(True)  # no recognition (miss named, recognition was but to short)
                    detected_frames.append(sys_stop - max(sys_start, lab_start))
                    description.append('end To Early')
                    break
                if rec_time > max_rec_time:  # if recognition out of time
                    is_recognition.append(True)  # no recognition
                    detected_frames.append(min(sys_stop, lab_stop) - max(lab_start, sys_start))
                    description.append('Start to Late')
                    break  # due to intersection_of_sets, there is no way next interval can be good
                else:
                    is_recognition.append(True)  # finally we have recognition in time, and long enough
                    detected_frames.append(min(sys_stop, lab_stop) - max(lab_start, sys_start))
                    description.append('OK')
                    break
    return {'is_recognition': is_recognition,
            'recognition_time': recognition_time,
            'labeled_frames': labeled_frames,
            'detected_frames': detected_frames,
            'description': description}


@wrapping(prefix='......', kind='not_class')
def true_positive(fs_lab_obj):
    to_excel = {3: [np.nan, np.nan, np.nan, np.nan],
                '50': [np.nan, np.nan, np.nan, np.nan],
                4: [np.nan, np.nan, np.nan, np.nan],
                5: [np.nan, np.nan, np.nan, np.nan]}
    for l in [3, 4, 5]:
        rec = fs_lab_obj.get_recognitions(lvl=l)
        if len(rec[0]) != 0:
            true_positive_rate = sum(rec[0]) / len(rec[0])
            to_excel[l][0] = true_positive_rate
            idx = np.where(rec[0] == 1)[0]
            if idx.size != 0:
                max_rec_time = np.max(rec[1][idx])
                min_rec_time = np.min(rec[1][idx])

                mean_rec_time = np.mean(rec[1][idx].clip(0))
                to_excel[l][1] = min_rec_time
                to_excel[l][2] = max_rec_time
                to_excel[l][3] = mean_rec_time
    return to_excel
