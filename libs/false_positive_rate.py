import config.constant as c
import numpy as np
from libs.debugging import wrapping
from libs.loggingFuncs import print_and_log
# import generate_excel as ge


@wrapping(prefix='......', kind='not_class')
def prep(fs_sys_objects, fs_lab_objects, logger):

    to_check = c.TO_CHECK_FOR_FALSE_POSITIVES
    for fs in to_check:
        freeview=False
        if fs == "freeview":
            freeview = True
        sys_name = fs_lab_objects[fs].get_sys_name()
        try:
            sys_fs_occurence = fs_sys_objects[sys_name].check_if_fs_occurred(freeview=freeview)
        except KeyError:
            continue
        if sys_fs_occurence is None:
            print_and_log(logger, f"........No detected events by system for: {fs}")
            continue
        checking = fs_lab_objects[fs].get_no_fs()
        if checking is not None:
            for severity in sys_fs_occurence:
                print_and_log(logger, f"........looking for FP for: {sys_name} - severity {severity}")
                execution2(fs_sys_objects[c.LAB_TO_SYS[fs]], fs_lab_objects[fs], checking, severity, fs_lab_objects, logger=logger)


@wrapping(prefix='......', kind='not_class')
def execution2(fs_sys_obj, fs_lab_obj, label_severities_to_find, system_severity_to_check, fs_lab_objects, logger):

    label_starts, label_stops, idx_label = fs_lab_obj.get_timers_for_specific_severity(lvl=label_severities_to_find)

    system_starts, system_stops, idx_sys = fs_sys_obj.get_timers_for_specific_severity(lvl=system_severity_to_check)

    fail_frames, all_frames, lab_start = false_recognition(system_starts=system_starts, system_stops=system_stops,
                                                           label_starts=label_starts, label_stops=label_stops,
                                                           logger=logger)
    if lab_start is not None:
        labeled_fs = find_labeled_fs(fs_lab_objects, lab_start)
    else:
        labeled_fs = None
    fs_sys_obj.add_fpr(fail_frames, all_frames, system_severity_to_check, labeled_fs)
    return None


@wrapping(prefix='......', kind='not_class')
def false_recognition(system_starts, system_stops, label_starts, label_stops, logger, max_bufor_time=0):
    if len(label_starts) != len(label_stops):
        return print_and_log(logger, f'........length of label_start = {len(label_starts)} != length of label_stop = {len(label_stops)}')
    if len(system_starts) != len(system_stops):
        return print_and_log(logger, f'........length of system_start = {len(system_starts)} != length of system_stop = {len(system_stops)}')
    if len(label_starts) == 0:
        return print_and_log(logger, f'........No label with failsafe = None provided')
    if len(system_starts) == 0:
        return 0, np.sum(np.array(label_stops) - np.array(label_starts))
    fp_start = None
    start = []
    stop = []
    if len(system_starts) == 0:
        return None

    for sys_start, sys_stop in zip(system_starts, system_stops):
        for lab_start, lab_stop in zip(label_starts, label_stops):
            if lab_start > sys_stop:
                break
            elif lab_stop < sys_start:
                continue
            else:
                start.append(max(lab_start, sys_start))
                stop.append(min(lab_stop, sys_stop))
                fp_start = lab_start
    fail_frames = np.sum(np.array(stop) - np.array(start))
    all_frames = np.sum(np.array(label_stops) - np.array(label_starts))

    return fail_frames, all_frames, fp_start

def find_labeled_fs(objs, grabIndex):
    for name, obj in objs.items():
        if name != 'blockage':
            idx = np.searchsorted(obj.start_time, grabIndex, side='right')
            severity = obj.severity[idx - 1]
            if severity == -1:
                continue
            else:
                return name
        else:
            continue

    return 'freeview'


@wrapping(prefix='......', kind='not_class')
def false_positive(fs_sys_obj, km, h):
    to_excel = {2: [np.nan, np.nan, np.nan, np.nan],
                '50': [np.nan, np.nan, np.nan, np.nan],
                4: [np.nan, np.nan, np.nan, np.nan],
                5: [np.nan, np.nan, np.nan, np.nan]}
    fp = fs_sys_obj.get_fpr()
    for l in [2, 4, 5]:
        to_excel[l][0] = fp[l][0]
        to_excel[l][2] = fp[l][0] / (km / 400)
        to_excel[l][3] = fp[l][0] / (h / 100)
    return to_excel
