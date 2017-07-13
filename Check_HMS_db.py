# -*- coding: utf-8 -*-
# purpose:  check hms from database
#           in sqlite3
# author:   Márcio Yamashita
# created:  27-June-2017
# modified:

import sqlite3
import pyocnp
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.dates import DateFormatter
from matplotlib.dates import MinuteLocator, HourLocator, DayLocator, MonthLocator, YearLocator

degree = u"\u00b0"

class Read_Db(object):
    """docstring for Read_Db"""
    def __init__(self, ucd):
        super(Read_Db, self).__init__()
        self._db = pyocnp.PROD_DBACCESS
        self._ucd = ucd
        self.id = pyocnp.ucdid_byname_ocndb(self._ucd, str_dbaccess=self._db)
        self.ucd = pyocnp.ucdname_byid_ocndb(self.id, str_dbaccess=self._db)
        self.hms_bd_name = '.\\HMS\\%s.db' % self.ucd
        self.conn = sqlite3.connect(self.hms_bd_name)

    def plot_var(self, intervalo, var, step=1, lim=0):
        tb = " TB_HMS.HMS_"
        if var == 'PITCH':
            var_qry = (tb + var + "," +
                       tb + var + "_DM_20M," +
                       tb + var + "_UM_20M,")
            col = ['HMS_PITCH', 'HMS_PITCH_DM_20M', 'HMS_PITCH_UM_20M']
        elif var == 'ROLL':
            var_qry = (tb + var + "," +
                       tb + var + "_PM," +
                       tb + var + "_SM,")
            col = ['HMS_ROLL', 'HMS_ROLL_PM', 'HMS_ROLL_SM']
        elif var == 'INCL':
            var_qry = (tb + var + "," + tb + var + "_M,")
            col = ['HMS_INCL', 'HMS_INCL_M']
        else:
            var_qry = (tb + var + ',')
            col = ['HMS_' + var]
        fig = plt.figure(facecolor=(1.0, 1.0, 1.0), figsize=(12, 8))
        ax = fig.add_subplot(1, 1, 1)
        ax.grid('on')
        if self.test_time_input(intervalo):
            qry = ("SELECT TB_HMS.HMS_DT_AQUISICAO," +
                   var_qry +
                   " TB_HMS.HMS_POUSO_PERMITIDO"
                   " FROM TB_HMS"
                   " WHERE"
                   " TB_HMS.HMS_DT_AQUISICAO"
                   " BETWEEN '" + self.ini +
                   "' AND '" + self.fin +
                   "' ORDER BY"
                   " TB_HMS.HMS_DT_AQUISICAO;")
            df = pd.read_sql_query(qry, self.conn, index_col='HMS_DT_AQUISICAO',
                                   parse_dates={'HMS_DT_AQUISICAO':
                                                '%Y-%m-%d %H:%M:%S'})
            if df.empty:
                msg = 'Query request returned an empty object'
                ax.text(0.2, 0.5, msg, family='serif', style='italic',
                        ha='center', wrap=True)
            else:
                data = df[col]
                ax, t_out = self.plot_sub(data, ax, step, lim)
                ax.set_title('%s @ %s' % (var, ucd))
                self.setaxdate(ax, df.index.min(), df.index.max())
            return df

    def plot_atitude_var_ind(self, intervalo, step=1):
        u""" Função para plots de variaveis independentes,
        PITCH, ROLL e HEAVE.
        Para verificação dos sensores."""
        fig = plt.figure(facecolor=(1.0, 1.0, 1.0), figsize=(12, 8))
        axPT = fig.add_subplot(311)
        axRL = fig.add_subplot(312, sharex=axPT)
        axHV = fig.add_subplot(313, sharex=axPT)
        if self.test_time_input(intervalo):
            qry = ("SELECT TB_HMS.HMS_DT_AQUISICAO,"
                   " TB_HMS.HMS_PITCH,"
                   " TB_HMS.HMS_ROLL,"
                   " TB_HMS.HMS_HEAVE"
                   " FROM TB_HMS"
                   " WHERE"
                   " TB_HMS.HMS_DT_AQUISICAO"
                   " BETWEEN '" + self.ini +
                   "' AND '" + self.fin +
                   "' ORDER BY"
                   " TB_HMS.HMS_DT_AQUISICAO;")
            df = pd.read_sql_query(qry, self.conn, index_col='HMS_DT_AQUISICAO',
                                   parse_dates={'HMS_DT_AQUISICAO':
                                                '%Y-%m-%d %H:%M:%S'})
            if df.empty:
                msg = 'Query request returned an empty object'
                axPT.text(0.2, 0.5, msg, family='serif', style='italic',
                          ha='center', wrap=True)
                axRL.text(0.2, 0.5, msg, family='serif', style='italic',
                          ha='center', wrap=True)
                axHV.text(0.2, 0.5, msg, family='serif', style='italic',
                          ha='center', wrap=True)
            else:
                title = '{}{}'.format(' Sensores @ ', ucd)
                axPT.set_title(title)
                axPT.plot(df['HMS_PITCH'][::step])
                axPT.set_ylabel('PITCH [%s]' % degree)
                axRL.plot(df['HMS_ROLL'][::step])
                axRL.set_ylabel('ROLL [%s]' % degree)
                axHV.plot(df['HMS_HEAVE'][::step])
                axHV.set_ylabel('HEAVE [m]')
                self.setaxdate(axHV, df.index.min(), df.index.max())
                self.clean_ax(axRL)
                self.clean_ax(axPT)
            return df

    def plot_atitude_full(self, intervalo, step=1, aer=0):
        u""" Função para plots de variaveis independentes,
        PITCH, ROLL e INCLINATION e HEAVE RATE"""
        fig = plt.figure(facecolor=(1.0, 1.0, 1.0), figsize=(12, 8))
        axPT = fig.add_subplot(411)
        axRL = fig.add_subplot(412, sharex=axPT)
        axIN = fig.add_subplot(413, sharex=axPT)
        axVArf = fig.add_subplot(414, sharex=axPT)

        if self.test_time_input(intervalo):
            qry = ("SELECT TB_HMS.HMS_DT_AQUISICAO,"
                   " TB_HMS.HMS_PITCH,"
                   " TB_HMS.HMS_PITCH_DM_20M,"
                   " TB_HMS.HMS_PITCH_UM_20M,"
                   " TB_HMS.HMS_ROLL,"
                   " TB_HMS.HMS_ROLL_PM,"
                   " TB_HMS.HMS_ROLL_SM,"
                   " TB_HMS.HMS_INCL,"
                   " TB_HMS.HMS_INCL_M,"
                   " TB_HMS.HMS_HEAVE,"
                   " TB_HMS.HMS_HEAVE_VEL_M,"
                   " TB_HMS.HMS_POUSO_PERMITIDO"
                   " FROM TB_HMS"
                   " WHERE"
                   " TB_HMS.HMS_DT_AQUISICAO"
                   " BETWEEN '" + self.ini +
                   "' AND '" + self.fin +
                   "' ORDER BY"
                   " TB_HMS.HMS_DT_AQUISICAO;")
            df = pd.read_sql_query(qry, self.conn, index_col='HMS_DT_AQUISICAO',
                                   parse_dates={'HMS_DT_AQUISICAO':
                                                '%Y-%m-%d %H:%M:%S'})
            if df.empty:
                msg = 'Query request returned an empty object'
                axPT.text(0.2, 0.5, msg, family='serif', style='italic',
                          ha='center', wrap=True)
                axRL.text(0.2, 0.5, msg, family='serif', style='italic',
                          ha='center', wrap=True)
                axIN.text(0.2, 0.5, msg, family='serif', style='italic',
                          ha='center', wrap=True)
                axVArf.text(0.2, 0.5, msg, family='serif', style='italic',
                            ha='center', wrap=True)
            else:
                lim = 3 if aer == 0 else 4

                data = df[['HMS_PITCH', 'HMS_PITCH_DM_20M', 'HMS_PITCH_UM_20M']]
                axPT, PT = self.plot_sub(data, axPT, step, lim)
                axPT.set_ylabel('PITCH [%s]' % degree)
                axPT.set_ylim(-(lim+.5), lim+5)

                data = df[['HMS_ROLL', 'HMS_ROLL_PM', 'HMS_ROLL_SM']]
                axRL, RL = self.plot_sub(data, axRL, step, lim)
                axRL.set_ylabel('ROLL [%s]' % degree)
                axRL.set_ylim(-(lim+.5), lim+5)

                data = df[['HMS_INCL', 'HMS_INCL_M']]
                axIN, IN = self.plot_sub(data, axIN, step, lim+.5)
                axIN.set_ylabel('INCLINATION [%s]' % degree)
                axIN.set_ylim(0, 5)

                data = df[['HMS_HEAVE_VEL_M']]
                axVArf, VArf = self.plot_sub(data, axVArf, step, 1.3)
                axVArf.set_ylim(0, 2)

                axVArf.set_ylabel('VArf [m/s]')

                title_values = self.title_values(PT, RL, IN, VArf)
                if title_values:
                    full_title = (title_values[0] + ucd + '\n')
                    for i in title_values[1:]:
                        full_title = full_title + i
                else:
                    full_title = ucd
                axPT.set_title(full_title)

                self.setaxdate(axVArf, df.index.min(), df.index.max())
                self.clean_ax(axIN)
                self.clean_ax(axRL)
                self.clean_ax(axPT)

                i = df.index[0].isoformat().replace(':', '')
                f = df.index[-1].isoformat().replace(':', '')
                fig.savefig('.\\HMS\\figures\\%s-%s-%s.png' % (ucd, i, f))
            return df

    def title_values(self, PT, RL, IN, VArf):
        title_values = []
        close_ = (PT | RL | IN | VArf)
        if close_.sum():
            only_PT = (PT & ~(RL | IN | VArf))  # only pitch
            only_RL = (RL & ~(PT | IN | VArf))  # only roll
            only_IN = (IN & ~(PT | RL | VArf))  # only inclinação
            only_VArf = (VArf & ~(PT | RL | IN))  # only VArf
            text = '{:.2%}{}'.format(1.*close_.sum()/close_.count(),
                                     " Heliporto Fechado @ ")
            title_values.append(text)
            title_values.append('')
            if PT.sum():
                if only_PT.sum():
                    text = '{:.2%}{}'.format(1.*only_PT.sum()/only_PT.count(),
                                             " Pitch ")
                    title_values[-1] = title_values[-1] + text
                PT_IN = (((PT & IN) & ~RL) & ~VArf)
                if PT_IN.sum():
                    text = '{:.2%}{}'.format(1.*PT_IN.sum()/PT_IN.count(),
                                             " Pitch/Incl ")
                    title_values[-1] = title_values[-1] + text
                PT_RL_IN = ((PT & RL & IN) & ~VArf)
                if PT_RL_IN.sum():
                    text = '{:.2%}{}'.format(1.*PT_RL_IN.sum()/PT_RL_IN.count(),
                                             " Pitch/Roll/Incl ")
                    title_values[-1] = title_values[-1] + text
                PT_IN_VArf = (((PT & IN) & ~RL) & VArf)
                if PT_IN_VArf.sum():
                    text = '{:.2%}{}'.format(1.*PT_IN_VArf.sum()/PT_IN_VArf.count(),
                                             " Pitch/Incl/VArf ")
                    title_values[-1] = title_values[-1] + text
                PT_RL_IN_VArf = (PT & RL & IN & VArf)
                if PT_RL_IN_VArf.sum():
                    text = '{:.2%}{}'.format(1.*PT_RL_IN_VArf.sum()/PT_RL_IN_VArf.count(),
                                             " Pitch/Roll/Incl/VArf ")
                    title_values[-1] = title_values[-1] + text
                title_values[-1] = title_values[-1] + '\n'
            if RL.sum():
                if only_RL.sum():
                    text = '{:.2%}{}'.format(1.*only_RL.sum()/only_RL.count(),
                                             " Roll ")
                    title_values[-1] = title_values[-1] + text
                RL_IN = (((RL & IN) & ~PT) & ~VArf)
                if RL_IN.sum():
                    text = '{:.2%}{}'.format(1.*RL_IN.sum()/RL_IN.count(),
                                             " Roll/Incl ")
                    title_values[-1] = title_values[-1] + text
                RL_IN_VArf = (((RL & IN) & ~PT) & VArf)
                if RL_IN_VArf.sum():
                    text = '{:.2%}{}'.format(1.*RL_IN_VArf.sum()/RL_IN_VArf.count(),
                                             " Roll/VArf ")
                    title_values[-1] = title_values[-1] + text
                title_values[-1] = title_values[-1] + '\n'
            if only_IN.sum():
                    text = '{:.2%}{}'.format(1.*only_IN.sum()/only_IN.count(),
                                             " Incl ")
                    title_values[-1] = title_values[-1] + text
            if only_VArf.sum():
                text = '{:.2%}{}'.format(1.*only_VArf.sum()/only_VArf.count(),
                                         " VArf ",)
                title_values.append(text)
        return title_values

    # ============================================================ #
    def plot_sub(self, data, axes, step, lim=0):
        lgnd, t_out = [], []
        axes.plot(data.index[::step], data[data.keys()[0]][::step])
        if lim != 0:  # se fornecido os limites para plot
            axes.axhspan(-lim, lim, facecolor='green', alpha=0.2)
            t_out = data[data.keys()[0]] > lim
            if data.keys().size == 3:
                axes.plot(data[data.keys()[1:3]], ':', color='coral')
                t_out = (data[data.keys()[1]] <
                         -lim) | (data[data.keys()[2]] > lim)
                self.landing_nok(data.index, axes, t_out)
                axes.plot(data[data.keys()[1]][t_out],
                          ',', color='purple')
                axes.plot(data[data.keys()[2]][t_out],
                          ',', color='purple')
            if data.keys().size == 2:
                axes.plot(data[data.keys()[1]], ':', color='coral')
                t_out = data[data.keys()[1]] > lim
                self.landing_nok(data.index, axes, t_out)
                axes.plot(data.index[t_out], data[data.keys()[1]][t_out], ',',
                          color='purple')
            if t_out.sum() != 0:
                lgnd.append('{:.2%}{}'.format(1.*t_out.sum()/t_out.count(),
                            ' fora '))
                axes.legend(lgnd)
        return axes, t_out

    # ============================================================ #
    def test_time_input(self, dtime):
        u""" Teste para input de datas."""
        if np.size(dtime) == 2:
            try:
                i = datetime.strptime(dtime[0], "%d/%m/%Y %H:%M:%S")
                self.ini = i.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                print 'Corrigir entrada inicial DD/MM/YYYY HH:MM:SS'
                return False
            try:
                f = datetime.strptime(dtime[1], "%d/%m/%Y %H:%M:%S")
                self.fin = f.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                print 'Corrigir entrada final DD/MM/YYYY HH:MM:SS'
                return False
            if len(dtime[0]) != 19:
                print 'Corrigir entrada inicial DD/MM/YYYY HH:MM:SS'
                return False
            if len(dtime[1]) != 19:
                print 'Corrigir entrad final DD/MM/YYYY HH:MM:SS'
                return False
            if (datetime.strptime(dtime[0], "%d/%m/%Y %H:%M:%S") >
                    datetime.strptime(dtime[1], "%d/%m/%Y %H:%M:%S")):
                print 'Data Inicial maior que Data Final'
                return False
        else:
            print 'Lista deve conter 2 datas'
            return False
        return True

    # Customização da figura
    # ============================================================ #
    def clean_ax(self, axes):
        u""" Limpeza de eixo temporal."""
        axes.fmt_xdata = DateFormatter('%d/%m/%y %H:%M:%S')
        for label in axes.xaxis.get_majorticklabels():
            label.set_visible(False)
        for label in axes.xaxis.get_minorticklabels():
            label.set_visible(False)

    def landing_nok(self, xrange, axes, mask, color='red'):
        axes.fill_between(xrange, axes.get_ylim()[0], axes.get_ylim()[1],
                          where=mask, color=color, alpha=0.4)

    def setaxdate(self, axes, datemn, datemx):
        u""" Customizar rótulos de eixo temporal. """
        # Limites inferior e superior do eixo.
        (axes.set_xlim([datemn - timedelta(hours=1), datemx +
                        timedelta(hours=1)]) if datemn == datemx else
         axes.set_xlim([datemn, datemx]))
        axes.fmt_xdata = DateFormatter('%d/%m/%y %H:%M:%S')
        # Escala temporal: < 1 hora.
        if (datemx - datemn) < timedelta(hours=1):
            axes.xaxis.set_major_locator(MinuteLocator(byminute=(00, 15,
                                                                 30, 45)))
            axes.xaxis.set_major_formatter(DateFormatter('%H:%M'))
            axes.xaxis.set_minor_locator(MinuteLocator(byminute=(05, 10, 20,
                                                                 25, 35, 40,
                                                                 50, 55)))
            axes.xaxis.set_minor_formatter(DateFormatter(''))
        # Escala temporal: < 12 horas.
        elif timedelta(hours=1) < (datemx - datemn) < timedelta(hours=12):
            axes.xaxis.set_major_locator(HourLocator(byhour=(0, 3, 6, 9, 12,
                                                             15, 18, 21)))
            axes.xaxis.set_major_formatter(DateFormatter('%d/%m/%y\n%H:%M'))
            axes.xaxis.set_minor_locator(HourLocator())
            axes.xaxis.set_minor_formatter(DateFormatter(''))
        # Escala temporal: > 12horas, 10[ dias.
        elif timedelta(hours=12) <= (datemx - datemn) < timedelta(hours=240):
            axes.xaxis.set_major_locator(DayLocator())
            axes.xaxis.set_major_formatter(DateFormatter('%d/%m/%y'))
            axes.xaxis.set_minor_locator(HourLocator(byhour=(6, 12, 18)))
            axes.xaxis.set_minor_formatter(DateFormatter('%H:%M'))
        # Escala temporal: [11, 45[ dias.
        elif 10 <= (datemx.toordinal() - datemn.toordinal()) < 45:
            axes.xaxis.set_major_locator(DayLocator(bymonthday=(3, 8, 13,
                                                                18, 23, 28)))
            axes.xaxis.set_major_formatter(DateFormatter('%d/%m/%y'))
            axes.xaxis.set_minor_locator(DayLocator())
            axes.xaxis.set_minor_formatter(DateFormatter(''))
        # Escala temporal: [45, 183[ dias.
        elif 45 <= (datemx.toordinal() - datemn.toordinal()) < 183:
            axes.xaxis.set_major_locator(MonthLocator())
            axes.xaxis.set_major_formatter(DateFormatter('%m/%Y'))
            axes.xaxis.set_minor_locator(DayLocator(bymonthday=(5, 10,
                                                                15, 20, 25)))
            axes.xaxis.set_minor_formatter(DateFormatter('%d'))
        # Escala temporal: >= 365 dias.
        else:
            axes.xaxis.set_major_locator(YearLocator())
            axes.xaxis.set_major_formatter(DateFormatter('%Y'))
            axes.xaxis.set_minor_locator(MonthLocator())
            axes.xaxis.set_minor_formatter(DateFormatter('%m'))

        for label in axes.xaxis.get_majorticklabels():
            label.set_rotation(45)
        for label in axes.xaxis.get_minorticklabels():
            label.set_rotation(45)


if __name__ == '__main__':

    ucd = 'P-62'
    data = Read_Db(ucd)
    # fornecer lista com 2 valores (Tempo inicial e Tempo final)
    intervalo = ['01/06/2017 00:00:00', '30/06/2017 23:59:59']
    var = 'ROLL'
    step = 1

    # dados = data.plot_var(intervalo, var, step, lim=0)

    # dados = data.plot_atitude_var_ind(intervalo, step=100)

    dados = data.plot_atitude_full(intervalo, step, aer=0)
