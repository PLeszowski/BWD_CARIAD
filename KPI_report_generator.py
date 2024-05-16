import json
import os
import pandas as pd
import numpy as np
from config import constant as c
import time
from tqdm import tqdm


class KPIReport:

    FPS = 36

    def __init__(self):
        self.files = None
        self.no_recognition = ''
        self.totalDistanceDriven = 0
        self.totalNumberOfFrames = 0
        self.initFullNames = c.KPI_NAMES_INIT
        self.init25 = [item + '_25' for item in self.initFullNames]
        self.init75 = [item + '_75' for item in self.initFullNames]
        self.init99 = [item + '_99' for item in self.initFullNames]
        self.initColumns = self.initFullNames + self.init25 + self.init75 + self.init99
        TPRinitRows = ['FramesLabeled', 'MeanRecognitionTime', 'FramesDetected', 'FramesDetectedInTime', 'NumberOfScenes',
                       'Detection threshold', 'TestedHours', 'TestedKM', 'MinRecognitionTime', 'MaxRecognitionTime']
        FPRinitRows = ['FalseEvents', 'FalseFrames', 'MTBF', 'threshold']
        self.resultTPRDataFrame = pd.DataFrame(data=0, columns=self.initColumns, index=TPRinitRows)
        for k, v in c.DETECTION_THRESHOLD.items():
            col_names = self.resultTPRDataFrame.columns[self.resultTPRDataFrame.columns.str.contains(pat=k)]
            self.resultTPRDataFrame.loc['Detection threshold', col_names] = v
        self.resultTPRDataFrame.loc['MinRecognitionTime'] = 9999
        self.resultFPRDataFrame = pd.DataFrame(data=0, columns=self.initColumns, index=FPRinitRows)
        self.resultCTDataFrame = pd.DataFrame(data=0, columns=self.initFullNames, index=self.initFullNames)
        self.TPRformattedDF = pd.DataFrame()
        self.FPRformattedDF = pd.DataFrame()
        self.recognition_time_dict = {}
        self.ave_veh_speed_dict = {}
        for v in c.KPI_NAMES_INIT:
            self.recognition_time_dict[v] = []
        for v in c.KPI_NAMES_VSPEED_INIT:
            self.ave_veh_speed_dict[v] = []
        print(id(self.recognition_time_dict))
        print(id(self.ave_veh_speed_dict))
        pass

    def mainLogic(self, path):
        self.name = os.path.basename(path)
        self.path = os.path.dirname(path)
        to_slow = 0
        new_list = []
        events = {}
        sun_and_night_list = []
        rain2 = []
        for file_name in tqdm(os.listdir(path)):
            # print(file)
            try:
                self.files = self.__class__.open_json_file(path, file_name)
            except:
                continue
            for line in self.files:
                if 'DistanceDriven' in line:
                    try:
                        if line['DistanceDriven']*36000/(line['TotalNumberOfFrames']) < 0:  # mniejszy niz ms
                            to_slow += line['TotalNumberOfFrames']
                            continue
                    except:
                        continue
                    self.totalDistanceDriven += line['DistanceDriven']
                    self.totalNumberOfFrames += line['TotalNumberOfFrames']
                else:
                    continue
                # TPR

                if line['LabeledFs']:
                    # print(line['LabeledFs'][0]['FsName'])
                    for labeledFS in line['LabeledFs']:
                        if ((labeledFS['DayNight'] == "NIGHT" or labeledFS['DayNight'] == "Night") and not c.KPI_GENERATE_NIGHT) or \
                                ((labeledFS['DayNight'] == "DAY" or labeledFS['DayNight'] == "Day") and not c.KPI_GENERATE_DAY):
                            continue
                        # if (labeledFS["FsName"] == "Fading by Sun" or labeledFS["FsName"] == "Sun Ray") and labeledFS["DayNight"] == "NIGHT":
                        #     sun_and_night_list.append(f'{labeledFS["FsName"]} - {labeledFS["DayNight"]} in: {file_name}')
                        # if labeledFS['FsName'] == 'Snowfall':
                        #     x=1
                        #     continue
                        # if (((labeledFS['FsName'] in ['Blur', 'Frozen Windshield', 'Full Blockage', 'Road Spray']) & (int(labeledFS['Severity']) == 25)) |
                        #     ((labeledFS['FsName'] in ['Blur', 'Fog', 'Frozen Windshield', 'Full Blockage', 'Fading by Sun', 'Sun Ray', 'Road Spray']) & (int(labeledFS['Severity']) == 75))):
                        #     continue
                        self.resultTPRDataFrame.loc['FramesLabeled', labeledFS['FsName']] += labeledFS['FramesLabeled']
                        self.resultTPRDataFrame.loc['FramesLabeled', (labeledFS['FsName'] + '_' + str(labeledFS['Severity']))] += labeledFS['FramesLabeled']
                        self.resultTPRDataFrame.loc['TestedKM', labeledFS['FsName']] += (labeledFS['FramesLabeled'] / line['TotalNumberOfFrames']) * line['DistanceDriven']
                        self.resultTPRDataFrame.loc['TestedKM', (labeledFS['FsName'] + '_' + str(labeledFS['Severity']))] += (labeledFS['FramesLabeled'] / line['TotalNumberOfFrames']) * line['DistanceDriven']
                        self.resultTPRDataFrame.loc['NumberOfScenes', labeledFS['FsName']] += 1
                        events.setdefault(f"{labeledFS['FsName']}_{str(labeledFS['Severity'])}", 0)
                        events[f"{labeledFS['FsName']}_{str(labeledFS['Severity'])}"] += 1
                        # append event average speed to ave_veh_speed_dict total
                        if "EventAveSpeed" in labeledFS:  # not counted for freeview
                            self.ave_veh_speed_dict['Total'].append(labeledFS["EventAveSpeed"])
                            self.ave_veh_speed_dict[labeledFS['FsName']].append(labeledFS['EventAveSpeed'])
                        if labeledFS['IsRecognition'] is True:
                            self.recognition_time_dict[labeledFS['FsName']].append(labeledFS['RecognitionTime'])
                            self.resultTPRDataFrame.loc['FramesDetected', labeledFS['FsName']] += labeledFS['FramesDetected']
                            self.resultTPRDataFrame.loc['MeanRecognitionTime', labeledFS['FsName']] += labeledFS['RecognitionTime'] #Cumulative sum, divided by number of occurences later
                            # self.resultTPRDataFrame.loc['NumberOfScenes', labeledFS['FsName']] += 1
                            self.resultTPRDataFrame.loc['FramesDetected', (labeledFS['FsName'] + '_' + str(labeledFS['Severity']))] += labeledFS['FramesDetected']
                            self.resultTPRDataFrame.loc['MeanRecognitionTime', (labeledFS['FsName'] + '_' + str(labeledFS['Severity']))] += labeledFS['RecognitionTime'] #Cumulative sum, divided by number of occurences later
                            if self.resultTPRDataFrame.loc['MinRecognitionTime', (labeledFS['FsName'] + '_' + str(labeledFS['Severity']))] > labeledFS['RecognitionTime']:
                                self.resultTPRDataFrame.loc['MinRecognitionTime', (labeledFS['FsName'] + '_' + str(labeledFS['Severity']))] = labeledFS['RecognitionTime']
                            if self.resultTPRDataFrame.loc['MaxRecognitionTime', (labeledFS['FsName'] + '_' + str(labeledFS['Severity']))] < labeledFS['RecognitionTime']:
                                self.resultTPRDataFrame.loc['MaxRecognitionTime', (labeledFS['FsName'] + '_' + str(labeledFS['Severity']))] = labeledFS['RecognitionTime']
                            self.resultTPRDataFrame.loc['NumberOfScenes', (labeledFS['FsName'] + '_' + str(labeledFS['Severity']))] += 1
                            if c.KPI_RECOG_TIME:
                                if labeledFS['RecognitionTime'] < self.resultTPRDataFrame.loc['Detection threshold', labeledFS['FsName']]:
                                    self.resultTPRDataFrame.loc['FramesDetectedInTime', labeledFS['FsName']] += labeledFS['FramesDetected']
                                    self.resultTPRDataFrame.loc['FramesDetectedInTime', (labeledFS['FsName'] + '_' + str(labeledFS['Severity']))] += labeledFS['FramesDetected']
                                    self.resultCTDataFrame.at[f'{labeledFS["FsName"]}', f'{labeledFS["FsName"]}'] += 1
                            else:
                                self.no_recognition = 'no_rec_time'
                                self.resultTPRDataFrame.loc['FramesDetectedInTime', labeledFS['FsName']] += labeledFS['FramesDetected']
                                self.resultTPRDataFrame.loc['FramesDetectedInTime', (labeledFS['FsName'] + '_' + str(labeledFS['Severity']))] += labeledFS['FramesDetected']
                                self.resultCTDataFrame.at[f'{labeledFS["FsName"]}', f'{labeledFS["FsName"]}'] += 1
                # FPR
                if line['FalsePositive']:
                    # print("found False Positive!")
                    try:
                        for FP in line['FalsePositive']:
                            if ((FP['DayNight'] == "NIGHT" or FP['DayNight'] == "Night") and not c.KPI_GENERATE_NIGHT) or ((FP['DayNight'] == "DAY" or FP['DayNight'] == "Day") and not c.KPI_GENERATE_DAY):
                                continue
                            if (((FP['FsName'] in ['Blur', 'Frozen Windshield', 'Full Blockage', 'Out of Focus']) & (int(FP['Severity']) == 2)) |
                                    ((FP['FsName'] in ['Fog', 'Frozen Windshield', 'Full Blockage', 'Fading by Sun']) & (int(FP['Severity']) == 4))):
                                x=1
                                continue

                            if c.PARTIALS_NAMES_SYS[FP['FsName']] == 'Rain':
                                if 'snowfall' in FP["Labeled"]:
                                    x=1
                                    continue
                            if c.PARTIALS_NAMES_SYS[FP['FsName']] == 'Snowfall':
                                if 'rain' in FP["Labeled"]:
                                    x=1
                                    continue
                            if c.PARTIALS_NAMES_SYS[FP['FsName']] == 'Rain':
                                if FP['Severity'] == 5:
                                    for rr in FP['Other']:
                                        t = [rr[0].replace('_pic_', '_v01_').replace('pickle.xz', 'MF4')]
                                        t.extend(rr[5][1:13])
                                        t.append(rr[2])
                                        rain2.append(t)
                                        #rain.append(rr[0].replace('_pic_', '_v01_').replace('pickle.xz', 'MF4'))

                                    # rain.append([FP['LogNameEventStart'], FP['LogNameEventStop']])
                                x=1
                            self.resultFPRDataFrame.loc['FalseEvents', c.PARTIALS_NAMES_SYS[FP['FsName']]] += 1
                            self.resultFPRDataFrame.loc['FalseEvents', (c.PARTIALS_NAMES_SYS[FP['FsName']] + '_' + str(c.SEVERITY_MAP[FP['Severity']]))] += 1
                            self.resultFPRDataFrame.loc['FalseFrames', c.PARTIALS_NAMES_SYS[FP['FsName']]] += FP['NumberOfFrames']
                            self.resultFPRDataFrame.loc['FalseFrames', (c.PARTIALS_NAMES_SYS[FP['FsName']] + '_' + str(c.SEVERITY_MAP[FP['Severity']]))] += FP['NumberOfFrames']
                            # if len(FP["Labeled"]) == 0:
                            if not FP["Labeled"]:
                                self.resultCTDataFrame.at[
                                    f'{c.PARTIALS_NAMES_SYS[FP["FsName"]]}', f'Free View'] += 1
                                continue
                            for iiii in FP["Labeled"]:
                                self.resultCTDataFrame.at[f'{c.PARTIALS_NAMES_SYS[FP["FsName"]]}', f'{c.PARTIALS_NAMES_LAB[iiii]}'] += 1
                    except:
                        x=1
                        self.resultCTDataFrame.at[f'{c.PARTIALS_NAMES_SYS[FP["FsName"]]}', f'Free View'] += 1
                        #self.resultCTDataFrame.at[f'{FP["FsName"]}', f'{c.PARTIALS_NAMES_LAB[FP["Labeled"]]}'] += 1

        # Dividing cumulative sums by number of occurences
        # TPR
        self.resultTPRDataFrame.loc['MeanRecognitionTime'] = self.resultTPRDataFrame.loc['MeanRecognitionTime'] / self.resultTPRDataFrame.loc['NumberOfScenes']
        self.resultTPRDataFrame.loc['TPRate'] = self.resultTPRDataFrame.loc['FramesDetected'] / self.resultTPRDataFrame.loc['FramesLabeled'] * 100
        self.resultTPRDataFrame.loc['TPRateInTime'] = self.resultTPRDataFrame.loc['FramesDetectedInTime'] / self.resultTPRDataFrame.loc['FramesLabeled'] * 100
        self.resultTPRDataFrame.loc['TestedHours'] = self.resultTPRDataFrame.loc['FramesLabeled'] / (KPIReport.FPS * 3600) #assuming 36 FPS
        # FPR
        self.resultFPRDataFrame.loc['OverallFPRKM'] = self.resultFPRDataFrame.loc['FalseEvents'] / (self.totalDistanceDriven / 400)
        self.resultFPRDataFrame.loc['OverallFPRPercent'] = self.resultFPRDataFrame.loc['FalseFrames'] / self.totalNumberOfFrames
        self.resultFPRDataFrame.loc['OverallFPRHours'] = self.resultFPRDataFrame.loc['FalseEvents'] / ((self.totalNumberOfFrames / (KPIReport.FPS * 3600))/100)

        # print(self.resultTPRDataFrame)
        print('total distance: ', self.totalDistanceDriven)
        print('total hours: ', self.totalNumberOfFrames/(KPIReport.FPS*3600))
        KPIReport.convertDataFrameToExcel(self)

    def convertDataFrameToExcel(self):
        # region TPR excel formatter
        self.TPRformattedDF['hours'] = self.resultTPRDataFrame.loc['TestedHours'][self.initFullNames]  # omitting .values gives row names
        self.TPRformattedDF['kilometers'] = self.resultTPRDataFrame.loc['TestedKM'][self.initFullNames].values
        self.TPRformattedDF['number of scenes'] = self.resultTPRDataFrame.loc['NumberOfScenes'][self.initFullNames].values
        self.TPRformattedDF['Overall TPR'] = self.resultTPRDataFrame.loc['TPRateInTime'][self.initFullNames].values
        self.TPRformattedDF['TPR 25'] = self.resultTPRDataFrame.loc['TPRateInTime'][self.init25].values
        self.TPRformattedDF['min. rec. time 25'] = self.resultTPRDataFrame.loc['MinRecognitionTime'][self.init25].values
        self.TPRformattedDF['max. rec. time 25'] = self.resultTPRDataFrame.loc['MaxRecognitionTime'][self.init25].values
        self.TPRformattedDF['mean. rec. time 25'] = self.resultTPRDataFrame.loc['MeanRecognitionTime'][self.init25].values
        self.TPRformattedDF['TPR 75'] = self.resultTPRDataFrame.loc['TPRateInTime'][self.init75].values
        self.TPRformattedDF['min. rec. time 75'] = self.resultTPRDataFrame.loc['MinRecognitionTime'][self.init75].values
        self.TPRformattedDF['max. rec. time 75'] = self.resultTPRDataFrame.loc['MaxRecognitionTime'][self.init75].values
        self.TPRformattedDF['mean. rec. time 75'] = self.resultTPRDataFrame.loc['MeanRecognitionTime'][self.init75].values
        self.TPRformattedDF['TPR 99'] = self.resultTPRDataFrame.loc['TPRateInTime'][self.init99].values
        self.TPRformattedDF['min. rec. time 99'] = self.resultTPRDataFrame.loc['MinRecognitionTime'][self.init99].values
        self.TPRformattedDF['max. rec. time 99'] = self.resultTPRDataFrame.loc['MaxRecognitionTime'][self.init99].values
        self.TPRformattedDF['mean. rec. time 99'] = self.resultTPRDataFrame.loc['MeanRecognitionTime'][self.init99].values
        
        self.TPRformattedDF['min. rec. time 25'].loc[self.TPRformattedDF['min. rec. time 25'] == 9999] = np.nan
        self.TPRformattedDF['max. rec. time 25'].loc[self.TPRformattedDF['max. rec. time 25'] == 0] = np.nan
        self.TPRformattedDF['min. rec. time 75'].loc[self.TPRformattedDF['min. rec. time 75'] == 9999] = np.nan
        self.TPRformattedDF['max. rec. time 75'].loc[self.TPRformattedDF['max. rec. time 75'] == 0] = np.nan
        self.TPRformattedDF['min. rec. time 99'].loc[self.TPRformattedDF['min. rec. time 99'] == 9999] = np.nan
        self.TPRformattedDF['max. rec. time 99'].loc[self.TPRformattedDF['max. rec. time 99'] == 0] = np.nan
        print(self.TPRformattedDF)
        # endregion

        # region FPR excel formatter
        self.resultFPRDataFrame.loc['threshold'] = '<1/100h' # this line is only to generate column names for the excel
        self.FPRformattedDF['deleteMe'] = self.resultFPRDataFrame.loc['threshold'][self.initFullNames]  # this column is deleted at the end of block
        self.FPRformattedDF['hours'] = self.totalNumberOfFrames / (KPIReport.FPS * 3600)
        self.FPRformattedDF['kilometers'] = self.totalDistanceDriven
        self.FPRformattedDF['number of scenes'] = self.totalNumberOfFrames / (KPIReport.FPS * 60)
        self.FPRformattedDF['Overall FPR (1/400 km)'] = self.resultFPRDataFrame.loc['OverallFPRKM']
        self.FPRformattedDF['Overall FPR (percentage)'] = self.resultFPRDataFrame.loc['OverallFPRPercent']
        self.FPRformattedDF['Overall FPRHours'] = self.resultFPRDataFrame.loc['OverallFPRHours']
        self.FPRformattedDF['false events 25'] = self.resultFPRDataFrame.loc['FalseEvents'][self.init25].values
        self.FPRformattedDF['MTBF 25'] = self.resultFPRDataFrame.loc['MTBF'][self.init25].values
        self.FPRformattedDF['FPRKM 25'] = self.resultFPRDataFrame.loc['OverallFPRKM'][self.init25].values
        self.FPRformattedDF['FPRHours 25'] = self.resultFPRDataFrame.loc['OverallFPRHours'][self.init25].values
        self.FPRformattedDF['false events 75'] = self.resultFPRDataFrame.loc['FalseEvents'][self.init75].values
        self.FPRformattedDF['MTBF 75'] = self.resultFPRDataFrame.loc['MTBF'][self.init75].values
        self.FPRformattedDF['FPRKM 75'] = self.resultFPRDataFrame.loc['OverallFPRKM'][self.init75].values
        self.FPRformattedDF['FPRHours 75'] = self.resultFPRDataFrame.loc['OverallFPRHours'][self.init75].values
        self.FPRformattedDF['false events 99'] = self.resultFPRDataFrame.loc['FalseEvents'][self.init99].values
        self.FPRformattedDF['MTBF 99'] = self.resultFPRDataFrame.loc['MTBF'][self.init99].values
        self.FPRformattedDF['FPRKM 99'] = self.resultFPRDataFrame.loc['OverallFPRKM'][self.init99].values
        self.FPRformattedDF['FPRHours 99'] = self.resultFPRDataFrame.loc['OverallFPRHours'][self.init99].values
        self.FPRformattedDF.drop(columns=['deleteMe'], inplace=True)  # deleting obsolete column
        print(self.FPRformattedDF)
        #endregion

        # recognition time distribution (percentile)
        rec_time_no_nan_list = []
        recog_time_percentile_df = pd.DataFrame(index=c.PERCENTILE_RECOG_TIME_COL, columns=c.KPI_NAMES_INIT)
        for col in recog_time_percentile_df.columns:
            for row in recog_time_percentile_df.index:
                if self.recognition_time_dict[col]:
                    for value in self.recognition_time_dict[col]:
                        if value is not np.nan and value is not None:
                            rec_time_no_nan_list.append(value)
                    try:
                        recog_time_percentile_df.loc[row, col] = np.percentile(rec_time_no_nan_list, row)
                    except TypeError:
                        print('ERROR: np.percentile(rec_time_no_nan_list, row)')
                        continue

        # average vehicle speed distribution (percentile)
        ave_speed_no_nan_list = []
        ave_speed_percentile_df = pd.DataFrame(index=c.PERCENTILE_RECOG_TIME_COL, columns=c.KPI_NAMES_VSPEED_INIT)
        for col in ave_speed_percentile_df.columns:
            for row in ave_speed_percentile_df.index:
                if self.ave_veh_speed_dict[col]:
                    for value in self.ave_veh_speed_dict[col]:
                        if value is not np.nan and value is not None:
                            ave_speed_no_nan_list.append(value)
                    try:
                        ave_speed_percentile_df.loc[row, col] = np.percentile(ave_speed_no_nan_list, row)
                    except TypeError as e:
                        print('ERROR: np.percentile(ave_speed_no_nan_list, row)')
                        print(row)
                        with open('/net/8k3/e0fs01/irods/PLKRA-PROJECTS/ADCAM/7-Tools/ADCAM/BWD/output/CARIAD_X060_001/bad.json', 'w') as f:
                            json.dump(ave_speed_no_nan_list, f, indent=2)
                        raise e

        timestr = time.strftime("%Y%m%d%H%M%S")
        day_night_str = ''
        if c.KPI_GENERATE_DAY:
            day_night_str = day_night_str + '_D'
        if c.KPI_GENERATE_NIGHT:
            day_night_str = day_night_str + '_N'
        with pd.ExcelWriter(f'{self.path}/{self.no_recognition}_{self.name}_{timestr}{day_night_str}.xlsx') as writer:
            self.TPRformattedDF.to_excel(writer, sheet_name='TPR')
            self.FPRformattedDF.to_excel(writer, sheet_name='FPR')
            self.resultCTDataFrame.to_excel(writer, sheet_name='Cross')
            # recognition time distribution to excel
            recog_time_percentile_df.fillna(0, inplace=True)
            recog_time_percentile_df.T.to_excel(writer, sheet_name='TRecog')
            # average vehicle speed distribution to excel
            ave_speed_percentile_df.fillna(0, inplace=True)
            ave_speed_percentile_df.T.to_excel(writer, sheet_name='V_average')
            self.resultTPRDataFrame.to_excel(writer, sheet_name='TPR_results')
            self.resultFPRDataFrame.to_excel(writer, sheet_name='FPR_results')

    # HELPERS
    @staticmethod
    def open_json_file(path, name):
        json_path = os.path.join(path, name)
        try:
            with open(json_path, 'rb') as f:
                return json.load(f)
        except Exception as e:
            print(f'CANT OPEN {json_path}')
            print(f'Exception {e}')
            raise e

def main(folder):
    results = KPIReport()
    results.mainLogic(folder)


if __name__ == "__main__":
    start_time = time.time()
    p = c.KPI_GENERATOR_OUTPUT_FOLDER
    for file in os.listdir(p):
        if os.path.isdir(os.path.join(p, file)):
            main(os.path.join(p, file))
    browse_time = time.time()
    print("Script took: ", browse_time - start_time)
