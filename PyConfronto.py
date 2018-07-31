# -*- coding: utf-8 -*-
__authors__ = ["Márcio Katsumi Yamashita"]
__email__ = ["marcio.yamashita.tetra_tech@petrobras.com.br"]
__created_ = ["05-Jan-2017"]
__modified__ = ["26-Jul-2018 "]

import Tkinter as tki
import sys
import pyocnp
import zlib as zb
import numpy as np
from collections import OrderedDict
from pandas import DataFrame, Series
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.colors import rgb2hex
from matplotlib.dates import DateFormatter
from matplotlib.dates import HourLocator, DayLocator, MonthLocator, YearLocator
from matplotlib.ticker import FuncFormatter


class UCD_confronto:
    u""" Interface Gráfica Principal ao Usuário (GUI) baseada em Tkinter. """

    def __init__(self, root):
        u""" Instanciar elementos gráficos (widgets) e ações atreladas. """
        # Definição de Cores ========================================= #
        # ============================================================ #
        BGCOLORBOX = (1.000, 1.000, 1.000)
        BGCOLORAPL = (0.392, 0.584, 0.929)
        BGCOLORSLT = (0.031, 0.572, 0.815)
        TXCOLORSTD = (0.000, 0.000, 0.000)  # texto padrão (preto)
        # Definição de Atributos ===================================== #
        # ============================================================ #
        # Janela gráfica de origem da aplicação.
        self._root = root
        # Bancos de dados disponíveis e chaves criptografadas de acesso.
        self._dbs = OrderedDict([(u"PROD", pyocnp.PROD_DBACCESS),
                                 (u"DESV", pyocnp.DESV_DBACCESS)])
        # Instância do BD.
        self._DBVIEW = u"UE6RK"
        # Opções de Parâmetros
        self._modapp = OrderedDict([
            (u"Int. Correntes", {u"sensores": [(71, u"AQUADOPP"),
                                               (3, u"FSI-2D"),
                                               (4, u"FSI-3D"),
                                               (2, u"ADCP"),
                                               (15, u"HADCP")],
                                 u"limite": 0.5}),
            (u"Dir. Correntes", {u"sensores": [(71, u"AQUADOPP"),
                                               (3, u"FSI-2D"),
                                               (4, u"FSI-3D"),
                                               (2, u"ADCP"),
                                               (15, u"HADCP")],
                                 u"limite": 10}),
            (u"Alt. Ondas", {u"sensores": [(4, u"FSI-3D"), (5, u"MIROS")],
                             u"limite": 0.5}),
            (u"Dir. Ondas", {u"sensores": [(4, u"FSI-3D"), (5, u"MIROS")],
                             u"limite": 20}),
            (u"Int. anem #1", {u"sensores": [(1, u"YOUNG")], u"limite": 3}),
            (u"Dir. anem #1", {u"sensores": [(1, u"YOUNG")], u"limite": 15}),
            (u"Int. anem #2", {u"sensores": [(1, u"YOUNG")], u"limite": 3}),
            (u"Dir. anem #2", {u"sensores": [(1, u"YOUNG")], u"limite": 15}),
            (u"Baro #1", {u"sensores": [(1, u"YOUNG")], u"limite": 1}),
            (u"Baro #2", {u"sensores": [(1, u"YOUNG")], u"limite": 1}),
            (u"Temp", {u"sensores": [(1, u"YOUNG")], u"limite": 2}),
            (u"Umid", {u"sensores": [(1, u"YOUNG")], u"limite": 5})])

        # Perfis de usuário.
        self._userprof = OrderedDict([
            (1, {u"perfil": u"PADRÃO",
                 u"BGCOLORAPL": (0.750, 0.750, 0.750)}),
            (2, {u"perfil": u"QUALIFICAÇÃO",
                 u"BGCOLORAPL": (0.392, 0.584, 0.929)}), ])

        # Frame Principal ============================================ #
        # ============================================================ #
        self._mainfrm = tki.Frame(self._root, bg=rgb2hex(BGCOLORAPL),
                                  bd=0, relief=tki.FLAT)

        # Barra de Opções.
        self._menubar = tki.Menu(self._mainfrm)

        # Barra/menu "Arquivo".
        menu = tki.Menu(self._menubar, tearoff=0)
        menu.add_command(label=u"Sair", command=lambda rt=self._root:
                         (rt.destroy(), plt.close('all')))
        self._menubar.add_cascade(label=u"Arquivo", menu=menu)

        # Barra/menu "Perfil".
        self._usergroup = tki.IntVar(value=1)
        uop = self._userprof[self._usergroup.get()]
        menu = tki.Menu(self._menubar, tearoff=0)
        for userid, userprof in self._userprof.iteritems():
            menu.add_radiobutton(label=userprof[u"perfil"], value=userid,
                                 variable=self._usergroup,
                                 command=self.setuserprof)
        self._menubar.add_cascade(label=u"Perfil", menu=menu)
        menu.add_separator()
        self._lim = tki.BooleanVar()
        menu.add_checkbutton(label=u"Alterar Limites", variable=self._lim,
                             command=self.setuplimits)
        # Associação da barra de opções ao frame principal.
        self._mainfrm.master.config(menu=self._menubar)

        # ============================================================ #
        # Frame de Período #
        # ============================================================ #
        self.fmt = '%d/%m/%Y %H:00:00'
        self._dtfrm = tki.Frame(self._mainfrm, bg=rgb2hex(BGCOLORAPL),
                                bd=2, relief=tki.GROOVE)
        self._dtfrm.pack(fill=tki.BOTH, padx=6, pady=4, side=tki.TOP)

        # Subframe de Período #
        # ============================================================ #
        self._datefrm = tki.Frame(self._dtfrm, bg=rgb2hex(BGCOLORAPL),
                                  bd=1, relief=tki.GROOVE)
        self._datefrm.pack(padx=1, pady=0, side=tki.LEFT, fill=tki.X,
                           expand=tki.YES)

        # Variável mutante da data inicial declarada (previamente
        # escolhida há 3 dias daquele de hoje).
        self._idate = tki.StringVar()
        self._idate.set((datetime.utcnow() -
                         timedelta(hours=72)).strftime(self.fmt))
        # Variável mutante da data final declarada (previamente
        # escolhida como o dia de hoje).
        self._fdate = tki.StringVar()
        self._fdate.set(datetime.utcnow().strftime(self.fmt))

        # Rótulo Data Ininal.
        tki.Label(self._datefrm, bd=0, bg=rgb2hex(BGCOLORAPL), fg='white',
                  text=u"Data Inicial", font=('Verdana', '8', 'bold'),
                  relief=tki.FLAT,
                  justify=tki.CENTER).grid(column=2, row=0, padx=2,
                                           pady=0, sticky=tki.EW)

        # Rótulo Data Final.
        tki.Label(self._datefrm, bd=0, bg=rgb2hex(BGCOLORAPL), fg='white',
                  text=u"Data Final", font=('Verdana', '8', 'bold'),
                  relief=tki.FLAT,
                  justify=tki.CENTER).grid(column=6, row=0, padx=2,
                                           pady=0, sticky=tki.EW)

        # Rótulo "Período".
        self._datefrm_rot = tki.Label(self._datefrm, bg=rgb2hex(BGCOLORAPL),
                                      bd=0, fg='white', text=u"Período:",
                                      font=('Verdana', '9', 'bold'),
                                      relief=tki.FLAT, justify=tki.RIGHT)
        self._datefrm_rot.grid(column=0, row=1, rowspan=2, padx=4,
                               pady=0, sticky=tki.NSEW)

        # Botões de acréscimo e decréscimo da data inicial
        dt = 1    # incremento (em dias)
        self._idatdbup = tki.Button(self._datefrm, bd=1, text=u"\u25B2",
                                    font=('Default', '5', 'bold'),
                                    command=lambda di=self._idate,
                                    df=self._fdate, dt=dt, md=self.moddatevar,
                                    mds=self.moddatestr:
                                    md(di, dt) if mds(di, dt) <= mds(df, 0)
                                    else md(di, 0))
        self._idatdbup.grid(column=1, row=1, padx=0, pady=0, sticky=tki.S)

        dt = -1    # decremento (em dias)
        self._idatdbdw = tki.Button(self._datefrm, bd=1, text=u"\u25BC",
                                    font=('Default', '5', 'bold'),
                                    command=lambda di=self._idate, dt=dt,
                                    md=self.moddatevar: md(di, dt))
        self._idatdbdw.grid(column=1, row=2, padx=0, pady=0, sticky=tki.N)

        dt = 1. / 24.    # incremento (em horas)
        self._idathbup = tki.Button(self._datefrm, bd=1, text=u"\u25B3",
                                    font=('Default', '5', 'bold'),
                                    command=lambda di=self._idate,
                                    df=self._fdate, dt=dt, md=self.moddatevar,
                                    mds=self.moddatestr:
                                    md(di, dt) if mds(di, dt) <= mds(df, 0)
                                    else md(di, 0))
        self._idathbup.grid(column=3, row=1, padx=0, pady=0, sticky=tki.S)

        dt = -1. / 24.    # decremento (em horas)
        self._idathbdw = tki.Button(self._datefrm, bd=1, text=u"\u25BD",
                                    font=('Default', '5', 'bold'),
                                    command=lambda di=self._idate, dt=dt,
                                    md=self.moddatevar: md(di, dt))
        self._idathbdw.grid(column=3, row=2, padx=0, pady=0, sticky=tki.N)

        # Campo de entrada da data inicial de consulta
        self._idatent = tki.Entry(self._datefrm, bd=3, width=19,
                                  textvariable=self._idate, justify=tki.CENTER)
        self._idatent.grid(column=2, row=1, rowspan=2, padx=0, pady=2,
                           ipady=2, sticky=tki.EW)

        # Rótulo de controle e interligação de espaçamento.
        tki.Label(self._datefrm, bg=rgb2hex(BGCOLORAPL), bd=0, relief=tki.FLAT,
                  fg='white', text=u"até", font=('Verdana', '9', 'normal'),
                  justify=tki.CENTER).grid(column=4, row=1, rowspan=2, padx=8,
                                           pady=0, sticky=tki.NSEW)

        # Campo de entrada da data final de consulta
        self._fdatent = tki.Entry(self._datefrm, bd=3, width=19,
                                  textvariable=self._fdate, justify=tki.CENTER)
        self._fdatent.grid(column=6, row=1, rowspan=2, padx=0, pady=2,
                           ipady=2, sticky=tki.E)

        # Botões de acréscimo e decréscimo da data final
        dt = 1    # incremento (em dias)
        self._fdatdbup = tki.Button(self._datefrm, bd=1, text=u"\u25B2",
                                    font=('Default', '5', 'bold'),
                                    command=lambda df=self._fdate, dt=dt,
                                    md=self.moddatevar: md(df, dt))
        self._fdatdbup.grid(column=5, row=1, padx=0, pady=0, sticky=tki.S)

        dt = -1    # decremento (em dias)
        self._fdatdbdw = tki.Button(self._datefrm, bd=1, text=u"\u25BC",
                                    font=('Default', '5', 'bold'),
                                    command=lambda di=self._idate,
                                    df=self._fdate, dt=dt, md=self.moddatevar,
                                    mds=self.moddatestr:
                                    md(df, dt) if mds(df, dt) >= mds(di, 0)
                                    else md(df, 0))
        self._fdatdbdw.grid(column=5, row=2, padx=0, pady=0, sticky=tki.N)

        dt = 1. / 24.    # incremento (em horas)
        self._fdathbup = tki.Button(self._datefrm, bd=1, text=u"\u25B3",
                                    font=('Default', '5', 'bold'),
                                    command=lambda df=self._fdate, dt=dt,
                                    md=self.moddatevar: md(df, dt))
        self._fdathbup.grid(column=7, row=1, padx=0, pady=0, sticky=tki.S)

        dt = -1. / 24.    # decremento (em horas)
        self._fdathbdw = tki.Button(self._datefrm, bd=1, text=u"\u25BD",
                                    font=('Default', '5', 'bold'),
                                    command=lambda di=self._idate,
                                    df=self._fdate, dt=dt, md=self.moddatevar,
                                    mds=self.moddatestr:
                                    md(df, dt) if mds(df, dt) >= mds(di, 0)
                                    else md(di, 0))
        self._fdathbdw.grid(column=7, row=2, padx=0, pady=0, sticky=tki.N)

        self._idate.trace("w", lambda vn, en, md, dn=self._idatent:
                          dn.config(fg=rgb2hex(TXCOLORSTD)))
        self._fdate.trace("w", lambda vn, en, md, dn=self._fdatent:
                          dn.config(fg=rgb2hex(TXCOLORSTD)))

        # Subframe de porcentagens #
        # ============================================================ #
        self._perfrm = tki.Frame(self._dtfrm, bd=1, relief=tki.GROOVE,
                                 bg=rgb2hex((0.750, 0.750, 0.750)))
        self._perfrm.pack(padx=1, pady=0, side=tki.LEFT, fill=tki.X,
                          expand=tki.YES)

        # Variável mutante de percentagem inicial falhas
        self._iperfail = tki.StringVar()
        self._iperfail.set(5)
        # Variável mutante de percentagem inicial reprovações
        self._iperrep = tki.StringVar()
        self._iperrep.set(5)

        # Rótulo % falhas.
        tki.Label(self._perfrm, bd=0, bg=rgb2hex(BGCOLORAPL), fg='white',
                  text=u"% Falhas", font=('Verdana', '8', 'bold'),
                  relief=tki.FLAT,
                  justify=tki.CENTER).grid(column=2, row=0, padx=2,
                                           pady=0, sticky=tki.EW)

        # Rótulo % reprovações.
        tki.Label(self._perfrm, bd=0, bg=rgb2hex(BGCOLORAPL), fg='white',
                  text=u"% Reprovações", font=('Verdana', '8', 'bold'),
                  relief=tki.FLAT,
                  justify=tki.CENTER).grid(column=3, row=0, padx=2,
                                           pady=0, sticky=tki.EW)

        # Rótulo "Limites".
        self._perfrm_rot = tki.Label(self._perfrm, bg=rgb2hex(BGCOLORAPL),
                                     bd=0, fg='white', text=u"Limites: ",
                                     font=('Verdana', '9', 'bold'),
                                     relief=tki.FLAT, justify=tki.RIGHT)
        self._perfrm_rot.grid(column=0, row=1, rowspan=2, padx=4,
                              pady=0, sticky=tki.NSEW)

        # Campo de entrada de percentagem inicial de falhas
        self._iperfailent = tki.Entry(self._perfrm, bd=3, width=10,
                                      textvariable=self._iperfail,
                                      justify=tki.CENTER)
        self._iperfailent.grid(column=2, row=1, rowspan=2, padx=0, pady=2,
                               ipady=2, sticky=tki.EW)
        # Campo de entrada de percentagem de reprovações
        self._iperrepent = tki.Entry(self._perfrm, bd=3, width=10,
                                     textvariable=self._iperrep,
                                     justify=tki.CENTER)
        self._iperrepent.grid(column=3, row=1, rowspan=2, padx=0, pady=2,
                              ipady=2, sticky=tki.E)

        #  previamente desabilitada
        self.disable(self._perfrm.winfo_children())

        # Subframe de diferenças #
        # ============================================================ #
        self._delfrm = tki.Frame(self._dtfrm, bd=1, relief=tki.GROOVE,
                                 bg=rgb2hex((0.750, 0.750, 0.750)))
        self._delfrm.pack(padx=1, pady=0, side=tki.LEFT, fill=tki.X,
                          expand=tki.YES)

        # Variável mutante de delta máximo aceitável
        self._idelrep = tki.StringVar()

        # Rótulo Delta máx.
        tki.Label(self._delfrm, bd=0, bg=rgb2hex(BGCOLORAPL), fg='white',
                  text=u"Delta máx", font=('Verdana', '8', 'bold'),
                  relief=tki.FLAT,
                  justify=tki.CENTER).grid(column=2, row=0, padx=2,
                                           pady=0, sticky=tki.EW)

        # Campo de entrada de delta máximo aceitavel
        self._idelent = tki.Entry(self._delfrm, bd=3, width=10,
                                  textvariable=self._idelrep,
                                  justify=tki.CENTER)
        self._idelent.grid(column=2, row=1, rowspan=2, padx=0, pady=2,
                           ipady=2, sticky=tki.E)

        #  previamente desabilitada
        self.disable(self._delfrm.winfo_children())

        # ============================================================ #
        # Frame de Controle
        # ============================================================ #
        self._ctrl_frm = tki.Frame(self._mainfrm, bg=rgb2hex(BGCOLORAPL),
                                   bd=2, relief=tki.GROOVE)
        self._ctrl_frm.pack(fill=tki.BOTH, padx=6, pady=4, side=tki.LEFT)

        # Subframe Controle
        # ============================================================ #
        self._ctrl_Sfrm = tki.Frame(self._ctrl_frm, bg=rgb2hex(BGCOLORAPL),
                                    bd=0, relief=tki.GROOVE)
        self._ctrl_Sfrm.pack(padx=2, pady=2, side=tki.TOP)

        # Label Controle
        tki.Label(self._ctrl_Sfrm, bd=0, bg=rgb2hex(BGCOLORAPL), fg='white',
                  text=u"CONTROLE", font=('Verdana', '10', 'bold'),
                  relief=tki.FLAT,
                  justify=tki.CENTER).grid(column=1, row=0, padx=2,
                                           pady=0, sticky=tki.EW)

        # Menu de Opções de BDs Controle
        self._ctrl_Sfrm_bd = tki.Label(self._ctrl_Sfrm, bg=rgb2hex(BGCOLORAPL),
                                       fg='white', bd=0, text=u"Banco:",
                                       font=('Verdana', '9', 'bold'),
                                       relief=tki.FLAT, justify=tki.LEFT)
        self._ctrl_Sfrm_bd.grid(column=0, row=1, rowspan=1, padx=10,
                                pady=2, sticky=tki.NSEW)

        # Variável mutante do BD Controle
        self._db_ctrl_var = tki.StringVar()

        # Menu de BDs disponíveis para consulta.
        self._db_ctrl_opt = tki.OptionMenu(self._ctrl_Sfrm, self._db_ctrl_var,
                                           *self._dbs.keys(),
                                           command=self.list_ucds_ctrl)
        self._db_ctrl_opt.grid(column=1, row=1, rowspan=1, padx=4, pady=0,
                               sticky=tki.NSEW)

        # Menu de Opções de Parâmetros Controle
        self._ctrl_Sfrm_param = tki.Label(self._ctrl_Sfrm,
                                          bg=rgb2hex(BGCOLORAPL),
                                          bd=0, fg='white', text=u"Param.:",
                                          font=('Verdana', '9', 'bold'),
                                          relief=tki.FLAT, justify=tki.CENTER)
        self._ctrl_Sfrm_param.grid(column=0, row=2, rowspan=1,
                                   padx=2, pady=2, sticky=tki.NSEW)

        # Variável mutante do Parâmetro Controle
        self._param_ctrl_var = tki.StringVar()

        # Menu de Parâmetros disponíveis para consulta.
        self._param_ctrl_opt = tki.OptionMenu(self._ctrl_Sfrm,
                                              self._param_ctrl_var,
                                              *self._modapp.keys(),
                                              command=self.askparam_ctrl)
        self._param_ctrl_opt.grid(column=1, row=2, rowspan=1, padx=4, pady=0,
                                  sticky=tki.NSEW)

        # Menu de Opções Sensores Controle
        self._ctrl_Sfrm_sensor = tki.Label(self._ctrl_Sfrm,
                                           bg=rgb2hex(BGCOLORAPL),
                                           bd=0, fg='white', text=u"Sensor:",
                                           font=('Verdana', '9', 'bold'),
                                           relief=tki.FLAT, justify=tki.CENTER)
        self._ctrl_Sfrm_sensor.grid(column=0, row=3, rowspan=1,
                                    padx=10, pady=2, sticky=tki.NSEW)

        # Variável mutante do Sensor Controle
        self._sensor_ctrl_var = tki.StringVar()

        # Menu de Sensor disponíveis para consulta.
        self._sensor_ctrl_opt = tki.OptionMenu(self._ctrl_Sfrm,
                                               self._sensor_ctrl_var, ())
        self._sensor_ctrl_opt.grid(column=1, row=3, rowspan=1, padx=4, pady=0,
                                   sticky=tki.NSEW)

        # Subframe de UCDs Controle
        # ============================================================ #
        self._ctrl_Sfrm_ucdsmenu = tki.Label(self._ctrl_Sfrm,
                                             bg=rgb2hex(BGCOLORAPL),
                                             bd=0, fg='white', text=u"UCDs:",
                                             font=('Verdana', '9', 'bold'),
                                             relief=tki.FLAT,
                                             justify=tki.CENTER)
        self._ctrl_Sfrm_ucdsmenu.grid(column=0, columnspan=1, row=5, rowspan=2,
                                      padx=2, pady=0, sticky=tki.N)

        # Listagem de UCDs disponíveis para consulta.
        self._ucdslbx_ctrl = tki.Listbox(self._ctrl_Sfrm, bd=1,
                                         activestyle='none',
                                         selectmode=tki.SINGLE,
                                         width=16, height=1,
                                         selectborderwidth=3,
                                         setgrid=tki.NO,
                                         exportselection=tki.FALSE,
                                         selectbackground=rgb2hex(BGCOLORSLT),
                                         font=('Verdana', '11', 'bold'))
        self._ucdslbx_ctrl.grid(column=1, row=5, rowspan=2, padx=0, pady=0,
                                sticky=tki.NS)

        # Menu de UCDs para consulta facilitada.
        self._ucdsmenuctrl = tki.Menu(self._root, tearoff=0)

        # Opção de declaração de camada vertical do sensor ADCP com
        # visualização condicional à seleção.
        self._layer_ctrl = tki.IntVar()
        self._layerlbl_ctrl = tki.Label(self._ctrl_Sfrm, bd=0, fg='white',
                                        bg=rgb2hex(BGCOLORAPL),
                                        text=u"camada:", relief=tki.FLAT,
                                        font=('Verdana', '7', 'bold'),
                                        justify=tki.RIGHT)
        self._layerent_ctrl = tki.Entry(self._ctrl_Sfrm, bd=1, width=2,
                                        textvariable=self._layer_ctrl,
                                        font=('Default', '7', 'normal'),
                                        bg=rgb2hex(BGCOLORBOX),
                                        justify=tki.RIGHT)

        # Botão de incremento de camada.
        self._layerbup_ctrl = tki.Button(self._ctrl_Sfrm, bd=1, text=u"\u25B2",
                                         font=('Default', '5', 'bold'),
                                         command=lambda ly=self._layer_ctrl:
                                         ly.set(ly.get() + 1))

        # Botão de decremento de camada.
        self._layerbdw_ctrl = tki.Button(self._ctrl_Sfrm, bd=1, text=u"\u25BC",
                                         font=('Default', '5', 'bold'),
                                         command=lambda ly=self._layer_ctrl:
                                         ly.set(ly.get() - 1) if ly.get() > 0
                                         else ly.set(ly.get() + 0))

        # ============================================================ #
        # Frame de UCDs Teste
        # ============================================================ #
        self._teste_frm = tki.Frame(self._mainfrm, bg=rgb2hex(BGCOLORAPL),
                                    bd=2, relief=tki.GROOVE)
        self._teste_frm.pack(fill=tki.BOTH, padx=6, pady=4, side=tki.LEFT)

        # Subframe de BDs Teste
        # ============================================================ #
        self._teste_Sfrm = tki.Frame(self._teste_frm, bg=rgb2hex(BGCOLORAPL),
                                     bd=0, relief=tki.GROOVE)
        self._teste_Sfrm.pack(padx=2, pady=2, side=tki.TOP)

        # Label TESTE
        tki.Label(self._teste_Sfrm, bd=0, bg=rgb2hex(BGCOLORAPL), fg='white',
                  text=u"TESTE", font=('Verdana', '10', 'bold'),
                  relief=tki.FLAT,
                  justify=tki.CENTER).grid(column=1, row=0, padx=2,
                                           pady=0, sticky=tki.EW)

        # Menu de Opções de BDs Teste
        self._teste_Sfrm_bd = tki.Label(self._teste_Sfrm, fg='white', bd=0,
                                        bg=rgb2hex(BGCOLORAPL), text=u"Banco:",
                                        font=('Verdana', '9', 'bold'),
                                        relief=tki.FLAT, justify=tki.LEFT)
        self._teste_Sfrm_bd.grid(column=0, row=1, rowspan=1, padx=10,
                                 pady=2, sticky=tki.NSEW)

        # Variável mutante do BD Teste
        self._db_teste_var = tki.StringVar()

        # Menu de BDs disponíveis para consulta.
        self._db_teste_opt = tki.OptionMenu(self._teste_Sfrm,
                                            self._db_teste_var,
                                            *self._dbs.keys(),
                                            command=self.list_ucds_teste)
        self._db_teste_opt.grid(column=1, row=1, rowspan=1, padx=4, pady=0,
                                sticky=tki.NSEW)

        # Menu de Opções de Parâmetros Teste
        self._teste_Sfrm_param = tki.Label(self._teste_Sfrm, bd=0, fg='white',
                                           bg=rgb2hex(BGCOLORAPL),
                                           text=u"Param.:",
                                           font=('Verdana', '9', 'bold'),
                                           relief=tki.FLAT, justify=tki.CENTER)
        self._teste_Sfrm_param.grid(column=0, row=2, rowspan=1,
                                    padx=2, pady=2, sticky=tki.NSEW)

        # Variável mutante do Parâmetro selecionado.
        self._param_teste_var = tki.StringVar()

        # Menu de Parâmetros disponíveis para consulta.
        self._param_teste_opt = tki.OptionMenu(self._teste_Sfrm,
                                               self._param_teste_var,
                                               *self._modapp.keys(),
                                               command=self.askparam_teste)
        self._param_teste_opt.grid(column=1, row=2, rowspan=1, padx=4, pady=0,
                                   sticky=tki.NSEW)

        # Menu de Opções de Sensores Teste
        self._teste_Sfrm_sensor = tki.Label(self._teste_Sfrm, bd=0, fg='white',
                                            bg=rgb2hex(BGCOLORAPL),
                                            text=u"Sensor:", relief=tki.FLAT,
                                            font=('Verdana', '9', 'bold'),
                                            justify=tki.CENTER)
        self._teste_Sfrm_sensor.grid(column=0, row=3, rowspan=1,
                                     padx=10, pady=2, sticky=tki.NSEW)

        # Variável mutante do Sensor Teste
        self._sensor_teste_var = tki.StringVar()

        # Menu de Sensor disponíveis para consulta.
        self._sensor_teste_opt = tki.OptionMenu(self._teste_Sfrm,
                                                self._sensor_teste_var,
                                                ())
        self._sensor_teste_opt.grid(column=1, row=3, rowspan=1, padx=4, pady=0,
                                    sticky=tki.NSEW)

        # Subframe de UCDs Teste
        # ============================================================ #
        self._teste_Sfrm_ucdsmenu = tki.Label(self._teste_Sfrm, bd=0,
                                              bg=rgb2hex(BGCOLORAPL),
                                              text=u"UCDs:", fg='white',
                                              font=('Verdana', '9', 'bold'),
                                              relief=tki.FLAT,
                                              justify=tki.CENTER)
        self._teste_Sfrm_ucdsmenu.grid(column=0, columnspan=1,  padx=2, pady=0,
                                       row=4, rowspan=2, sticky=tki.N)

        # Listagem de UCDs disponíveis para consulta.
        self._ucdslbx_teste = tki.Listbox(self._teste_Sfrm, bd=1,
                                          activestyle='none',
                                          selectmode=tki.SINGLE,
                                          width=16, height=1,
                                          selectborderwidth=3,
                                          setgrid=tki.NO,
                                          exportselection=tki.FALSE,
                                          selectbackground=rgb2hex(BGCOLORSLT),
                                          font=('Verdana', '11', 'bold'))
        self._ucdslbx_teste.grid(column=1, columnspan=1, row=4, rowspan=2,
                                 padx=0, pady=0, sticky=tki.NS)

        # Menu de UCDs para consulta facilitada.
        self._ucdsmenuteste = tki.Menu(self._root, tearoff=0)

        # Opção de declaração de camada vertical do sensor ADCP com
        # visualização condicional à seleção.
        self._layer_teste = tki.IntVar()
        self._layerlbl_teste = tki.Label(self._teste_Sfrm, bd=0, fg='white',
                                         bg=rgb2hex(BGCOLORAPL),
                                         text=u"camada:",
                                         font=('Verdana', '7', 'bold'),
                                         relief=tki.FLAT, justify=tki.RIGHT)
        self._layerent_teste = tki.Entry(self._teste_Sfrm, bd=1, width=2,
                                         textvariable=self._layer_teste,
                                         font=('Default', '7', 'normal'),
                                         background=rgb2hex(BGCOLORBOX),
                                         justify=tki.RIGHT)

        # Botão de incremento de camada.
        self._layerbup_teste = tki.Button(self._teste_Sfrm, bd=1,
                                          text=u"\u25B2",
                                          font=('Default', '5', 'bold'),
                                          command=lambda ly=self._layer_teste:
                                          ly.set(ly.get() + 1))

        # Botão de decremento de camada.
        self._layerbdw_teste = tki.Button(self._teste_Sfrm, bd=1,
                                          text=u"\u25BC",
                                          font=('Default', '5', 'bold'),
                                          command=lambda ly=self._layer_teste:
                                          ly.set(ly.get() - 1) if ly.get() > 0
                                          else ly.set(ly.get() + 0))
        self._root.update_idletasks()

        # ============================================================ #
        # Frame de Mensagem
        # ============================================================ #
        self._msgfrm = tki.Frame(self._mainfrm, bg=rgb2hex(BGCOLORAPL),
                                 bd=0, relief=tki.FLAT)
        self._msgfrm.pack(expand=tki.YES, padx=0, pady=0, side=tki.TOP)

        # Subframe de Mensagem
        # ============================================================ #
        self._qrymsg = tki.Label(self._msgfrm, bg=rgb2hex(BGCOLORAPL),
                                 bd=0, fg='white', text=u"Mensagem:",
                                 font=('Verdana', '9', 'bold'),
                                 relief=tki.FLAT, justify=tki.CENTER)
        self._qrymsg.grid(column=1, columnspan=1, row=1, rowspan=1,
                          padx=1, pady=1, sticky=tki.N)

        # Variável mutante da ensagem
        self._msg = tki.StringVar()
        self._msg.set("Escolha os Parâmetros")

        # Opções de mensagem
        self._qrymsgbox = tki.Label(self._msgfrm, bd=1, width=25, fg='yellow',
                                    bg=rgb2hex(BGCOLORAPL),
                                    font=('Verdana', '12', 'bold'),
                                    textvariable=self._msg, justify=tki.CENTER)
        self._qrymsgbox.grid(column=1, columnspan=1, row=2, rowspan=1,
                             padx=1, pady=1, sticky=tki.N)

        # ============================================================ #
        # Frame de Execução
        # ============================================================ #
        self._modfrm = tki.Frame(self._mainfrm, bg=rgb2hex(BGCOLORAPL),
                                 bd=2, relief=tki.GROOVE)
        self._modfrm.pack(fill=tki.BOTH, padx=6, pady=4, side=tki.RIGHT)

        # Label Execução
        self._modfrm_name = tki.Label(self._modfrm, bd=0, text=u"Execução:",
                                      bg=rgb2hex(BGCOLORAPL), fg='white',
                                      font=('Verdana', '9', 'bold'),
                                      relief=tki.FLAT, justify=tki.CENTER)
        self._modfrm_name.pack(padx=0, pady=0, side=tki.TOP,
                               anchor=tki.CENTER, expand=tki.YES, fill=tki.X)

        # Módulos de estado da aplicação.
        self._modvar = tki.StringVar()
        self._modfrm1 = tki.Frame(self._modfrm, bg=rgb2hex(BGCOLORAPL),
                                  bd=0, relief=tki.GROOVE)

        self._modfrm1.pack(padx=0, pady=0, ipadx=0, ipady=0, side=tki.TOP,
                           anchor=tki.CENTER, expand=tki.YES, fill=tki.X)

        self._qrybt = tki.Button(self._modfrm1,
                                 bd=2, text="Plot", command=self.askplot)
        self._qrybt.pack(padx=0, pady=0, ipadx=2, ipady=0, side=tki.LEFT,
                         anchor=tki.CENTER, expand=tki.YES, fill=tki.X)

        self._mainfrm.pack(fill=tki.BOTH, padx=0, pady=0, side=tki.TOP)
        self._root.update()
        # Carregamento de agrupamentos de UCDs definidos pela aplicação.
        self._uselvar = tki.StringVar()

    def enable(self, childList):
        userid = self._usergroup.get()
        for child in childList:
            child.configure(state='normal', bg=rgb2hex(
                self._userprof[userid][u"BGCOLORAPL"]))

    def disable(self, childList):
        userid = self._usergroup.get()
        for child in childList:
            child.configure(state='disable', bg=rgb2hex(
                self._userprof[userid][u"BGCOLORAPL"]))

    def setuplimits(self):
        if self._usergroup.get() == 2:
            if self._lim.get():
                self._iperfailent.configure(
                    state='normal', bg=rgb2hex((1.000, 1.000, 1.000)))
                self._iperrepent.configure(
                    state='normal', bg=rgb2hex((1.000, 1.000, 1.000)))
                self._idelent.configure(
                    state='normal', bg=rgb2hex((1.000, 1.000, 1.000)))
            else:
                self._iperfailent.configure(state='disable')
                self._iperrepent.configure(state='disable')
                self._idelent.configure(state='disable')
        else:
            self._lim.set(False)

    def setuserprof(self):
        """ Selecionar perfil de usuário. """
        userid = self._usergroup.get()
        if userid == 2:
            self.enable(self._perfrm.winfo_children())
            self._perfrm.configure(bg=rgb2hex(
                self._userprof[userid][u"BGCOLORAPL"]))
            self.enable(self._delfrm.winfo_children())
            self._delfrm.configure(bg=rgb2hex(
                self._userprof[userid][u"BGCOLORAPL"]))
            self._iperfailent.configure(state='disable')
            self._iperrepent.configure(state='disable')
            self._idelent.configure(state='disable')
            self._lim.set(False)
        else:
            self._perfrm.configure(
                bg=rgb2hex(self._userprof[userid][u"BGCOLORAPL"]))
            self._delfrm.configure(bg=rgb2hex(
                self._userprof[userid][u"BGCOLORAPL"]))
            self.disable(self._perfrm.winfo_children())
            self.disable(self._delfrm.winfo_children())
            self._lim.set(False)

    def moddatevar(self, date, dtdays):
        u""" Aumentar/diminuir data do período de consulta. """
        try:
            date.set((datetime.strptime(date.get(), self.fmt) +
                      timedelta(dtdays)).strftime(self.fmt))
        except Exception:
            date.set(datetime.utcnow().strftime(self.fmt))

    def moddatestr(self, date, dtdays):
        """ Aumentar/diminuir data qualquer. """
        try:
            return(datetime.strptime(date.get(), self.fmt) + timedelta(dtdays))
        except Exception:
            return(datetime.utcnow().strftime(self.fmt))

    def ucds(self, loc, dbvalue):
        """ Criar lista de UCDs disponíveis para consulta no BD. """
        # Requisição das UCDs ao BD #
        # ============================================================ #
        # Erros esperados/contornados:
        #     [-] falha de comunicação com o BD.
        try:
            dbqry = ("SELECT"
                     " TB_LOCAL_INSTAL.LOIN_CD_LOCAL,"
                     " UNISTR(TB_LOCAL_INSTAL.LOIN_TX_LOCAL)"
                     " FROM"
                     " UE6RK.TB_LOCAL_INSTAL"
                     " ORDER BY"
                     " TB_LOCAL_INSTAL.LOIN_TX_LOCAL")
            ucds = pyocnp.odbqry_all(dbqry,
                                     pyocnp.asciidecrypt(self._dbs[dbvalue]))
        except Exception:
            # Atualização de status: BD inacessivel.
            self._msg.set(u'%s INDISPONÍVEL' % dbvalue)
            raise
        # Limpeza do menu de UCDs
        getattr(self, '_ucdslbx_{}'.format(loc)).delete(0, tki.END)
        setattr(self, '_ucds_{}'.format(loc), ucds)
        for lstid, lstnm in getattr(self, '_ucds_{}'.format(loc)):
            getattr(self, '_ucdslbx_{}'.format(loc)).insert(tki.END, lstnm)
        self._ucdsmenuvars = list()
        self.menuaval(getattr(self, '_ucdsmenu{}'.format(loc)),
                      getattr(self, '_{}_Sfrm_ucdsmenu'.format(loc)),
                      getattr(self, '_ucdslbx_{}'.format(loc)),
                      self._ucdsmenuvars)
        getattr(self, '_{}_Sfrm_ucdsmenu'.format(loc))["cursor"] = "sizing"
        getattr(self,
                '_{}_Sfrm_ucdsmenu'.format(loc))["text"] = u"UCDs:\n\u2630"

    def list_ucds_ctrl(self, dbvalue):
        u""" Listar UCDs disponíveis para consulta no BD. """
        self.ucds('ctrl', dbvalue)

    def list_ucds_teste(self, dbvalue):
        u""" Listar UCDs disponíveis para consulta no BD. """
        self.ucds('teste', dbvalue)

    def menu_param(self, loc, param):
        # Limpeza do menu de sensores
        menu = getattr(self, '_sensor_{0}_opt'.format(loc))["menu"]
        menu.delete(0, "end")
        getattr(self, '_sensor_{0}_var'.format(loc)).set(' ')
        # Oferta da lista de sensores disponíveis.
        setattr(self, '_eqps_{}'.format(loc), self._modapp[param][u"sensores"])
        for lstid, lstnm in getattr(self, '_eqps_{}'.format(loc)):
            menu.add_command(label=lstnm, command=lambda value=lstnm:
                             getattr(self,
                                     '_sensor_{0}_var'.format(loc)).set(value))
        # Oferecer/Ocultar da seleção de camada do ADCP.
        (self.adcp_layer(loc, True) if "Correntes" in
            getattr(self, '_param_{}_var'.format(loc)).get()
            else self.adcp_layer(loc, False))

    def askparam_ctrl(self, param):
        u""" Listar Parâmetros Controle disponíveis para consulta. """
        self.menu_param('ctrl', param)
        # limite do parâmetro.
        self._idelrep.set(self._modapp[param][u"limite"])

    def askparam_teste(self, param):
        u""" Listar Parâmetros Teste disponíveis para consulta. """
        self.menu_param('teste', param)

    def adcp_layer(self, loc, in_=False):
        KW = {'_layerlbl': {'column': 1,  'row': 8, 'padx': 0, 'pady': 0,
                            'columnspan': 1, 'rowspan': 2, 'sticky': tki.E},
              '_layerent': {'column': 2,  'row': 8, 'padx': 0, 'pady': 0,
                            'columnspan': 2, 'rowspan': 2, 'sticky': tki.E},
              '_layerbup': {'column': 4,  'row': 8, 'padx': 0, 'pady': 0,
                            'columnspan': 1, 'rowspan': 1, 'sticky': tki.S},
              '_layerbdw': {'column': 4,  'row': 9, 'padx': 0, 'pady': 0,
                            'columnspan': 1, 'rowspan': 1, 'sticky': tki.N}}
        [getattr(self, '{0}_{1}'.format(i, loc)).grid(**KW[i]) if in_ else
            getattr(self,
                    '{0}_{1}'.format(i, loc)).grid_forget() for i in KW.keys()]

    def mk_qry(self, loc):
        try:
            setattr(self, 'dbqry', self._dbs[
                getattr(self, '_db_{0}_var'.format(loc)).get()])
            ucd_id = getattr(self, '_ucds_{0}'.format(loc))[
                getattr(self, '_ucdslbx_{0}'.format(loc)).curselection()[0]][0]
            setattr(self, 'ucdqry', ucd_id)
            eqp_id = [id for id, nm in getattr(self, '_eqps_{0}'.format(loc))
                      if nm == getattr(
                          self, '_sensor_{0}_var'.format(loc)).get()][0]
            setattr(self, 'eqpqry', eqp_id)
            setattr(
                self, 'lyrqry', getattr(self, '_layer_{0}'.format(loc)).get())
            Data = self.GET_data(
                self.ucdqry, getattr(self, '_param_{0}_var'.format(loc)).get())
            setattr(self, '_msg_{0}'.format(loc),
                    'NOK' if Data == 'error' else 'OK')
            return Data
        except Exception:
            setattr(self, '_msg_{0}'.format(loc), 'NOK')

    def askplot(self):
        """ Busca os dados e faz o plots. """
        plt.close()
        # First illustrate basic pyplot interface,
        # using defaults where possible.
        fig = plt.figure(1, facecolor=(1.0, 1.0, 1.0), figsize=(12, 8))
        self.ax = fig.add_subplot(1, 1, 1)
        self.ax.grid('on')

        # Diagramação e exibição da figura.
        fig.show()
        fig.canvas.draw()
        lgnd = []
        self._msg_ctrl, self._msg_teste = ' ', ' '

        # Desativação temporária do botão de consulta aos dados.
        self._qrybt["state"] = tki.DISABLED
        self._msg.set(u"Aguarde")
        self._root.update()

        Data_control = self.mk_qry('ctrl')
        Data_teste = self.mk_qry('teste')
        self.ax.set_title(' ')
        if self._msg_ctrl == 'OK' and self._msg_teste == 'OK':
            self.ax.plot(Data_control['t'], Data_control['data0'], '.-g')
            lgnd.append('{} @ {}'.format(Data_control['tag'],
                                         self._db_ctrl_var.get()))
            self.ax.set_ylabel(u'{} ({})'.format(Data_control['data0quant'],
                                                 Data_control['data0unit']),
                               fontsize=12)
            self.df = DataFrame({'CTRL': Series(Data_control['data0'],
                                                index=Data_control['t']),
                                 'TESTE': Series(Data_teste['data0'],
                                                 index=Data_teste['t'])})
            if self._param_ctrl_var.get()[:9] == "Int. anem":
                idx = Data_control['data0'] <= 3
                if sum(idx) > 0:
                    self.ax.plot(Data_control['t'][idx],
                                 Data_control['data0'][idx], 'og')
                    lgnd.append('Vento abaixo de 3m/s')
            if Data_control['data0quant'] == Data_teste['data0quant']:
                self.df['diff'] = abs(self.df.CTRL - self.df.TESTE)
                if self._param_ctrl_var.get()[:9] == "Dir. anem":
                    idx = self.df['diff'] > 180
                    self.df['diff'][idx] = (360 - self.df['diff'][idx])
                self.ax.plot(Data_teste['t'], Data_teste['data0'], '.-y')
                ttl = (u'Diferença média absoluta ({:1.2f} \u00B1 {:1.2f})'
                       '{}'.format(self.df['diff'].mean(), self.df[
                           'diff'].std(), Data_control['data0unit']))
                self.ax.set_title(ttl)
                lgnd.append('{} @ {}'.format(Data_teste['tag'],
                                             self._db_teste_var.get()))
                if self._param_teste_var.get()[:9] == "Int. anem":
                    idx = Data_teste['data0'] <= 3
                    if sum(idx) > 0:
                        self.ax.plot(Data_teste['t'][idx],
                                     Data_teste['data0'][idx], 'oy')
                        lgnd.append('Vento abaixo de 3m/s')
                if self._usergroup.get() == 2:
                    rep, idx = self.count_rep(self._idelrep.get(), lgnd)
                    falhas = self.count_fail(Data_teste)
                    ttl = (u'[{:1.1f}%] Falhas na série de Teste\n'
                           u'[{:1.1f}%] Reprovações acima do Limite de'
                           '{}{}').format(falhas, rep, self._idelrep.get(),
                                          Data_control['data0unit'])
                    self.ax.plot(self.df.index[idx.values],
                                 self.df['TESTE'][idx], 'Dk')
                    if (falhas >= float(self._iperfail.get())) or (rep >= float(self._iperrep.get())):
                        self.ax.set_title(ttl, color='r')
                    else:
                        self.ax.set_title(ttl)
                self.ax.legend(lgnd, framealpha=0.6, loc=0)
                self.setaxdate(fig.axes[0], self.df.index.min(),
                               self.df.index.max())
            else:
                self.ax0 = self.ax.twinx()
                self.ax0.tick_params(axis='y', colors='y')
                self.ax0.set_ylabel(u'{} ({})'.format(Data_teste['data0quant'],
                                                      Data_teste['data0unit']),
                                    fontsize=12, color='y')
                self.ax0.plot(Data_teste['t'], Data_teste['data0'], '.-y')
                lgnd.append('{} @ {}'.format(Data_teste['tag'],
                                             self._db_teste_var.get()))
                if self._param_teste_var.get()[:3] == "Dir":
                    self.ax0.set_ylim((0., 360.))
                if self._param_teste_var.get()[:3] == "Bar":
                    (self.ax0.get_yaxis().set_major_formatter(
                     FuncFormatter(lambda x, p: '%1.2f' % x)))
                if self._param_teste_var.get()[:9] == "Int. anem":
                    idx = Data_teste['data0'] <= 3
                    if sum(idx) > 0:
                        self.ax0.plot(Data_teste['t'][idx], Data_teste[
                                      'data0'][idx], 'oy')
                        lgnd.append('Vento abaixo de 3m/s')
                if self._usergroup.get() == 2:
                    falhas = self.count_fail(Data_teste)
                    ttl = u'[{:1.1f}%] Falhas na série de Teste'.format(falhas)
                    if falhas >= float(self._iperfail.get()):
                        self.ax.set_title(ttl, color='r')
                    else:
                        self.ax.set_title(ttl)
                lns = self.ax.lines + self.ax0.lines
                plt.legend(lns, lgnd, framealpha=0.6, loc=0)
            self.ax.set_xlabel('Consulta em: {:{f}} UTC'.format(
                datetime.utcnow(), f="%d/%m/%Y %H:%M:%S"))
            if self._param_ctrl_var.get()[:3] == "Dir":
                self.ax.set_ylim((0., 360.))
            if self._param_ctrl_var.get()[:3] == "Bar":
                (self.ax.get_yaxis().set_major_formatter(
                 FuncFormatter(lambda x, p: '%1.2f' % x)))
            self.setaxdate(fig.axes[0], self.df.index.min(),
                           self.df.index.max())
        elif self._msg_ctrl == 'OK' and self._msg_teste == 'NOK':
            self.ax.plot(Data_control['t'], Data_control['data0'], '.-g')
            lgnd.append('{} @ {}'.format(Data_control['tag'],
                                         self._db_ctrl_var.get()))
            self.ax.set_ylabel(u'{} ({})'.format(Data_control['data0quant'],
                                                 Data_control['data0unit']),
                               fontsize=12)
            if self._param_ctrl_var.get()[:3] == "Dir":
                self.ax.set_ylim((0., 360.))
            if self._param_ctrl_var.get()[:3] == "Bar":
                (self.ax.get_yaxis().set_major_formatter(
                 FuncFormatter(lambda x, p: '%1.2f' % x)))
            if self._param_ctrl_var.get()[:9] == "Int. anem":
                idx = Data_control['data0'] <= 3
                if sum(idx) > 0:
                    self.ax.plot(Data_control['t'][idx],
                                 Data_control['data0'][idx], 'og')
                    lgnd.append('Vento abaixo de 3m/s')
            self.ax.set_xlabel('Consulta em: {:{f}} UTC'.format(
                datetime.utcnow(), f="%d/%m/%Y %H:%M:%S"))
            self.ax.legend(lgnd, framealpha=0.6, loc=0)
            self.setaxdate(fig.axes[0], Data_control['t'].min(),
                           Data_control['t'].max())
        elif self._msg_ctrl == 'NOK' and self._msg_teste == 'OK':
            self.ax.plot(Data_teste['t'], Data_teste['data0'], '.-y')
            lgnd.append('{} @ {}'.format(Data_teste['tag'],
                                         self._db_teste_var.get()))
            self.ax.set_ylabel(u'{} ({})'.format(Data_teste['data0quant'],
                                                 Data_teste['data0unit']),
                               fontsize=12)
            if self._param_teste_var.get()[:3] == "Dir":
                self.ax.set_ylim((0., 360.))
            if self._param_teste_var.get()[:3] == "Bar":
                (self.ax.get_yaxis().set_major_formatter(
                 FuncFormatter(lambda x, p: '%1.2f' % x)))
            if self._param_teste_var.get()[:9] == "Int. anem":
                idx = Data_teste['data0'] <= 3
                if sum(idx) > 0:
                    self.ax.plot(Data_teste['t'][idx],
                                 Data_teste['data0'][idx], 'oy')
                    lgnd.append('Vento abaixo de 3m/s')
            if self._usergroup.get() == 2:
                falhas = self.count_fail(Data_teste)
                lgnd.append('Reprovações')
                ttl = u'[{:1.1f}%] Falhas na série de Teste'.format(falhas)
                if falhas >= float(self._iperfail.get()):
                    self.ax.set_title(ttl, color='r')
                else:
                    self.ax.set_title(ttl)
            self.ax.set_xlabel('Consulta em: {:{f}} UTC'.format(
                datetime.utcnow(), f="%d/%m/%Y %H:%M:%S"))
            self.ax.legend(lgnd, framealpha=0.6, loc=0)
            self.setaxdate(fig.axes[0], Data_teste['t'].min(),
                           Data_teste['t'].max())
        elif self._msg_ctrl == 'NOK' and self._msg_teste == 'NOK':
            plt.close()

        try:
            self._qrymsgbox.config(fg='blue')
            self._msg.set(u'PAR. CONTROLE %s \n PAR. TESTE %s'
                          % (self._msg_ctrl, self._msg_teste))
            # Conferência de conformidade de datas.
            try:
                datetime.strptime(self._idate.get(), self.fmt)
            except Exception:
                self._msg.set(u'Corrigir Data')
                self._idatent.config(fg='red')
                self._qrymsgbox.config(fg='purple')
            try:
                datetime.strptime(self._fdate.get(), self.fmt)
            except Exception:
                self._msg.set(u'Corrigir Data')
                self._fdatent.config(fg='red')
                self._qrymsgbox.config(fg='purple')
            if (datetime.strptime(self._idate.get(), self.fmt) >
                    datetime.strptime(self._fdate.get(), self.fmt)):
                self._idatent.config(fg='red')
                self._qrymsgbox.config(fg='purple')
                self._msg.set(u'Corrigir Intervalo \nErroneo')
        except Exception:
            pass

        fig.canvas.draw()
        self._root.update()
        self._qrybt["state"] = tki.NORMAL

    def popupmenu(self, event, menu, menubt, lbxmain, lstvars):
        u""" Exibir menu facilitado para seleção. """
        # Nomenclaturas na listagem disponível.
        lbxlst = lbxmain.get(0, tki.END)
        # Índices selecionados na listagem disponível.
        curlst = lbxmain.curselection()
        for itemidx, item in enumerate(lbxlst):
            lstvars[itemidx].set(0)
            if itemidx in curlst:
                lstvars[itemidx].set(1)
        # Abertura do menu.
        menu.post(menubt.winfo_rootx(), menubt.winfo_rooty())

    def menuaval(self, menu, menubt, lbxmain, lstvars):
        u""" Disponibilizar menu facilitado para seleção. """
        # Nomenclaturas na listagem disponível.
        lbxlst = lbxmain.get(0, tki.END)
        # Oferta e atualização do menu.
        menu.delete(0, tki.END)

        for itemidx, item in enumerate(lbxlst):
            # Variável mutante de seleção.
            lstvars.append(tki.IntVar())
            menu.add_checkbutton(
                label=item, variable=lstvars[itemidx],
                command=lambda lbl=lbxmain, ix=itemidx,
                qb=self._qrybt,  mf=self._mainfrm,
                go=self._uselvar:
                    (lbl.selection_clear(ix) if ix in lbl.curselection() else
                     lbl.selection_clear(0, tki.END), lbl.selection_set(ix),
                     lbl.see(ix), qb.config(state=tki.NORMAL)))
            # Quebra de coluna a cada número fixo de itens.
            if not(itemidx % 15):
                menu.entryconfigure(itemidx, columnbreak=1)
        # Associação da ação ao widget.
        menubt.bind("<Button-1>", lambda ev, pp=self.popupmenu, mn=menu,
                    mnb=menubt, lb=lbxmain, lv=lstvars:
                        pp(ev, mn, mnb, lb, lv))

    def count_fail(self, data):
        dtmn = datetime.strptime(self._idate.get(), self.fmt)
        dtmx = datetime.strptime(self._fdate.get(), self.fmt)
        R_expect = (int((dtmx - dtmn).total_seconds() //
                        3600) + 1)
        R_received = float(len(data['data0']))
        N_nan = (R_received -
                 np.count_nonzero(np.isnan(data['data0'])))
        falhas = 100 * (1 - (N_nan / R_expect))
        return falhas

    def count_rep(self, ref, lgnd):
        idx = self.df['diff'] >= float(ref)
        R_received = float(len(self.df['TESTE']))
        N_nan = (R_received -
                 np.count_nonzero(np.isnan(self.df['TESTE'])))
        rep = 100 * (sum(idx) / N_nan)
        if rep > 0:
            lgnd.append(u'Reprovações')
        return rep, idx

    # Funções de buscas
    # ============================================================ #
    def GET_data(self, ucdid, par):
        u""" Busca de dados da seleção. """
        try:
            dataSpan = [self._idate.get(), self._fdate.get()]
            eqp = self.eqpqry
            bd = self.dbqry
            if par == u"Int. Correntes":
                binSpan = [self.lyrqry, self.lyrqry]
                if eqp == 2:
                    Data = pyocnp.adcp_ocndbqry(ucdid, binSpan, dataSpan,
                                                ['HCSP'], eqp, bd)
                    Data.put(u'tag', Data['tag'].split('@')[0] +
                             ' <ADCP c:%s>' % self.lyrqry)
                elif eqp == 15:
                    Data = pyocnp.hadcp_ocndbqry(ucdid, binSpan, dataSpan,
                                                 ['HCSP'], eqp, bd)
                    Data.put(u'tag', Data['tag'].split('@')[0] +
                             ' <HADCP c:%s>' % self.lyrqry)
                elif eqp == 3:
                    Data = pyocnp.ocea2d_ocndbqry(ucdid, dataSpan, ['HCSP'],
                                                  eqp, bd)
                    Data.put(u'tag', Data['tag'].split('@')[0] + ' ' +
                             Data['tag'].split()[-3])
                elif eqp == 71:
                    Data = pyocnp.ocea2d_ocndbqry(ucdid, dataSpan, ['HCSP'],
                                                  eqp, bd)
                    Data.put(u'tag', Data['tag'].split()[0] + ' <AQUADOPP>')
                elif eqp == 4:
                    Data = pyocnp.ocea3d_ocndbqry(ucdid, dataSpan, ['HCSP'],
                                                  eqp, bd)
                    Data.put(u'tag', Data['tag'].split('@')[0] + ' ' +
                             Data['tag'].split()[-3])
            elif par == u"Dir. Correntes":
                binSpan = [self.lyrqry, self.lyrqry]
                if eqp == 2:
                    Data = pyocnp.adcp_ocndbqry(ucdid, binSpan, dataSpan,
                                                ['HCDT'], eqp, bd)
                    Data.put(u'tag', Data['tag'].split('@')[0] +
                             ' <ADCP c:%s>' % self.lyrqry)
                elif eqp == 15:
                    Data = pyocnp.hadcp_ocndbqry(ucdid, binSpan, dataSpan,
                                                 ['HCDT'], eqp, bd)
                    Data.put(u'tag', Data['tag'].split('@')[0] +
                             ' <HADCP c:%s>' % self.lyrqry)
                elif eqp == 3:
                    Data = pyocnp.ocea2d_ocndbqry(ucdid, dataSpan, ['HCDT'],
                                                  eqp, bd)
                    Data.put(u'tag', Data['tag'].split('@')[0] + ' ' +
                             Data['tag'].split()[-3])
                elif eqp == 71:
                    Data = pyocnp.ocea2d_ocndbqry(ucdid, dataSpan, ['HCDT'],
                                                  eqp, bd)
                    Data.put(u'tag', Data['tag'].split()[0] + ' <AQUADOPP>')
                elif eqp == 4:
                    Data = pyocnp.ocea3d_ocndbqry(ucdid, dataSpan, ['HCDT'],
                                                  eqp, bd)
                    Data.put(u'tag', Data['tag'].split('@')[0] + ' ' +
                             Data['tag'].split()[-3])
            elif par == u"Alt. Ondas":
                if eqp == 4:
                    Data = pyocnp.ocea3d_ocndbqry(ucdid, dataSpan, ['VAVH'],
                                                  eqp, bd)
                    Data.put(u'tag', Data['tag'].split('@')[0] + ' ' +
                             Data['tag'].split()[-3])
                elif eqp == 5:
                    Data = pyocnp.miros_ocndbqry(ucdid, dataSpan, ['VAVH'],
                                                 eqp, bd)
                    Data.put(u'tag', Data['tag'].split('@')[0] + ' ' +
                             Data['tag'].split()[-3])
            elif par == u"Dir. Ondas":
                if eqp == 4:
                    Data = pyocnp.ocea3d_ocndbqry(ucdid, dataSpan, ['VPEDM'],
                                                  eqp, bd)
                    Data.put(u'tag', Data['tag'].split('@')[0] + ' ' +
                             Data['tag'].split()[-3])
                elif eqp == 5:
                    Data = pyocnp.miros_ocndbqry(ucdid, dataSpan, ['VPEDM'],
                                                 eqp, bd)
                    Data.put(u'tag', Data['tag'].split('@')[0] + ' ' +
                             Data['tag'].split()[-3])
            elif par == u"Int. anem #1":
                Data = pyocnp.meteo_ocndbqry(ucdid, dataSpan, ['WSPD'],
                                             eqp, bd)
                Data.put(u'tag', Data['tag'].split('@')[0] + ' <anem #1>')
            elif par == u"Dir. anem #1":
                Data = pyocnp.meteo_ocndbqry(ucdid, dataSpan, ['WDIR'],
                                             eqp, bd)
                Data.put(u'tag', Data['tag'].split('@')[0] + ' <anem #1>')
            elif par == u"Int. anem #2":
                tag = (pyocnp.ucdname_byid_ocndb(
                    ucdid, str_dbaccess=bd)[0] + ' <anem #2>')
                self.ax.set_title('Buscando %s - Aguarde -' % tag)
                plt.draw()
                quant = (u'intensidade vento horizontal')
                dbqry = ("SELECT"
                         " UE6RK.TB_YOUNG_ST.YOME_DT_AQUISICAO, "
                         " AVG(TB_YOUNG_ST.YOST_VL_IWSPD_AN_2) / "
                         " (1 + 0.137 * LOG(10,"
                         " (AVG(TB_YOUNG_MESTRE.YOME_VL_COTA_ANE_2))/10))"
                         " FROM"
                         " UE6RK.TB_YOUNG_ST, UE6RK.TB_YOUNG_MESTRE"
                         " WHERE"
                         " UE6RK.TB_YOUNG_ST.LOIN_CD_LOCAL ="
                         " UE6RK.TB_YOUNG_MESTRE.LOIN_CD_LOCAL AND"
                         " UE6RK.TB_YOUNG_ST.YOME_DT_AQUISICAO ="
                         " UE6RK.TB_YOUNG_MESTRE.YOME_DT_AQUISICAO AND"
                         " UE6RK.TB_YOUNG_ST.LOIN_CD_LOCAL=" +
                         unicode(ucdid) + " AND"
                         " UE6RK.TB_YOUNG_ST.YOME_DT_AQUISICAO >= TO_DATE('" +
                         self._idate.get() + "', 'DD/MM/YYYY HH24:MI:SS') AND"
                         " UE6RK.TB_YOUNG_ST.YOME_DT_AQUISICAO <= TO_DATE('" +
                         self._fdate.get() + "', 'DD/MM/YYYY HH24:MI:SS')"
                         " GROUP BY"
                         " UE6RK.TB_YOUNG_ST.YOME_DT_AQUISICAO"
                         " ORDER BY"
                         " UE6RK.TB_YOUNG_ST.YOME_DT_AQUISICAO")
                qryresults = pyocnp.odbqry_all(dbqry, pyocnp.asciidecrypt(bd))
                qryarray = np.array(qryresults)
                if not any(qryarray[:, 1]):
                    Data = 'error'
                else:
                    Data = pyocnp.OcnpRootData()
                    Data.put(u't', qryarray[:, 0])
                    Data.put(u'tag', tag)
                    Data.put(u'data0', qryarray[:, 1].astype('Float64'))
                    Data.put(u'data0quant', quant)
                    Data.put(u'data0unit', u'm/s')
            elif par == u"Dir. anem #2":
                tag = (pyocnp.ucdname_byid_ocndb(
                    ucdid, str_dbaccess=bd)[0] + " <anem #2>")
                self.ax.set_title('Buscando %s - Aguarde -' % tag)
                plt.draw()
                dbqry = ("SELECT"
                         " UE6RK.TB_YOUNG_ST.YOME_DT_AQUISICAO,"
                         " AVG(UE6RK.TB_YOUNG_ST.YOST_VL_IWDIR_AN_2) +"
                         " AVG(UE6RK.TB_YOUNG_MESTRE.YOME_VL_OFFS_ANE_2),"
                         " AVG(UE6RK.TB_YOUNG_MESTRE.YOME_VL_APROA),"
                         " AVG(UE6RK.TB_YOUNG_MESTRE.YOME_VL_SIN_APROA),"
                         " MAX(UE6RK.TB_YOUNG_MESTRE.YOME_IN_GIRO_ANE2)"
                         " FROM"
                         " UE6RK.TB_YOUNG_ST, UE6RK.TB_YOUNG_MESTRE"
                         " WHERE"
                         " UE6RK.TB_YOUNG_ST.LOIN_CD_LOCAL ="
                         " UE6RK.TB_YOUNG_MESTRE.LOIN_CD_LOCAL AND"
                         " UE6RK.TB_YOUNG_ST.YOME_DT_AQUISICAO ="
                         " UE6RK.TB_YOUNG_MESTRE.YOME_DT_AQUISICAO AND"
                         " UE6RK.TB_YOUNG_ST.LOIN_CD_LOCAL =" +
                         unicode(ucdid) + " AND"
                         " UE6RK.TB_YOUNG_ST.YOME_DT_AQUISICAO >= TO_DATE('" +
                         self._idate.get() + "', 'DD/MM/YYYY HH24:MI:SS') AND"
                         " UE6RK.TB_YOUNG_ST.YOME_DT_AQUISICAO <= TO_DATE('" +
                         self._fdate.get() + "', 'DD/MM/YYYY HH24:MI:SS') "
                         " GROUP BY"
                         " UE6RK.TB_YOUNG_ST.YOME_DT_AQUISICAO"
                         " ORDER BY"
                         " UE6RK.TB_YOUNG_ST.YOME_DT_AQUISICAO")
                qryresults = pyocnp.odbqry_all(dbqry, pyocnp.asciidecrypt(bd))
                qryarray = np.array(qryresults)
                quant = (u'direção vento horizontal')
                if not any(qryarray[:, 1]):
                    Data = 'error'
                else:
                    Data = pyocnp.OcnpRootData()
                    for i, j in enumerate(qryarray[:, -1]):
                        wdir = qryarray[i, 1]
                        gyro = qryarray[i, 3]
                        apro = qryarray[i, 2]
                        if (wdir is not None) & (gyro is not None):
                            wdir = (wdir + gyro) % \
                                360 if j == 'S' else (wdir + apro) % 360
                        elif wdir is None:
                            wdir = None
                        elif gyro is None:
                            wdir = None if j == 'S' else (wdir + apro) % 360
                    Data.put(u't', qryarray[:, 0])
                    Data.put(u'tag', tag)
                    Data.put(u'data0', qryarray[:, 1].astype('Float64'))
                    Data.put(u'data0quant', quant)
                    Data.put(u'data0unit', u"\u00b0")
            elif par == u"Baro #1":
                Data = pyocnp.meteo_ocndbqry(ucdid, dataSpan, ['ATMS'],
                                             eqp, bd)
                Data.put(u'tag', Data['tag'].split('@')[0] + ' <baro #1>')
            elif par == u"Baro #2":
                tag = (pyocnp.ucdname_byid_ocndb(ucdid,
                                                 str_dbaccess=bd)[0] +
                       ' <baro #2>')
                self.ax.set_title('Buscando %s - Aguarde -' % tag)
                plt.draw()
                dbqry = ("SELECT"
                         " UE6RK.TB_IMPORTACOES.IMPO_TX_PATH_ARQ,"
                         " UE6RK.TB_IMPORTACOES.IMPO_NM_ARQUIVO"
                         " FROM"
                         " UE6RK.TB_IMPORTACOES"
                         " WHERE"
                         " UE6RK.TB_IMPORTACOES.LOIN_CD_LOCAL =" +
                         unicode(ucdid) + " AND"
                         " UE6RK.TB_IMPORTACOES.EQUI_CD_EQUIPAMENT = 1 AND"
                         " UE6RK.TB_IMPORTACOES.IMPO_DT_AQUISICAO >="
                         " TO_DATE('" + self._idate.get() +
                         "', 'DD/MM/YYYY HH24:MI:SS') AND"
                         " UE6RK.TB_IMPORTACOES.IMPO_DT_AQUISICAO <="
                         " TO_DATE('" + self._fdate.get() +
                         "', 'DD/MM/YYYY HH24:MI:SS')"
                         " ORDER BY"
                         " UE6RK.TB_IMPORTACOES.IMPO_DT_AQUISICAO")
                qryresults = pyocnp.odbqry_all(dbqry, pyocnp.asciidecrypt(bd))
                R = 287
                g = 9.81
                press2, t = [], []
                for path, fname in qryresults:
                    filename = path[:-13] + '\\SUCESSO\\' + fname \
                        if path.endswith('P') else path + \
                        '\\SUCESSO\\' + fname
                    # Dicionário de acrônimos de parâmetros
                    # e/ou dados associados
                    headdctl = {u'TIME': list(),
                                u'COTA_PRES': list(),
                                u'DRYT': list(),
                                u'ATMS_2': list(),
                                u'DPATMS_2': list()}
                    # Tentativa de abertura/leitura do arquivo.
                    try:
                        with open(filename, 'rb') as filegz:
                            txtgz = filegz.read()
                    except IOError as err:
                        # Reportagem de erro de abertura/leitura do arquivo.
                        print u"<<Reading Error>> File: " + repr(filename)
                        print(u" " + repr(err)[0:repr(err).find("(")] +
                              u": [Errno " + unicode(err.args[0]) + u"] " +
                              unicode(err.args[1]))
                    else:
                        # Tentativa de descompactação do conteúdo arquivado.
                        try:
                            txtugz = zb.decompress(txtgz).decode('cp1252')
                        except zb.error as err:
                            # Reportagem de erro de descompactação do conteúdo.
                            print(u"<<Decompressing Error>> File: " +
                                  repr(filename))
                            print u"  zlibError: " + unicode(err)
                            pass
                        else:
                            # Substituição de tabulações por espaços.
                            txtugz = txtugz.replace(u"\t", u" ")
                            # Substituição de valores não aquisitados
                            # por 'NaN', demarcados originalmente com
                            # o símbolo padrão '--'.
                            txtugz = txtugz.replace(u"*.*", u" --")
                            txtugz = txtugz.replace(u"*", u" ")
                            txtugz = txtugz.replace(u" --", u" NaN")
                            # Particionamento do conteúdo do arquivo em linhas.
                            txtlns = txtugz.splitlines()
                            # Tentativa de importação dos parâmetros e dados.
                            try:
                                # Identificação da data de aquisição.
                                for ln in txtlns:
                                    if u"Data hora da aquisição" in ln:
                                        aqs = " ".join(ln.split(u" ")[-2:])
                                        (headdctl['TIME']
                                         .append(datetime
                                                 .strptime(aqs,
                                                           "%d/%m/%Y %H:%M:%S")
                                                 )
                                         )
                                    elif u"sensor de pressão" in ln:
                                        (headdctl['COTA_PRES'].append(
                                         float(ln.split(u":")[-1].strip())))
                                    elif u"Média" in ln and\
                                         np.size(ln.split()) == 10:
                                        lndata = ln.split()
                                        (headdctl['DRYT']
                                         .append(float(lndata[5])))
                                        (headdctl['ATMS_2']
                                         .append(float(lndata[9])))
                                    elif u"Média" in ln and\
                                         np.size(ln.split()) != 10:
                                        lndata = ln.split()
                                        headdctl['DRYT'].append(None)
                                        headdctl['ATMS_2'].append(None)
                            except Exception as err:
                                # Reportagem de erro de importação do conteúdo.
                                print(u"<<Importing Error>> File: " +
                                      repr(filename))
                                print(u" " + repr(err)[0:repr(err).find("(")] +
                                      u": " + unicode(err))
                    press2.append(headdctl['ATMS_2'][0] *
                                  np.exp(g /
                                         (R * (headdctl['DRYT'][0] + 273.15)) *
                                         headdctl['COTA_PRES'][0]))
                    t.append(headdctl['TIME'][0])
                if not any(press2):
                    Data = 'error'
                else:
                    Data = pyocnp.OcnpRootData()
                    Data.put(u't', np.asarray(t))
                    Data.put(u'tag', tag)
                    Data.put(u'data0', press2)
                    Data.put(u'data0unit', u"hPa")
                    Data.put(u'data0quant', u"pressão atmosférica nm")
            elif par == u"Temp":
                Data = pyocnp.meteo_ocndbqry(ucdid, dataSpan, ['DRYT'],
                                             eqp, bd)
                Data.put(u'tag', Data['tag'].split('@')[0] +
                         ' ' + Data['tag'].split()[-3])
            elif par == u"Umid":
                Data = pyocnp.meteo_ocndbqry(ucdid, dataSpan, ['RELH'],
                                             eqp, bd)
                Data.put(u'tag', Data['tag'].split('@')[0] +
                         ' ' + Data['tag'].split()[-3])
        except Exception:
            # Captura e exibição de exceção.
            errtype, ermairvalue, errtbk = sys.exc_info()
        return Data if 'Data' in locals() else 'error'

    # Customização da figura
    # ============================================================ #
    def setaxdate(self, axes, datemn, datemx):
        u""" Customizar rótulos de eixo temporal. """
        # Limites inferior e superior do eixo.
        (axes.set_xlim([datemn - timedelta(hours=1), datemx +
                        timedelta(hours=1)]) if datemn == datemx else
         axes.set_xlim([datemn, datemx]))
        axes.fmt_xdata = DateFormatter('%d/%m/%y %H:%M')
        # Escala temporal: < 1 dia.
        if (datemx.toordinal() - datemn.toordinal()) == 0:
            axes.xaxis.set_major_locator(HourLocator())
            axes.xaxis.set_major_formatter(DateFormatter('%d/%m/%y\n%H:%M'))
            axes.xaxis.set_minor_locator(HourLocator())
            axes.xaxis.set_minor_formatter(DateFormatter(''))
        # Escala temporal: ]0, 5[ dias.
        elif 0 < (datemx.toordinal() - datemn.toordinal()) < 5:
            axes.xaxis.set_major_locator(DayLocator())
            axes.xaxis.set_major_formatter(DateFormatter('%d/%m/%y'))
            axes.xaxis.set_minor_locator(HourLocator(byhour=(3, 6, 9, 12,
                                                             15, 18, 21)))
            axes.xaxis.set_minor_formatter(DateFormatter('%H:%M'))
        # Escala temporal: [5, 11[ dias.
        elif 5 <= (datemx.toordinal() - datemn.toordinal()) < 11:
            axes.xaxis.set_major_locator(DayLocator())
            axes.xaxis.set_major_formatter(DateFormatter('%d/%m/%y'))
            axes.xaxis.set_minor_locator(HourLocator(byhour=(6, 12, 18)))
            axes.xaxis.set_minor_formatter(DateFormatter('%H:%M'))
        # Escala temporal: [11, 45[ dias.
        elif 11 <= (datemx.toordinal() - datemn.toordinal()) < 45:
            axes.xaxis.set_major_locator(DayLocator())
            axes.xaxis.set_major_formatter(DateFormatter('%d/%m/%y'))
            axes.xaxis.set_minor_locator(HourLocator(byhour=(12)))
            axes.xaxis.set_minor_formatter(DateFormatter('%H:%M'))
        # Escala temporal: [45, 183[ dias.
        elif 45 <= (datemx.toordinal() - datemn.toordinal()) < 183:
            axes.xaxis.set_major_locator(MonthLocator())
            axes.xaxis.set_major_formatter(DateFormatter('%m/%y'))
            axes.xaxis.set_minor_locator(DayLocator(bymonthday=(5, 10,
                                                                15, 20, 25)))
            axes.xaxis.set_minor_formatter(DateFormatter('%d'))
        # Escala temporal: [183, 365[ dias.
        elif 183 <= (datemx.toordinal() - datemn.toordinal()) < 365:
            axes.xaxis.set_major_locator(MonthLocator())
            axes.xaxis.set_major_formatter(DateFormatter('%m/%Y'))
            axes.xaxis.set_minor_locator(DayLocator())
            axes.xaxis.set_minor_formatter(DateFormatter(''))
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


def main():
    u"""Função para rodar interface usuário."""
    root = tki.Tk()
    root.title(u"Confrontos de Dados UCDs" +
               u" - OCEANOP - versão 2.0")
    root.resizable(width=False, height=False)
    UCD_confronto(root)
    root.mainloop()


if __name__ == "__main__":
    main()
