"""
Module takes bad label dictionaries as input, which have one split per event, searches hilrepp json output files, and for each split in input, generates split list for whole event in output
Makes new bad label dictionaries with entire event splits
Patryk Leszowski
APTIV
BWD
"""
import config.constant as c
import sys
import json
import os


class BadLabels:

    PARTIALS_LAB_NAMES = {
        'Blur': c.LAB_BLUR_IMAGE,
        'Fog': c.LAB_FOG,
        'Frozen Windshield': c.LAB_FROZEN_WINDSHIELD,
        'Full Blockage': c.LAB_FULL_BLOCKAGE,
        'Fading by Sun': c.LAB_LOWSUN,
        'Partial Blockage': c.LAB_PARTIAL_BLOCKAGE,
        'Snowfall': c.LAB_SNOWFALL,
        'Rain': c.LAB_RAIN,
        'Road Spray': c.LAB_SPLASHES,
        'Sun Ray': c.LAB_SUNRAY,
        'Free View': c.LAB_FREEVIEW
    }
    # FP bad labeled splits (one split per event) ---------------------------------------------------------------------------------------------------------------------
    FP_BAD_LABEL_CP60 = {
        c.SYS_BLUR: ['ADCAM_WBATR95060NC89209_20211111_081453_pic_0120.pickle.xz',
                     'ADCAM_WBATR95060NC89307_20211027_142854_pic_0531.pickle.xz',
                     'ADCAM_WBATR95060NC89209_20211206_064006_pic_0176.pickle.xz',
                     'ADCAM_WBATR95060NC89209_20220105_060457_pic_0197.pickle.xz',
                     'ADCAM_WBA7G81060B248889_20220114_062940_pic_0217.pickle.xz',
                     'ADCAM_WBATR95060NC89209_20211206_064006_pic_0169.pickle.xz',
                     'ADCAM_WBATR95060NC89307_20220107_163720_pic_0356.pickle.xz',
                     'ADCAM_WBA7G81060B248889_20220118_160238_pic_0526.pickle.xz',
                     'ADCAM_WBATR95060NC89307_20220203_062153_pic_0815.pickle.xz',
                     'ADCAM_WBATR95060NC89307_20211209_063951_pic_1115.pickle.xz'],
        c.SYS_FOG: [],
        c.SYS_FROZEN_WINDSHIELD: ['ADCAM_WBATR95060NC89209_20211206_064006_pic_0169.pickle.xz'],
        c.SYS_FULL_BLOCKAGE: ['ADCAM_WBATX35060NE02496_20220214_064130_pic_0478.pickle.xz'], # test
        c.SYS_FADING_BY_SUN: ['ADCAM_WBATX35060NE02496_20220214_064130_pic_0908.pickle.xz'],
        c.SYS_SUN_RAY: [],
        c.SYS_RAIN: ['ADCAM_WBA7G81060B248889_20211209_165853_pic_0430.pickle.xz',
                     'ADCAM_WBATR95030NC87773_20211215_055931_pic_0359.pickle.xz',
                     'ADCAM_WBATR95030NC87773_20220107_181654_pic_0103.pickle.xz',
                     'ADCAM_WBATR95030NC87773_20220109_121526_pic_0222.pickle.xz',
                     'ADCAM_WBATR95030NC87773_20220119_145523_pic_0964.pickle.xz',
                     'ADCAM_WBATR95030NC87773_20220119_185024_pic_0131.pickle.xz',
                     'ADCAM_WBATR95060NC89209_20211209_171411_pic_0381.pickle.xz',
                     'ADCAM_WBATR95060NC89209_20211209_183941_pic_0150.pickle.xz',
                     'ADCAM_WBATR95060NC89209_20220109_120440_pic_0196.pickle.xz',
                     'ADCAM_WBATR95060NC89307_20220216_061306_pic_0270.pickle.xz',
                     'ADCAM_WBATX35060NE02496_20220109_104528_pic_0940.pickle.xz',
                     'ADCAM_WBATX35060NE02496_20220120_152632_pic_0210.pickle.xz',
                     'ADCAM_WBATX35060NE02496_20220120_200332_pic_0036.pickle.xz',
                     'ADCAM_WBATX35060NE02496_20220210_200134_pic_0030.pickle.xz',
                     'ADCAM_WBATR95060NC89307_20220105_061425_pic_0209.pickle.xz',
                     'ADCAM_WBATR95060NC89209_20220208_063622_pic_0169.pickle.xz',
                     'ADCAM_WBATR95030NC87773_20211124_063917_pic_0174.pickle.xz',
                     'ADCAM_WBATR95060NC89209_20220109_120440_pic_0205.pickle.xz',
                     'ADCAM_WBATR95060NC89307_20220107_163720_pic_0356.pickle.xz',
                     'ADCAM_WBATR95030NC87773_20220216_054928_pic_0289.pickle.xz',
                     'ADCAM_WBATR95030NC87773_20220221_054953_pic_0309.pickle.xz',
                     'ADCAM_WBA7G81060B248889_20211215_062913_pic_0345.pickle.xz',
                     'ADCAM_WBATR95060NC89209_20220105_165313_pic_0478.pickle.xz',
                     'ADCAM_WBATX35060NE02496_20211217_060407_pic_0487.pickle.xz',
                     'ADCAM_WBATR95030NC87773_20211213_055943_pic_0618.pickle.xz',
                     'ADCAM_WBA7G81060B248889_20220203_155103_pic_0623.pickle.xz',
                     'ADCAM_WBA7G81060B248889_20220117_154837_pic_0629.pickle.xz',
                     'ADCAM_WBATX35060NE02496_20211117_155427_pic_0649.pickle.xz',
                     'ADCAM_WBATR95060NC89307_20220127_160124_pic_0912.pickle.xz',
                     'ADCAM_WBATR95060NC89209_20211116_160537_pic_1300.pickle.xz',
                     'ADCAM_WBATR95060NC89209_20211203_151506_pic_1410.pickle.xz',
                     'ADCAM_WBATX35060NE02496_20211119_091916_pic_0070.pickle.xz'],
        c.SYS_PARTIAL_BLOCKAGE: ['ADCAM_WBATR95060NC89209_20211206_064006_pic_0178.pickle.xz',
                                 'ADCAM_WBATR95060NC89307_20220105_061425_pic_0209.pickle.xz'],
        c.SYS_ROAD_SPRAY: [],
        c.SYS_OUT_OF_FOCUS: [],
        c.SYS_FREEVIEW: []
    }

    FP_BAD_LABEL_MID = {
        c.SYS_BLUR: ['ADCAM_WBATR95050NC87113_20190520_180421_pic_0121.pickle.xz',
                     'ADCAM_WBA7H01020B267499_20191001_150025_pic_1051.pickle.xz',
                     'ADCAM_WBA7H01020B267499_20190511_200337_pic_0099.pickle.xz',
                     'ADCAM_WBA7H01000B267498_20210212_184519_pic_0828.pickle.xz',
                     'ADCAM_WBA7G81060B248889_20191213_143823_pic_0133.pickle.xz',
                     'ADCAM_WBA7F21060B236144_20190525_074604_pic_0302.pickle.xz'],
        c.SYS_FOG: ['ADCAM_WBA7H01070B267515_20190404_112734_pic_1229.pickle.xz',
                    'ADCAM_WBA7H01020B267499_20190918_203039_pic_0415.pickle.xz',
                    'ADCAM_WBA7H01020B267499_20190903_232139_pic_0120.pickle.xz',
                    'ADCAM_WBA7H01020B267499_20190903_175925_pic_1525.pickle.xz',
                    'ADCAM_WBA7H01020B267499_20190627_221413_pic_0602.pickle.xz',
                    'ADCAM_WBA7H01020B267499_20190614_222738_pic_0782.pickle.xz',
                    'ADCAM_WBA7H01020B267499_20190607_213938_pic_0200.pickle.xz',
                    'ADCAM_WBA7H01000B267498_20210826_103131_pic_0126.pickle.xz',
                    'ADCAM_WBA7H01000B267498_20201231_000906_pic_0635.pickle.xz',
                    'ADCAM_WBA7H01000B267498_20201219_052600_pic_0258.pickle.xz',
                    'ADCAM_WBA7H01000B267498_20190405_135356_pic_0061.pickle.xz',
                    'ADCAM_WBA7H01000B267498_20190405_092510_pic_1211.pickle.xz',
                    'ADCAM_WBA7H01000B267498_20190404_154043_pic_0605.pickle.xz',
                    'ADCAM_WBA7G81060B248889_20191203_054620_pic_0066.pickle.xz',
                    'ADCAM_WBA7G81060B248889_20190521_233818_pic_0174.pickle.xz',
                    'ADCAM_WBA7G81060B248889_20190521_000605_pic_0546.pickle.xz',
                    'ADCAM_WBA7G81060B248889_20190510_170948_pic_0588.pickle.xz',
                    'ADCAM_WBA7G81060B248889_20190510_072620_pic_0238.pickle.xz',
                    'ADCAM_WBA7G81060B248889_20190509_222817_pic_0200.pickle.xz',
                    'ADCAM_WBA7G81060B248889_20190429_185732_pic_0148.pickle.xz',
                    'ADCAM_WBA7G81020B248890_20201219_040811_pic_0105.pickle.xz',
                    'ADCAM_WBA7G81020B248890_20190619_222917_pic_1658.pickle.xz',
                    'ADCAM_WBA7G81020B248890_20190405_074552_pic_1217.pickle.xz',
                    'ADCAM_WBA7G81020B248890_20190404_101545_pic_1357.pickle.xz',
                    'ADCAM_WBA7F21090B235800_20190528_161702_pic_0888.pickle.xz',
                    'ADCAM_WBA7F21090B235800_20190528_002648_pic_0613.pickle.xz',
                    'ADCAM_WBA7F21060B236144_20190601_030412_pic_0495.pickle.xz',
                    'ADCAM_5UXTR9C51KLE21663_20190504_004742_pic_1415.pickle.xz'],
        c.SYS_FROZEN_WINDSHIELD: ['ADCAM_WBA7H01000B267498_20210208_083602_pic_1718.pickle.xz'],
        c.SYS_FULL_BLOCKAGE: ['ADCAM_WBA7G81020B248890_20210323_195627_pic_0754.pickle.xz'],
        c.SYS_FADING_BY_SUN: ['ADCAM_WBA7H01020B267499_20190425_161057_pic_0758.pickle.xz',
                              'ADCAM_WBA7G81060B248889_20190607_193100_pic_0085.pickle.xz',
                              'ADCAM_WBA7G81060B248889_20190523_190352_pic_0242.pickle.xz',
                              'ADCAM_WBA7G81060B248889_20190514_191248_pic_0363.pickle.xz',
                              'ADCAM_WBA7G81060B248889_20190513_180715_pic_0337.pickle.xz',
                              'ADCAM_WBA7G81020B248890_20200119_124708_pic_0284.pickle.xz',
                              'ADCAM_WBA7G81020B248890_20191015_131523_pic_1178.pickle.xz',
                              'ADCAM_WBA7G81020B248890_20191015_074809_pic_0405.pickle.xz',
                              'ADCAM_WBA7G81020B248890_20190621_202213_pic_0262.pickle.xz',
                              'ADCAM_WBA7G81020B248890_20190615_142408_pic_2191.pickle.xz',
                              'ADCAM_WBA7G81020B248890_20190607_200255_pic_0192.pickle.xz',
                              'ADCAM_WBA7G81020B248890_20190523_180913_pic_0185.pickle.xz',
                              'ADCAM_WBA7G81020B248890_20190523_052546_pic_0763.pickle.xz',
                              'ADCAM_WBA7F21090B235800_20190524_165512_pic_0625.pickle.xz',
                              'ADCAM_WBA7F21080B235965_20191105_222851_pic_0615.pickle.xz',
                              'ADCAM_WBA7F21060B236144_20190501_184933_pic_0858.pickle.xz'],
        c.SYS_SUN_RAY: ['ADCAM_WBATR95050NC87113_20190510_183609_pic_0605.pickle.xz',
                        'ADCAM_WBATR95030NC87773_20191219_074251_pic_0187.pickle.xz',
                        'ADCAM_WBA7H01020B267499_20191009_101636_pic_0144.pickle.xz',
                        'ADCAM_WBA7H01020B267499_20190712_170745_pic_0204.pickle.xz',
                        'ADCAM_WBA7H01020B267499_20190601_181637_pic_0166.pickle.xz',
                        'ADCAM_WBA7H01020B267499_20190529_205903_pic_0090.pickle.xz',
                        'ADCAM_WBA7H01020B267499_20190523_141918_pic_1111.pickle.xz',
                        'ADCAM_WBA7H01000B267498_20190626_163553_pic_0567.pickle.xz',
                        'ADCAM_WBA7G81080G784732_20191009_061537_pic_1138.pickle.xz',
                        'ADCAM_WBA7G81060B248889_20190607_193100_pic_0085.pickle.xz',
                        'ADCAM_WBA7G81060B248889_20190607_161713_pic_0375.pickle.xz',
                        'ADCAM_WBA7G81060B248889_20190603_081915_pic_0258.pickle.xz',
                        'ADCAM_WBA7G81060B248889_20190406_170451_pic_0742.pickle.xz',
                        'ADCAM_WBA7G81060B248889_20190403_155513_pic_1030.pickle.xz',
                        'ADCAM_WBA7G81020B248890_20200203_123659_pic_0137.pickle.xz',
                        'ADCAM_WBA7G81020B248890_20200117_132908_pic_0116.pickle.xz',
                        'ADCAM_WBA7G81020B248890_20191015_131523_pic_1178.pickle.xz',
                        'ADCAM_WBA7G81020B248890_20191009_123619_pic_0429.pickle.xz',
                        'ADCAM_WBA7G81020B248890_20190702_064710_pic_0289.pickle.xz',
                        'ADCAM_WBA7G81020B248890_20190629_163858_pic_1209.pickle.xz',
                        'ADCAM_WBA7G81020B248890_20190614_233446_pic_1239.pickle.xz',
                        'ADCAM_WBA7G81020B248890_20190604_161508_pic_1048.pickle.xz',
                        'ADCAM_WBA7G81020B248890_20190601_081130_pic_0062.pickle.xz',
                        'ADCAM_WBA7F21090B235800_20190525_161300_pic_1009.pickle.xz',
                        'ADCAM_WBA7F21080B236145_20191024_141932_pic_0346.pickle.xz',
                        'ADCAM_WBA7F21080B236145_20191023_115814_pic_0455.pickle.xz',
                        'ADCAM_WBA7F21080B236145_20191022_140617_pic_0122.pickle.xz',
                        'ADCAM_WBA7F21080B236145_20191022_050326_pic_0099.pickle.xz',
                        'ADCAM_WBA7F21080B236145_20191021_062047_pic_0175.pickle.xz',
                        'ADCAM_WBA7F21080B236145_20191021_045447_pic_0261.pickle.xz',
                        'ADCAM_WBA7F21080B236145_20191020_135830_pic_0220.pickle.xz',
                        'ADCAM_WBA7F21080B236145_20191020_050124_pic_0047.pickle.xz',
                        'ADCAM_WBA7F21060B236144_20191113_055858_pic_0461.pickle.xz',
                        'ADCAM_WBA7F21060B236144_20190522_094129_pic_0797.pickle.xz',
                        'ADCAM_WBA7F21060B236144_20190406_165141_pic_0644.pickle.xz'],
        c.SYS_RAIN: ['ADCAM_WBATR95050NC87113_20190817_075520_pic_0347.pickle.xz',
                     'ADCAM_WBATR95050NC87113_20190813_001238_pic_0144.pickle.xz',
                     'ADCAM_WBATR95050NC87113_20190812_210205_pic_0200.pickle.xz',
                     'ADCAM_WBATR95050NC87113_20190808_134630_pic_1445.pickle.xz',
                     'ADCAM_WBATR95050NC87113_20190807_210224_pic_0174.pickle.xz',
                     'ADCAM_WBATR95050NC87113_20190521_095407_pic_1371.pickle.xz',
                     'ADCAM_WBATR95050NC87113_20190509_214412_pic_0061.pickle.xz',
                     'ADCAM_WBATR95050NC87113_20190508_190040_pic_0958.pickle.xz',
                     'ADCAM_WBA7H01020B267499_20191020_154527_pic_1074.pickle.xz',
                     'ADCAM_WBA7H01020B267499_20191020_134945_pic_0220.pickle.xz',
                     'ADCAM_WBA7H01020B267499_20191002_193828_pic_0456.pickle.xz',
                     'ADCAM_WBA7H01020B267499_20191002_143119_pic_0084.pickle.xz',
                     'ADCAM_WBA7H01020B267499_20191001_200254_pic_0032.pickle.xz',
                     'ADCAM_WBA7H01020B267499_20191001_183713_pic_0054.pickle.xz',
                     'ADCAM_WBA7H01020B267499_20190903_072133_pic_1097.pickle.xz',
                     'ADCAM_WBA7H01020B267499_20190822_084100_pic_0140.pickle.xz',
                     'ADCAM_WBA7H01020B267499_20190613_023425_pic_0036.pickle.xz',
                     'ADCAM_WBA7H01020B267499_20190612_225320_pic_0440.pickle.xz',
                     'ADCAM_WBA7H01020B267499_20190612_030330_pic_0036.pickle.xz',
                     'ADCAM_WBA7H01020B267499_20190612_021450_pic_0037.pickle.xz',
                     'ADCAM_WBA7H01020B267499_20190609_011217_pic_0287.pickle.xz',
                     'ADCAM_WBA7H01020B267499_20190608_173828_pic_0270.pickle.xz',
                     'ADCAM_WBA7H01020B267499_20190608_123355_pic_1676.pickle.xz',
                     'ADCAM_WBA7H01020B267499_20190607_232238_pic_0387.pickle.xz',
                     'ADCAM_WBA7H01020B267499_20190604_163552_pic_1523.pickle.xz',
                     'ADCAM_WBA7H01020B267499_20190511_150052_pic_1080.pickle.xz',
                     'ADCAM_WBA7H01020B267499_20190511_012459_pic_0036.pickle.xz',
                     'ADCAM_WBA7H01020B267499_20190511_003952_pic_0051.pickle.xz',
                     'ADCAM_WBA7H01020B267499_20190508_215616_pic_0091.pickle.xz',
                     'ADCAM_WBA7H01020B267499_20190429_224121_pic_0050.pickle.xz',
                     'ADCAM_WBA7H01000B267498_20200220_021920_pic_1061.pickle.xz',
                     'ADCAM_WBA7H01000B267498_20190411_222215_pic_0005.pickle.xz',
                     'ADCAM_WBA7H01000B267498_20190404_220753_pic_0040.pickle.xz',
                     'ADCAM_WBA7H01000B267498_20190404_204121_pic_0317.pickle.xz',
                     'ADCAM_WBA7G81080G784732_20191004_133501_pic_1002.pickle.xz',
                     'ADCAM_WBA7G81080G784732_20191002_111707_pic_0404.pickle.xz',
                     'ADCAM_WBA7G81080G784732_20190918_124200_pic_0084.pickle.xz',
                     'ADCAM_WBA7G81060B248889_20191206_150911_pic_0241.pickle.xz',
                     'ADCAM_WBA7G81060B248889_20190530_164752_pic_0285.pickle.xz',
                     'ADCAM_WBA7G81060B248889_20190523_125425_pic_0072.pickle.xz',
                     'ADCAM_WBA7G81060B248889_20190430_130747_pic_1901.pickle.xz',
                     'ADCAM_WBA7G81060B248889_20190404_193237_pic_0884.pickle.xz',
                     'ADCAM_WBA7G81060B248889_20190404_110100_pic_0740.pickle.xz',
                     'ADCAM_WBA7G81020B248890_20210521_165441_pic_2275.pickle.xz',
                     'ADCAM_WBA7G81020B248890_20200506_015724_pic_0660.pickle.xz',
                     'ADCAM_WBA7G81020B248890_20200304_174411_pic_0690.pickle.xz',
                     'ADCAM_WBA7G81020B248890_20200118_152024_pic_0162.pickle.xz',
                     'ADCAM_WBA7G81020B248890_20191111_090354_pic_0127.pickle.xz',
                     'ADCAM_WBA7G81020B248890_20191003_214014_pic_0030.pickle.xz',
                     'ADCAM_WBA7G81020B248890_20190618_145323_pic_0276.pickle.xz',
                     'ADCAM_WBA7G81020B248890_20190521_143538_pic_1329.pickle.xz',
                     'ADCAM_WBA7G81020B248890_20190429_175325_pic_0878.pickle.xz',
                     'ADCAM_WBA7G81020B248890_20190406_215338_pic_0014.pickle.xz',
                     'ADCAM_WBA7F21090B235800_20190530_030310_pic_0304.pickle.xz',
                     'ADCAM_WBA7F21090B235800_20190528_230212_pic_0498.pickle.xz',
                     'ADCAM_WBA7F21090B235800_20190527_082606_pic_0183.pickle.xz',
                     'ADCAM_WBA7F21090B235800_20190526_220625_pic_0089.pickle.xz',
                     'ADCAM_WBA7F21090B235800_20190526_204327_pic_0140.pickle.xz',
                     'ADCAM_WBA7F21090B235800_20190523_095441_pic_0193.pickle.xz',
                     'ADCAM_WBA7F21080B235965_20191215_041616_pic_1274.pickle.xz',
                     'ADCAM_WBA7F21080B235965_20191027_025816_pic_0030.pickle.xz',
                     'ADCAM_WBA7F21060B236144_20190528_090859_pic_0214.pickle.xz',
                     'ADCAM_WBA7F21060B236144_20190528_080119_pic_0257.pickle.xz',
                     'ADCAM_WBA7F21060B236144_20190526_192951_pic_1447.pickle.xz',
                     'ADCAM_WBA7F21060B236144_20190506_123412_pic_0161.pickle.xz',
                     'ADCAM_WBA7F21060B236144_20190503_235925_pic_0204.pickle.xz',
                     'ADCAM_WBA7F21060B236144_20190501_000735_pic_0035.pickle.xz',
                     'ADCAM_WBA7F21060B236144_20190430_195449_pic_0942.pickle.xz',
                     'ADCAM_WBA7F21060B236144_20190424_201150_pic_0839.pickle.xz',
                     'ADCAM_WBA7F21060B236144_20190405_035116_pic_0036.pickle.xz',
                     'ADCAM_5UXTR9C51KLE21663_20190521_024624_pic_1095.pickle.xz',
                     'ADCAM_WBA7F210X0B235966_20191022_074545_pic_0670.pickle.xz'],
        c.SYS_PARTIAL_BLOCKAGE: ['ADCAM_WBA7H01000B267498_20190404_115432_pic_0418.pickle.xz',
                                 'ADCAM_WBA7G81020B248890_20210412_211303_pic_0311.pickle.xz'],
        c.SYS_ROAD_SPRAY: ['ADCAM_WBA7H01020B267499_20190612_200003_pic_0234.pickle.xz',
                           'ADCAM_WBA7H01020B267499_20190604_163552_pic_1523.pickle.xz',
                           'ADCAM_WBA7G81020B248890_20200213_123642_pic_1486.pickle.xz',
                           'ADCAM_WBA7G81020B248890_20190618_145323_pic_0276.pickle.xz'],
        c.SYS_OUT_OF_FOCUS: [],
        c.SYS_FREEVIEW: []
    }

    # FN bad labeled splits (one split per event) ---------------------------------------------------------------------------------------------------------------------
    FN_BAD_LABEL_CP60 = {
        c.LAB_BLUR_IMAGE: ['ADCAM_WBATR95030NC87773_20220209_075432_pic_0102.pickle.xz'],
        c.LAB_FOG: ['ADCAM_WBATX35060NE02496_20220409_062003_pic_0156.pickle.xz',
                    'ADCAM_WBATX35060NE02496_20211216_060731_pic_0703.pickle.xz',
                    'ADCAM_WBATX35060NE02496_20211112_175836_pic_0177.pickle.xz',
                    'ADCAM_WBATX35060NE02496_20211111_080610_pic_0165.pickle.xz',
                    'ADCAM_WBATR95060NC89307_20211208_071140_pic_0266.pickle.xz',
                    'ADCAM_WBATR95060NC89209_20211111_081453_pic_0157.pickle.xz',
                    'ADCAM_WBATR95030NC87773_20220107_135947_pic_0102.pickle.xz',
                    'ADCAM_WBATR95030NC87773_20211217_055937_pic_0942.pickle.xz',
                    'ADCAM_WBATR95030NC87773_20211216_055826_pic_0848.pickle.xz',
                    'ADCAM_WBA7G81060B248889_20211217_063107_pic_0252.pickle.xz',
                    'ADCAM_WBA7G81060B248889_20211216_063012_pic_0666.pickle.xz',
                    'ADCAM_WBA7G81060B248889_20211028_085845_pic_0128.pickle.xz'],
        c.LAB_FROZEN_WINDSHIELD: [],
        c.LAB_FULL_BLOCKAGE: [],
        c.LAB_LOWSUN: ['ADCAM_WBATX35060NE02496_20220318_145817_pic_0646.pickle.xz',
                       'ADCAM_WBATX35060NE02496_20220214_064130_pic_0383.pickle.xz',
                       'ADCAM_WBATX35060NE02496_20220127_063308_pic_0523.pickle.xz',
                       'ADCAM_WBATR95060NC89307_20220303_150305_pic_0180.pickle.xz',
                       'ADCAM_WBATR95060NC89209_20220301_063846_pic_0730.pickle.xz',
                       'ADCAM_WBATR95060NC89209_20211025_123650_pic_0131.pickle.xz',
                       'ADCAM_WBATR95060NC89209_20211022_132649_pic_0043.pickle.xz',
                       'ADCAM_WBATR95060NC89209_20210930_083523_pic_0536.pickle.xz',
                       'ADCAM_WBATR95030NC87773_20220219_125612_pic_0168.pickle.xz',
                       'ADCAM_WBATR95030NC87773_20220210_094455_pic_0074.pickle.xz',
                       'ADCAM_WBA7G81060B248889_20220228_145930_pic_0164.pickle.xz',
                       'ADCAM_WBA7G81060B248889_20211109_083156_pic_0537.pickle.xz'],
        c.LAB_PARTIAL_BLOCKAGE: ['ADCAM_WBATX35060NE02496_20211206_060637_pic_0228.pickle.xz',
                                 'ADCAM_WBATR95060NC89307_20220302_063922_pic_1896.pickle.xz',
                                 'ADCAM_WBATR95060NC89307_20211221_070716_pic_0569.pickle.xz',
                                 'ADCAM_WBATR95060NC89307_20211208_180312_pic_0186.pickle.xz',
                                 'ADCAM_WBATR95060NC89307_20211119_171534_pic_0011.pickle.xz',
                                 'ADCAM_WBATR95060NC89307_20210906_164431_pic_0222.pickle.xz',
                                 'ADCAM_WBATR95060NC89307_20210821_102615_pic_1212.pickle.xz',
                                 'ADCAM_WBATR95030NC87773_20211105_193137_pic_0014.pickle.xz',
                                 'ADCAM_WBATR95030NC87773_20211014_180316_pic_1447.pickle.xz'],
        c.LAB_SNOWFALL: ['ADCAM_WBATX35060NE02496_20220121_062951_pic_0102.pickle.xz'],
        c.LAB_RAIN: ['ADCAM_WBATX35060NE02496_20220211_063031_pic_0240.pickle.xz',
                     'ADCAM_WBATX35060NE02496_20220210_200134_pic_0037.pickle.xz',
                     'ADCAM_WBATX35060NE02496_20220210_165644_pic_0324.pickle.xz',
                     'ADCAM_WBATX35060NE02496_20220207_094952_pic_0036.pickle.xz',
                     'ADCAM_WBATX35060NE02496_20220201_155113_pic_0432.pickle.xz',
                     'ADCAM_WBATX35060NE02496_20220120_200332_pic_0042.pickle.xz',
                     'ADCAM_WBATX35060NE02496_20220107_151745_pic_0534.pickle.xz',
                     'ADCAM_WBATX35060NE02496_20211214_155910_pic_1194.pickle.xz',
                     'ADCAM_WBATX35060NE02496_20211209_155508_pic_0432.pickle.xz',
                     'ADCAM_WBATX35060NE02496_20211119_065651_pic_0213.pickle.xz',
                     'ADCAM_WBATX35060NE02496_20211117_155427_pic_0628.pickle.xz',
                     'ADCAM_WBATX35060NE02496_20211116_190558_pic_0634.pickle.xz',
                     'ADCAM_WBATR95060NC89307_20220315_165301_pic_0132.pickle.xz',
                     'ADCAM_WBATR95060NC89307_20220211_062255_pic_0492.pickle.xz',
                     'ADCAM_WBATR95060NC89307_20220126_161928_pic_0432.pickle.xz',
                     'ADCAM_WBATR95060NC89307_20220125_061339_pic_0594.pickle.xz',
                     'ADCAM_WBATR95060NC89307_20220109_120458_pic_0078.pickle.xz',
                     'ADCAM_WBATR95060NC89307_20220104_151421_pic_0444.pickle.xz',
                     'ADCAM_WBATR95060NC89307_20211203_140306_pic_2256.pickle.xz',
                     'ADCAM_WBATR95060NC89307_20210827_130114_pic_0334.pickle.xz',
                     'ADCAM_WBATR95060NC89209_20220225_150715_pic_0675.pickle.xz',
                     'ADCAM_WBATR95060NC89209_20220221_153409_pic_0201.pickle.xz',
                     'ADCAM_WBATR95060NC89209_20220221_063550_pic_0036.pickle.xz',
                     'ADCAM_WBATR95060NC89209_20220218_151819_pic_0114.pickle.xz',
                     'ADCAM_WBATR95060NC89209_20220216_160027_pic_0112.pickle.xz',
                     'ADCAM_WBATR95060NC89209_20220216_142205_pic_0253.pickle.xz',
                     'ADCAM_WBATR95060NC89209_20220215_063614_pic_0150.pickle.xz',
                     'ADCAM_WBATR95060NC89209_20220208_063622_pic_0144.pickle.xz',
                     'ADCAM_WBATR95060NC89209_20220201_102612_pic_0289.pickle.xz',
                     'ADCAM_WBATR95060NC89209_20220131_064141_pic_0126.pickle.xz',
                     'ADCAM_WBATR95060NC89209_20220128_180513_pic_0252.pickle.xz',
                     'ADCAM_WBATR95060NC89209_20220127_150547_pic_0120.pickle.xz',
                     'ADCAM_WBATR95060NC89209_20220127_064843_pic_0102.pickle.xz',
                     'ADCAM_WBATR95060NC89209_20220109_120440_pic_0167.pickle.xz',
                     'ADCAM_WBATR95060NC89209_20220107_175006_pic_0120.pickle.xz',
                     'ADCAM_WBATR95060NC89209_20211209_171411_pic_0325.pickle.xz',
                     'ADCAM_WBATR95060NC89209_20211207_064128_pic_0102.pickle.xz',
                     'ADCAM_WBATR95060NC89209_20211203_151506_pic_0615.pickle.xz',
                     'ADCAM_WBATR95060NC89209_20211111_160931_pic_0432.pickle.xz',
                     'ADCAM_WBATR95060NC89209_20211006_160405_pic_0030.pickle.xz',
                     'ADCAM_WBATR95030NC87773_20220216_161229_pic_0309.pickle.xz',
                     'ADCAM_WBATR95030NC87773_20220216_145350_pic_0389.pickle.xz',
                     'ADCAM_WBATR95030NC87773_20220215_125619_pic_0150.pickle.xz',
                     'ADCAM_WBATR95030NC87773_20220204_055839_pic_0336.pickle.xz',
                     'ADCAM_WBATR95030NC87773_20220127_145449_pic_0408.pickle.xz',
                     'ADCAM_WBATR95030NC87773_20220127_075641_pic_0144.pickle.xz',
                     'ADCAM_WBATR95030NC87773_20220120_145725_pic_0121.pickle.xz',
                     'ADCAM_WBATR95030NC87773_20211222_145705_pic_1174.pickle.xz',
                     'ADCAM_WBATR95030NC87773_20211214_145923_pic_0716.pickle.xz',
                     'ADCAM_WBATR95030NC87773_20211214_060016_pic_0150.pickle.xz',
                     'ADCAM_WBATR95030NC87773_20211210_150214_pic_0312.pickle.xz',
                     'ADCAM_WBATR95030NC87773_20211210_055716_pic_0373.pickle.xz',
                     'ADCAM_WBATR95030NC87773_20211201_150107_pic_0963.pickle.xz',
                     'ADCAM_WBATR95030NC87773_20211125_150000_pic_0826.pickle.xz',
                     'ADCAM_WBA7G81060B248889_20220224_154230_pic_0120.pickle.xz',
                     'ADCAM_WBA7G81060B248889_20220218_105749_pic_0098.pickle.xz',
                     'ADCAM_WBA7G81060B248889_20220209_064908_pic_0222.pickle.xz',
                     'ADCAM_WBA7G81060B248889_20220204_145807_pic_0816.pickle.xz',
                     'ADCAM_WBA7G81060B248889_20220203_095835_pic_0036.pickle.xz',
                     'ADCAM_WBA7G81060B248889_20220202_155629_pic_0565.pickle.xz',
                     'ADCAM_WBA7G81060B248889_20220127_091224_pic_0207.pickle.xz',
                     'ADCAM_WBA7G81060B248889_20220126_155346_pic_0420.pickle.xz',
                     'ADCAM_WBA7G81060B248889_20220126_063143_pic_0648.pickle.xz',
                     'ADCAM_WBA7G81060B248889_20220121_063332_pic_0360.pickle.xz',
                     'ADCAM_WBA7G81060B248889_20220112_154921_pic_0408.pickle.xz',
                     'ADCAM_WBA7G81060B248889_20220112_062429_pic_0794.pickle.xz',
                     'ADCAM_WBA7G81060B248889_20211215_062913_pic_0288.pickle.xz',
                     'ADCAM_WBA7G81060B248889_20211213_063043_pic_0416.pickle.xz',
                     'ADCAM_WBA7G81060B248889_20211210_150141_pic_0606.pickle.xz',
                     'ADCAM_WBA7G81060B248889_20211210_063810_pic_0438.pickle.xz',
                     'ADCAM_WBA7G81060B248889_20211206_063201_pic_0484.pickle.xz',
                     'ADCAM_WBA7G81060B248889_20211203_160218_pic_0634.pickle.xz',
                     'ADCAM_WBA7G81060B248889_20211117_182058_pic_0104.pickle.xz',
                     'ADCAM_WBA7G81060B248889_20211117_063601_pic_0521.pickle.xz',
                     'ADCAM_WBA7G81060B248889_20211116_161004_pic_0672.pickle.xz',
                     'ADCAM_WBA7G81060B248889_20211019_150445_pic_0078.pickle.xz',
                     'ADCAM_WBA7G81060B248889_20210826_074200_pic_0241.pickle.xz'],
        c.LAB_SPLASHES: ['ADCAM_WBATX35060NE02496_20220104_153017_pic_0498.pickle.xz',
                         'ADCAM_WBATR95060NC89209_20220304_065038_pic_0136.pickle.xz',
                         'ADCAM_WBATR95030NC87773_20220109_121526_pic_0216.pickle.xz',
                         'ADCAM_WBA7G81060B248889_20220222_163303_pic_0198.pickle.xz',
                         'ADCAM_WBA7G81060B248889_20211019_150445_pic_0078.pickle.xz'],
        c.LAB_SUNRAY: ['ADCAM_WBATX35060NE02496_20211029_142848_pic_0288.pickle.xz',
                       'ADCAM_WBATR95060NC89307_20220307_162206_pic_0528.pickle.xz',
                       'ADCAM_WBATR95060NC89307_20220304_060318_pic_0518.pickle.xz',
                       'ADCAM_WBATR95060NC89209_20220301_150522_pic_0252.pickle.xz',
                       'ADCAM_WBA7G81060B248889_20211222_104857_pic_0384.pickle.xz'],
        c.LAB_FREEVIEW: []
    }

    FN_BAD_LABEL_MID = {
        c.LAB_BLUR_IMAGE: ['ADCAM_WBA7H01000B267498_20210507_194845_pic_0012.pickle.xz'],
        c.LAB_FOG: ['ADCAM_WBA7H01020B267499_20190430_193953_pic_0090.pickle.xz',
                    'ADCAM_WBA7H01000B267498_20201219_065354_pic_0030.pickle.xz',
                    'ADCAM_WBA7G81020B248890_20201219_040811_pic_0038.pickle.xz'],
        c.LAB_FROZEN_WINDSHIELD: [],
        c.LAB_FULL_BLOCKAGE: [],
        c.LAB_LOWSUN: ['ADCAM_WBA7H01070B267515_20190514_153531_pic_0142.pickle.xz',
                       'ADCAM_WBA7H01070B267515_20190424_143755_pic_0070.pickle.xz',
                       'ADCAM_WBA7H01020B267499_20191021_143934_pic_0565.pickle.xz',
                       'ADCAM_WBA7H01020B267499_20190528_100955_pic_0228.pickle.xz',
                       'ADCAM_WBA7H01020B267499_20190517_151512_pic_0417.pickle.xz',
                       'ADCAM_WBA7H01020B267499_20190510_150320_pic_0395.pickle.xz',
                       'ADCAM_WBA7H01020B267499_20190427_155641_pic_0043.pickle.xz',
                       'ADCAM_WBA7H01000B267498_20190413_182828_pic_0194.pickle.xz',
                       'ADCAM_WBA7H01000B267498_20190410_161617_pic_0683.pickle.xz',
                       'ADCAM_WBA7G81060B248889_20190509_150424_pic_0074.pickle.xz',
                       'ADCAM_WBA7G81060B248889_20190426_122651_pic_0832.pickle.xz',
                       'ADCAM_WBA7G81060B248889_20190426_091107_pic_0553.pickle.xz',
                       'ADCAM_WBA7G81060B248889_20190413_072235_pic_0258.pickle.xz',
                       'ADCAM_WBA7G81020B248890_20190528_093045_pic_0333.pickle.xz',
                       'ADCAM_WBA7G81020B248890_20190525_175116_pic_0236.pickle.xz',
                       'ADCAM_WBA7G81020B248890_20190416_085223_pic_0056.pickle.xz',
                       'ADCAM_WBA7F21060B236144_20190601_093147_pic_0054.pickle.xz',
                       'ADCAM_WBA7F21060B236144_20190509_214308_pic_0164.pickle.xz',
                       'ADCAM_WBA7F21060B236144_20190413_123202_pic_0217.pickle.xz'],
        c.LAB_PARTIAL_BLOCKAGE: ['ADCAM_WBA7H01000B267498_20210212_184519_pic_0174.pickle.xz'],
        c.LAB_SNOWFALL: [],
        c.LAB_RAIN: ['ADCAM_WBATR95050NC87113_20190527_172002_pic_0122.pickle.xz',
                     'ADCAM_WBATR95050NC87113_20190519_195634_pic_0595.pickle.xz',
                     'ADCAM_WBATR95050NC87113_20190508_190040_pic_0824.pickle.xz',
                     'ADCAM_WBATR95050NC87113_20190508_131957_pic_0304.pickle.xz',
                     'ADCAM_WBATR95030NC87773_20200511_162300_pic_0926.pickle.xz',
                     'ADCAM_WBATR95030NC87773_20200329_221218_pic_0048.pickle.xz',
                     'ADCAM_WBATR95030NC87773_20200227_111348_pic_0270.pickle.xz',
                     'ADCAM_WBA7H01070B267515_20190413_011644_pic_0009.pickle.xz',
                     'ADCAM_WBA7H01030B267513_20191009_101404_pic_0810.pickle.xz',
                     'ADCAM_WBA7H01020B267499_20190527_212350_pic_1177.pickle.xz',
                     'ADCAM_WBA7H01020B267499_20190516_222439_pic_0039.pickle.xz',
                     'ADCAM_WBA7H01020B267499_20190510_230604_pic_0238.pickle.xz',
                     'ADCAM_WBA7H01020B267499_20190508_215616_pic_0068.pickle.xz',
                     'ADCAM_WBA7H01000B267498_20210828_145136_pic_0348.pickle.xz',
                     'ADCAM_WBA7H01000B267498_20210828_103055_pic_0273.pickle.xz',
                     'ADCAM_WBA7H01000B267498_20210828_084328_pic_0211.pickle.xz',
                     'ADCAM_WBA7H01000B267498_20210826_103131_pic_0054.pickle.xz',
                     'ADCAM_WBA7H01000B267498_20190731_083040_pic_0481.pickle.xz',
                     'ADCAM_WBA7H01000B267498_20190413_221405_pic_0044.pickle.xz',
                     'ADCAM_WBA7G81060B248889_20191213_112815_pic_0192.pickle.xz',
                     'ADCAM_WBA7G81060B248889_20190522_151637_pic_0175.pickle.xz',
                     'ADCAM_WBA7G81060B248889_20190403_195912_pic_2637.pickle.xz',
                     'ADCAM_WBA7G81020B248890_20210522_140632_pic_0121.pickle.xz',
                     'ADCAM_WBA7G81020B248890_20210412_211303_pic_0018.pickle.xz',
                     'ADCAM_WBA7G81020B248890_20200205_150755_pic_1224.pickle.xz',
                     'ADCAM_WBA7G81020B248890_20191114_191338_pic_0051.pickle.xz',
                     'ADCAM_WBA7G81020B248890_20190706_202036_pic_0342.pickle.xz',
                     'ADCAM_WBA7G81020B248890_20190510_095115_pic_0058.pickle.xz',
                     'ADCAM_WBA7G81020B248890_20190430_132851_pic_0357.pickle.xz',
                     'ADCAM_WBA7G81020B248890_20190416_174913_pic_0234.pickle.xz',
                     'ADCAM_WBA7F21090B235800_20190530_030310_pic_0127.pickle.xz',
                     'ADCAM_WBA7F21080B236145_20191022_185456_pic_0480.pickle.xz',
                     'ADCAM_WBA7F21080B235965_20191106_233707_pic_0942.pickle.xz',
                     'ADCAM_WBA7F21060B236144_20190426_234757_pic_0625.pickle.xz',
                     'ADCAM_WBA7F21060B236144_20190426_212310_pic_0539.pickle.xz',
                     'ADCAM_WBA7F21060B236144_20190414_103408_pic_0266.pickle.xz',
                     'ADCAM_WBA7F210X0B235966_20191023_084542_pic_0702.pickle.xz',
                     'ADCAM_WBA7F210X0B235966_20200102_072529_pic_0349.pickle.xz'],
        c.LAB_SPLASHES: ['ADCAM_WBATR95050NC87113_20190519_195634_pic_0595.pickle.xz',
                         'ADCAM_WBA7H01070B267515_20190510_023230_pic_0035.pickle.xz',
                         'ADCAM_WBA7H01020B267499_20190514_132045_pic_0193.pickle.xz',
                         'ADCAM_WBA7G81020B248890_20210606_135211_pic_0168.pickle.xz',
                         'ADCAM_WBA7G81020B248890_20210522_140632_pic_0121.pickle.xz',
                         'ADCAM_WBA7G81020B248890_20190510_095115_pic_0058.pickle.xz'],
        c.LAB_SUNRAY: ['ADCAM_WBA7H01020B267499_20191022_064817_pic_0768.pickle.xz',
                       'ADCAM_WBA7G81020B248890_20190605_171406_pic_0092.pickle.xz',
                       'ADCAM_WBA7G81020B248890_20190425_143906_pic_0245.pickle.xz',
                       'ADCAM_WBA7F21060B236144_20190524_144341_pic_0136.pickle.xz',
                       'ADCAM_WBA7F21060B236144_20190524_100645_pic_0239.pickle.xz'],
        c.LAB_FREEVIEW: []
    }


class BadLabelFinder(BadLabels):

    def __init__(self):
        self.project = c.PROJECT
        if self.project == 'cp60':
            self.path_to_hilreps = c.BAD_LABELS_PATH_TO_PARTIAL_RESULTS_CP60
        elif self.project == 'mid':
            self.path_to_hilreps = c.BAD_LABELS_PATH_TO_PARTIAL_RESULTS_MID
        else:
            print(f'WRONG PROJECT: {self.project}')
            sys.exit()
        # self.bad_label_events_output_dict_path = r'/net/8k3/e0fs01/irods/PLKRA-PROJECTS/ADCAM/7-Tools/ADCAM/BWD/scripts_new_logic/BWD_BAD_LABELS'
        self.bad_label_events_output_dict_path = c.BAD_LABEL_DICT_FOLDER
        self.ext = '.json'
        self.label_name_dict = c.PARTIALS_NAMES_LAB
        self.signal_name_dict = c.PARTIALS_NAMES_SYS
        self.name_to_label_dict = self.PARTIALS_LAB_NAMES
        self.hilrep_output_json_list = []
        self.hilrep_full_fn_events_dict = {}  # dictionary of all fn events from path_to_hilreps
        self.hilrep_full_fp_events_dict = {}  # dictionary of all fp events from path_to_hilreps
        self.hilrep_full_fn_events_counters_dict = {}
        self.hilrep_full_fp_events_counters_dict = {}
        self.bad_label_fn_events_output_dict = {}  # fn output dictionary with matched bad labels to events
        self.bad_label_fp_events_output_dict = {}  # fn output dictionary with matched bad labels to events
        self.bad_labels_fn_dict = {}  # fn bad label dictionary
        self.bad_labels_fp_dict = {}  # fp bad label dictionary
        super().__init__()

    def init_dict(self):
        for fs in self.label_name_dict.keys():
            self.hilrep_full_fn_events_dict[fs] = {}
            self.bad_label_fn_events_output_dict[fs] = []
            self.hilrep_full_fn_events_counters_dict[fs] = 0
        for fs in self.signal_name_dict.keys():
            self.hilrep_full_fp_events_dict[fs] = {}
            self.bad_label_fp_events_output_dict[fs] = []
            self.hilrep_full_fp_events_counters_dict[fs] = 0
        if self.project == 'cp60':
            self.bad_labels_fn_dict = self.FN_BAD_LABEL_CP60
            self.bad_labels_fp_dict = self.FP_BAD_LABEL_CP60
        elif self.project == 'mid':
            self.bad_labels_fn_dict = self.FN_BAD_LABEL_MID
            self.bad_labels_fp_dict = self.FP_BAD_LABEL_MID
        else:
            print(f'WRONG PROJECT: {self.project}')
            sys.exit()

    def get_df_files(self):
        try:
            allfiles = os.listdir(self.path_to_hilreps)
        except (FileNotFoundError, PermissionError, NotADirectoryError) as e:
            print(f'DfBinder: ERROR: Cant open {self.path_to_hilreps}')
            print(e)
            raise e
        else:
            if allfiles:
                for file in allfiles:
                    if file.endswith(self.ext):
                        self.hilrep_output_json_list.append(file)
            else:
                print(f'DfBinder: No pickles in {self.path_to_hilreps}')
                print(FileNotFoundError)
                raise FileNotFoundError

    @staticmethod
    def load_json(path, file=None):
        """
        Load object
        :param path: path to folder
        :param file: json file name
        :return:
        """
        if file:
            if '.json' not in file:
                filename = file + '.json'
            else:
                filename = file
            path = os.path.join(path, filename)
        try:
            with open(path, 'r') as f:
                print(f'loading json: {path}')
                return json.load(f)
        except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
            print(f'failed to load json: {path}')
            print(e)
            raise e

    @staticmethod
    def save_json(obj, path, file=None):
        """
        :param obj: object to be serialized
        :param path: path to folder
        :param file: file name
        :return:
        Save object to json
        """
        print(f'saving json: {file}')
        if file:
            if '.json' not in file:
                filename = file + '.json'
            else:
                filename = file
            path = os.path.join(path, filename)
        try:
            with open(path, 'w') as f:
                json.dump(obj, f, indent=2)
        except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
            print(f'failed to save json: {path}')
            print(e)
            raise e

    @staticmethod
    def generate_event_list(start_split, stop_split):
        split_list = []
        log_name = start_split[0:44]
        start_log_int = int(start_split[44:48])
        stop_log_int = int(stop_split[44:48])
        for i in range(start_log_int, stop_log_int + 1):
            i_string = f'{log_name}{i:04d}.pickle.xz'
            split_list.append(i_string)
        return split_list

    def get_hilrep_full_events(self):
        # make dictionaries (2) of all fn and fp events in path_to_hilreps
        for file in self.hilrep_output_json_list:
            hilrep_list = self.load_json(self.path_to_hilreps, file)
            for hilrep_dict in hilrep_list:
                if type(hilrep_dict) == dict:
                    if "LabeledFs" in hilrep_dict.keys():
                        fn_event_list = hilrep_dict["LabeledFs"]
                        for fn_dict in fn_event_list:
                            if "FsName" in fn_dict.keys() and "LogNameEventStart" in fn_dict.keys() and "LogNameEventStop" in fn_dict.keys() and "IsRecognition" in fn_dict.keys():
                                if not fn_dict["IsRecognition"]:
                                    fs = self.name_to_label_dict[fn_dict["FsName"]]
                                    start_split = fn_dict["LogNameEventStart"]
                                    stop_split = fn_dict["LogNameEventStop"]
                                    event_list = self.generate_event_list(start_split, stop_split)
                                    self.hilrep_full_fn_events_dict[fs][self.hilrep_full_fn_events_counters_dict[fs]] = event_list
                                    self.hilrep_full_fn_events_counters_dict[fs] += 1
                    if "FalsePositive" in hilrep_dict.keys():
                        fn_event_list = hilrep_dict["FalsePositive"]
                        for fn_dict in fn_event_list:
                            if "FsName" in fn_dict.keys() and "LogNameEventStart" in fn_dict.keys() and "LogNameEventStop" in fn_dict.keys():
                                fs = fn_dict["FsName"]
                                start_split = fn_dict["LogNameEventStart"]
                                stop_split = fn_dict["LogNameEventStop"]
                                event_list = self.generate_event_list(start_split, stop_split)
                                self.hilrep_full_fp_events_dict[fs][self.hilrep_full_fp_events_counters_dict[fs]] = event_list
                                self.hilrep_full_fp_events_counters_dict[fs] += 1

    def make_output_bad_labeled_events_dicts(self):
        # FN
        for fs in self.label_name_dict.keys():
            for bad_label_split in self.bad_labels_fn_dict[fs]:
                bad_label_event_dict = self.hilrep_full_fn_events_dict[fs]
                if bad_label_event_dict:
                    for bad_label_event_list in bad_label_event_dict.values():
                        if bad_label_split in bad_label_event_list:
                            self.bad_label_fn_events_output_dict[fs] += bad_label_event_list
        for fs, event_list in self.bad_label_fn_events_output_dict.items():
            sorted_list = list(set(event_list))
            sorted_list.sort()
            self.bad_label_fn_events_output_dict[fs] = sorted_list

        # FP
        for fs in self.signal_name_dict.keys():
            for bad_label_split in self.bad_labels_fp_dict[fs]:
                bad_label_event_dict = self.hilrep_full_fp_events_dict[fs]
                if bad_label_event_dict:
                    for bad_label_event_list in bad_label_event_dict.values():
                        if bad_label_split in bad_label_event_list:
                            self.bad_label_fp_events_output_dict[fs] += bad_label_event_list
        for fs, event_list in self .bad_label_fp_events_output_dict.items():
            if event_list:
                sorted_list = list(set(event_list))
                sorted_list.sort()
                self.bad_label_fp_events_output_dict[fs] = sorted_list

    def save_output_bad_labeled_events_dicts(self):
        if not os.path.isdir(self.bad_label_events_output_dict_path):
            os.makedirs(self.bad_label_events_output_dict_path, exist_ok=True)
        self.save_json(self.bad_label_fn_events_output_dict, self.bad_label_events_output_dict_path, f'bad_label_events_{self.project}_fn.json')
        self.save_json(self.bad_label_fp_events_output_dict, self.bad_label_events_output_dict_path, f'bad_label_events_{self.project}_fp.json')


def main():
    bad_label_finder = BadLabelFinder()
    bad_label_finder.init_dict()
    bad_label_finder.get_df_files()
    bad_label_finder.get_hilrep_full_events()
    bad_label_finder.make_output_bad_labeled_events_dicts()
    bad_label_finder.save_output_bad_labeled_events_dicts()
    print()


if __name__ == "__main__":
    main()
