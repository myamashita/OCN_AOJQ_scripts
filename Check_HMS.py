# -*- coding: utf-8 -*-
# purpose:  Create database in sqlite
#           Insert data
# author:   Márcio Yamashita
# created:  27-June-2017
# modified:

import sqlite3
import pyocnp
import errno
import os
from datetime import datetime, timedelta
import zlib as zb


class CheckBd(object):
    """docstring for CheckBd"""
    def __init__(self, ucd):
        super(CheckBd, self).__init__()
        # Banco de dado chave criptografada de acesso.
        self._db = pyocnp.PROD_DBACCESS
        self._ucd = ucd
        self.id = pyocnp.ucdid_byname_ocndb(self._ucd, str_dbaccess=self._db)
        self.ucd = pyocnp.ucdname_byid_ocndb(self.id, str_dbaccess=self._db)
        self.hms_bd_name = '.\\HMS\\%s.db' % self.ucd
        if not os.path.exists(os.path.dirname(self.hms_bd_name)):
            try:
                os.makedirs(os.path.dirname(self.hms_bd_name))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
        if not os.path.exists(self.hms_bd_name):
            self.createbd(self.hms_bd_name)

    def createbd(self, name):
        self.conn = sqlite3.connect(name)
        self.conn.executescript('''CREATE TABLE TB_HMS
                                (LOIN_TX_LOCAL INT NOT NULL,
                                HMS_DT_AQUISICAO DATE NOT NULL,
                                HMS_NR_CONTADOR INT NOT NULL,
                                HMS_CATEGORIA_AERONAVE INT,
                                HMS_DIA_NOITE INT,
                                HMS_POUSO_PERMITIDO INT,
                                HMS_PITCH REAL,
                                HMS_PITCH_DM_20M REAL,
                                HMS_PITCH_UM_20M REAL,
                                HMS_ROLL REAL,
                                HMS_ROLL_PM REAL,
                                HMS_ROLL_SM REAL,
                                HMS_INCL REAL,
                                HMS_INCL_M REAL,
                                HMS_HEAVE REAL,
                                HMS_HEAVE_M REAL,
                                HMS_HEAVE_PER REAL,
                                HMS_HEAVE_VEL_M REAL);
                                CREATE TABLE TB_IMPORTACOES
                                (IMPO_NR_IMPORTACAO INTEGER
                                PRIMARY KEY AUTOINCREMENT,
                                IMPO_DT_IMPORTACAO DATE NOT NULL,
                                LOIN_CD_LOCAL INT NOT NULL,
                                IMPO_DT_AQUISICAO DATE NOT NULL UNIQUE);''')
        self.conn.close()
        pass


class InsertDataDb(object):
    """docstring for InsertDataDb"""
    def __init__(self, ucd, i_date, f_date):
        super(InsertDataDb, self).__init__()
        # Banco de dado chave criptografada de acesso.
        self._db = pyocnp.DESV_DBACCESS
        self._ucd = ucd
        self.id = pyocnp.ucdid_byname_ocndb(self._ucd, str_dbaccess=self._db)
        self.ucd = pyocnp.ucdname_byid_ocndb(self.id, str_dbaccess=self._db)
        self.i_date = i_date
        self.f_date = f_date
        dbqry = ("SELECT"
                 " UE6RK.TB_PARAMETROS_INST.PAIN_TX_PATH_ARQ"
                 " FROM"
                 " UE6RK.TB_PARAMETROS_INST"
                 " WHERE"
                 " UE6RK.TB_PARAMETROS_INST.LOIN_CD_LOCAL = " +
                 unicode(self.id[0]))

        qryresults = pyocnp.odbqry_all(dbqry,
                                       pyocnp.asciidecrypt(self._db))[0][0][:-4]
        self.path = qryresults + 'HMS\\'
        self.hms_bd_name = '.\\HMS\\%s.db' % self.ucd
        if not os.path.exists(os.path.dirname(self.path)):
            print 'This path does not exists'
            try:
                os.remove(self.hms_bd_name)
                print 'The %s was removed' % self.hms_bd_name
                return
            except:
                pass
        if os.path.exists(os.path.dirname(self.path)):
            self.gen_file_list()
            self.get_data()

    def gen_file_list(self):
        '''to genereate list files'''
        ini = datetime.strptime(self.i_date, "%d/%m/%Y %H:%M:%S")
        fim = datetime.strptime(self.f_date, "%d/%m/%Y %H:%M:%S")
        self.list_files = []
        ininame = self.path + '%sHMS' % CheckBd(self._ucd).id[0]
        while ini <= fim:
            fname = ininame + '%s.hms_gz' % ini.strftime(u"%Y-%m-%d-%H-00")
            self.list_files.append(fname)
            ini = ini + timedelta(hours=1)
        pass

    def get_data(self):
        self.conn = sqlite3.connect(self.hms_bd_name)
        self.curs = self.conn.cursor()
        for i in self.list_files:
            self.load_file(i)
        self.conn.commit()
        self.conn.close()

    def load_file(self, hmsfile):
        filename = hmsfile
        qry_meta = ("INSERT INTO TB_IMPORTACOES "
                    "(IMPO_DT_IMPORTACAO, "
                    "LOIN_CD_LOCAL, "
                    "IMPO_DT_AQUISICAO) "
                    "VALUES(?,?,?);")
        qry_data = ("INSERT INTO TB_HMS "
                    "(LOIN_TX_LOCAL, "
                    "HMS_DT_AQUISICAO, "
                    "HMS_NR_CONTADOR, "
                    "HMS_CATEGORIA_AERONAVE, "
                    "HMS_DIA_NOITE, "
                    "HMS_POUSO_PERMITIDO, "
                    "HMS_PITCH, "
                    "HMS_PITCH_DM_20M, "
                    "HMS_PITCH_UM_20M, "
                    "HMS_ROLL, "
                    "HMS_ROLL_PM, "
                    "HMS_ROLL_SM, "
                    "HMS_INCL, "
                    "HMS_INCL_M, "
                    "HMS_HEAVE, "
                    "HMS_HEAVE_M, "
                    "HMS_HEAVE_PER, "
                    "HMS_HEAVE_VEL_M) "
                    "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);")

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
                print u"<<Decompressing Error>> File: " + repr(filename)
                print u"  zlibError: " + unicode(err)
            else:
                # Substituição de tabulações por espaços.
                txtugz = txtugz.replace(u"\t", u" ")
                # Substituição de valores não aquisitados por 'NaN',
                # demarcados originalmente com o símbolo padrão '--'.
                txtugz = txtugz.replace(u"*.*", u" --")
                txtugz = txtugz.replace(u"*", u" ")
                txtugz = txtugz.replace(u" --", u" NaN")
                # Particionamento do conteúdo do arquivo em linhas.
                txtlns = txtugz.splitlines()
                # Tentativa de importação dos parâmetros e dados
                try:
                    # Identificação da data de aquisição (finish file).
                    aqs = " ".join(txtlns[0].split(u" ")[-2:])
                    d = datetime.strptime(aqs, "%d/%m/%Y %H:%M:%S")
                    try:
                        qry_meta_insert = [datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"), unicode(self.id[0]),
                            d.strftime("%Y-%m-%d %H:%M:%S")]
                        self.curs.execute(qry_meta, qry_meta_insert)
                    except sqlite3.IntegrityError:
                        print u'%s já importado' % os.path.basename(filename)
                    else:
                        # Linha de primeiro dado coletado
                        nl = 8
                        ct = 1
                        while True:
                            try:
                                lndata = txtlns[nl].split()
                                # Dia de aquisição de cada amostra.
                                if d.hour:
                                    dsample = d.date()
                                else:
                                    dsample = (d - timedelta(1)).date()
                                # Hora de aquisição da amostra.
                                hsample = datetime.strptime(lndata[0],
                                                            "%H:%M:%S").time()
                                # Aquisição da amostra.
                                DT_AQS = d.combine(dsample, hsample)
                                HMS_DT_AQUISICAO = DT_AQS.strftime(
                                    "%Y-%m-%d %H:%M:%S")
                                qry_data_insert = [unicode(self.id[0]),
                                    HMS_DT_AQUISICAO, ct, lndata[9], lndata[10],
                                    lndata[11], lndata[12], lndata[13],
                                    lndata[14], lndata[15], lndata[16],
                                    lndata[17], lndata[18], lndata[19],
                                    lndata[20], lndata[21], lndata[22],
                                    lndata[23]]
                                self.curs.execute(qry_data, qry_data_insert)
                                nl += 1
                                ct += 1
                            except IndexError as err:
                                break
                except Exception as err:
                    # Reportagem de erro de importação do conteúdo.
                    print(u"<<Importing Error>> File: " +
                          repr(filename))
                    print(u" " + repr(err)[0:repr(err).find("(")] +
                          u": " + unicode(err))

if __name__ == '__main__':

    ucd = ['P-62', 'P-56', 'P-55', 'P-54', 'P-53', 'P-52', 'P-51', 'P-50',
           'P-48', 'P-43', 'P-40', 'P-38', 'P-32', 'P-35', 'P-37']
    date_ini = (datetime.utcnow() -
                timedelta(hours=72)).strftime(u"%d/%m/%Y" +
                                              u" %H:00:00")
    date_end = datetime.utcnow().strftime(u"%d/%m/%Y %H:00:00")

    for plat in ucd:
        print plat
        CheckBd(plat)
        InsertDataDb(plat, date_ini, date_end)
