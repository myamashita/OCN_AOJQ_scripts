# -*- coding: utf-8 -*-
# purpose:  Check ID da UCD
# author:   Márcio Yamashita
# created:  30-set-2016
# modified: 12-apr-2017 AOJQ

from __future__ import division
import Tkinter as tki
from collections import OrderedDict
import pyocnp
from matplotlib.colors import rgb2hex


class UCD_ID:
    u""" Interface Gráfica Principal ao Usuário (GUI) baseada em Tkinter. """

    def __init__(self, root):
        u""" Instanciar elementos gráficos (widgets) e ações atreladas. """
        # Definição de Cores ========================================= #
        # ============================================================ #
        BGCOLORBOX = (1.000, 1.000, 1.000)
        BGCOLORAPL = (0.392, 0.584, 0.929)
        BGCOLORSLT = (0.031, 0.572, 0.815)

        # Definição de Atributos ===================================== #
        # ============================================================ #
        # Janela gráfica de origem da aplicação.
        self._root = root

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
                         (rt.destroy()))
        self._menubar.add_cascade(label=u"Arquivo", menu=menu)

        # Associação da barra de opções ao frame principal.
        self._mainfrm.master.config(menu=self._menubar)

        # Frame de Período e Banco #
        # ============================================================ #
        self._dbdfrm = tki.Frame(self._mainfrm, bg=rgb2hex(BGCOLORAPL),
                                 bd=2, relief=tki.GROOVE)
        self._dbdfrm.pack(fill=tki.X, padx=6, pady=4, side=tki.TOP)

        # Subframe de BD #
        # ============================================================ #
        self._dbfrm = tki.Frame(self._dbdfrm, bg=rgb2hex(BGCOLORAPL),
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
                                     *self._dbs.keys(),
                                     command=self.askucds)
        self._dbopt.grid(column=8, row=1, rowspan=1, padx=4, pady=0,
                         sticky=tki.NSEW)

        # Frame de UCDs PROD
        # ============================================================ #
        self._ucdfrm = tki.Frame(self._mainfrm, bg=rgb2hex(BGCOLORAPL),
                                 bd=0, relief=tki.FLAT)
        self._ucdfrm.pack(fill=tki.BOTH, padx=6, pady=4, side=tki.LEFT)

        self._ucdsmenub = tki.Label(self._ucdfrm, bg=rgb2hex(BGCOLORAPL),
                                    bd=0, fg='white', text=u"UCDs:",
                                    font=('Verdana', '9', 'bold'),
                                    relief=tki.FLAT, justify=tki.CENTER)

        self._ucdsmenub.grid(column=0, columnspan=1, row=0, rowspan=2,
                             padx=2, pady=0, sticky=tki.N)

        # Listagem de UCDs disponíveis para consulta.
        self._ucdslbx = tki.Listbox(self._ucdfrm, bd=1, selectmode=tki.SINGLE,
                                    width=22, height=6, selectborderwidth=2,
                                    setgrid=tki.NO, exportselection=tki.FALSE,
                                    selectbackground=rgb2hex(BGCOLORSLT),
                                    font=('Default', '8', 'normal'))

        self._ucdslly = tki.Scrollbar(self._ucdfrm, bd=0, orient=tki.VERTICAL,
                                      command=self._ucdslbx.yview)

        self._ucdslbx.grid(column=1, columnspan=1, row=0, rowspan=2,
                           padx=0, pady=0, sticky=tki.NS)
        self._ucdslly.grid(column=2, columnspan=2, row=0, rowspan=2,
                           padx=0, pady=0, sticky=tki.NSEW)

        self._ucdslbx.configure(yscrollcommand=self._ucdslly.set)
        self._root.update_idletasks()

        # Menu de UCDs para consulta facilitada.
        self._ucdsmenu = tki.Menu(self._root, tearoff=0)

        # Subframe de Consulta #
        # ============================================================ #
        self._qryfrm = tki.Frame(self._mainfrm, bg=rgb2hex(BGCOLORBOX),
                                 bd=3, relief=tki.SUNKEN)
        self._qryfrm.pack(expand=tki.YES, padx=0, pady=0, side=tki.RIGHT)

        # Botão de plotagem dos dados desejados
        # (condicionalmente e previamente desabilitado).
        self._qrybt = tki.Button(self._qryfrm, bd=1, text=u"Consulta",
                                 font=('Default', '10', 'bold'),
                                 command=self.askid)
        self._qrybt.grid(column=1, row=1, rowspan=1, padx=0,
                         pady=1, ipadx=1, ipady=1)
        self._qrybt["state"] = tki.DISABLED

        # Subframe de Mensagem #
        # ============================================================ #
        self._msgfrm = tki.Frame(self._mainfrm, bg=rgb2hex(BGCOLORAPL),
                                 bd=0, relief=tki.FLAT)
        self._msgfrm.pack(expand=tki.YES, padx=0, pady=0, side=tki.BOTTOM)
        self._qrymsg = tki.Label(self._msgfrm, bg=rgb2hex(BGCOLORAPL),
                                 bd=0, fg='white', text=u"Mensagem:",
                                 font=('Verdana', '9', 'bold'),
                                 relief=tki.FLAT, justify=tki.CENTER)

        self._qrymsg.grid(column=1, columnspan=1, row=1, rowspan=1,
                          padx=1, pady=1, sticky=tki.N)

        self._msg = tki.StringVar()
        self._msg.set("Escolha o Banco")
        self._qrymsgbox = tki.Label(self._msgfrm, bd=1, width=25,
                                    bg=rgb2hex(BGCOLORAPL), fg='yellow',
                                    font=('Verdana', '12', 'bold'),
                                    textvariable=self._msg, justify=tki.CENTER)
        self._qrymsgbox.grid(column=1, columnspan=1, row=2, rowspan=1,
                             padx=1, pady=1, sticky=tki.N)
        self._root.update()

        self._mainfrm.pack(fill=tki.BOTH, padx=0, pady=0, side=tki.TOP)

        # Carregamento de agrupamentos de UCDs definidos pela aplicação.
        self._uselvar = tki.StringVar()
        self._ucdslbx.curselection()

    def askucds(self, dbvalue):
        u""" Listar UCDs disponíveis para consulta no BD escolhido. """
        # Desativação temporária do botão de consulta aos dados.
        self._qrybt["state"] = tki.DISABLED

        # Limpeza do menu de UCDs.
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
            dbqry = ("SELECT"
                     " TB_LOCAL_INSTAL.LOIN_CD_LOCAL,"
                     " UNISTR(TB_LOCAL_INSTAL.LOIN_TX_LOCAL)"
                     " FROM"
                     " UE6RK.TB_LOCAL_INSTAL"
                     " ORDER BY"
                     " TB_LOCAL_INSTAL.LOIN_TX_LOCAL")
            ucds = pyocnp.odbqry_all(dbqry,
                                     pyocnp.asciidecrypt(self._dbs[dbvalue]))
        except:
            # Atualização de status: BD inacessivel.
            self._msg.set(u'%s INDISPONÍVEL' % self._dbvar.get())
            raise

        # Oferta da lista de UCDs disponíveis.
        self._ucds = ucds
        for lstid, lstnm in ucds:
            self._ucdslbx.insert(tki.END, lstnm)

        self._ucdslbx.bind('<<ListboxSelect>>', lambda ev,
                           qb=self._qrybt, mf=self._mainfrm,
                           ms=self._msg, go=self._uselvar:
                           (qb.config(state=tki.NORMAL),
                            ms.set("Escolha a UCD\n e Consulte")
                            if(ev.widget.curselection() and
                               mf["cursor"] != "watch")
                            else qb.config(state=tki.DISABLED),
                            go.set(u"")))

        # Oferta e atualização do menu de UCDs.
        self._ucdsmenuvars = list()
        self.menuaval(self._ucdsmenu, self._ucdsmenub,
                      self._ucdslbx, self._ucdsmenuvars)
        self._ucdsmenub["cursor"] = "sizing"
        self._ucdsmenub["text"] = u"UCDs:\n\u2630"
        self._msg.set("Escolha a UCD\n e Consulte")

    def popupmenu(self, event, menu, menubt, lbxmain, lstvars):
        u""" Exibir menu facilitado para seleção. """
        # Nomenclaturas na listagem disponível.
        lbxlst = lbxmain.get(0, tki.END)
        # Índice selecionado na listagem disponível.
        curlst = lbxmain.curselection()
        for itemidx, item in enumerate(lbxlst):
            lstvars[itemidx].set(0)
            if itemidx in curlst:
                lstvars[itemidx].set(1)
        # Abertura do menu.
        menu.post(menubt.winfo_rootx(), menubt.winfo_rooty())
        self._msg.set("Escolha a UCD\n e Consulte")

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
                command=lambda lbl=lbxmain, ix=itemidx, mn=menu, mnb=menubt,
                qb=self._qrybt,  mf=self._mainfrm,
                go=self._uselvar:
                    (lbl.selection_clear(0, tki.END), lbl.selection_set(ix),
                     lbl.see(ix), qb.config(state=tki.NORMAL)
                     if(lbl.curselection() and mf["cursor"] != "watch")
                     else qb.config(state=tki.DISABLED),
                     go.set(u"")))
            # Quebra de coluna a cada número fixo de itens.
            if not(itemidx % 15):
                menu.entryconfigure(itemidx, columnbreak=1)
        # Associação da ação ao widget.
        menubt.bind("<Button-1>", lambda ev, pp=self.popupmenu, mn=menu,
                    mnb=menubt, lb=lbxmain, lv=lstvars:
                        pp(ev, mn, mnb, lb, lv))

    def askid(self):
        """ Consultar id da UCD. """
        # Desativação temporária do botão de consulta aos dados.
        self._qrybt["state"] = tki.DISABLED
        # UCD selecionada para consulta.
        ucdcode = self._ucds[self._ucdslbx.curselection()[0]][0]
        ucdname = self._ucds[self._ucdslbx.curselection()[0]][1]
        self._msg.set(u"Id de %s é:\n %s" % (ucdname, ucdcode))
        self._ucdslbx.select_clear(0, tki.END)


def main():
    u""" Função principal para chamar tk. """
    root = tki.Tk()
    root.title(u"Identificador da UCD" +
               u" - OCEANOP")
    root.resizable(width=False, height=False)
    UCD_ID(root)
    root.mainloop()


if __name__ == "__main__":

    main()
