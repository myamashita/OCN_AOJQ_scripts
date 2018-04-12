# -*- coding: utf-8 -*-
#
# purpose:  ADCP profile
# author:   Márcio Yamashita
# created:  24-march-2016
# modified: 12-april-2018 AOJQ


from __future__ import division

import Tkinter as tki
import tkMessageBox
import datetime as dtm
from collections import OrderedDict

import pyocnp
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from matplotlib.colors import rgb2hex
from matplotlib.dates import DateFormatter
from matplotlib.dates import HourLocator, DayLocator, MonthLocator, YearLocator


class ADCP_Profile:
    """ Interface Gráfica Principal ao Usuário (GUI) baseada em Tkinter. """

    def __init__(self, root):
        """ Instanciar elementos gráficos (widgets) e ações atreladas. """
        # Definição de Cores ========================================= #
        # ============================================================ #
        BGCOLORBOX = (1.000, 1.000, 1.000)
        BGCOLORAPL = (0.392, 0.584, 0.929)
        BGCOLORSLT = (0.031, 0.572, 0.815)

        # Definição de Atributos ===================================== #
        # ============================================================ #

        # Janela gráfica de origem da aplicação.
        self._root = root

        # Título da aplicação.
        self._aptitle = u"Oceanop - Meteo-Oceanografia Operacional"

        # Subtítulo da aplicação.
        self._apsubtitle = u"..."

        # Bancos de dados disponíveis e chaves criptografadas de acesso.
        BDOCNPROD_MAINPATH = ('eNoLdTUL8g6Id3cJ1nd0DTIJMfNwdwgI8ncBAFU2BsQ=')
        BDOCNDESV_MAINPATH = ('eNoLdTUL8tYPBZEGBg4ursFhAC4gBNw=')
        self._dbs = OrderedDict([(u"PROD", BDOCNPROD_MAINPATH),
                                 (u"DESV", BDOCNDESV_MAINPATH)])
        # Instância do BD.
        self._DBVIEW = u"UE6RK"

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

        # Barra/menu "Colorbar".
        menu = tki.Menu(self._menubar, tearoff=0)
        menu.user_cmap_intens = tki.Menu(menu, tearoff=0)
        self._user_int = tki.IntVar()
        menu.user_cmap_intens.add_radiobutton(label=ur'jet',
                                              value=0, variable=self._user_int)
        menu.user_cmap_intens.add_radiobutton(label=ur'hvs',
                                              value=1, variable=self._user_int)
        menu.user_cmap_intens.add_radiobutton(label=ur'ocean',
                                              value=2, variable=self._user_int)

        menu.add_cascade(label=u"Intens.", menu=menu.user_cmap_intens)
        self._user_int.set(0)

        menu.user_cmap_direc = tki.Menu(menu, tearoff=0)
        self._user_dir = tki.IntVar()
        menu.user_cmap_direc.add_radiobutton(label=ur'jet',
                                             value=0, variable=self._user_dir)
        menu.user_cmap_direc.add_radiobutton(label=ur'hvs',
                                             value=1, variable=self._user_dir)
        menu.user_cmap_direc.add_radiobutton(label=ur'ocean',
                                             value=2, variable=self._user_dir)

        menu.add_cascade(label=u"Direc.", menu=menu.user_cmap_direc)
        self._user_dir.set(1)

        menu.user_cmap_EI = tki.Menu(menu, tearoff=0)
        self._user_EI = tki.IntVar()
        menu.user_cmap_EI.add_radiobutton(label=ur'jet',
                                          value=0, variable=self._user_EI)
        menu.user_cmap_EI.add_radiobutton(label=ur'hvs',
                                          value=1, variable=self._user_EI)
        menu.user_cmap_EI.add_radiobutton(label=ur'ocean',
                                          value=2, variable=self._user_EI)

        menu.add_cascade(label=u"Echo I.", menu=menu.user_cmap_EI)
        self._user_EI.set(0)

        menu.user_cmap_CM = tki.Menu(menu, tearoff=0)
        self._user_CM = tki.IntVar()
        menu.user_cmap_CM.add_radiobutton(label=ur'jet',
                                          value=0, variable=self._user_CM)
        menu.user_cmap_CM.add_radiobutton(label=ur'hvs',
                                          value=1, variable=self._user_CM)
        menu.user_cmap_CM.add_radiobutton(label=ur'ocean',
                                          value=2, variable=self._user_CM)

        menu.add_cascade(label=u"Cor M.", menu=menu.user_cmap_CM)
        self._user_CM.set(0)

        self._menubar.add_cascade(label=u"Colormap", menu=menu)

        # Associação da barra de opções ao frame principal.
        self._mainfrm.master.config(menu=self._menubar)

        # Frame de Período e Banco #
        # ============================================================ #
        self._dbdtfrm = tki.Frame(self._mainfrm, bg=rgb2hex(BGCOLORAPL),
                                  bd=2, relief=tki.GROOVE)
        self._dbdtfrm.pack(fill=tki.X, padx=6, pady=4, side=tki.TOP)

        # Subframe de Período #
        # ============================================================ #
        self._datefrm = tki.Frame(self._dbdtfrm, bg=rgb2hex(BGCOLORAPL),
                                  bd=0, relief=tki.GROOVE)
        self._datefrm.pack(padx=1, pady=0, side=tki.LEFT, fill=tki.X,
                           expand=tki.YES)
        # Variável mutante da data inicial declarada (previamente
        # escolhida há 30 dias daquele de hoje).
        self._idate = tki.StringVar()
        self._idate.set((dtm.datetime.utcnow() -
                         dtm.timedelta(hours=720)).strftime(u"%d/%m/%Y" +
                                                            u" %H:00:00"))
        # Variável mutante da data final declarada (previamente
        # escolhida como o dia de hoje).
        self._fdate = tki.StringVar()
        self._fdate.set(dtm.datetime.utcnow().strftime(u"%d/%m/%Y %H:00:00"))
        # Rótulo "Período".
        self._datefrm_rot = tki.Label(self._datefrm, bg=rgb2hex(BGCOLORAPL),
                                      bd=0, fg='white', text=u"Período:",
                                      font=('Verdana', '9', 'bold'),
                                      relief=tki.FLAT, justify=tki.RIGHT)
        self._datefrm_rot.grid(column=0, row=1, rowspan=2, padx=4,
                               pady=0, sticky=tki.NSEW)
        # Data Ininal.
        tki.Label(self._datefrm, bd=0, bg=rgb2hex(BGCOLORAPL), fg='white',
                  text=u"Data Inicial", font=('Verdana', '8', 'bold'),
                  relief=tki.FLAT, justify=tki.CENTER).grid(column=2, row=0,
                                                            padx=2, pady=0,
                                                            sticky=tki.EW)
        # Data Final.
        tki.Label(self._datefrm, bd=0, bg=rgb2hex(BGCOLORAPL), fg='white',
                  text=u"Data Final", font=('Verdana', '8', 'bold'),
                  relief=tki.FLAT, justify=tki.CENTER).grid(column=6, row=0,
                                                            padx=2, pady=0,
                                                            sticky=tki.EW)
        # Campo de entrada da data inicial de consulta
        self._idatent = tki.Entry(self._datefrm, bd=3, width=19,
                                  textvariable=self._idate, justify=tki.CENTER)
        self._idatent.grid(column=2, row=1, rowspan=2, padx=10, pady=2,
                           ipady=2, sticky=tki.EW)
        # Campo de entrada da data final de consulta
        self._fdatent = tki.Entry(self._datefrm, bd=3, width=19,
                                  textvariable=self._fdate, justify=tki.CENTER)
        self._fdatent.grid(column=6, row=1, rowspan=2, padx=10, pady=2,
                           ipady=2, sticky=tki.E)

        # Subframe de BD #
        # ============================================================ #
        self._dbfrm = tki.Frame(self._dbdtfrm, bg=rgb2hex(BGCOLORAPL),
                                bd=0, relief=tki.GROOVE)
        self._dbfrm.pack(padx=1, pady=0, side=tki.BOTTOM)

        # Opções de BDs.
        self._dbfrm_name = tki.Label(self._dbfrm, bg=rgb2hex(BGCOLORAPL),
                                     fg='white', bd=0, text=u"Banco:",
                                     font=('Verdana', '9', 'bold'),
                                     relief=tki.FLAT, justify=tki.LEFT)
        self._dbfrm_name.grid(column=7, row=1, rowspan=2, padx=10,
                              pady=2, sticky=tki.NSEW)

        # Variável mutante do BD selecionado.
        self._dbvar = tki.StringVar()

        # Menu de BDs disponíveis para consulta.
        self._dbopt = tki.OptionMenu(self._dbfrm, self._dbvar,
                                     *self._dbs.keys(), command=self.askucds)
        self._dbopt.grid(column=8, row=1, rowspan=1, padx=4, pady=0,
                         sticky=tki.NSEW)

        # Frame de UCDs
        # ============================================================ #
        self._ucdfrm = tki.Frame(self._mainfrm, bg=rgb2hex(BGCOLORAPL),
                                 bd=2, relief=tki.GROOVE)
        self._ucdfrm.pack(fill=tki.BOTH, padx=6, pady=4, side=tki.LEFT)

        self._ucdsmenub = tki.Label(self._ucdfrm, bg=rgb2hex(BGCOLORAPL),
                                    bd=0, fg='white', text=u"UCDs:",
                                    font=('Verdana', '9', 'bold'),
                                    relief=tki.FLAT, justify=tki.CENTER)

        self._ucdsmenub.grid(column=0, columnspan=1, row=0, rowspan=2,
                             padx=2, pady=0, sticky=tki.N)

        # Listagem de UCDs disponíveis para consulta.
        self._ucdslbx = tki.Listbox(self._ucdfrm, bd=1,
                                    selectmode=tki.SINGLE,
                                    width=20, height=6,
                                    selectborderwidth=2,
                                    setgrid=tki.NO, exportselection=tki.FALSE,
                                    selectbackground=rgb2hex(BGCOLORSLT),
                                    font=('Default', '8', 'normal'))

        self._ucdslly = tki.Scrollbar(self._ucdfrm, bd=0, orient=tki.VERTICAL,
                                      command=self._ucdslbx.yview)

        self._ucdslbx.grid(column=1, columnspan=1,
                           row=0, rowspan=2, padx=0, pady=0, sticky=tki.NS)
        self._ucdslly.grid(column=2, columnspan=2,
                           row=0, rowspan=2, padx=0, pady=0, sticky=tki.NSEW)

        self._ucdslbx.configure(yscrollcommand=self._ucdslly.set)
        self._root.update_idletasks()

        # Menu de UCDs para consulta facilitada.
        self._ucdsmenu = tki.Menu(self._root, tearoff=0)

        # Subframe de Setup #
        # ============================================================ #
        self._stpfrm = tki.Frame(self._mainfrm, bg=rgb2hex(BGCOLORAPL),
                                 bd=2, relief=tki.GROOVE)
        self._stpfrm.pack(expand=tki.YES, padx=1, pady=1, side=tki.LEFT)

        # Variável mutante do setup selecionado.
        self._stpvar = tki.StringVar()

        self._stplabel = tki.Label(self._stpfrm, bg=rgb2hex(BGCOLORAPL),
                                   bd=0, fg='white', text=u"Setups:",
                                   font=('Verdana', '9', 'bold'),
                                   relief=tki.FLAT, justify=tki.CENTER)
        self._stplabel.grid(column=1, columnspan=1, row=0, rowspan=1,
                            padx=1, pady=1, sticky=tki.N)

        self._stpkeys = tki.Label(self._stpfrm, bg=rgb2hex(BGCOLORAPL),
                                  relief=tki.FLAT)
        self._stpkeys.grid(column=1, columnspan=1, row=3, rowspan=2,
                           padx=1, pady=1, sticky=tki.N)
        MODES = [("Int./Dir.", "1"), ("Echo Int.", "2"), ("Correlation", "3")]

        for text, mode in MODES:
            b = tki.Radiobutton(self._stpkeys, text=text, fg='white',
                                bg=rgb2hex(BGCOLORAPL), 
                                selectcolor=rgb2hex(BGCOLORAPL),
                                variable=self._stpvar, value=mode)
            b.pack(anchor=tki.W)

        self._stpvar.set("1")

        # Subframe de Mensagem #
        # ============================================================ #
        self._msgfrm = tki.Frame(self._mainfrm, bg=rgb2hex(BGCOLORAPL),
                                 bd=0, relief=tki.FLAT)
        self._msgfrm.pack(expand=tki.YES, padx=0, pady=0, side=tki.LEFT)
        self._qrymsg = tki.Label(self._msgfrm, bg=rgb2hex(BGCOLORAPL),
                                 bd=0, fg='white', text=u"Mensagem:",
                                 font=('Verdana', '9', 'bold'),
                                 relief=tki.FLAT, justify=tki.CENTER)

        self._qrymsg.grid(column=2, columnspan=1, row=1, rowspan=1,
                          padx=1, pady=1, sticky=tki.N)

        self._msg = tki.StringVar()
        self._msg.set("Escolha o Banco")
        self._qrymsgbox = tki.Label(self._msgfrm, bg=rgb2hex(BGCOLORAPL), bd=1,
                                    width=25, font=('Verdana', '9', 'bold'),
                                    fg='yellow', textvariable=self._msg,
                                    justify=tki.CENTER)
        self._qrymsgbox.grid(column=2, columnspan=1, row=2, rowspan=1,
                             padx=1, pady=1, sticky=tki.N)

        # Subframe de Consulta #
        # ============================================================ #
        self._qryfrm = tki.Frame(self._mainfrm, bg=rgb2hex(BGCOLORBOX),
                                 bd=3, relief=tki.SUNKEN)
        self._qryfrm.pack(expand=tki.YES, padx=0, pady=0, side=tki.RIGHT)

        # Botão de plotagem dos dados desejados
        # (condicionalmente e previamente desabilitado).
        self._qrybt = tki.Button(self._qryfrm, bd=1, text=u"Consulta",
                                 font=('Default', '10', 'bold'),
                                 command=self.askdata)
        self._qrybt.grid(column=3, row=1, rowspan=1, padx=0, pady=1,
                         ipadx=1, ipady=1)
        self._qrybt["state"] = tki.DISABLED

        self._root.update()

        self._mainfrm.pack(fill=tki.BOTH, padx=0, pady=0, side=tki.TOP)

        # Carregamento de agrupamentos de UCDs definidos pela aplicação.
        self._uselvar = tki.StringVar()
        self._ucdslbx.curselection()

    def askucds(self, dbvalue):
        """ Listar UCDs disponíveis para consulta no BD PROD. """

        # Desativação temporária do botão de consulta aos dados.
        self._qrybt["state"] = tki.DISABLED

        # Limpeza do menu de pré-seleção de UCDs por agrupamento.
        self._ucdslbx.delete(0, tki.END)

        self._ucdsmenub["cursor"] = ""
        self._ucdsmenub["text"] = u"UCDs:"

        # Atualização da aplicação para exibição das modificações.
        self._root.update()

        # Requisição das UCDs ao BD #
        # ============================================================ #
        # Erros esperados/contornados:
        #     [-] falha de comunicação com o BD.
        try:
            dbqry = (
                "SELECT"
                " TB_LOCAL_INSTAL.LOIN_CD_LOCAL,"
                " UNISTR(TB_LOCAL_INSTAL.LOIN_TX_LOCAL)"
                " FROM"
                " UE6RK.TB_LOCAL_INSTAL"
                " LEFT JOIN"
                " UE6RK.TB_PARAMETROS_INST"
                " ON"
                " UE6RK.TB_LOCAL_INSTAL.LOIN_CD_LOCAL ="
                " UE6RK.TB_PARAMETROS_INST.LOIN_CD_LOCAL"
                " WHERE"
                " UE6RK.TB_PARAMETROS_INST.EQUI_CD_EQUIPAMENT = '2'"
                " ORDER BY"
                " TB_LOCAL_INSTAL.LOIN_TX_LOCAL")
            ucds = pyocnp.odbqry_all(dbqry,
                                     pyocnp.asciidecrypt(self._dbs[dbvalue]))
        except:
            # Atualização de status: BD inacessivel.
            print 'dbaccessfail'
            raise

        # Oferta da lista de UCDs disponíveis.
        self._ucds = ucds
        for lstid, lstnm in ucds:
            self._ucdslbx.insert(tki.END, lstnm)

        self._ucdslbx.bind('<<ListboxSelect>>', lambda ev, qb=self._qrybt,
                           mf=self._mainfrm, go=self._uselvar:
                           (qb.config(state=tki.NORMAL)
                            if(ev.widget.curselection() and
                               mf["cursor"] != "watch")
                            else qb.config(state=tki.DISABLED), go.set(u"")))

        # Oferta e atualização do menu de UCDs.
        self._ucdsmenuvars = list()

        self.menuaval(self._ucdsmenu, self._ucdsmenub,
                      self._ucdslbx, self._ucdsmenuvars)

        self._ucdsmenub["cursor"] = "sizing"
        self._ucdsmenub["text"] = u"UCDs:\n\u2630"
        self._msg.set("Escolha a UCD\n e Consulte")

    def popupmenu(self, event, menu, menubt, lbxmain, lstvars):
        """ Exibir menu facilitado para seleção. """

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
        """ Disponibilizar menu facilitado para seleção. """
        # Nomenclaturas na listagem disponível.
        lbxlst = lbxmain.get(0, tki.END)
        # Oferta e atualização do menu.
        menu.delete(0, tki.END)

        for itemidx, item in enumerate(lbxlst):
            # Variável mutante de seleção.
            lstvars.append(tki.IntVar())
            menu.add_checkbutton(label=item, variable=lstvars[itemidx],
                                 command=lambda lbl=lbxmain, ix=itemidx,
                                 mn=menu, mnb=menubt, qb=self._qrybt,
                                 mf=self._mainfrm, go=self._uselvar:
                                 (lbl.selection_clear(ix) if ix in
                                  lbl.curselection() else
                                  lbl.selection_clear(0, tki.END),
                                  lbl.selection_set(ix), lbl.see(ix),
                                  qb.config(state=tki.NORMAL)
                                  if(lbl.curselection() and
                                     mf["cursor"] != "watch") else
                                  qb.config(state=tki.DISABLED), go.set(u""), ))

            # Quebra de coluna a cada número fixo de itens.
            if not(itemidx % 10):
                menu.entryconfigure(itemidx, columnbreak=1)
        # Associação da ação ao widget.

        menubt.bind("<Button-1>", lambda ev, pp=self.popupmenu, mn=menu,
                    mnb=menubt, lb=lbxmain, lv=lstvars:
                        pp(ev, mn, mnb, lb, lv))

    def listview(self, event):
        """ Reposicionar visão da lista por tecla acionada. """
        if event.char:
            for itemidx, item in enumerate(event.widget.get(0, tki.END)):
                if item[0].upper() == event.char.upper():
                    event.widget.see(itemidx)
                    event.widget.activate(itemidx)
                    break

    def askdata(self):
        """ Consultar, plotar dados do BD. """
        # Conferência de conformidade nas datas declaradas.
        try:
            dtm.datetime.strptime(self._idate.get(),
                                  "%d/%m/%Y %H:%M:%S")
            dtm.datetime.strptime(self._fdate.get(),
                                  "%d/%m/%Y %H:%M:%S")
        except Exception:
            # Sinalização em cores de alerta nas datas.
            self._idatent.config(fg='red')
            self._fdatent.config(fg='red')
            # Atualização da aplicação para exibição das modificações.
            self._root.update()
            raise

        # Desativação temporária do botão de consulta aos dados.
        self._qrybt["state"] = tki.DISABLED

        # Normalização de cores das datas.
        self._idatent.config(fg="black")
        self._fdatent.config(fg="black")

        # UCD selecionada para consulta.
        ucdsqry = self._ucds[self._ucdslbx.curselection()[0]][0]
        # UCD name selecionada para consulta.
        ucdname = self._ucds[self._ucdslbx.curselection()[0]][1]

        # Sensor adcp para consulta.
        eqpsqry = 2

        # Pesquisando
        self._msg.set("Pesquisando Banco de Dados.")
        self._root.update()

        if self._stpvar.get() == '1':
            try:
                data = pyocnp.adcp_ocndbqry(ucdsqry,
                                            [0, 50], [self._idate.get(),
                                                      self._fdate.get()],
                                            ['HCSP', 'HCDT'], eqpsqry,
                                            self._dbs[self._dbvar.get()],
                                            self._DBVIEW)
                param = pyocnp.adcp_mt_ocndbqry(ucdsqry, [self._idate.get(),
                                                          self._fdate.get()],
                                                ['COTA', 'DST_TRS_CM',
                                                 'DST_CAMADA'], eqpsqry,
                                                self._dbs[self._dbvar.get()],
                                                self._DBVIEW)
                self._msg.set("Pesquisa com resultados.")
                # call plot
                self.plot_figure_SP_DT(data, param)
                # Reativação do botão de consulta aos dados.
                self._qrybt["state"] = tki.NORMAL
            except RuntimeError:
                self._msg.set(u"Base de dados vazia para:\n%s" % ucdname)
                self._ucdslbx.selection_clear(0, tki.END)
        elif self._stpvar.get() == '2':
            try:
                data = pyocnp.adcp_st_ocndbqry(ucdsqry,
                                               [0, 50], [self._idate.get(),
                                                         self._fdate.get()],
                                               ['EI_1', 'EI_2', 'EI_3', 'EI_4'],
                                               eqpsqry,
                                               self._dbs[self._dbvar.get()],
                                               self._DBVIEW)
                param = pyocnp.adcp_mt_ocndbqry(ucdsqry, [self._idate.get(),
                                                          self._fdate.get()],
                                                ['COTA', 'DST_TRS_CM',
                                                 'DST_CAMADA'], eqpsqry,
                                                self._dbs[self._dbvar.get()],
                                                self._DBVIEW)
                self._msg.set("Pesquisa com resultados.")
                # call plot
                self.plot_figure_EI(data, param)
                # Reativação do botão de consulta aos dados.
                self._qrybt["state"] = tki.NORMAL
            except RuntimeError:
                self._msg.set(u"Base de dados vazia para:\n%s" % ucdname)
                self._ucdslbx.selection_clear(0, tki.END)
        elif self._stpvar.get() == '3':
            try:
                data = pyocnp.adcp_st_ocndbqry(ucdsqry,
                                               [0, 50], [self._idate.get(),
                                                         self._fdate.get()],
                                               ['CM_1', 'CM_2', 'CM_3', 'CM_4'],
                                               eqpsqry,
                                               self._dbs[self._dbvar.get()],
                                               self._DBVIEW)
                param = pyocnp.adcp_mt_ocndbqry(ucdsqry, [self._idate.get(),
                                                          self._fdate.get()],
                                                ['COTA', 'DST_TRS_CM',
                                                 'DST_CAMADA'], eqpsqry,
                                                self._dbs[self._dbvar.get()],
                                                self._DBVIEW)
                self._msg.set("Pesquisa com resultados.")
                # call plot
                self.plot_figure_CM(data, param)
                # Reativação do botão de consulta aos dados.
                self._qrybt["state"] = tki.NORMAL
            except RuntimeError:
                self._msg.set(u"Base de dados vazia para:\n%s" % ucdname)
                self._ucdslbx.selection_clear(0, tki.END)

    def plot_figure_SP_DT(self, data, param):
        # colormap para plot
        c_map = [plt.cm.jet, plt.cm.hsv, plt.cm.ocean]
        c_0 = c_map[self._user_int.get()]
        c_1 = c_map[self._user_dir.get()]
        equaltidx = list()
        for date in data['t']:
            equaltidx.append((param['t'] == date).nonzero()[0][0])
        z = param['data0'][equaltidx] + param['data1'][equaltidx] / 100. + \
            param['data2'][equaltidx] / 2. + \
            param['data2'][equaltidx] * data['z']
        cotas = np.unique(param['data0'])
        plt.close('all')
        fig = plt.figure(1, facecolor=(1.0, 1.0, 1.0), figsize=(10, 8))
        fig.show()
        # Diagramação e exibição da figura.
        fig.subplots_adjust(bottom=0.1, right=0.985, top=0.95)
        fig.suptitle(data['tag'].split(u'@')[0] + self._dbvar.get())
        axSP = fig.add_subplot(211)
        axDT = fig.add_subplot(212)

        axSP.set_ylabel(u"Profundidade [m]")
        axDT.set_ylabel(u"Profundidade [m]")

        axSP.invert_yaxis()
        axDT.invert_yaxis()

        for i in cotas:
            idx = param['data0'][equaltidx] == i
            X_axis_range = pd.date_range(start=data['t'][idx].min(),
                                         end=data['t'][idx].max(),
                                         freq='H').to_pydatetime()
            cols = list(set(X_axis_range) - set(param['t']))

            time = np.append(data['t'][idx], cols)
            cols = np.full(np.size(cols), np.nan)
            camada = np.append(data['z'][idx], cols)
            profundidade = np.append(z[idx], cols)
            intensidade = np.append(data['data0'][idx], cols)
            direction = np.append(data['data1'][idx], cols)

            d = {u'time': time, u'camada': camada,
                 u'intensidade': intensidade,
                 u'direção': direction,
                 u'profundidade': profundidade}

            df = pd.DataFrame(d).pivot(u'profundidade', u'time')

            cs = axSP.contourf(df['intensidade'].columns, df.index,
                               df['intensidade'],
                               levels=np.arange(0, data['data0'].max(),
                                                0.1), cmap=c_0)
            cd = axDT.contourf(df['intensidade'].columns,
                               df.index, df[u'direção'],
                               levels=np.arange(0, 361, 20),
                               cmap=c_1)
            axSP.scatter(data['t'], z, c='k', alpha=0.05, marker='.')
            axDT.scatter(data['t'], z, c='k', alpha=0.05, marker='.')

        csc = plt.colorbar(mappable=cs, ax=cs.ax, pad=0.0125)
        cdc = plt.colorbar(mappable=cd, ax=cd.ax, pad=0.0125)
        csc.set_label('[m/s]')
        cdc.set_label('Graus')

        ax0, ax1 = axSP.twinx(), axDT.twinx()
        ax0.set_ylabel(u"Camada ")
        ax1.set_ylabel(u"Camada ")
        ax0.yaxis.tick_left()
        ax1.yaxis.tick_left()
        ax0.yaxis.set_label_position('left')
        ax1.yaxis.set_label_position('left')

        axSP.spines["left"].set_position(('outward', 40))
        axDT.spines["left"].set_position(('outward', 40))

        ax0.set_ylim(data['z'].min(), data['z'].max())
        ax1.set_ylim(data['z'].min(), data['z'].max())

        axSP.set_ylim(df.index.max(), df.index.min())
        axDT.set_ylim(df.index.max(), df.index.min())

        ax0.invert_yaxis()
        ax1.invert_yaxis()
        fmt_major_minor(cd.ax)
        clean_major_minor(cs.ax)

        fig.canvas.draw()
        self._root.update()

    def plot_figure_EI(self, data, param):
        # colormap para plot
        c_map = [plt.cm.jet, plt.cm.hsv, plt.cm.ocean]
        c_0 = c_map[self._user_EI.get()]

        if plt.fignum_exists(2):
            plt.close(2)
            fig = plt.figure(2, facecolor=(1.0, 1.0, 1.0), figsize=(10, 8))
        else:
            fig = plt.figure(2, facecolor=(1.0, 1.0, 1.0), figsize=(10, 8))
        fig.show()
        # Diagramação e exibição da figura.
        fig.subplots_adjust(bottom=0.1, right=0.985, top=0.95, hspace=0.1)
        fig.suptitle(data['tag'].split(u'@')[0] +
                     self._dbvar.get() + ' ECHO INTENS.')

        axEI1 = fig.add_subplot(411)
        axEI2 = fig.add_subplot(412, sharex=axEI1)
        axEI3 = fig.add_subplot(413, sharex=axEI1)
        axEI4 = fig.add_subplot(414, sharex=axEI1)

        equaltidx = list()
        for date in data['t']:
            equaltidx.append((param['t'] == date).nonzero()[0][0])
        z = param['data0'][equaltidx] + param['data1'][equaltidx] / 100. + \
            param['data2'][equaltidx] / 2. + \
            param['data2'][equaltidx] * data['z']
        cotas = np.unique(param['data0'])
        for i in cotas:
            idx = param['data0'][equaltidx] == i
            X_axis_range = pd.date_range(start=data['t'][idx].min(),
                                         end=data['t'][idx].max(),
                                         freq='H').to_pydatetime()
            cols = list(set() - set(param['t']))

            time = np.append(data['t'][idx], cols)
            cols = np.full(np.size(cols), np.nan)
            camada = np.append(data['z'][idx], cols)
            profundidade = np.append(z[idx], cols)
            E1 = np.append(data['data0'][idx], cols)
            E2 = np.append(data['data1'][idx], cols)
            E3 = np.append(data['data2'][idx], cols)
            E4 = np.append(data['data3'][idx], cols)
            d = {u'time': time, u'camada': camada,
                 u'E1': E1, u'E2': E2,
                 u'E3': E3, u'E4': E4,
                 u'profundidade': profundidade}

            df = pd.DataFrame(d).pivot(u'profundidade', u'time')
            ce1 = axEI1.contourf(df['E1'].columns, df.index, df['E1'],
                                 levels=np.arange(40, data['data0'].max(),
                                                  1), cmap=c_0)
            ce2 = axEI2.contourf(df['E2'].columns, df.index, df[u'E2'],
                                 levels=np.arange(40, data['data1'].max(),
                                                  1), cmap=c_0)
            ce3 = axEI3.contourf(df['E3'].columns, df.index, df[u'E3'],
                                 levels=np.arange(40, data['data2'].max(),
                                                  1), cmap=c_0)
            ce4 = axEI4.contourf(df['E4'].columns, df.index, df[u'E4'],
                                 levels=np.arange(40, data['data3'].max(),
                                                  1), cmap=c_0)
            ce1.ax.invert_yaxis()
            ce2.ax.invert_yaxis()
            ce3.ax.invert_yaxis()
            ce4.ax.invert_yaxis()
            ce1c = plt.colorbar(mappable=ce1, ax=ce1.ax, pad=0.0125)
            ce2c = plt.colorbar(mappable=ce2, ax=ce2.ax, pad=0.0125)
            ce3c = plt.colorbar(mappable=ce3, ax=ce3.ax, pad=0.0125)
            ce4c = plt.colorbar(mappable=ce4, ax=ce4.ax, pad=0.0125)
            ce3c.set_label('COUNTS', labelpad=10, y=0.95)
            axEI3.set_ylabel('Profundidade [m]', labelpad=10, y=0.95)
            fmt_major_minor(ce4.ax)
            clean_major_minor(ce1.ax)
            clean_major_minor(ce2.ax)
            clean_major_minor(ce3.ax)
        fig.canvas.draw()
        self._root.update()

    def plot_figure_CM(self, data, param):
        # colormap para plot
        c_map = [plt.cm.jet, plt.cm.hsv, plt.cm.ocean]
        c_0 = c_map[self._user_CM.get()]

        if plt.fignum_exists(3):
            plt.close(3)
            fig = plt.figure(3, facecolor=(1.0, 1.0, 1.0), figsize=(10, 8))
        else:
            fig = plt.figure(3, facecolor=(1.0, 1.0, 1.0), figsize=(10, 8))
        fig.show()
        # Diagramação e exibição da figura.
        fig.subplots_adjust(bottom=0.1, right=0.985, top=0.95, hspace=0.1)
        fig.suptitle(data['tag'].split(u'@')[0] +
                     self._dbvar.get() + ' COR. MAG.')

        axCM1 = fig.add_subplot(411)
        axCM2 = fig.add_subplot(412, sharex=axCM1)
        axCM3 = fig.add_subplot(413, sharex=axCM1)
        axCM4 = fig.add_subplot(414, sharex=axCM1)

        equaltidx = list()
        for date in data['t']:
            equaltidx.append((param['t'] == date).nonzero()[0][0])
        z = param['data0'][equaltidx] + param['data1'][equaltidx] / 100. + \
            param['data2'][equaltidx] / 2. + \
            param['data2'][equaltidx] * data['z']
        cotas = np.unique(param['data0'])
        for i in cotas:
            idx = param['data0'][equaltidx] == i
            X_axis_range = pd.date_range(start=data['t'][idx].min(),
                                         end=data['t'][idx].max(),
                                         freq='H').to_pydatetime()
            cols = list(set() - set(param['t']))

            time = np.append(data['t'][idx], cols)
            cols = np.full(np.size(cols), np.nan)
            camada = np.append(data['z'][idx], cols)
            profundidade = np.append(z[idx], cols)
            C1 = np.append(data['data0'][idx], cols)
            C2 = np.append(data['data1'][idx], cols)
            C3 = np.append(data['data2'][idx], cols)
            C4 = np.append(data['data3'][idx], cols)
            d = {u'time': time, u'camada': camada,
                 u'C1': C1, u'C2': C2,
                 u'C3': C3, u'C4': C4,
                 u'profundidade': profundidade}

            df = pd.DataFrame(d).pivot(u'profundidade', u'time')
            cc1 = axCM1.contourf(df['C1'].columns, df.index, df['C1'],
                                 levels=np.arange(data['data0'].min(),
                                                  data['data0'].max(), 1),
                                 cmap=c_0)
            cc2 = axCM2.contourf(df['C2'].columns, df.index, df[u'C2'],
                                 levels=np.arange(data['data0'].min(),
                                                  data['data1'].max(), 1),
                                 cmap=c_0)
            cc3 = axCM3.contourf(df['C3'].columns, df.index, df[u'C3'],
                                 levels=np.arange(data['data0'].min(),
                                                  data['data2'].max(), 1),
                                 cmap=c_0)
            cc4 = axCM4.contourf(df['C4'].columns, df.index, df[u'C4'],
                                 levels=np.arange(data['data0'].min(),
                                                  data['data3'].max(), 1),
                                 cmap=c_0)
            cc1.ax.invert_yaxis()
            cc2.ax.invert_yaxis()
            cc3.ax.invert_yaxis()
            cc4.ax.invert_yaxis()
            cc1c = plt.colorbar(mappable=cc1, ax=cc1.ax, pad=0.0125)
            cc2c = plt.colorbar(mappable=cc2, ax=cc2.ax, pad=0.0125)
            cc3c = plt.colorbar(mappable=cc3, ax=cc3.ax, pad=0.0125)
            cc4c = plt.colorbar(mappable=cc4, ax=cc4.ax, pad=0.0125)
            cc3c.set_label('COUNTS', labelpad=10, y=0.95)
            axCM3.set_ylabel('Profundidade [m]', labelpad=10, y=0.95)
            fmt_major_minor(cc4.ax)
            clean_major_minor(cc1.ax)
            clean_major_minor(cc2.ax)
            clean_major_minor(cc3.ax)
        fig.canvas.draw()
        self._root.update()


def clean_major_minor(axe):
    for label in axe.xaxis.get_majorticklabels():
        label.set_visible(False)
    for label in axe.xaxis.get_minorticklabels():
        label.set_visible(False)


def fmt_major_minor(axe):
    axe.fmt_xdata = DateFormatter('%d/%m/%y %H:%M')
    x_lim = axe.get_xlim()
    if (x_lim[-1] - x_lim[0]) == 0:
        axe.xaxis.set_major_locator(HourLocator())
        axe.xaxis.set_major_formatter(DateFormatter('%d/%m/%y\n%H:%M'))
    elif 0 < (x_lim[-1] - x_lim[0]) < 5:
        axe.xaxis.set_major_locator(DayLocator())
        axe.xaxis.set_major_formatter(DateFormatter('%d/%m/%y'))
        axe.xaxis.set_minor_locator(HourLocator(byhour=(3, 6, 9, 12,
                                                        15, 18, 21)))
        axe.xaxis.set_minor_formatter(DateFormatter('%H:%M'))
    elif 5 <= (x_lim[-1] - x_lim[0]) < 11:
        axe.xaxis.set_major_locator(DayLocator())
        axe.xaxis.set_major_formatter(DateFormatter('%d/%m/%y'))
        axe.xaxis.set_minor_locator(HourLocator(byhour=(6, 12, 18)))
        axe.xaxis.set_minor_formatter(DateFormatter('%H:%M'))
    elif 11 <= (x_lim[-1] - x_lim[0]) < 45:
        axe.xaxis.set_major_locator(DayLocator(interval=3))
        axe.xaxis.set_major_formatter(DateFormatter('%d/%m/%y'))
        axe.xaxis.set_minor_locator(HourLocator(byhour=(12, 00)))
    else:
        axe.xaxis.set_minor_locator(MonthLocator())
        axe.xaxis.set_major_locator(YearLocator())
        axe.xaxis.set_major_formatter(DateFormatter('%Y'))
    for label in axe.xaxis.get_majorticklabels():
        label.set_fontsize(8)
        label.set_ha('right')
        label.set_rotation(45)
    for label in axe.xaxis.get_minorticklabels():
        label.set_fontsize(7)
        label.set_ha('right')
        label.set_rotation(45)
    for label in axe.get_yticklabels():
        label.set_fontsize(8)


def main():
    def callback():
        if tkMessageBox.askokcancel("Sair", "Deseja realmente sair?"):
            root.destroy()
            plt.close('all')
    root = tki.Tk()
    root.title(u"Perfis Temporais em UCDs" +
               u" - OCEANOP" +
               u" [ADCP Profile]")
    root.protocol("WM_DELETE_WINDOW", callback)

    root.resizable(width=False, height=False)
    ADCP_Profile(root)
    root.mainloop()

if __name__ == "__main__":
    main()
