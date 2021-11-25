# -*- coding: utf-8 -*-
""" 
download_fnl

2021/nov  1.0  eliana   initial version (Linux/Python)
"""
# < imports >--------------------------------------------------------------------------------------

# python library
import datetime
import logging
import os
import requests
import sys

# < defines >--------------------------------------------------------------------------------------

DS_URL = "https://rda.ucar.edu/cgi-bin/login"
DDCT_VALUES = {"email":"pgiriart@gmail.com", "passwd":"R0mLnAoB", "action":"login"}
DS_PATH = "https://rda.ucar.edu/data/ds083.2"
DS_WRF_HOME = "/home/mlabru/works_lpd/mlabru/Works/wrk.icea/Public/05.prj.met/02.git.met/WRF"

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
def _download(fs_file, f_cookies):
    """
    faz o download
    """
    # build file URL
    ls_file_url = os.path.join(DS_PATH, fs_file)

    # extrai o filename
    ls_file_name = os.path.basename(fs_file)

    # logger
    M_LOG.debug("Downloading: %s", str(ls_file_name))

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
    print("li_filesize", li_filesize)

    # abre o arquivo
    with open(ls_file_name, "wb") as lfh:
        # chunk size
        chunk_size = 1048576

        # for all chunks in file... 
        for chunk in lo_resp.iter_content(chunk_size=chunk_size):
            # grava o chunk no arquivo
            lfh.write(chunk)
            # ainfa não terminou ?
            if chunk_size < li_filesize:
                # exibe o status atual
                check_file_status(ls_file_name, li_filesize)

# -------------------------------------------------------------------------------------------------
def download_FNL(fo_date, fi_duracao):
    """
    faz o download
    """
    # data início    
    ls_data_ini = fo_date["data_ini"]
    print("ls_data_ini", ls_data_ini)

    # strip data início
    ls_ano = ls_data_ini[0:4]
    ls_mes = ls_data_ini[4:6]
    ls_dia = ls_data_ini[6:8]
    print("AMD", ls_ano, ls_mes, ls_dia)

    # convert to datetime
    ldt_ini = datetime.datetime.strptime(ls_data_ini, "%Y%m%d")
    print("ldt_ini", ldt_ini)

    # diretório das FNLs
    ls_fnl_dir = os.path.join(DS_WRF_HOME, "data/fnl", ls_data_ini)
    print("ls_fnl_dir", ls_fnl_dir)
    
    # diretório das FNLs existe ?
    if not os.path.exists(ls_fnl_dir):
        # cria o diretório das FNLs
        os.mkdir(ls_fnl_dir)

    # vai para o diretório das FNLs
    os.chdir(ls_fnl_dir)

    # authenticate
    lo_resp = requests.post(DS_URL, data=DDCT_VALUES)

    if lo_resp.status_code != 200:
        # logger
        M_LOG.error("Bad Authentication: %s", str(lo_resp.text))
        # abort
        exit(1)

    # tempo decorrido
    li_tempo_decorrido = 0
    # hora atual
    li_hora_atu = int(fo_date["hora_ini"])

    # enquanto durar...
    while li_tempo_decorrido <= fi_duracao:
        # hora atual (str)
        ls_hora = "{:0>2d}".format(li_hora_atu)

        # arquivo para download
        ls_file = f"grib2/{ls_ano}/{ls_ano}.{ls_mes}/fnl_{ls_data_ini}_{ls_hora}_00.grib2"
 
        # faz o download do arquivo
        _download(ls_file, lo_resp.cookies)

        # incrementa a hora atual
        li_hora_atu += 6
        # incrementa o tempo decorrido
        li_tempo_decorrido += 6
        print("li_tempo_decorrido", li_tempo_decorrido)

        # next day ?
        if li_hora_atu >= 24:
            # reset hora atual
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

    ldct_date = {"data_ini":"20211124", "hora_ini":"12"}
    
    # run application
    download_FNL(ldct_date, 24)
    
# < the end >--------------------------------------------------------------------------------------
