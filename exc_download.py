# -*- coding: utf-8 -*-
""" 
exc_download

2021/nov  1.0  eliana   initial version (Linux/Python)
"""
# < imports >--------------------------------------------------------------------------------------

# python library
import datetime
import logging
import os
import requests
import sys

# local
import exc_defs as df

# < defines >--------------------------------------------------------------------------------------

# chunk size
DI_CHUNK_SIZE = 1048576

# NCAR login
DS_URL = "https://rda.ucar.edu/cgi-bin/login"
# NCAR data
DS_PATH = "https://rda.ucar.edu/data/ds083.2"

# < logging >--------------------------------------------------------------------------------------

# logger
M_LOG = logging.getLogger(__name__)
M_LOG.setLevel(logging.DEBUG)

# -------------------------------------------------------------------------------------------------
def check_file_status(fs_filepath, fi_filesize):
    """
    check file status
    """
    # new line
    sys.stdout.write('\r')
    sys.stdout.flush()

    # tamanho do arquivo
    li_size = int(os.stat(fs_filepath).st_size)

    # show completed percentual
    sys.stdout.write("{0:.3f}% Completed".format((li_size / fi_filesize) * 100))
    sys.stdout.flush()

# -------------------------------------------------------------------------------------------------
def _download_file(fs_file, f_cookies):
    """
    faz o download

    :param fs_file (str): filename to download
    :param f_cookies (): cookies
    """
    # build file URL
    ls_file_url = os.path.join(DS_PATH, fs_file)

    # extrai o filename
    ls_file_name = os.path.basename(fs_file)

    # logger
    M_LOG.info("Downloading: %s", str(ls_file_name))

    # request file
    lo_resp = requests.get(ls_file_url, cookies=f_cookies, allow_redirects=True, stream=True)
    '''
    if lo_resp.status_code != 200:
        # logger
        M_LOG.error("Erro no download: %s", str(lo_resp.text))
        # abort
        exit(1)
    '''
    # tamanho do arquivo
    li_filesize = int(lo_resp.headers["Content-length"])
    M_LOG.debug("li_filesize: %d", li_filesize)

    # abre o arquivo
    with open(ls_file_name, "wb") as lfh:
        # for all chunks in file... 
        for lchunk in lo_resp.iter_content(chunk_size=DI_CHUNK_SIZE):
            # grava o chunk no arquivo
            lfh.write(lchunk)

            # ainfa não terminou ?
            if DI_CHUNK_SIZE < li_filesize:
                # exibe o status atual
                check_file_status(ls_file_name, li_filesize)

# -------------------------------------------------------------------------------------------------
def download_FNL(fo_date, fi_tempo, fs_dir_fnl):
    """
    faz o download

    :param fo_date (ConfigParser): dados da data de previsão
    :param fi_tempo (int): tempo de previsão
    :param fs_dir_fnl (str): diretório de dados
    """
    # data início    
    ls_data_ini = fo_date["data_ini"]
    M_LOG.debug("ls_data_ini: %s", ls_data_ini)

    # strip data início
    ls_ano = ls_data_ini[0:4]
    ls_mes = ls_data_ini[4:6]
    ls_dia = ls_data_ini[6:8]
    M_LOG.debug("YMD: %s-%s-%s", ls_ano, ls_mes, ls_dia)

    # convert to datetime
    ldt_ini = datetime.datetime.strptime(ls_data_ini, "%Y%m%d")
    M_LOG.debug("ldt_ini: %s", str(ldt_ini))

    # diretório das FNLs
    ls_dir_fnl = os.path.join(fs_dir_fnl, ls_data_ini)
    M_LOG.debug("ls_dir_fnl: %s", ls_dir_fnl)
    
    # diretório das FNLs existe ?
    if not os.path.exists(ls_dir_fnl):
        # logger
        M_LOG.info("Criando diretório de fnl: %s", ls_dir_fnl)
        # cria o diretório das FNLs
        os.mkdir(ls_dir_fnl)

    # vai para o diretório das FNLs
    os.chdir(ls_dir_fnl)

    # authenticate
    lo_resp = requests.post(DS_URL, data=df.hc.DDCT_VALUES)

    if 200 != lo_resp.status_code:
        # logger
        M_LOG.error("Bad Authentication: %s", str(lo_resp.text))
        # abort
        exit(1)

    # tempo decorrido
    li_tempo_decorrido = 0
    # hora atual
    li_hora_atu = int(fo_date["hora_ini"])

    # enquanto durar...
    while li_tempo_decorrido <= fi_tempo:
        # hora atual (str)
        ls_hora = "{:0>2d}".format(li_hora_atu)

        # arquivo para download
        ls_file = f"grib2/{ls_ano}/{ls_ano}.{ls_mes}/fnl_{ls_data_ini}_{ls_hora}_00.grib2"
 
        # faz o download do arquivo
        _download_file(ls_file, lo_resp.cookies)

        # incrementa a hora atual
        li_hora_atu += df.DI_INTERVALO
        # incrementa o tempo decorrido
        li_tempo_decorrido += df.DI_INTERVALO
        M_LOG.debug("li_tempo_decorrido: %d", li_tempo_decorrido)

        # next day ?
        if li_hora_atu >= 24:
            # reseta hora atual
            li_hora_atu = 0
            # incrementa em 1 dia a data atual
            ldt_ini += datetime.timedelta(days=1)
            # converte para string
            ls_data_ini = ldt_ini.strftime("%Y%m%d")

            # strip dia, mês ano
            ls_ano = ls_data_ini[0:4]
            ls_mes = ls_data_ini[4:6]
            ls_dia = ls_data_ini[6:8]

# -------------------------------------------------------------------------------------------------
# this is the bootstrap process
    
if "__main__" == __name__:
    # logger
    logging.basicConfig(level=logging.DEBUG)
    
    # disable logging
    # logging.disable(sys.maxint)

    # sample
    ldct_date = {"data_ini":"20211112", "hora_ini":"12"}
    
    # run application
    download_FNL(ldct_date, 48)
    
# < the end >--------------------------------------------------------------------------------------
