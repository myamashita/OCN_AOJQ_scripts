# -*- coding: utf-8 -*-

# Márcio
# inicio:23/07/2018
# Consulta ao BD OCNTOOLS para extração de relatório de ocorrências.
# PYTHON 2/3 compatible code

from base64 import b64decode as b64
import cx_Oracle as cxOr
import pandas as pd


def connect_ocn_db():
    dbaccess = b64('VU9DTlRXUC9JRjU2OTU1NERGQFBST0Q=').decode('unicode_escape')
    conn = cxOr.connect(dbaccess)
    return conn


def get_report(conn, ini, fim):
    """
    close_qry ocorrencias fechadas no periodo de medição;
    open_qry ocorrencias na avaliação em aberto;
    return dataframe concatenado.
    """
    close_qry = ('{0} A.{1} OCORRENCIA, C.{2} ENTRADA, A.{2} SAIDA,'
                 ' D.OCOR_CD_USUARIO_AVALIADOR USUARIO, ROUND(A.{2}-C.{2},2)'
                 ' DELTA {3} ({0} FT.{1}, FT.{4}, FT.{2} {3} {5} FT {6}'
                 ' FT.{4} = 4) A, ({0} Q.{1} {3} {5} Q {6} Q.{4} = 3'
                 ' INTERSECT {0} F.{1} {3} {5} F {6} F.{4} = 4 AND'
                 ' F.{2} >= TO_DATE(\'{7}\', \'{8}\') AND'
                 ' F.{2} <= TO_DATE(\'{9}\', \'{8}\')) B,'
                 ' ({0} QT.{1}, QT.{4}, QT.{2} {3} {5} QT {6} QT.{4} = 3) C,'
                 ' UOCNTW.TB_OCORRENCIA D {6} A.{1} = B.{1} AND'
                 ' C.{1} = B.{1} AND D.{1} = B.{1} ORDER BY'
                 ' C.{2}').format('SELECT', 'OCOR_CD_OCORRENCIA',
                                  'STOC_DT_STATUS', 'FROM', 'STOC_CD_STATUS',
                                  'UOCNTW.TB_STATUS_OCORRENCIA', 'WHERE', ini,
                                  'DD/MM/YYYY HH24:MI:SS', fim)
    df1 = pd.read_sql_query(close_qry, conn)

    open_qry = ('{0} A.{1} OCORRENCIA, A.{2} ENTRADA,'
                ' B.OCOR_CD_USUARIO_AVALIADOR USUARIO FROM {3}.{4} A,'
                ' {3}.TB_OCORRENCIA B {5} A.{6} = 3 AND'
                ' A.{2} >= TO_DATE(\'{7}\', \'{8}\') AND'
                ' A.{1} NOT IN ({0} F.{1} FROM {3}.{4} F {5} F.{6} = 4 AND'
                ' F.{2} >= TO_DATE(\'{7}\', \'{8}\')) AND'
                ' A.{1} = B.{1} ORDER BY'
                ' A.{2}').format('SELECT', 'OCOR_CD_OCORRENCIA',
                                 'STOC_DT_STATUS', 'UOCNTW',
                                 'TB_STATUS_OCORRENCIA', 'WHERE',
                                 'STOC_CD_STATUS', ini,
                                 'DD/MM/YYYY HH24:MI:SS')
    df2 = pd.read_sql_query(open_qry, conn)
    return pd.concat([df1, df2], axis=0, ignore_index=True)


if __name__ == '__main__':
    conn = connect_ocn_db()

    ini = '26/06/2018  00:00:00'
    fim = '25/07/2018  23:59:59'

    report = get_report(conn, ini, fim)
    cols = ['OCORRENCIA', 'ENTRADA', 'SAIDA', 'USUARIO', 'DELTA']
    report[cols].to_csv('ocorrencias_ocntools.csv')
