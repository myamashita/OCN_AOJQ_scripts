# -*- coding: utf-8 -*-
# purpose:  Check missing ADCP data in PROD database
# author:   Márcio Yamashita
# created:  24-april-2017
# modified:


import Tkinter as tki
import pyocnp
from collections import OrderedDict
import matplotlib.pyplot as plt
from matplotlib.colors import rgb2hex
from datetime import datetime, timedelta


class ADCP_PROD:
    u""" Interfaze Gráfica Principal ao Usuário (GUI) baseada em Tkinter. """

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
        self._modapp = OrderedDict([(u"ADCP", 2),
                                    (u"AQUADOPP", 71),
                                    (u"FSI-2D", 3),
                                    (u"FSI-3D", 4),
                                    (u"MIROS", 5),
                                    (u"YOUNG", 1)])
        # Bacias disponíveis e código da região
        self._rgs = OrderedDict([(u"BS", 2),
                                 (u"BC", 1),
                                 (u"BES", 3),
                                 (u"CAMAMU", 5),
                                 (u"SEAL", 7),
                                 (u"CEARÁ", 6),
                                 (u"POTIGUAR", 4)])

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

        # Associação da barra de opções ao frame principal.
        self._mainfrm.master.config(menu=self._menubar)

        # ============================================================ #
        # Frame de Período #
        # ============================================================ #
        self._dtfrm = tki.Frame(self._mainfrm, bg=rgb2hex(BGCOLORAPL),
                                bd=2, relief=tki.GROOVE)
        self._dtfrm.pack(fill=tki.X, padx=6, pady=4, side=tki.TOP)

        # Subframe de Período #
        # ============================================================ #
        self._datefrm = tki.Frame(self._dtfrm, bg=rgb2hex(BGCOLORAPL),
                                  bd=0, relief=tki.GROOVE)
        self._datefrm.pack(padx=1, pady=0, side=tki.LEFT, fill=tki.X,
                           expand=tki.YES)

        # Variável mutante da data atual declarada.
        self._idate = tki.StringVar()
        self._idate.set(datetime.utcnow().strftime(u"%d/%m/%Y" + u" %H:00:00"))

        # Variável mutante do intervalo checado.
        self._fdate = tki.IntVar()
        self._fdate.set(6)

        # Rótulo Data Atual.
        tki.Label(self._datefrm, bd=0, bg=rgb2hex(BGCOLORAPL), fg='white',
                  text=u"Referência UTC", font=('Verdana', '8', 'bold'),
                  relief=tki.FLAT,
                  justify=tki.CENTER).grid(column=2, row=0, padx=2,
                                           pady=0, sticky=tki.EW)

        # Rótulo Horas Anteriores.
        tki.Label(self._datefrm, bd=0, bg=rgb2hex(BGCOLORAPL), fg='white',
                  text=u"Horas Anteriores", font=('Verdana', '8', 'bold'),
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

        # Botões de acréscimo e decréscimo da data de referência
        dt = 1    # incremento (em dias)
        self._idatdbup = tki.Button(self._datefrm, bd=1, text=u"\u25B2",
                                    font=('Default', '5', 'bold'),
                                    command=lambda di=self._idate,
                                    dt=dt, md=self.moddatevar,
                                    mds=self.moddatestr: md(di, dt))
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
                                    dt=dt, md=self.moddatevar,
                                    mds=self.moddatestr: md(di, dt))
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
                  fg='white', text=u"e", font=('Verdana', '9', 'normal'),
                  justify=tki.CENTER).grid(column=4, row=1, rowspan=2, padx=8,
                                           pady=0, sticky=tki.NSEW)

        # Campo de entrada da data final de consulta
        self._fdatent = tki.Entry(self._datefrm, bd=3, width=19,
                                  textvariable=self._fdate, justify=tki.CENTER)
        self._fdatent.grid(column=6, row=1, rowspan=2, padx=0, pady=2,
                           ipady=2, sticky=tki.E)

        # Botões de acréscimo e decréscimo de horas para consulta
        # incremento (em horas)
        self._fdathbup = tki.Button(self._datefrm, bd=1, text=u"\u25B2",
                                    font=('Default', '5', 'bold'),
                                    command=lambda df=self._fdate:
                                    df.set(df.get()+1))
        self._fdathbup.grid(column=7, row=1, padx=0, pady=0, sticky=tki.S)

        # decremento (em horas)
        self._fdathbdw = tki.Button(self._datefrm, bd=1, text=u"\u25BC",
                                    font=('Default', '5', 'bold'),
                                    command=lambda df=self._fdate:
                                    df.set(df.get()-1 if df.get() > 0
                                           else df.set(df.get()+0)))
        self._fdathbdw.grid(column=7, row=2, padx=0, pady=0, sticky=tki.N)

        self._idate.trace("w", lambda vn, en, md, dn=self._idatent:
                          dn.config(fg=rgb2hex(TXCOLORSTD)))
        self._fdate.trace("w", lambda vn, en, md, dn=self._fdatent:
                          dn.config(fg=rgb2hex(TXCOLORSTD)))

        # ============================================================ #
        # Frame de Opções
        # ============================================================ #
        self._opt_frm = tki.Frame(self._mainfrm, bg=rgb2hex(BGCOLORAPL),
                                  bd=2, relief=tki.GROOVE)
        self._opt_frm.pack(fill=tki.BOTH, padx=6, pady=4, side=tki.LEFT)

        # Subframe Opções
        # ============================================================ #
        self._opt_Sfrm = tki.Frame(self._opt_frm, bg=rgb2hex(BGCOLORAPL),
                                   bd=0, relief=tki.GROOVE)
        self._opt_Sfrm.pack(padx=2, pady=2, side=tki.TOP)

        # Label Opções
        tki.Label(self._opt_Sfrm, bd=0, bg=rgb2hex(BGCOLORAPL), text=u"Opções",
                  fg='white', font=('Verdana', '10', 'bold'), relief=tki.FLAT,
                  justify=tki.CENTER).grid(column=1, row=0, padx=2,
                                           pady=0, sticky=tki.EW)

        # Menu de Opções de BDs
        self._opt_Sfrm_bd = tki.Label(self._opt_Sfrm, bg=rgb2hex(BGCOLORAPL),
                                      fg='white', bd=0, text=u"Banco:",
                                      font=('Verdana', '9', 'bold'),
                                      relief=tki.FLAT, justify=tki.LEFT)
        self._opt_Sfrm_bd.grid(column=0, row=1, rowspan=1, padx=10,
                               pady=2, sticky=tki.NSEW)

        # Variável mutante do BD
        self._db_var = tki.StringVar()

        # Menu de BDs disponíveis para consulta.
        self._db_opt = tki.OptionMenu(self._opt_Sfrm, self._db_var,
                                      *self._dbs.keys())
        self._db_opt.grid(column=1, row=1, rowspan=1, padx=4, pady=0,
                          sticky=tki.NSEW)

        # Menu de Opções de Arquivos
        self._opt_Sfrm_arq = tki.Label(self._opt_Sfrm,
                                       bg=rgb2hex(BGCOLORAPL),
                                       bd=0, fg='white', text=u"Arq.:",
                                       font=('Verdana', '9', 'bold'),
                                       relief=tki.FLAT, justify=tki.CENTER)
        self._opt_Sfrm_arq.grid(column=0, row=2, rowspan=1,
                                padx=2, pady=2, sticky=tki.NSEW)

        # Variável mutante do Arquivos
        self._arq_var = tki.StringVar()

        # Menu de Arquivos disponíveis para consulta.
        self._arq_opt = tki.OptionMenu(self._opt_Sfrm, self._arq_var,
                                       *self._modapp.keys())
        self._arq_opt.grid(column=1, row=2, rowspan=1, padx=4, pady=0,
                           sticky=tki.NSEW)

        # Menu de Opções de Bacias
        self._Sfrm_bacia = tki.Label(self._opt_Sfrm,
                                     bg=rgb2hex(BGCOLORAPL),
                                     bd=0, fg='white', text=u"Bacia:",
                                     font=('Verdana', '9', 'bold'),
                                     relief=tki.FLAT, justify=tki.CENTER)
        self._Sfrm_bacia.grid(column=0, row=3, rowspan=1,
                              padx=2, pady=2, sticky=tki.NSEW)

        # Variável mutante da Bacia
        self._bacia_var = tki.StringVar()

        # Menu de Parâmetros disponíveis para consulta.
        self._bacia_opt = tki.OptionMenu(self._opt_Sfrm, self._bacia_var,
                                         *self._rgs.keys(),
                                         command=self.askucds)
        self._bacia_opt.grid(column=1, row=3, rowspan=1, padx=4, pady=0,
                             sticky=tki.NSEW)

        # Subframe de UCDs Controle
        self._Sfrm_ucdsmenu = tki.Label(self._opt_Sfrm, bg=rgb2hex(BGCOLORAPL),
                                        bd=0, fg='white', text=u"UCDs:",
                                        font=('Verdana', '9', 'bold'),
                                        relief=tki.FLAT, justify=tki.CENTER)
        self._Sfrm_ucdsmenu.grid(column=0, columnspan=1, row=4, rowspan=2,
                                 padx=2, pady=0, sticky=tki.N)

        # Listagem de UCDs disponíveis para consulta.
        self._ucdslbx = tki.Listbox(self._opt_Sfrm, bd=1, activestyle='none',
                                    selectmode=tki.MULTIPLE, setgrid=tki.NO,
                                    height=1, selectborderwidth=3, width=15,
                                    exportselection=tki.FALSE,
                                    selectbackground=rgb2hex(BGCOLORSLT),
                                    font=('Verdana', '11', 'bold'))
        self._ucdslbx.grid(column=1, row=4, rowspan=2, padx=0, pady=0,
                           sticky=tki.NS)

        # Menu de UCDs para consulta facilitada.
        self._ucdsmenub = tki.Menu(self._root, tearoff=0)




        self._mainfrm.pack(fill=tki.BOTH, padx=0, pady=0, side=tki.TOP)

        self._db_var.set(self._dbs.keys()[0])
        self._arq_var.set(self._modapp.keys()[0])

        self._uselvar = tki.StringVar()
        self._root.update()

    def moddatevar(self, date, dtdays):
        u""" Aumentar/diminuir data do período de consulta. """
        try:
            date.set((datetime.strptime(date.get(), "%d/%m/%Y %H:00:00") +
                      timedelta(dtdays)).strftime(u"%d/%m/%Y %H:00:00"))
        except:
            date.set(datetime.utcnow().strftime(u"%d/%m/%Y %H:00:00"))

    def moddatestr(self, date, dtdays):
        """ Aumentar/diminuir data qualquer. """
        try:
            return(datetime.strptime(date.get(), "%d/%m/%Y %H:00:00") +
                   timedelta(dtdays))
        except:
            return(datetime.utcnow().strftime(u"%d/%m/%Y %H:00:00"))

    def askucds(self, dbvalue):
        u""" Listar UCDs disponíveis para consulta no BD. """
        # Limpeza do menu de UCDs Controle
        self._ucdslbx.delete(0, tki.END)
        ipsh()
        dbs = self._dbs[self._db_var.get()]
        eqp = self._modapp[self._arq_var.get()]
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
                     " LEFT JOIN"
                     " UE6RK.TB_PARAMETROS_INST"
                     " ON"
                     " UE6RK.TB_LOCAL_INSTAL.LOIN_CD_LOCAL ="
                     " UE6RK.TB_PARAMETROS_INST.LOIN_CD_LOCAL"
                     " WHERE"
                     " UE6RK.TB_LOCAL_INSTAL.REGI_CD_REGIAO =" +
                     unicode(self._rgs[dbvalue]) +
                     " AND"
                     " UE6RK.TB_PARAMETROS_INST.EQUI_CD_EQUIPAMENT =" +
                     unicode(eqp) +
                     " ORDER BY"
                     " TB_LOCAL_INSTAL.LOIN_TX_LOCAL")
            ucds = pyocnp.odbqry_all(dbqry,
                                     pyocnp.asciidecrypt(dbs))
        except:
            # Atualização de status: BD inacessivel.
            #self._msg.set(u'%s INDISPONÍVEL' % self._db_opt.get())
            raise
        # Oferta da lista de UCDs disponíveis.
        self._ucds = ucds
        for lstid, lstnm in ucds:
            self._ucdslbx.insert(tki.END, lstnm)

        # Oferta e atualização do menu de UCDs.
        self._ucdsmenuvars = list()

        self.menuaval(self._ucdsmenub, self._Sfrm_ucdsmenu,
                      self._ucdslbx, self._ucdsmenuvars)

        self._Sfrm_ucdsmenu["cursor"] = "sizing"
        self._Sfrm_ucdsmenu["text"] = u"UCDs:\n\u2630"

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
                                 mn=menu, mnb=menubt,
                                 mf=self._mainfrm, go=self._uselvar:
                                 (lbl.selection_clear(ix) if ix in
                                  lbl.curselection() else
                                  lbl.selection_set(ix), lbl.see(ix)))

            # Quebra de coluna a cada número fixo de itens.
            if not(itemidx % 10):
                menu.entryconfigure(itemidx, columnbreak=1)
        # Associação da ação ao widget.

        menubt.bind("<Button-1>", lambda ev, pp=self.popupmenu, mn=menu,
                    mnb=menubt, lb=lbxmain, lv=lstvars:
                        pp(ev, mn, mnb, lb, lv))

def main():
    u""" Função principal para chamar tk. """
    root = tki.Tk()
    root.title(u"Missing ADCP data at PROD" +
               u" - OCEANOP")
    root.resizable(width=False, height=False)
    ADCP_PROD(root)
    root.mainloop()


if __name__ == "__main__":

    main()
