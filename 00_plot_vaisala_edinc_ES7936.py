# -*- coding: utf-8 -*-
__authors__ = ["Márcio Yamashita"]
__email__ = ["marciokatsumiyamashita@gmail.com"]
__created__ = ["16-AGO-2016"]
__purpose__ = ["Plot Vaisala EDINC porta serial - Based on CEMPES"]
__credits__ = ["""funções string2float wind2wind10
# corrige_wind_dir calc_real_feel stick_plot
# provenientes do CEMPES"""]

# import modules that I'm using
import Tkinter

import matplotlib
matplotlib.use('TKAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from matplotlib import gridspec
from matplotlib._png import read_png
from matplotlib.dates import DateFormatter, HourLocator, date2num
from matplotlib.colors import colorConverter
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter, MaxNLocator
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from mpl_toolkits.basemap import Basemap

import os
from datetime import datetime
import numpy as np

import serial
import threading
import itertools
from collections import deque

data_now = deque(maxlen=1)
wspd_600, wdir_600 = deque(maxlen=600), deque(maxlen=600)
umid_600, rain_600 = deque(maxlen=600), deque(maxlen=600)
pres_600, temp_600 = deque(maxlen=600), deque(maxlen=600)

wspd_24h, wdir_24h = deque(maxlen=144), deque(maxlen=144)
wspd_u_24h, wspd_v_24h = deque(maxlen=144), deque(maxlen=144)
umid_24h, rain_24h, rain_24h_acu = deque(
    maxlen=144), deque(maxlen=144), deque(maxlen=144)
pres_24h, temp_24h = deque(maxlen=144), deque(maxlen=144)
timeline = deque(maxlen=144)
raj = deque(['0.0'], maxlen=1)


class SensorThread(threading.Thread):

    def run(self):
        ser = serial.Serial(4)  # COM5 no PC ES7936
        ser.baudrate = 19200
        ser.bytesize = serial.EIGHTBITS  # number of bits per bytes
        ser.parity = serial.PARITY_NONE  # set parity check: no parity
        ser.stopbits = serial.STOPBITS_ONE  # number of stop bits
        try:
            try:
                database = np.load('database.npz')
                map(wspd_24h.append, database['arr_0'])
                map(wdir_24h.append, database['arr_1'])
                map(wspd_u_24h.append, database['arr_2'])
                map(wspd_v_24h.append, database['arr_3'])
                map(umid_24h.append, database['arr_4'])
                map(rain_24h.append, database['arr_5'])
                map(rain_24h_acu.append, database['arr_6'])
                map(pres_24h.append, database['arr_7'])
                map(temp_24h.append, database['arr_8'])
                map(timeline.append, database['arr_9'])
                del database
            except:
                pass
            while True:
                response = ser.readline()
                if response[:3] == '0R0' and len(response.split(',')) == 23:
                    data_now.appendleft(
                        datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
                    wdir_600.appendleft(corrige_wind_dir(string2float(
                        response.split(',')[2]), 23.4) * (np.pi / 180.0))
                    wspd_600.appendleft(string2float(response.split(',')[5]))
                    umid_600.appendleft(string2float(response.split(',')[9]))
                    rain_600.appendleft(string2float(response.split(',')[13]))
                    temp_600.appendleft(string2float(response.split(',')[7]))
                    pres_600.appendleft(press2sea_level_OCN(string2float(
                        response.split(',')[10]), string2float(
                        response.split(',')[7]), 79))
                    raj.appendleft(max(itertools.islice(wspd_600, 0, 119)))
                    if datetime.now().strftime('%M')[-1] == '0'\
                            and datetime.now().strftime('%S') == '00':
                        wdir_24h.appendleft(np.arctan2(
                            np.sin(np.mean(wdir_600)), np.cos(
                                np.mean(wdir_600))) % (2 * np.pi))
                        wspd_24h.appendleft(np.mean(wspd_600) * 3.6)
                        wspd_u_24h.appendleft(-wspd_24h[0]
                                              * np.sin(wdir_24h[0]))
                        wspd_v_24h.appendleft(-wspd_24h[0]
                                              * np.cos(wdir_24h[0]))
                        umid_24h.appendleft(np.mean(umid_600))
                        rain_24h.appendleft(np.mean(rain_600))
                        rain_24h_acu.appendleft(np.sum(rain_600) / 3600)
                        temp_24h.appendleft(np.mean(temp_600))
                        pres_24h.appendleft(np.mean(pres_600))
                        timeline.appendleft(datetime.now())
                        np.savez('database.npz', wspd_24h, wdir_24h,
                                 wspd_u_24h, wspd_v_24h, umid_24h, rain_24h,
                                 rain_24h_acu, pres_24h, temp_24h, timeline)
        except:
            ser.close()


def corrige_wind_dir(alpha, azimute):
    """
    Equacao para corrigir a direcao do vento medidada pela estacao a partir do
    angulo entre o norte da estacao e o norte geografico.
    Inputs:
        alpha: array ou float com os valores de direcao medidos pela estacao em
               graus
        azimute: angulo em graus entre a direcao norte e a direcao da estacao.
    Outputs:
        Array ou float com a direcao do vento corrigida para o norte geografico
    """
    return alpha + azimute - 360.0 * (np.minimum(0, np.sign(alpha + azimute)))


def calc_real_feel(V, T):
    """
    Equacao para calcular a sensacao termica a partir da velocidade do vento e
    da temperatura.
    Inputs:
        V: array ou float com a velocidade do vento em m/s
        T: array ou float com a temperatura do ar em Celsius
    Outputs:
        Array ou float com valores de sensacao termica (real feel) em Celsius
    """
    return 33.0 + (10.0 * np.sqrt(V) + 10.45 - V) * (T - 33.0) / 22.0


def press2sea_level_OCN(P, T, h):
    """
    Equacao para correcao da pressao para o nivel medio do mar utilizada na OCN
    P = p*exp((g/(R*(t+273.15)))*c)) onde g = 9.81 R = 287 e c = cota
    Inputs:
        P: array ou float com valores de pressao em mbar ou hPa
        T: array ou float com valores de temperatura do ar em Celsius
        h: float com altitude em metros
    Outputs:
        Array com pressao atmosferica ao nivel do mar
    """
    return P * np.exp(9.81 * h / (287 * (T + 273.15)))


def string2float(s):
    """
    Funcao para converter string contendo letras e numeros em float
    Inputs:
        s: string contendo letras e numeros. Exemplo: s='0.76m/s'
    Outputs:
        Float interpretado da string ignorando caracteres nao numericos.
    """
    try:
        sf = ''.join(c for c in s if c in '1234567890.')
        sf = float(sf)
        return sf
    except:
        return s


def stick_plot(time, vel, u, v, c=None, normed=False, convention='wind', **kw):
    """
    Funcao para plotar stick plot
    Inputs:
        time: array ou lista com valores do eixo x
        vel: array ou lista com valores do eixo y
        u: array ou lista com componentes u
        v: array ou lista com componentes v
        c: array ou lista para colorir as setas
        normed: switch para normalizar os vetores
                (todos os sticks ficam com o mesmo tamanho).
                Default: normed=False
        convention: 'wind' para que a direcao seja a direcao de origem e
                    ("de onde vem") ou 'current' para que direcao seja a
                    direcao de destino ("pra onde vai")

    @authors: Thiago Pires de Paula
              PETROBRAS - CENPES/PDDP/TEO
    """
    width = kw.pop('width', 0.002)
    headwidth = kw.pop('headwidth', 0)
    headlength = kw.pop('headlength', 0)
    headaxislength = kw.pop('headaxislength', 0)
    angles = kw.pop('angles', 'uv')
    ax = kw.pop('ax', None)
    if angles != 'uv':
        raise AssertionError("Stickplot angles must be 'uv' so that"
                             "if *U*==*V* the angle of the arrow on"
                             "the plot is 45 degrees CCW from the *x*-axis.")
    time, u, v = map(np.asanyarray, (time, u, v))
    if not ax:
        fig, ax = plt.subplots()
    if normed:
        if 'wind' in [convention]:
            Dir = np.arctan2(u, v) * (180 / np.pi) + 180
            u = -1.0 * np.sin(Dir * np.pi / 180.0)
            v = -1.0 * np.cos(Dir * np.pi / 180.0)
        elif 'current' in [convention]:
            Dir = np.arctan2(u, v) * (180 / np.pi)
            u = 1.0 * np.sin(Dir * np.pi / 180.0)
            u = 1.0 * np.sin(Dir * np.pi / 180.0)
        else:
            raise ValueError(
                'Escolha a convencao de direcao com o "wind" ou "current"')
    if c:
        q = ax.quiver(time, vel, u, v, c, angles='uv', width=width,
                      headwidth=headwidth, headlength=headlength,
                      headaxislength=headaxislength, **kw)
    else:
        q = ax.quiver(time, vel, u, v, angles='uv', width=width,
                      headwidth=headwidth, headlength=headlength,
                      headaxislength=headaxislength, **kw)
    return q


def wind2wind10(W, h):
    """
    Equacao para correcao do vento de uma altura h para o vento a 10 m.
    Inputs:
        W: array ou float com valores de velocidade do vento na altura h
        h: altura do vento original em metros.
    Outputs:
       Array ou float com velocidade do vento a 10 m.
    """
    return W / (1.0 + 0.137 * np.log(h / 10.0))


def get_grad(color):
    z = np.empty((100, 1, 4), dtype=float)
    rgb = colorConverter.to_rgb(color)
    z[:, :, :3] = rgb
    z[:, :, -1] = np.linspace(0, 1.0, 100)[:, None]
    return z


class App_Window(Tkinter.Tk):

    def __init__(self, parent):
        Tkinter.Tk.__init__(self, parent)
        self.parent = parent
        self.initialize()

    def initialize(self):
        font = {'size': 12}
        matplotlib.rc('font', **font)
        matplotlib.style.use("dark_background")

        pixels = [1920, 1080]
        fig = Figure(figsize=(pixels[0] / 96.0, pixels[1] / 96.0),
                     edgecolor='none', facecolor='k')

        i0 = 1
        i = 14
        j = 36
        s = 3

        # ----------------------------------------------------------------------
        # Eixos para os graficos
        # ----------------------------------------------------------------------
        gs1, gs2 = gridspec.GridSpec(i, j), gridspec.GridSpec(i, j)
        # ----------------------------------------------------------------------
        # Grafico de temperatura xaxis compartilhado com os demais graficos
        graf_temp = fig.add_subplot(gs1[i0 + 3 * s:i0 + 4 * s:11, 0:15])
        # Grafico de pressao
        graf_press = fig.add_subplot(gs1[i0 + 2 * s:i0 + 3 * s:11, 0:15],
                                     sharex=graf_temp)
        # Grafico umidade e precipitacao
        graf_umid = fig.add_subplot(gs1[i0 + s:i0 + 2 * s, 0:15],
                                    sharex=graf_temp)
        graf_rain = graf_umid.twinx()
        # Grafico de vento e direcao do vento
        graf_vento = fig.add_subplot(gs1[i0:i0 + s, 0:15], sharex=graf_temp)
        # ----------------------------------------------------------------------
        # Icone da pressao
        icon_pres = fig.add_subplot(gs1[i0 + 2 * s:i0 + 3 * s, 16:21],
                                    frameon=False)
        # Icone do vento
        icon_vent = fig.add_subplot(gs1[i0:i0 + s, 16:18], frameon=False)
        # Icone de umidade
        icon_umid = fig.add_subplot(gs1[i0 + s:i0 + 2 * s, 16:18],
                                    frameon=False)
        # Icone de temperatura
        icon_temp = fig.add_subplot(gs1[i0 + 3 * s:i0 + 4 * s, 16:18],
                                    frameon=False)
        # Icone direcao do vento agora
        icon_vento_dir = fig.add_subplot(gs2[i0:i0 + s, 19:22], frameon=False,
                                         projection='polar')
        # Icone de precipitacao
        icon_rain = fig.add_subplot(gs2[i0 + s:i0 + 2 * s, 18:21],
                                    frameon=False)
        # Icone de sensação térmica
        self.icon_feel = fig.add_subplot(gs2[i0 + 3 * s:i0 + 4 * s, 18:21],
                                         frameon=False)
        # Icone de rajada
        icon_gust = fig.add_subplot(gs1[i0:4, 23:27], frameon=False)
        # Icone de windrose
        icon_rose = fig.add_subplot(gs1[i0:4, 28:32], frameon=False,
                                    projection='polar')
        # ----------------------------------------------------------------------
        # Titulo Gráficos
        self.title_1 = fig.add_subplot(gs1[0, 0:12], frameon=False)
        # Titulo Icones
        self.title_2 = fig.add_subplot(gs1[0, 16:21], frameon=False)
        # Titulo Logos
        self.title_3 = fig.add_subplot(gs1[-2, 23::], frameon=False)

        map = fig.add_subplot(gs1[5:-2, 23::])

        gs1.update(wspace=0.01, hspace=0.3, left=0.04, top=1, bottom=0.000001)
        gs2.update(wspace=0.03, hspace=0.75, top=1, bottom=0.000001)

        # ----------------------------------------------------------------------
        # Plota os icones
        # ----------------------------------------------------------------------
        dir_icon = '.\images'
        zoom_f = 1.6
        kw = dict(frameon=False, xycoords="data", boxcoords="data",
                  xy=(0, 0), box_alignment=(0.0, 0.0))
        # Desenha os icones de vento
        img_today = read_png(os.path.join(dir_icon, 'wind.png'))
        imagebox = OffsetImage(img_today, zoom=0.07 * zoom_f)
        ab = AnnotationBbox(imagebox, xybox=(0.1, 0.1), **kw)
        icon_vent.add_artist(ab)
        # ----------------------------------------------------------------------
        # Gerando eixo polar para as setas para o vento
        directions = ['N', 'NW', 'W', 'SW', 'S', 'SE', 'E', 'NE']
        icon_vento_dir.set_theta_zero_location('N')
        icon_vento_dir.set_theta_direction(1)
        icon_vento_dir.set_xticklabels(directions)
        icon_vento_dir.tick_params(axis='x', colors='w')
        icon_vento_dir.tick_params(axis='y', colors='w')
        icon_vento_dir.grid(color='w')

        # Desenha o icone de rajada
        img_today = read_png(os.path.join(dir_icon, 'rajada.png'))
        imagebox = OffsetImage(img_today, zoom=0.15 * zoom_f)
        ab = AnnotationBbox(imagebox, xybox=(0.0, 0.1), **kw)
        icon_gust.add_artist(ab)
        icon_gust.set_title(u'Rajada 2 minutos', fontsize=11, x=0.4, y=1,
                            fontweight='bold')

        # ----------------------------------------------------------------------
        # Gerando eixo polar para plot
        icon_rose.set_theta_zero_location('N')
        icon_rose.set_theta_direction(1)
        icon_rose.set_xticklabels(directions)
        icon_rose.tick_params(axis='x', colors='w')
        icon_rose.tick_params(axis='y', colors='w')
        icon_rose.grid(color='w')

        # Desenha os icones de umidade
        img_today = read_png(os.path.join(dir_icon, 'humidity.png'))
        imagebox = OffsetImage(img_today, zoom=0.075 * zoom_f)
        ab = AnnotationBbox(imagebox, xybox=(0.325, 0.10), **kw)
        icon_umid.add_artist(ab)

        # Desenha os icones de precipitacao
        img_today = read_png(os.path.join(dir_icon, 'rain.png'))
        imagebox = OffsetImage(img_today, zoom=0.09 * zoom_f)
        ab = AnnotationBbox(imagebox, xybox=(0.275, 0.0), **kw)
        icon_rain.add_artist(ab)

        # Desenha os icones de pressao
        img_today = read_png(os.path.join(dir_icon, 'pressure.png'))
        imagebox = OffsetImage(img_today, zoom=0.125 * zoom_f)
        ab = AnnotationBbox(imagebox, xybox=(0.35, 0.0), **kw)
        icon_pres.add_artist(ab)

        # Desenha os icones de temperatura
        img_today = read_png(os.path.join(dir_icon, 'temp.png'))
        imagebox = OffsetImage(img_today, zoom=0.11 * zoom_f)
        ab = AnnotationBbox(imagebox, xybox=(0.22, 0.0), **kw)
        icon_temp.add_artist(ab)

        # Desenha o icone de sensacao termica atual
        img_today = read_png(os.path.join(dir_icon, 'realfeel.png'))
        imagebox = OffsetImage(img_today, zoom=0.10 * zoom_f)
        self.ab = AnnotationBbox(imagebox, xybox=(0.3, 0.1), **kw)
        self.icon_feel.add_artist(self.ab)
        self.icon_feel.set_title(u'Sensação\nTérmica', fontsize=11,
                                 x=0.55, y=-0.2)
        self.img = itertools.cycle(['realfeel_cky.png', 'realfeel_fms.png',
                                    'realfeel_fna.png'])

        # logo Petrobras
        img_today = read_png(os.path.join(dir_icon, 'Principal_h_cor_RGB.png'))
        imagebox = OffsetImage(img_today, zoom=0.2)
        # opcao 1: logo ao lado do credito
        ab = AnnotationBbox(imagebox, xybox=(0.0, 0.05), **kw)
        self.title_3.add_artist(ab)
        # logo Oceanop
        img_today = read_png(os.path.join(dir_icon, 'oceanop_logo.png'))
        imagebox = OffsetImage(img_today, zoom=0.4)
        # opcao 1: logo ao lado do credito
        ab = AnnotationBbox(imagebox, xybox=(0.8, 0.1), **kw)
        self.title_3.add_artist(ab)

        # ----------------------------------------------------------------------
        # Cria mapa base
        # ----------------------------------------------------------------------
        # Coordenadas da estacao meteorologica # 22 24 4.02**41 48 29.30
        Xest, Yest = -41.808138888889, -22.401116666667
        # Coordenadas da janela da imagem 2223.936_4148.723_2224.175_4148.264
        Xmin, Xmax = -41.81205, -41.8044
        Ymin, Ymax = -22.402916666667, -22.398933333333
        # Mapa base com a localizacao da estacao
        m = Basemap(ax=map, epsg=4326, projection='merc', llcrnrlat=Ymin,
                    urcrnrlat=Ymax, llcrnrlon=Xmin, urcrnrlon=Xmax,
                    resolution='c')

        imgfile = os.path.join(dir_icon,
                               '2223.936_4148.723_2224.175_4148.264.jpg')
        img = plt.imread(imgfile)
        m.imshow(img, origin='upper')

        # Plota pontos de interesse
        bprops = dict(boxstyle='round', facecolor='w', alpha=0.35)
        aprops2 = dict(arrowstyle='simple', connectionstyle='arc3, rad=-0.2',
                       relpos=(0., 1.),  facecolor='k', alpha=0.6)

        map.text(-41.8066588889, -22.40111, 'EDINC',
                 horizontalalignment='center', verticalalignment='center',
                 fontweight='bold', fontsize=16, color='k', bbox=bprops)

        pest, = map.plot(Xest, Yest, 'ro', markersize=4)

        map.annotate(u"Estação\nMeteorológica", xy=(Xest, Yest),
                     xycoords='data', xytext=(-41.809, -22.403),
                     size=12, va='top', ha='left', arrowprops=aprops2,
                     bbox=bprops, fontweight='bold')

        # Insere seta apontando para o norte no canto inferior direito
        imgfile = read_png(os.path.join(dir_icon, 'north_arrow.png'))
        imagebox = OffsetImage(imgfile, zoom=0.11)
        lonmin, lonmax = m.boundarylonmin, m.boundarylonmax
        latmin, latmax = min(m.boundarylats), max(m.boundarylats)
        xy = (lonmax - 0.08 * (lonmax - lonmin),
              latmax - 0.9 * (latmax - latmin))
        ab = AnnotationBbox(imagebox, xy, frameon=False, xycoords="data",
                            boxcoords="data", box_alignment=(0.0, 0.0))
        map.add_artist(ab)

        fontdict = {'color': 'w', 'va': 'center', 'ha': 'center',
                    'fontsize': 13, 'fontweight': 'bold'}
        self.i_vent = icon_vent.text(0.5, 0.8, 'NA', fontdict=fontdict)
        self.i_gust = icon_gust.text(0.5, 0.8, 'NA', fontdict=fontdict)
        self.i_umid = icon_umid.text(0.5, 0.75, 'NA', fontdict=fontdict)
        self.i_rain = icon_rain.text(0.5, 0.8, 'NA', fontdict=fontdict)
        self.i_pres = icon_pres.text(0.2, 0.7, 'NA', fontdict=fontdict)
        self.i_temp = icon_temp.text(0.25, 0.75, 'NA', fontdict=fontdict)
        self.i_feel = self.icon_feel.text(0.275, 0.75, 'NA', fontdict=fontdict)

        # Set icones e titulos
        axis_icon_names = [icon_pres, icon_vent, icon_umid, icon_rain,
                           icon_gust, icon_pres, icon_temp, self.icon_feel,
                           self.title_1, self.title_2, self.title_3]
        for i in axis_icon_names:
            i.set_axis_off()

        # Set titulos nos graficos
        graf_vento.set_title(u'Vento [km/h]', x=0.12, y=0.75,
                             fontweight='bold', fontsize=11)
        graf_press.set_title(u'Pressão Atmosférica [hPa]', x=0.23, y=0.75,
                             fontweight='bold', fontsize=11)
        graf_umid.set_title(u'Umidade Relativa [%]', x=0.19, y=0.75,
                            fontweight='bold', fontsize=11)
        graf_temp.set_title(u'Temperatura do Ar [\N{DEGREE SIGN}C]', x=0.205,
                            y=0.75, fontweight='bold', fontsize=11)
        map.set_title(u'Localização da Estação Meteorólogica', fontsize=15,
                      fontweight='bold', loc='left', y=1.05)

        self.canvasFig = fig
        #             [0]wind, [1]humi, [2]pres, [3]temp
        self.cor = ['#4CB050', '#2196F5', '#FF9702', '#F44236']
        x, y = [], []

        self.line0, = graf_vento.plot(x, y, self.cor[0])
        self.line1, = graf_umid.plot(x, y, self.cor[1])
        self.line2, = graf_rain.plot(x, y, self.cor[1], linestyle='--')
        self.line3, = graf_press.plot(x, y, self.cor[2])
        self.line4, = graf_temp.plot(x, y, self.cor[3])

        icon_vento_dir.axes.yaxis.set_ticklabels([])
        icon_rose.axes.yaxis.set_ticklabels([])

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=Tkinter.TOP, fill=Tkinter.BOTH,
                                         expand=1)
        self.canvas._tkcanvas.pack(side=Tkinter.TOP, fill=Tkinter.BOTH,
                                   expand=1)

        self.after(500, self.icon_refresh, icon_vento_dir, icon_rose)
        self.update()

    def refreshFigure(self):
        x = list(timeline)
        xmin, xmax = date2num(min(timeline)), date2num(max(timeline))

        self.line0.set_data(x, np.array(wspd_24h))
        self.line1.set_data(x, list(umid_24h))
        self.line2.set_data(x, list(rain_24h))
        self.line3.set_data(x, list(pres_24h))
        self.line4.set_data(x, list(temp_24h))

        ax0 = self.canvas.figure.axes[0]  # temp
        ax1 = self.canvas.figure.axes[1]  # pres
        ax2 = self.canvas.figure.axes[2]  # umid
        ax3 = self.canvas.figure.axes[3]  # chuva
        ax4 = self.canvas.figure.axes[4]  # vento

        ax0.set_xlim(min(x), max(x))
        try:  # temp
            self.grad0.remove()
            self.fill0.remove()
        except:
            pass
        self.grad0 = ax0.imshow(get_grad(self.cor[3]), aspect='auto',
                                extent=[xmin, xmax, min(temp_24h),
                                        max(temp_24h)], origin='lower')
        self.fill0 = ax0.axes.fill_between(x, list(temp_24h),
                                           max(temp_24h), color='k')
        ax0.set_ylim(min(temp_24h), max(temp_24h))

        try:  # pres
            self.grad1.remove()
            self.fill1.remove()
        except:
            pass
        self.grad1 = ax1.imshow(get_grad(self.cor[2]), aspect='auto',
                                extent=[xmin, xmax, min(pres_24h),
                                        max(pres_24h)], origin='lower')
        self.fill1 = ax1.axes.fill_between(x, list(pres_24h), max(pres_24h),
                                           color='k')
        ax1.set_ylim(min(pres_24h), max(pres_24h))

        try:  # umid
            self.grad2.remove()
            self.fill2.remove()
        except:
            pass
        self.grad2 = ax2.imshow(get_grad(self.cor[1]), aspect='auto',
                                extent=[xmin, xmax, min(umid_24h),
                                        max(umid_24h)], origin='lower')
        self.fill2 = ax2.axes.fill_between(x, list(umid_24h), max(umid_24h),
                                           color='k')
        ax2.set_ylim(min(umid_24h), max(umid_24h))
        ax3.set_ylim([-0.1, np.maximum(1.0, np.round(1.2 * max(rain_24h)))])

        try:  # wind
            self.grad4.remove()
            self.fill4.remove()
        except:
            pass
        self.grad4 = ax4.imshow(get_grad(self.cor[0]), aspect='auto',
                                extent=[xmin, xmax, min(wspd_24h),
                                        max(wspd_24h)], origin='lower')
        self.fill4 = ax4.axes.fill_between(x, np.array(wspd_24h),
                                           max(wspd_24h), color='k')
        ax4.set_ylim(min(wspd_24h), max(wspd_24h))

        try:  # Stick a cada 20 minutos
            self.quiver.remove()
        except:
            pass
        self.quiver = stick_plot(date2num(timeline)[::2], np.mean(wspd_24h),
                                 np.array(wspd_u_24h)[::2],
                                 np.array(wspd_v_24h)[::2],
                                 normed=False, color=self.cor[0], alpha=1,
                                 width=0.001, headwidth=5, headlength=8,
                                 headaxislength=8, ax=ax4)
        # Plota taxa de precipitacao com legendas
        ax3.legend((ax2.axes.get_lines()[0], ax3.axes.get_lines()[0]),
                   ['Umidade Relativa (%)', u'Precipitação (mm/hora)'],
                   fontsize=12, loc=1, framealpha=0.5, fancybox=[1, 1, 1, 1])

        # Ajuste o ylim do eixo de vento, caso max(wind) < 10 km/h,
        # limita em 10 km/h
        if max(wspd_24h) < 10.0:
            ax4.set_ylim([4, 10.0])
            ax4.set_yticks(np.arange(5))
        # Corrige formato do eixo y nos graficos de pressao e vento
        ax1.get_yaxis().set_major_formatter(FuncFormatter(lambda x,
                                                          p: '%1.1f' % x))
        ax4.get_yaxis().set_major_formatter(FuncFormatter(lambda x,
                                                          p: '%1.1f' % x))

        # SET figure
        ax0.axes.fmt_xdata = DateFormatter('%d/%m/%y %H:%M')
        ax0.axes.xaxis.set_major_locator(HourLocator(byhour=(0, 6, 12, 18)))
        ax0.axes.xaxis.set_major_formatter(DateFormatter('%d/%m/%y\n%H:%M'))
        ax0.axes.xaxis.set_minor_locator(HourLocator(byhour=(3, 9, 15, 21)))
        ax0.axes.xaxis.set_minor_formatter(DateFormatter('%H:%M'))
        lines_map = [ax0, ax1, ax2, ax3, ax4]
        for i in lines_map:
            i.grid(True)
            i.yaxis.set_major_locator(MaxNLocator(4))
            if i == ax0:
                for label in ax0.xaxis.get_majorticklabels():
                    label.set_fontsize(10)
                    label.set_ha('right')
                    label.set_rotation(45)
                for label in ax0.xaxis.get_minorticklabels():
                    label.set_fontsize(8)
                    label.set_ha('right')
                    label.set_rotation(45)
            else:
                for label in i.xaxis.get_majorticklabels():
                    label.set_visible(False)
                for label in i.xaxis.get_minorticklabels():
                    label.set_visible(False)
        self.canvas.draw()

    def icon_refresh(self, icon_vento_dir, icon_rose):
        try:
            self.arrow.remove()
            self.arrow_.remove()
        except:
            pass
        try:
            self.i_vent.set_text(u'%1.1f km/h \n%1.1f nós'
                                 % (wspd_600[0] * 3.6,
                                    wspd_600[0] * 3.6 / 1.8520))
            self.i_gust.set_text(u'%1.1f km/h \n%1.1f nós' %
                                 (raj[0] * 3.6, raj[0] * 3.6 / 1.852))
            self.angle = np.arctan2(np.sin(
                deque(itertools.islice(wdir_600, 0, 119))).mean(),
                np.cos(deque(itertools.islice(wdir_600,
                                              0, 119))).mean()) % (2 * np.pi)
            self.arrow = icon_vento_dir.annotate("", xy=(
                -wdir_600[0], 0), xytext=(-wdir_600[0], 1),
                arrowprops=dict(arrowstyle='fancy', fc='#4CB050', ec='w'),
                size=20)
            self.arrow_ = icon_rose.annotate("", xy=(
                -self.angle, 0), xytext=(-self.angle, 1),
                arrowprops=dict(arrowstyle='fancy', fc='#4FADD0', ec='w'),
                size=20)
            self.i_umid.set_text(u'%1.1f%%' % umid_600[0])
            self.i_pres.set_text(u'%1.1f\nhPa' % pres_600[0])
            self.i_temp.set_text(u'%1.1f\n\N{DEGREE SIGN}C' % temp_600[0])
            self.i_feel.set_text(u'%1.1f\n\N{DEGREE SIGN}C' % np.round(
                calc_real_feel(wspd_600[0], temp_600[0])))
            self.title_2.set_title(u'Medição Agora:\n%s' % data_now[0],
                                   fontweight='bold', y=0.1, fontsize=15)
        except RuntimeError:
            pass
        if data_now[0][-2:] == '05':
            # Desenha o icone de sensacao termica atual
            self.ab.remove()
            img_today = read_png(os.path.join('.\images', self.img.next()))
            imagebox = OffsetImage(img_today, zoom=0.11 * 1.6)
            self.ab = AnnotationBbox(imagebox, xybox=(0.3, 0.1), frameon=False,
                                     xycoords="data", boxcoords="data",
                                     xy=(0, 0), box_alignment=(0.0, 0.0))
            self.icon_feel.add_artist(self.ab)
        if data_now[0][-4:] == '0:05':
            self.i_rain.set_text(u'%1.1f mm\n acumulado' %
                                 np.sum(rain_24h_acu))
            if np.size(timeline) > 1 and np.size(timeline) < 6:
                minutos = np.size(timeline) * 10
                self.title_1.set_title(u'Estação Meteorológica do ' +
                                       u'OCEANOP\nSéries temporais ' +
                                       u'dos últimos ' +
                                       '%s minutos' % minutos,
                                       fontweight='bold', y=-0.1, loc='left',
                                       fontsize=18)
                self.refreshFigure()
            if np.size(timeline) > 5:
                minutos = np.size(timeline) % 6 * 10
                self.title_1.set_title(u'Estação Meteorológica do ' +
                                       u'OCEANOP\nSéries temporais ' +
                                       u'das últimas ' +
                                       '%s:%02.f Horas' %
                                       (np.size(timeline) / 6, float(minutos)),
                                       fontweight='bold', y=-0.1, loc='left',
                                       fontsize=18)
                self.refreshFigure()
        self.canvas.draw()
        self.after(500, self.icon_refresh, icon_vento_dir, icon_rose)


if __name__ == "__main__":
    SensorThread().start()
    MainWindow = App_Window(None)
    MainWindow.resizable(width=False, height=False)
    MainWindow.state('zoomed')
    MainWindow.config(cursor='none')
    MainWindow.mainloop()
