# -*- coding: utf-8 -*-
# purpose:  Loads PHINS and DMS data P-37
# author:   Márcio Yamashita
# created:  09-Oct-2017
# modified:

import pandas as pd
from datetime import datetime, timedelta
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
degree = u"\u00b0"

def clean_ax(axes):
    u""" Limpeza de eixo temporal."""
    axes.fmt_xdata = DateFormatter('%d/%m/%y %H:%M:%S')
    for label in axes.xaxis.get_majorticklabels():
        label.set_visible(False)
    for label in axes.xaxis.get_minorticklabels():
        label.set_visible(False)

if __name__ == '__main__':

    bd_dms = '.\\DMS\\DMS_raw.db'
    bd_phins = '.\\PHINS\\PHINS_raw.db'
    bd_quadrans = '.\\QUADRANS\\QUADRANS_raw.db'
    gps_file = '.\\GPS\gps.xlsx'

    conn_DMS = sqlite3.connect(bd_dms)
    conn_PHINS = sqlite3.connect(bd_phins)
    conn_QUADRANS = sqlite3.connect(bd_quadrans)

    qry = ("SELECT *"
           " FROM TB_DMS;")
    df_dms = pd.read_sql_query(qry, conn_DMS, index_col='time',
                               parse_dates={'time': '%Y-%m-%d %H:%M:%S'})

    qry = ("SELECT *"
           " FROM TB_PHINS;")
    df_phins = pd.read_sql_query(qry, conn_PHINS, index_col='time',
                                 parse_dates={'time': '%Y-%m-%d %H:%M:%S'})

    qry = ("SELECT *"
           " FROM TB_QUADRANS;")
    df_quadrans = pd.read_sql_query(qry, conn_QUADRANS, index_col='time',
                                    parse_dates={'time': '%Y-%m-%d %H:%M:%S'})

    gps_data = pd.read_excel(gps_file, names=['data', 'aproa.', 'roll', 'pitch'])
    gps_data.index = gps_data['data']
    gps_data = gps_data.drop(['data'], axis=1)

    offset_pitch_phins = np.mean(gps_data.pitch - df_phins.pitch)
    df_phins['pitch_fixed'] = df_phins.pitch+offset_pitch_phins
    offset_roll_phins = np.mean(gps_data.roll - df_phins.roll)
    df_phins['roll_fixed'] = df_phins.roll + offset_roll_phins

    offset_pitch_dms = np.mean(df_phins.pitch_fixed - (-1*df_dms.pitch))
    df_dms['pitch_fixed'] = (-1*df_dms.pitch) + offset_pitch_dms
    offset_roll_dms = np.mean(df_phins.roll_fixed - df_dms.roll)
    df_dms['roll_fixed'] = df_dms.roll + offset_roll_dms

    offset_pitch_quadrans = np.mean(df_phins.pitch_fixed - df_quadrans.pitch)
    df_quadrans['pitch_fixed'] = df_quadrans.pitch + offset_pitch_quadrans
    offset_quadrans_dms = np.mean(df_phins.roll_fixed - df_quadrans.roll)
    df_quadrans['roll_fixed'] = df_quadrans.roll + offset_quadrans_dms

    # figures
    fig = plt.figure(facecolor=(1.0, 1.0, 1.0), figsize=(12, 8))
    axPT = fig.add_subplot(311)
    axRL = fig.add_subplot(312, sharex=axPT)
    axHV = fig.add_subplot(313, sharex=axPT)

    # axPT.plot(df_dms.pitch)
    axPT.plot(df_quadrans.pitch)
    axPT.plot(-df_dms.pitch-1.857, alpha=0.7)
    axPT.plot(df_phins.pitch, alpha=0.5)
    axPT.plot(gps_data.pitch, alpha=0.5)
    axPT.grid()
    axPT.set_ylabel('PITCH [%s]' % degree)
    axPT.legend(['QUADRANS', 'DMS_fixed', 'PHINS', 'GPS'])
    clean_ax(axPT)

    axRL.plot(df_quadrans.roll)
    axRL.plot(df_dms.roll, alpha=0.5)
    axRL.plot(df_phins.roll, alpha=0.7)
    axRL.plot(gps_data.roll, alpha=0.5)
    axRL.grid()
    axRL.set_ylabel('ROLL [%s]' % degree)
    axRL.legend(['QUADRANS', 'DMS_DADAS', 'PHINS', 'GPS'])
    clean_ax(axRL)

    axHV.plot(df_quadrans.heave)
    axHV.plot(df_dms.heave, alpha=0.7)
    axHV.plot(df_phins.heave, alpha=0.5)
    axHV.grid()
    axHV.set_ylabel('HEAVE [m]')
    axHV.legend(['QUADRANS', 'DMS_DADAS', 'PHINS'])
    axHV.xaxis.set_major_formatter(DateFormatter('%d/%m/%y\n %H:%M:%S'))
    for label in axHV.xaxis.get_majorticklabels():
        label.set_rotation(45)
    for label in axHV.xaxis.get_minorticklabels():
        label.set_rotation(45)

    # figure calibrate  PHINS
    fig = plt.figure(facecolor=(1.0, 1.0, 1.0), figsize=(12, 8))
    axPT = fig.add_subplot(211)
    axRL = fig.add_subplot(212, sharex=axPT)

    axPT.plot(df_phins.pitch, 'm', alpha=0.5)
    axPT.plot(gps_data.pitch, 'r', alpha=0.5)
    axPT.grid()
    axPT.set_title('Atitudes de [PHINS VS GPS]')
    axPT.set_ylabel('PITCH [%s]' % degree)
    axPT.legend(['PHINS', 'GPS'])
    clean_ax(axPT)

    axRL.plot(df_phins.roll, 'm', alpha=0.5)
    axRL.plot(gps_data.roll, 'r', alpha=0.5)
    axRL.set_xlim([gps_data.index.min(), gps_data.index.max()])
    axRL.grid()
    axRL.set_ylabel('ROLL [%s]' % degree)
    axRL.legend(['PHINS', 'GPS'])
    axRL.xaxis.set_major_formatter(DateFormatter('%d/%m/%y\n %H:%M:%S'))
    for label in axRL.xaxis.get_majorticklabels():
        label.set_rotation(45)
    for label in axRL.xaxis.get_minorticklabels():
        label.set_rotation(45)

    # figure fix PHINS
    fig = plt.figure(facecolor=(1.0, 1.0, 1.0), figsize=(12, 8))
    axPT = fig.add_subplot(211)
    axRL = fig.add_subplot(212, sharex=axPT)

    axPT.plot(df_phins.pitch_fixed, 'm', alpha=0.5)
    axPT.plot(gps_data.pitch, 'r', alpha=0.5)
    axPT.grid()
    axPT.set_title('PHINS ajustada via GPS')
    axPT.set_ylabel('PITCH [%s]' % degree)
    axPT.legend(['PHINS_FIXED', 'GPS'])
    clean_ax(axPT)

    axRL.plot(df_phins.roll_fixed, 'm', alpha=0.5)
    axRL.plot(gps_data.roll, 'r', alpha=0.5)
    axRL.grid()
    axRL.set_ylabel('ROLL [%s]' % degree)
    axRL.set_xlim([gps_data.index.min(), gps_data.index.max()])
    axRL.legend(['PHINS_FIXED', 'GPS'])
    axRL.xaxis.set_major_formatter(DateFormatter('%d/%m/%y\n %H:%M:%S'))
    for label in axRL.xaxis.get_majorticklabels():
        label.set_rotation(45)
    for label in axRL.xaxis.get_minorticklabels():
        label.set_rotation(45)

    # figure calibrate  DMS
    fig = plt.figure(facecolor=(1.0, 1.0, 1.0), figsize=(12, 8))
    axPT = fig.add_subplot(211)
    axRL = fig.add_subplot(212, sharex=axPT)

    axPT.plot(df_dms.pitch, 'c', alpha=0.5)
    axPT.plot(df_phins.pitch_fixed, 'm', alpha=0.5)
    axPT.grid()
    axPT.set_title('Atitudes de [DMS VS PHINS]')
    axPT.set_ylabel('PITCH [%s]' % degree)
    axPT.legend(['DMS', 'PHINS_FIXED'])

    clean_ax(axPT)
    axRL.plot(df_dms.roll, 'c', alpha=0.5)
    axRL.plot(df_phins.roll_fixed, 'm', alpha=0.5)
    axRL.set_xlim([df_dms.index.min(), df_dms.index.max()])

    axRL.grid()
    axRL.set_ylabel('ROLL [%s]' % degree)
    axRL.legend(['DMS', 'PHINS_FIXED'])

    axRL.xaxis.set_major_formatter(DateFormatter('%d/%m/%y\n %H:%M:%S'))
    for label in axRL.xaxis.get_majorticklabels():
        label.set_rotation(45)
    for label in axRL.xaxis.get_minorticklabels():
        label.set_rotation(45)

    # figure fix DMS
    fig = plt.figure(facecolor=(1.0, 1.0, 1.0), figsize=(12, 8))
    axPT = fig.add_subplot(211)
    axRL = fig.add_subplot(212, sharex=axPT)

    axPT.plot(df_dms.pitch_fixed, 'c', alpha=0.5)
    axPT.plot(df_phins.pitch_fixed, 'm', alpha=0.5)
    axPT.grid()
    axPT.set_title('DMS ajustada via PHINS')
    axPT.set_ylabel('PITCH [%s]' % degree)
    axPT.legend(['DMS_FIXED', 'PHINS_FIXED'])
    clean_ax(axPT)

    axRL.plot(df_dms.roll_fixed, 'c', alpha=0.5)
    axRL.plot(df_phins.roll_fixed, 'm', alpha=0.5)
    axRL.grid()
    axRL.set_ylabel('ROLL [%s]' % degree)
    axRL.set_xlim([df_dms.index.min(), df_dms.index.max()])
    axRL.legend(['DMS_FIXED', 'PHINS_FIXED'])
    axRL.xaxis.set_major_formatter(DateFormatter('%d/%m/%y\n %H:%M:%S'))
    for label in axRL.xaxis.get_majorticklabels():
        label.set_rotation(45)
    for label in axRL.xaxis.get_minorticklabels():
        label.set_rotation(45)

    # figure fix QUADRANS
    fig = plt.figure(facecolor=(1.0, 1.0, 1.0), figsize=(12, 8))
    axPT = fig.add_subplot(211)
    axRL = fig.add_subplot(212, sharex=axPT)

    axPT.plot(df_quadrans.pitch_fixed, alpha=0.5)
    axPT.plot(gps_data.pitch)
    axPT.grid()
    axPT.set_ylabel('PITCH [%s]' % degree)
    axPT.legend(['QUADRANS_FIXED %2.4f' % offset_pitch_quadrans, 'GPS'])
    clean_ax(axPT)

    axRL.plot(df_quadrans.roll_fixed, alpha=0.5)
    axRL.plot(gps_data.roll)
    axRL.grid()
    axRL.set_ylabel('ROLL [%s]' % degree)
    axRL.legend(['QUADRANS_FIXED %2.4f' % offset_quadrans_dms, 'GPS'])
    axRL.xaxis.set_major_formatter(DateFormatter('%d/%m/%y\n %H:%M:%S'))
    for label in axRL.xaxis.get_majorticklabels():
        label.set_rotation(45)
    for label in axRL.xaxis.get_minorticklabels():
        label.set_rotation(45)

    # figures to report
    # figure all sensor fixed via GPS
    fig = plt.figure(facecolor=(1.0, 1.0, 1.0), figsize=(12, 8))
    axPT = fig.add_subplot(211)
    axRL = fig.add_subplot(212, sharex=axPT)

    axPT.plot(df_quadrans.pitch_fixed, 'y')
    axPT.plot(df_dms.pitch_fixed, 'c', alpha=0.7)
    axPT.plot(df_phins.pitch_fixed, 'm', alpha=0.5)
    axPT.grid()
    axPT.set_title('Sensores ajustados via GPS')
    axPT.set_ylabel('PITCH [%s]' % degree)
    axPT.legend(['QUADRANS', 'DMS', 'PHINS', 'GPS'])
    clean_ax(axPT)

    axRL.plot(df_quadrans.roll_fixed, 'y')
    axRL.plot(df_dms.roll_fixed, 'c', alpha=0.7)
    axRL.plot(df_phins.roll_fixed, 'm', alpha=0.5)
    axRL.grid()
    axRL.set_ylabel('ROLL [%s]' % degree)
    axRL.legend(['QUADRANS', 'DMS', 'PHINS'])
    axRL.set_xlim([df_quadrans.index.min(), df_quadrans.index.max()])
    axRL.xaxis.set_major_formatter(DateFormatter('%d/%m/%y\n %H:%M:%S'))
    for label in axRL.xaxis.get_majorticklabels():
        label.set_rotation(45)
    for label in axRL.xaxis.get_minorticklabels():
        label.set_rotation(45)


    fig = plt.figure(facecolor=(1.0, 1.0, 1.0), figsize=(12, 8))
    axPT = fig.add_subplot(211)
    axRL = fig.add_subplot(212, sharex=axPT)
    axPT.plot(df_dms.pitch, 'c', alpha=0.5)
    axPT.grid()
    axPT.set_title('Sensor DMS')
    axPT.set_ylabel('PITCH [%s]' % degree)
    clean_ax(axPT)
    axRL.plot(df_dms.roll, 'c', alpha=0.5)
    axRL.grid()
    axRL.set_ylabel('ROLL [%s]' % degree)
    axRL.xaxis.set_major_formatter(DateFormatter('%d/%m/%y\n %H:%M:%S'))
    for label in axRL.xaxis.get_majorticklabels():
        label.set_rotation(45)
    for label in axRL.xaxis.get_minorticklabels():
        label.set_rotation(45)

    fig = plt.figure(facecolor=(1.0, 1.0, 1.0), figsize=(12, 8))
    axPT = fig.add_subplot(211)
    axRL = fig.add_subplot(212, sharex=axPT)
    axPT.plot(df_phins.pitch, 'm', alpha=0.5)
    axPT.grid()
    axPT.set_title('Sensor PHINS')
    axPT.set_ylabel('PITCH [%s]' % degree)
    clean_ax(axPT)
    axRL.plot(df_phins.roll, 'm', alpha=0.5)
    axRL.grid()
    axRL.set_ylabel('ROLL [%s]' % degree)
    axRL.xaxis.set_major_formatter(DateFormatter('%d/%m/%y\n %H:%M:%S'))
    for label in axRL.xaxis.get_majorticklabels():
        label.set_rotation(45)
    for label in axRL.xaxis.get_minorticklabels():
        label.set_rotation(45)

    fig = plt.figure(facecolor=(1.0, 1.0, 1.0), figsize=(12, 8))
    axPT = fig.add_subplot(211)
    axRL = fig.add_subplot(212, sharex=axPT)
    axPT.plot(df_quadrans.pitch, 'y', alpha=0.5)
    axPT.grid()
    axPT.set_title('Sensor QUADRANS')
    axPT.set_ylabel('PITCH [%s]' % degree)
    clean_ax(axPT)
    axRL.plot(df_quadrans.roll, 'y', alpha=0.5)
    axRL.grid()
    axRL.set_ylabel('ROLL [%s]' % degree)
    axRL.xaxis.set_major_formatter(DateFormatter('%d/%m/%y\n %H:%M:%S'))
    for label in axRL.xaxis.get_majorticklabels():
        label.set_rotation(45)
    for label in axRL.xaxis.get_minorticklabels():
        label.set_rotation(45)

    fig = plt.figure(facecolor=(1.0, 1.0, 1.0), figsize=(12, 8))
    axPT = fig.add_subplot(211)
    axRL = fig.add_subplot(212, sharex=axPT)
    axPT.plot(gps_data.pitch, 'r', alpha=0.5)
    axPT.grid()
    axPT.set_title('GPS Helideque')
    axPT.set_ylabel('PITCH [%s]' % degree)
    clean_ax(axPT)
    axRL.plot(gps_data.roll, 'r', alpha=0.5)
    axRL.grid()
    axRL.set_ylabel('ROLL [%s]' % degree)
    axRL.xaxis.set_major_formatter(DateFormatter('%d/%m/%y\n %H:%M:%S'))
    for label in axRL.xaxis.get_majorticklabels():
        label.set_rotation(45)
    for label in axRL.xaxis.get_minorticklabels():
        label.set_rotation(45)



    ## save all data
    df_quadrans = df_quadrans[['roll', 'pitch', 'heave']]
    df_dms = df_dms[['roll', 'pitch', 'heave']]
    df_phins2 = df_phins
    df_phins2 = df_phins2.drop(['surge', 'sway'], axis=1)

    result = pd.concat([df_quadrans, df_dms, df_phins2], axis=1, join_axes=[df_quadrans.index], keys=['QUADRANS', 'DMS', 'PHINS'])

    writer = pd.ExcelWriter('alldata.xlsx')
    result.to_excel(writer, 'Sheet1')
    writer.save()
