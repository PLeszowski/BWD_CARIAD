import numpy as np
import datetime
import pandas as pd
from libs.loggingFuncs import print_and_log
import config.constant as Const


def get_weather_sys(data, obj, logger):
    for key in obj.keys():
        try:
            get_failsafes_times(data[[key, 'COM_Cam_Frame_ID', 'File_Name']], obj[key], logger)
        except:
            print_and_log(logger, f'....**no {key} in sys')


def get_weather_lab(data, obj, logger):
    for key in obj.keys():
        try:
            get_failsafes_times_lab(data[[key, 'grabIndex', 'File_Name']], obj[key], logger)
        except:
            print_and_log(logger, f'....**no {key} in labeled')


def get_failsafes_times(failsafe_signal, fs_object, logger):
    print_and_log(logger, '....**Getting failsafes timers for ' + fs_object.name)
    if len(failsafe_signal) == 0:
        print_and_log(logger, '....**no data provided for: ' + fs_object.name)
    failsafe_signal = failsafe_signal[failsafe_signal.notnull()]
    idx = np.where(np.diff(failsafe_signal.iloc[:, 0]) != 0)[0]
    counter = 0
    for i in range(len(idx) + 1):
        try:
            df = failsafe_signal[counter: (int(idx[i]) + 1)]
        except:
            df = failsafe_signal[counter: len(failsafe_signal.iloc[:, 0])]
        index = np.where(np.diff(df.iloc[:, 0]) != 0)[0] + counter

        fs_object.add_start_time(df.iloc[:, 1][counter])
        fs_object.add_start_pic_name(df.iloc[:, 2][counter])
        for idx in index:
            fs_object.add_stop_time(df.iloc[:, 1][idx])
            fs_object.add_stop_pic_name(df.iloc[:, 2][idx])
            fs_object.add_severity_level((df.iloc[:, 0][idx]))
            try:
                fs_object.add_start_time(df.iloc[:, 1][idx + 1])
                fs_object.add_start_pic_name(df.iloc[:, 2][idx + 1])
            except:
                pass
        try:
            fs_object.add_stop_time(df.iloc[:, 1][idx[i]])
            fs_object.add_stop_pic_name(df.iloc[:, 2][idx[i]])
            fs_object.add_severity_level((df.iloc[:, 0][idx[i]]))
            counter = idx[i] + 1
        except:
            fs_object.add_stop_time(df.iloc[:, 1][len(failsafe_signal.iloc[:, 0]) - 1])
            fs_object.add_stop_pic_name(df.iloc[:, 2][len(failsafe_signal.iloc[:, 0]) - 1])
            fs_object.add_severity_level(df.iloc[:, 0][len(failsafe_signal.iloc[:, 0]) - 1])
            pass
        # fs_object.add_severity_level(df.iloc[:, 0][i])
        # fs_object.add_stop_time(df.iloc[0:, 1][i])
        fs_object.add_recognition_len()
    if len(fs_object.start_time) == len(fs_object.stop_time) == len(fs_object.severity):
        pass
    else:
        print_and_log(logger, f'....**Something went wrong {fs_object.start_time}{fs_object.stop_time}{fs_object.severity}')


def get_failsafes_times_lab(failsafe_signal, fs_object, logger):
    # failsafe_signal_fourth = failsafe_signal[failsafe_signal.index % 4 == 0]
    # failsafe_signal_fourth = failsafe_signal_fourth.reset_index(drop=True)

    print_and_log(logger, '....**Getting failsafes timers for ' + fs_object.name)
    if len(failsafe_signal) == 0:
        print_and_log(logger, '....**no data provided for: ' + fs_object.name)
    failsafe_signal_fourth = failsafe_signal[failsafe_signal.notnull()]
    failsafe_signal_fourth.iloc[:, [0, 1]] = failsafe_signal_fourth.iloc[:, [0, 1]].astype('int32')
    idx = np.where(np.diff(failsafe_signal_fourth.iloc[:, 0]) != 0)[0]
    counter = 0
    for i in range(len(idx) + 1):
        try:
            df = failsafe_signal_fourth[counter: (int(idx[i]) + 1)]
        except:
            df = failsafe_signal_fourth[counter: len(failsafe_signal_fourth.iloc[:, 0])]
        index = np.where(np.diff(df.iloc[:, 0]) != 0)[0] + counter

        fs_object.add_start_time(df.iloc[:, 1][counter])
        fs_object.add_start_pic_name(df.iloc[:, 2][counter])
        for idx in index:
            fs_object.add_stop_time(df.iloc[:, 1][idx])
            fs_object.add_stop_pic_name(df.iloc[:, 2][idx])
            fs_object.add_severity_level((df.iloc[:, 0][idx]))
            try:
                fs_object.add_start_time(df.iloc[:, 1][idx + 1])
                fs_object.add_start_pic_name(df.iloc[:, 2][idx + 1])
            except:
                pass
        try:
            fs_object.add_stop_time(df.iloc[:, 1][idx[i]])
            fs_object.add_stop_pic_name(df.iloc[:, 2][idx[i]])
            fs_object.add_severity_level((df.iloc[:, 0][idx[i]]))
            counter = idx[i] + 1
        except:
            fs_object.add_stop_time(df.iloc[:, 1][len(failsafe_signal_fourth.iloc[:, 0]) - 1])
            fs_object.add_stop_pic_name(df.iloc[:, 2][len(failsafe_signal.iloc[:, 0]) - 1])
            fs_object.add_severity_level(df.iloc[:, 0][len(failsafe_signal_fourth.iloc[:, 0]) - 1])
            pass
        # fs_object.add_severity_level(df.iloc[:, 0][i])
        # fs_object.add_stop_time(df.iloc[0:, 1][i])
        fs_object.add_recognition_len()
    if len(fs_object.start_time) == len(fs_object.stop_time) == len(fs_object.severity):
        pass
    else:
        print_and_log(logger, f'....**Something went wrong {fs_object.start_time}{fs_object.stop_time}{fs_object.severity}')


def get_freeview(data, fs_object, logger):

    df = data[(data['blurImage'] == '-1') &
              (data['fog'] == '-1') &
              (data['frozenWindshield'] == '-1') &
              (data['fullBlockage'] == '-1') &
              (data['partialBlockage'] == '-1') &
              (data['snowfall'] == '-1') &
              (data['rain'] == '-1') &
              (data['splashes'] == '-1') &
              (data['sunRay'] == '-1') &
              (data['lowSun'] == '-1')].reset_index()
    df = df[['index', 'grabIndex', 'File_Name']]
    if not df.empty:
        fs_object.add_start_time(df['grabIndex'].iloc[0])
        fs_object.add_start_pic_name(df['File_Name'].iloc[0])
        fs_object.add_severity_level(5)
        idx = np.where(np.diff(df['index']) > 1)[0]
        if len(idx) != 0:
            for i in idx:
                fs_object.add_stop_time(df['grabIndex'].loc[i])
                fs_object.add_stop_pic_name(df['File_Name'].loc[i])
                try:
                    fs_object.add_start_time(df['grabIndex'].loc[i + 1])
                    fs_object.add_start_pic_name(df['File_Name'].loc[i + 1])
                    fs_object.add_severity_level(5)
                except:
                    pass
        fs_object.add_stop_time(df['grabIndex'].iloc[-1])
        fs_object.add_stop_pic_name(df['File_Name'].iloc[-1])
        fs_object.add_recognition_len()
        if len(fs_object.start_time) == len(fs_object.stop_time) == len(fs_object.severity):
            pass
        else:
            print_and_log(logger, f'....**Something went wrong {fs_object.start_time}{fs_object.stop_time}{fs_object.severity}')
