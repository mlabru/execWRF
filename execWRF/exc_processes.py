# -*- coding: utf-8 -*-
"""
exc_processes

2022/apr  1.1  mlabru  graylog log management
2021/nov  1.0  eliana  initial version (Linux/Python)
"""
# < imports >----------------------------------------------------------------------------------

# python library
import datetime
import glob
import logging
import os
import shutil
import subprocess
import sys

# graylog
import graypy

# local
import exc_defs as df
import exc_namelist as mnl

# < logging >----------------------------------------------------------------------------------

# logger
M_LOG = logging.getLogger(__name__)
M_LOG.setLevel(df.DI_LOG_LEVEL)

# graylog handler
M_GLH = graypy.GELFUDPHandler("localhost", 12201)
M_LOG.addHandler(M_GLH)

# ---------------------------------------------------------------------------------------------
def process_all(fo_cfg_parser, fo_forecast_date, fs_token):
    """
    process all stages
    """
    # logger
    M_LOG.debug("process_all >>")

    # process WPS
    process_WPS(fo_cfg_parser, fo_forecast_date)
    # process WRF
    process_WRF(fo_cfg_parser, fo_forecast_date)
    # process ARWPost
    process_ARW(fo_cfg_parser, fo_forecast_date, fs_token)

# ---------------------------------------------------------------------------------------------
def process_ARW(fo_cfg_parser, fo_forecast_date, fs_token):
    """
    processa ARWpost:
    - cria namelist.ARWpost
    - executa ARWpost para o número de domínios definidos em wrf.conf

    :param fo_cfg_parser (ConfigParser): dados de configuração
    :param fo_forecast_date (ConfigParser): dados da data de previsão
    :param fs_token (str): forecast id
    """
    # logger
    M_LOG.debug("process_ARW >>")

    # logger
    M_LOG.info("Início do ARWpost: %s.", str(datetime.datetime.now()))

    # WRF section
    l_wrf = fo_cfg_parser["WRF"]
    assert l_wrf

    # cria diretório de log
    ls_dir_log = l_wrf["dir_log"]
    # diretório do ARW
    ls_dir_arw = l_wrf["dir_arw"]
    # diretório de saída
    ls_dir_out = l_wrf["dir_out"]

    # vai para o diretório dos executáveis do ARWpost
    os.chdir(ls_dir_arw)

    # para todos os domínios...
    for li_dom in range(1, int(fo_cfg_parser["CONFIG"]["p_maxdom"]) + 1):
        # logger
        M_LOG.info("Criando namelist ARWpost: namelist.ARWpost D0%d", li_dom)

        # cria namelist.ARWpost
        mnl.cria_namelist_ARWPost("namelist.ARWpost", fo_cfg_parser, fo_forecast_date, li_dom)

        # logger
        M_LOG.info("Execução do ARWpost.exe para o domínio %d", li_dom)
        try:
            # executa ARWpost.exe
            ls_res = subprocess.check_output("./ARWpost.exe", shell=True).decode(sys.stdout.encoding)

            # create output file
            with open(os.path.join(ls_dir_log, f"arwpostD{li_dom}.out"), 'w') as lfh:
                # save output
                lfh.writelines(ls_res)

            # for all arquivos de saida...
            for lfile in glob.glob(f"wrfd{li_dom}*"):
                # move os arquivos gerados para o diretório de saída
                shutil.move(lfile, os.path.join(ls_dir_out, os.path.basename(lfile)))

            # create file with output directory
            with open(os.path.join("/tmp", fs_token), 'w') as lfh:
                # save output
                lfh.writelines(ls_dir_out)

        # em caso de erro,...
        except subprocess.CalledProcessError:
            # logger
            M_LOG.error("Erro ao executar ARWpost.exe", exc_info=1)
            # abort
            sys.exit(-1)

    # for all wrfout files...
    for lfile in glob.glob("wrfout*"):
        # remove file
        os.remove(lfile)

# ---------------------------------------------------------------------------------------------
def process_WPS(fo_cfg_parser, fo_forecast_date):
    """
    processa WPS:
    - cria o arquivo namelist.wps
    - geogrid.exe => link_grib.csh => ungrib.exe => metgrid.exe
    - remove os arquivos que não serão utilizados

    :param fo_cfg_parser (ConfigParser): dados de configuração
    :param fo_forecast_date (ConfigParser): dados da data de previsão
    """
    # logger
    M_LOG.debug("process_WPS >>")

    # logger
    M_LOG.info("Início do WPS: %s.", str(datetime.datetime.now()))

    # WRF section
    l_wrf = fo_cfg_parser["WRF"]
    assert l_wrf

    # cria diretório de log
    ls_dir_log = l_wrf["dir_log"]

    # diretório de log existe ?
    if not os.path.exists(ls_dir_log):
        # logger
        M_LOG.info("Criando diretório de log: %s", ls_dir_log)
        # cria diretório de log
        os.makedirs(ls_dir_log)

    # diretório de saída
    ls_dir_out = l_wrf["dir_out"]

    # diretório de saída existe ?
    if not os.path.exists(ls_dir_out):
        # logger
        M_LOG.info("Criando diretório de saída: %s", ls_dir_out)
        # cria diretório de saída
        os.makedirs(ls_dir_out)

    # logger
    M_LOG.info("Removendo arquivos temporários anteriores.")

    # vai para o diretório dos executáveis do WRF
    os.chdir(l_wrf["dir_wrf_exec"])

    # para todos os arquivos de trabalho do WRF...
    for lfile in glob.glob("met_*"):
        # remove o arquivo
        os.remove(lfile)

    # vai para o diretório de execução do WPS
    os.chdir(l_wrf["dir_wps"])

    # for all temp files...
    for ls_tmp in ["GFS*", "geo_em*", "PFILE*", "FILE*", "GRIBFILE*"]:
        # for all files with extension...
        for lfile in glob.glob(ls_tmp):
            # remove o arquivo
            os.remove(lfile)

    # logger
    M_LOG.info("Criando namelist WPS: namelist.wps")

    # cria namelist.wps
    mnl.cria_namelist_WPS("namelist.wps", fo_cfg_parser, fo_forecast_date)

    # logger
    M_LOG.info("Execução do geogrid.exe")
    try:
        # executa geogrid.exe
        ls_res = subprocess.check_output("./geogrid.exe", shell=True).decode(sys.stdout.encoding)

        # create output file
        with open(os.path.join(ls_dir_log, "geogrid.out"), 'w') as lfh:
            # save output
            lfh.writelines(ls_res)

    # em caso de erro,...
    except subprocess.CalledProcessError:
        # logger
        M_LOG.error("Erro na execução do geogrid.exe", exc_info=1)
        # abort
        sys.exit(-1)

    # data de início da previsão
    ldt_ini = fo_forecast_date["data"]["data_ini"]

    # logger
    M_LOG.info("Criando links dos arquivos FNL")
    try:
        # comando
        ls_cmd_exe = "./link_grib.csh " + os.path.join(l_wrf["dir_fnl"], "*")
        # executa link_grib.csh
        ls_res = subprocess.check_output(ls_cmd_exe, shell=True).decode(sys.stdout.encoding)

    # em caso de erro,...
    except subprocess.CalledProcessError:
        # logger
        M_LOG.error("Erro na execução de link_grib.csh", exc_info=1)
        # abort
        sys.exit(-1)

    # logger
    M_LOG.info("Execução do ungrib.exe")
    try:
        # executa ungrib.exe
        ls_res = subprocess.check_output("./ungrib.exe", shell=True).decode(sys.stdout.encoding)

        # create output file
        with open(os.path.join(ls_dir_log, "ungrib.out"), 'w') as lfh:
            # save output
            lfh.writelines(ls_res)

    # em caso de erro,...
    except subprocess.CalledProcessError:
        # logger
        M_LOG.error("Erro ao executar ungrib.exe", exc_info=1)
        # abort
        sys.exit(-1)

    # logger
    M_LOG.info("Execução do metgrid.exe")
    try:
        # executa metgrid.exe
        ls_res = subprocess.check_output("./metgrid.exe", shell=True).decode(sys.stdout.encoding)

        # create output file
        with open(os.path.join(ls_dir_log, "metgrid.out"), 'w') as lfh:
            # save output
            lfh.writelines(ls_res)

    # em caso de erro,...
    except subprocess.CalledProcessError:
        # logger
        M_LOG.error("Erro ao executar metgrid.exe", exc_info=1)
        # abort
        sys.exit(-1)

    # logger
    M_LOG.info("(Re)movendo arquivos temporários.")

    # for all temp files...
    for ls_tmp in ["GFS*", "geo_em*", "PFILE*", "FILE*", "GRIBFILE*"]:
        # for all files with extension...
        for lfile in glob.glob(ls_tmp):
            # remove o arquivo
            os.remove(lfile)

    # for all log files...
    for lfile in glob.glob("*.log"):
        # move os arquivos de log do WPS para o diretório de log
        shutil.copy(lfile, ls_dir_log)

# ---------------------------------------------------------------------------------------------
def process_WRF(fo_cfg_parser, fo_forecast_date):
    """
    processa WRF:
    - real.exe => wrf.exe => move wrfout_* para diretorio ARWPost
    - remove os arquivos que não serão utilizados

    :param fo_cfg_parser (ConfigParser): dados de configuração
    :param fo_forecast_date (ConfigParser): dados da data de previsão
    """
    # logger
    M_LOG.debug("process_WRF >>")

    # logger
    M_LOG.info("Início do WRF: %s.", str(datetime.datetime.now()))

    # WRF section
    l_wrf = fo_cfg_parser["WRF"]
    assert l_wrf

    # diretório de log
    ls_dir_log = l_wrf["dir_log"]

    # vai para o diretório de execução do WRF
    os.chdir(l_wrf["dir_wrf_exec"])

    # logger
    M_LOG.info("Criando namelist WRF: namelist.input")

    # cria namelist.input
    mnl.cria_namelist_WRF("namelist.input", fo_cfg_parser, fo_forecast_date)

    # logger
    M_LOG.info("Execução do real.exe")
    try:
        # executa real.exe
        ls_res = subprocess.check_output("./real.exe", shell=True).decode(sys.stdout.encoding)

        # create output file
        with open(os.path.join(ls_dir_log, "real.out"), 'w') as lfh:
            # save output
            lfh.writelines(ls_res)

    # em caso de erro,...
    except subprocess.CalledProcessError:
        # logger
        M_LOG.error("Erro ao executar real.exe", exc_info=1)
        # for all rsl.error files...
        for lfile in glob.glob("rsl.error.*"):
            # salva o log do erro
            shutil.move(lfile, os.path.join(ls_dir_log, lfile))
        # abort
        sys.exit(-1)

    # logger
    M_LOG.info("Execução do wrf.exe")
    try:
        # comando
        # ls_cmd_exe = "mpirun -np 24 ./wrf.exe"
        ls_cmd_exe = "mpirun --use-hwthread-cpus -np 7 ./wrf.exe"

        # executa o WRF com multiprocessamento (mpirun)
        ls_res = subprocess.check_output(ls_cmd_exe, shell=True).decode(sys.stdout.encoding)

        # create output file
        with open(os.path.join(ls_dir_log, "wrf.out"), 'w') as lfh:
            # save output
            lfh.writelines(ls_res)

    # em caso de erro,...
    except subprocess.CalledProcessError:
        # logger
        M_LOG.error("Erro ao executar wrf.exe", exc_info=1)
        # for all rsl.error files...
        for lfile in glob.glob("rsl.error.*"):
            # salva o log do erro
            shutil.move(lfile, os.path.join(ls_dir_log, lfile))
        # abort
        sys.exit(-1)

    # logger
    M_LOG.info("(Re)movendo arquivos temporários.")

    # for all wrfout files...
    for lfile in glob.glob("wrfout_*"):
        # move os arquivos de saída wrfout_* para o diretório do ARWPost
        shutil.move(lfile, os.path.join(l_wrf["dir_arw"], lfile))

    # for all met*.nc files...
    for lfile in glob.glob("met*.nc"):
        # remove file
        os.remove(lfile)

# < the end >----------------------------------------------------------------------------------
