import pandas as pd
import pickle
import libs.labellingExtractor as le
import os
import lzma
from libs.loggingFuncs import print_and_log
from config.constant import CORE_PROTOCOL_MAPPING
from config.constant import SYS_VERSCHMUTZUNG_MOD
from config.constant import SYS_VERSCHMUTZUNG_FGE
from flexray_postprocessor.bhe_postprocessor import BhePostprocessor
import numpy as np
fr_postprocessor = BhePostprocessor()


def read_pickle(path):
    try:
        if path.endswith('.xz'):
            with lzma.open(path, 'rb') as f:
                return pickle.load(f)
        with open(path, 'rb') as f:
            return pickle.load(f)
    except EOFError:
        return 'EOFError'
    except FileNotFoundError:
        return 'FileNotFoundError'


def pickle_compress_saver(dictionary_input, path):
    with lzma.open(path, 'wb') as pf:
        pickle.dump(dictionary_input, pf, protocol=pickle.HIGHEST_PROTOCOL)


def read_from_raw(file_list, logger, fr=False):
    """
    :param file_list: list of pickles to open and merge to DF
    :return: DataFrame with proper signals
    """
    df_fs = pd.DataFrame()
    df_sync = pd.DataFrame()
    df_distance = pd.DataFrame()
    for file in file_list:
        print_and_log(logger, f'......{os.path.basename(file)}')
        # if os.path.basename(file) == 'ADCAM_WBA7F21060B236144_20191030_024038_pic_0210.pickle.xz':
        #     print()
        # read pickle
        data = read_pickle(file)
        # add postprossed flexray data
        data = fr_postprocessor.postprocess(data)
        if data == 'EOFError':
            print_and_log(message='!!!!Error "EOFError (cant open pickle)"', logger=logger)
            continue
        elif data == 'FileNotFoundError':
            print_and_log(message='!!!!Error "FileNotFoundError (cant open pickle)"', logger=logger)
            continue

        # FailSafe protocol
        try:
            temp = data['SPI']['EYEQ_TO_HOST']['Core_Failsafe_protocol']
            temp_velocty = data['SPI']['EYEQ_TO_HOST']['Core_Car_Output_protocol']

            # Truncate temp_velocity
            truncate_keys = [key for key in temp_velocty.keys() if 'CO' not in key]
            truncate_keys.remove('timestamp')
            truncate_keys.remove('timestamp_utc')
            truncate_keys.remove('asynchronous')
            for item in truncate_keys:
                del temp_velocty[item]
            temp_interpolated_vel = np.interp(temp['timestamp'], temp_velocty['timestamp'],
                                              temp_velocty['CO_Vehicle_Speed'], left=np.nan, right=np.nan)

        except KeyError as e:
            print_and_log(message=f'!!!!Error {e} not found!', logger=logger)
            continue
        try:
            sync = {'timestamp': data['SPI']['EYEQ_TO_HOST']['Core_Common_protocol']['timestamp'],
                    'COM_Sync_Frame_ID': data['SPI']['EYEQ_TO_HOST']['Core_Common_protocol']['COM_Sync_Frame_ID'],
                    'COM_Cam_Frame_ID': data['SPI']['EYEQ_TO_HOST']['Core_Common_protocol']['COM_Cam_Frame_ID']}#,
                    # 'COM_DayTime_Indicator': data['SPI']['EYEQ_TO_HOST']['Core_Common_protocol']['COM_DayTime_Indicator']}
        except KeyError as e:
            print_and_log(message=f'!!!!Error {e} not found!', logger=logger)
            continue

        # Calibration protocol
        try:
            cal = {'timestamp': data['SPI']['EYEQ_TO_HOST']['Core_Calibration_Output_protocol']['timestamp'],
                   'CO_main_safetyState': data['SPI']['EYEQ_TO_HOST']['Core_Calibration_Output_protocol']['CO_main_safetyState'],
                   'CO_main2road_euler_pitch': data['SPI']['EYEQ_TO_HOST']['Core_Calibration_Output_protocol']['CO_main2road_euler_pitch'],
                   'CO_main2road_euler_yaw': data['SPI']['EYEQ_TO_HOST']['Core_Calibration_Output_protocol']['CO_main2road_euler_yaw'],
                   'CO_main2road_euler_roll': data['SPI']['EYEQ_TO_HOST']['Core_Calibration_Output_protocol']['CO_main2road_euler_roll'],
                   'CO_main_camH': data['SPI']['EYEQ_TO_HOST']['Core_Calibration_Output_protocol']['CO_main_camH']}
        except KeyError as e:
            print_and_log(message=f'!!!!Error {e} not found!', logger=logger)
            continue

        # Add post processed Flexray data
        if fr:
            try:
                if 'FRAME_78_0_8_B' in data['FLEXRAY'] and 'BV3_SensorHeader' in data['FLEXRAY']['FRAME_78_0_8_B']:
                    flexray = {'timestamp': data['FLEXRAY']['FRAME_78_0_8_B']['BV3_SensorHeader']['timestamp'],
                               SYS_VERSCHMUTZUNG_MOD: data['FLEXRAY']['FRAME_78_0_8_B']['BV3_SensorHeader'][SYS_VERSCHMUTZUNG_MOD],
                               SYS_VERSCHMUTZUNG_FGE: data['FLEXRAY']['FRAME_78_0_8_B']['BV3_SensorHeader'][SYS_VERSCHMUTZUNG_FGE]}
                else:
                    flexray = {'timestamp': [],
                               SYS_VERSCHMUTZUNG_MOD: [],
                               SYS_VERSCHMUTZUNG_FGE: []}
            except KeyError as e:
                print_and_log(message=f'!!!!Error {e} not found!', logger=logger)
                continue
        else:
            data_len = len(data['SPI']['EYEQ_TO_HOST']['Core_Common_protocol']['timestamp'])
            flexray = {'timestamp': data['SPI']['EYEQ_TO_HOST']['Core_Common_protocol']['timestamp'],
                       SYS_VERSCHMUTZUNG_MOD: [-1] * data_len,
                       SYS_VERSCHMUTZUNG_FGE: [-1] * data_len}

        # temporary df
        df_fs_temp = pd.DataFrame.from_dict(temp)
        # adding filename to each row

        df_fs_temp['File_Name'] = os.path.basename(file)
        df_fs_temp['Velocity'] = temp_interpolated_vel
        # merging previous and temporary DataFrame (fs signals)
        df_fs = pd.concat([df_fs, df_fs_temp], ignore_index=True)
        # getting sync frame ID and cam frame ID from Common protocol
        df_sync_temp = pd.DataFrame.from_dict(sync)
        # getting cal data
        df_cal_temp = pd.DataFrame.from_dict(cal)
        # merging previous and temporary DataFrame (df_cal_temp)
        df_sync_temp = pd.merge_asof(df_sync_temp.sort_values('timestamp'), df_cal_temp, on='timestamp', direction='nearest')
        # if fr:
        # getting flexray data
        df_fr_temp = pd.DataFrame.from_dict(flexray)
        # merging previous and temporary DataFrame (df_cal_temp)
        df_sync_temp = pd.merge_asof(df_sync_temp.sort_values('timestamp'), df_fr_temp, on='timestamp', direction='nearest')
        df_sync_temp.drop('timestamp', axis=1,  inplace=True)

        # merging previous and temporary DataFrame (sync cam ID)
        # TODO checkign if Frame ID increasing by 1 every time example:
        #  pickle_0010, 0011, 0013 - what if 0012 is missing?
        df_sync = pd.concat([df_sync, df_sync_temp], ignore_index=True)
        # print()

    # meging camera ID and FS signals
    # TODO implement merging function (right now merge 1 to 1 assuming there was no drop
    print_and_log(logger, f'......Merging Com_Cam_Frame_ID to Core_failsafe_protocol by Sync_Frame_ID')
    if df_fs.empty or df_sync.empty:
        msg = f'No data from SPI found!'
        return msg
    df_final = pd.concat([df_fs, df_sync], axis=1)
    print_and_log(logger, f'......Stop reading system data - Return DataFrame')
    return df_final

def read_from_dict(file_list, logger):
    data = None
    for file in file_list:
        print_and_log(logger, f'......{os.path.basename(file)}')
        data = read_pickle(file)
    return data


def read_from_itrk(file_list, logger):
    df_lab = pd.DataFrame()
    for file in file_list:
        print_and_log(logger, f'......{os.path.basename(file)}')

        decoded, overall, values_mapping = le.LabellingExtractor().decode(file)
        values_trios = get_mapping_values(values_mapping)
        df_temp = pd.DataFrame.from_dict(decoded['Perfect']['FrameTag'], dtype='int64')
        df_by4 = df_temp[df_temp.index % 4 == 0].copy()
        # converting itrk values to general mapping to match the system
        df_by4 = convert_itrk_to_general_values(values_trios, df_by4)
        df_by4['itrk_name'] = os.path.basename(file)
        # replacing ignore value with -1
        # print_and_log(logger, f"......Replacing 'ignore' value with '-1'")
        # for column_name, column_data in df_by4.iteritems():
        #     if column_name in c.IGNORE_LAB.keys():
        #         df_by4[column_name] = df_by4[column_name].replace(c.IGNORE_LAB[column_name], -1)
        df_lab = pd.concat([df_lab, df_by4], ignore_index=True)
        print_and_log(logger, f'......Stop reading labeling data - Return DataFrame')
    # converting names to general system values
    df_lab = convert_general_values_to_CP_values(df_lab)
    return df_lab


def get_mapping_values(values_list):
    trios = []
    for value in values_list:
        trios.append(value.split()[2:])
    df = pd.DataFrame(trios)
    return df


def convert_itrk_to_general_values(values_map, input_df):
    output_df = input_df.copy().astype(str)
    # Change camPort name to cameraInstance, this is the only value that does not match in itrk header and value
    output_df.rename(columns={'camPort': 'cameraInstance'}, inplace=True)
    for column in output_df.columns:
        if column in values_map.values:
            output_df[column].replace(list(values_map[values_map[0] == column][1].values), list(values_map[values_map[0] == column][2].values), inplace=True)
    return output_df


def convert_general_values_to_CP_values(inputdf):
    output_df = inputdf.copy()
    output_df.replace(CORE_PROTOCOL_MAPPING, inplace=True)
    return output_df
