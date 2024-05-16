import os
import numpy as np
import matplotlib.pyplot as plt
import math


class CalPlot:
    def __init__(self, path):
        self.path = path

    @staticmethod
    def get_driven_distance(df):

        time_stamp = np.array(df['timestamp'])
        veh_speed = np.array(df['Velocity'])
        distance = [0]
        last_valid_dist = 0
        for i in range(1, time_stamp.size):
            v_mean = (veh_speed[i] + veh_speed[i - 1]) / 2
            dist = ((time_stamp[i] - time_stamp[i - 1]) * (v_mean / 3600)) + distance[i - 1]
            if not math.isnan(dist):
                last_valid_dist = dist
            distance.append(last_valid_dist)
        df['Distance'] = distance
        return df

    def make_plot(self, df, measurement, hilrep):
        try:
            if df.shape[0] > 0:
                df.reset_index(inplace=True)
                # shift pitch up on plot
                df['CLB_C2W_Pitch_offset'] = df['CLB_C2W_Pitch'] + 200
                # map state to more readable values
                df['CLB_C2W_State_offset'] = df['CLB_C2W_State'].map({15: 8, 51: 10, 60: 15, 83: 30})
                # make time start at zero
                df['time'] = df['timestamp'] - df['timestamp'].iloc[0]
                # add driven distance
                df = self.get_driven_distance(df)
                # define plot signals
                x = df['time']
                y1 = df['CLB_C2W_State_offset']
                y2 = df['CLB_C2W_Pitch_offset']
                y3 = df['FS_Frozen_Windshield_Lens_0']
                y4 = df['FS_Full_Blockage_0']
                y5 = df['FS_Partial_Blockage_0']
                y6 = df['FS_Low_Sun_0']
                y7 = df['FS_Sun_Ray_0']
                y8 = df['FS_Out_Of_Focus_0']
                y9 = df['FS_Rain']
                y10 = df['FS_Splashes_0']
                y11 = df['FS_Fog']
                y12 = df['CLB_C2W_Height']
                y13 = df['Velocity']
                y14 = df['Distance']
                # make plot size bigger
                fig = plt.figure(measurement, figsize=(20, 15), dpi=100)
                # add subplot with ticks every one value
                ax = fig.add_subplot(1, 1, 1)
                major_ticks = np.arange(-250, 251, 10)
                minor_ticks = np.arange(-250, 101, 1)
                ax.set_yticks(major_ticks)
                ax.set_yticks(minor_ticks, minor=True)
                # add a corresponding grid
                ax.grid(which='both')
                # plot signals
                plt.plot(x, y1, label="CLB_C2W_State")
                plt.plot(x, y2, label="CLB_C2W_Pitch")
                plt.plot(x, y12, label="CLB_C2W_Height")
                plt.plot(x, y3, label="FS_Frozen_Windshield")
                plt.plot(x, y4, label="FS_Full_Blockage")
                plt.plot(x, y5, label="FS_Partial_Blockage")
                plt.plot(x, y6, label="FS_Low_Sun")
                plt.plot(x, y7, label="FS_Sun_Ray")
                plt.plot(x, y8, label="FS_Out_Of_Focus")
                plt.plot(x, y9, label="FS_Rain")
                plt.plot(x, y10, label="FS_Splashes")
                plt.plot(x, y11, label="FS_Fog")
                plt.plot(x, y13, label="Velocity")
                plt.plot(x, y14, label="Distance")
                plt.title(measurement + "     " + hilrep)
                plt.legend()
                if not os.path.isdir(self.path):
                    os.makedirs(self.path, exist_ok=True)
                plot_file_name = os.path.join(self.path, hilrep + ".png")
                plt.savefig(plot_file_name)
                plt.clf()
        except Exception as e:
            print(e)
            raise e
