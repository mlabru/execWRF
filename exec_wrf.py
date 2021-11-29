# -*- coding: utf-8 -*-
"""
execWRF

2021/nov  1.0  eliana   initial version (Linux/Python)
"""
# < imports >--------------------------------------------------------------------------------------

# python library
import configparser
import datetime
import glob
import logging
import os
import shutil
import subprocess
import sys

# local
import exc_defs as df
import exc_download as dwn
import exc_namelist as mnl

# < defines >--------------------------------------------------------------------------------------

# horas de início de previsão válidas
DLST_HORA_OK = [0, 6, 12, 18]
# tempos de previsão válidos
DLST_TEMPO_OK = [24, 48, 72]
# regiões válidas
DLST_REGIAO_OK = ["N", "SE"]

# < logging >--------------------------------------------------------------------------------------

# logger
M_LOG = logging.getLogger(__name__)
M_LOG.setLevel(logging.DEBUG)

# -------------------------------------------------------------------------------------------------
def adjust_config(fo_config, fs_cfg_pn, fo_date, fi_tempo, fs_regiao):
    """
    ajusta a configuração dos parâmetros de previsão

    :param fo_config (ConfigParser): dados de configuração
    :param fs_cfg_pn (str): pathname do arquivo de configuração
    :param fo_date (ConfigParser): dados da data de previsão
    :param fi_tempo (int): tempo de previsão
    :param fs_regiao (str): região
    """
    # calcula o valor de l_n_dx
    fo_config["CONFIG"]["l_n_dx"] = fo_config["CONFIG"]["p_dx"].replace(',', '')

    # WRF section
    l_wrf = fo_config["WRF"]
    assert l_wrf

    # horas de previsão
    l_wrf["horas"] = str(fi_tempo)
    l_wrf["intervalo"] = str(df.DI_INTERVALO)

    # recria o arquivo de configuração
    with open(fs_cfg_pn, 'w') as lfh:
        # grava no arquivo de configuração
        fo_config.write(lfh)

    # parser das variáveis de configuração
    ldt_ini = fo_date["data"]["data_ini"]

    # parser das variáveis de configuração
    li_hora_ini = int(fo_date["data"]["hora_ini"])

    # diretório dos executáveis
    l_wrf["dir_wrf_exec"] = os.path.join(l_wrf["dir_wrf"], l_wrf["dir_wrf_exec"])

    # diretório do FNL
    l_wrf["dir_fnl"] = os.path.join(l_wrf["dir_wrf"], l_wrf["dir_fnl"])
    # diretório do GFS
    # l_wrf["dir_gfs"] = os.path.join(l_wrf["dir_wrf"], l_wrf["dir_gfs"])
    # diretório do WPS
    l_wrf["dir_wps"] = os.path.join(l_wrf["dir_wrf"], l_wrf["dir_wps"])
    # diretório do ARW
    l_wrf["dir_arw"] = os.path.join(l_wrf["dir_wrf"], l_wrf["dir_arw"])
    # diretório do GEOG
    l_wrf["dir_wrf_geog"] = os.path.join(l_wrf["dir_wrf"], l_wrf["dir_wrf_geog"])

    # token
    ls_token = "{}.{}{:02d}{:02d}".format(fs_regiao, ldt_ini, li_hora_ini, fi_tempo)

    # diretório de saída
    l_wrf["dir_out"] = os.path.join(l_wrf["dir_wrf"], l_wrf["dir_out"], f"wrf.{ls_token}")

    # diretório do log
    l_wrf["dir_log"] = os.path.join(l_wrf["dir_wrf"], l_wrf["dir_log"], f"wrf.{ls_token}")

# -------------------------------------------------------------------------------------------------
def arg_parse():
    """
    parser dos parâmetros de entrada

    :returns: arguments
    """
    # number of parameters
    if len(sys.argv) < 7:
        # avisa e aborta
        print_usage(f"Número de argumentos inválido: {len(sys.argv)}")

    # ano para previsão
    li_ano_ini = int(sys.argv[1]) if sys.argv[1].isdigit() else print_usage(f"Erro no ano: {sys.argv[1]}")

    # mes para previsão
    li_mes_ini = int(sys.argv[2]) if sys.argv[2].isdigit() else print_usage(f"Erro no mês: {sys.argv[2]}")
    li_mes_ini = li_mes_ini if 1 <= li_mes_ini <= 12 else print_usage(f"Erro: mês ({li_mes_ini}) inválido.")

    # dia para previsão
    li_dia_ini = int(sys.argv[3]) if sys.argv[3].isdigit() else print_usage(f"Erro no dia: {sys.argv[3]}")
    li_dia_ini = li_dia_ini if 1 <= li_dia_ini <= 31 else print_usage(f"Erro: dia ({li_dia_ini}) inválido.")

    # início para previsão
    li_hora_ini = int(sys.argv[4]) if sys.argv[4].isdigit() else print_usage(f"Erro na hora: {sys.argv[4]}")
    li_hora_ini = li_hora_ini if li_hora_ini in DLST_HORA_OK else print_usage(f"Erro: hora ({li_hora_ini}) inválida.")

    # tempo de previsão
    li_tempo = int(sys.argv[5]) if sys.argv[5].isdigit() else print_usage(f"Erro no tempo: {sys.argv[5]}")
    li_tempo = li_tempo if li_tempo in DLST_TEMPO_OK else print_usage(f"Erro: tempo ({li_tempo}) inválida.")

    # região de previsão
    ls_regiao = str(sys.argv[6]).strip().upper() if sys.argv[6].isalpha() else print_usage(f"Erro na região: {sys.argv[6]}")
    ls_regiao = ls_regiao if ls_regiao in DLST_REGIAO_OK else print_usage(f"Erro: região ({ls_regiao}) inválida.")

    # calcula a data final (data inicial + horas de previsão):
    ldt_final = datetime.datetime(li_ano_ini, li_mes_ini, li_dia_ini, li_hora_ini, 0, 0) + datetime.timedelta(hours=li_tempo)

    # cria configuração de data e hora
    lo_date = configparser.ConfigParser()
    assert lo_date

    # create data section
    lo_date["data"] = {}

    # data section
    ldct_date = lo_date["data"]
    ldct_date["data_ini"] = "{:4d}{:02d}{:02d}".format(li_ano_ini, li_mes_ini, li_dia_ini)
    ldct_date["ano_ini"] = "{:4d}".format(li_ano_ini)
    ldct_date["mes_ini"] = "{:02d}".format(li_mes_ini)
    ldct_date["dia_ini"] = "{:02d}".format(li_dia_ini)
    ldct_date["hora_ini"] = "{:02d}".format(li_hora_ini)
    ldct_date["data_final"] = "{}".format(datetime.datetime.strftime(ldt_final, "%Y%m%d"))
    ldct_date["ano_final"] = "{:4d}".format(ldt_final.year)
    ldct_date["mes_final"] = "{:02d}".format(ldt_final.month)
    ldct_date["dia_final"] = "{:02d}".format(ldt_final.day)
    ldct_date["hora_final"] = "{:02d}".format(ldt_final.hour)

    # cria arquivo de configuração de data e hora
    with open(os.path.join(df.DS_WRF_HOME, "data.conf"), 'w') as lfh:
        # grava todas as informações de data e hora em arquivo
        lo_date.write(lfh)

    # return
    return lo_date, li_tempo, ls_regiao

# -------------------------------------------------------------------------------------------------
def load_config(fs_regiao):
    """
    configura o parser de leitura do wrf.conf
    """
    # diretório base (PATH) de execução (onde estão os arquivos de configuração)
    ls_path = df.DS_WRF_HOME if df.DS_WRF_HOME else os.path.dirname(os.path.realpath(__file__))

    # pathname do arquivo de configuração
    ls_cfg_pn = os.path.join(ls_path, f"wrf_{fs_regiao}.conf")

    # arquivo de configuração exists ?
    if not os.path.exists(ls_cfg_pn):
        # logger
        M_LOG.error("Não foi encontrado o arquivo de configuração: %s.", ls_cfg_pn)
        # abort
        sys.exit(1)

    # cria o parser de configuração
    lo_config = configparser.ConfigParser()
    assert lo_config

    # lê o arquivo de configuração
    lo_config.read(ls_cfg_pn)

    # WRF path
    lo_config["WRF"]["dir_wrf"] = ls_path

    # return
    return lo_config, ls_cfg_pn

# -------------------------------------------------------------------------------------------------
def print_usage(fs_msg):
    """
    imprime na tela os argumentos de entrada válidos
    """
    # error message ?
    if fs_msg:
        # print error message
        print(fs_msg)

    # usage message
    print()
    print("Entre com os argumentos: <AAAA> <MM> <DD> <INÍCIO> <TEMPO> <REGIÃO> [E-MAIL]")
    print("    AAAA   = Ano")
    print("    MM     = Mês (01..12)")
    print("    DD     = Dia (01..31)")
    print("    HH     = Hora (00..23)")
    print("    INÍCIO = Hora de início da previsão ({})".format(DLST_HORA_OK))
    print("    TEMPO  = Tempo de previsão ({})".format(DLST_TEMPO_OK))
    print("    REGIÃO = Região ({})".format(DLST_REGIAO_OK))
    print("    E-MAIL = E-mail para resposta (opcional)")

    # abort
    sys.exit(1)

# -------------------------------------------------------------------------------------------------
def process_ARW(fo_config, fo_date):
    """
    processa ARWpost:
    - cria namelist.ARWpost
    - executa ARWpost para o número de domínios definidos em wrf.conf

    :param fo_config (ConfigParser): dados de configuração
    :param fo_date (ConfigParser): dados da data de previsão
    """
    # logger
    M_LOG.info("Início do ARWpost: %s.", str(datetime.datetime.now()))

    # WRF section
    l_wrf = fo_config["WRF"]
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
    for li_dom in (1, int(fo_config["CONFIG"]["p_maxdom"])):
        # logger
        M_LOG.info("Criando namelist ARWpost: namelist.ARWpost D0%d", li_dom)

        # cria namelist.ARWpost
        mnl.cria_namelist_ARWPost("namelist.ARWpost", fo_config, fo_date, li_dom)

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
                # logger
                M_LOG.debug("movendo: %s", lfile)
                # move os arquivos gerados para o diretório de saída
                shutil.move(lfile, os.path.join(ls_dir_out, os.path.basename(lfile)))

        # em caso de erro,...
        except subprocess.CalledProcessError:
            # logger
            M_LOG.error("Erro ao executar ARWpost.exe")
            # abort
            sys.exit(1)

    # for all wrfout files...
    for lfile in glob.glob("wrfout*"):
        # logger
        M_LOG.debug("removendo: %s", lfile)
        # remove file
        os.remove(lfile)

# -------------------------------------------------------------------------------------------------
def process_WPS(fo_config, fs_cfg_pn, fo_date):
    """
    processa WPS:
    - cria o arquivo namelist.wps
    - geogrid.exe => link_grib.csh => ungrib.exe => metgrid.exe
    - remove os arquivos que não serão utilizados

    :param fo_config (ConfigParser): dados de configuração
    :param fs_cfg_pn (str): pathname do arquivo de configuração
    :param fo_date (ConfigParser): dados da data de previsão
    """
    # logger
    M_LOG.info("Início do WPS: %s.", str(datetime.datetime.now()))

    # WRF section
    l_wrf = fo_config["WRF"]
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
    '''
    # diretório do GFS
    ls_dir_gfs = l_wrf["dir_gfs"]

    # diretório dos arquivos GFS existe ?
    if not os.path.exists(ls_dir_gfs):
        # logger
        M_LOG.info("Criando diretório do GFS: %s", ls_dir_gfs)
        # cria diretório do GFS
        os.makedirs(ls_dir_gfs)
    '''
    # logger
    M_LOG.info("Removendo arquivos temporários anteriores.")

    # vai para o diretório dos executáveis do WRF
    os.chdir(l_wrf["dir_wrf_exec"])

    # para todos os arquivos de trabalho do WRF...
    for lfile in glob.glob("met_*"):
        # logger
        M_LOG.debug("removendo: %s", lfile)
        # remove o arquivo
        os.remove(lfile)

    # vai para o diretório de execução do WPS
    os.chdir(l_wrf["dir_wps"])

    # for all temp files...
    for ls_tmp in ["GFS*", "geo_em*", "PFILE*", "FILE*", "GRIBFILE*"]:
        # for all files with extension...
        for lfile in glob.glob(ls_tmp):
            # logger
            M_LOG.debug("removendo: %s", lfile)
            # remove o arquivo
            os.remove(lfile)

    # logger
    M_LOG.info("Criando namelist WPS: namelist.wps")

    # cria namelist.wps
    mnl.cria_namelist_WPS("namelist.wps", fo_config, fo_date)

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
        M_LOG.error("Erro na execução do geogrid.exe")
        # abort
        sys.exit(1)

    # data de início da previsão
    ldt_ini = fo_date["data"]["data_ini"]

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
        M_LOG.error("Erro na execução de link_grib.csh")
        # abort
        sys.exit(1)

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
        M_LOG.error("Erro ao executar ungrib.exe")
        # abort
        sys.exit(1)

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
        M_LOG.error("Erro ao executar metgrid.exe")
        # abort
        sys.exit(1)

    # logger
    M_LOG.info("(Re)movendo arquivos temporários.")

    # for all temp files...
    for ls_tmp in ["GFS*", "geo_em*", "PFILE*", "FILE*", "GRIBFILE*"]:
        # for all files with extension...
        for lfile in glob.glob(ls_tmp):
            # logger
            M_LOG.debug("removendo: %s", lfile)
            # remove o arquivo
            os.remove(lfile)

    # for all log files...
    for lfile in glob.glob("*.log"):
        # logger
        M_LOG.debug("copiando: %s", lfile)
        # move os arquivos de log do WPS para o diretório de log
        shutil.copy(lfile, ls_dir_log)

# -------------------------------------------------------------------------------------------------
def process_WRF(fo_config, fo_date):
    """
    processa WRF:
    - real.exe => wrf.exe => move wrfout_* para diretorio ARWPost
    - remove os arquivos que não serão utilizados

    :param fo_config (ConfigParser): dados de configuração
    :param fo_date (ConfigParser): dados da data de previsão
    """
    # logger
    M_LOG.info("Início do WRF: %s.", str(datetime.datetime.now()))

    # WRF section
    l_wrf = fo_config["WRF"]
    assert l_wrf

    # cria diretório de log
    ls_dir_log = l_wrf["dir_log"]

    # vai para o diretório de execução do WRF
    os.chdir(l_wrf["dir_wrf_exec"])

    # logger
    M_LOG.info("Criando namelist WRF: namelist.input")

    # cria namelist.input
    mnl.cria_namelist_WRF("namelist.input", fo_config, fo_date)

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
        M_LOG.error("Erro ao executar real.exe")
        # for all rsl.error files...
        for lfile in glob.glob("rsl.error.*"):
            # logger
            M_LOG.debug("movendo: %s", lfile)
            # salva o log do erro
            shutil.move(lfile, os.path.join(ls_dir_log, lfile))
        # abort
        sys.exit(1)

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
        M_LOG.error("Erro ao executar wrf.exe")
        # for all rsl.error files...
        for lfile in glob.glob("rsl.error.*"):
            # logger
            M_LOG.debug("movendo: %s", lfile)
            # salva o log do erro
            shutil.move(lfile, os.path.join(ls_dir_log, lfile))
        # abort
        sys.exit(1)

    # logger
    M_LOG.info("(Re)movendo arquivos temporários.")

    # for all wrfout files...
    for lfile in glob.glob("wrfout_*"):
        # logger
        M_LOG.debug("movendo: %s", lfile)
        # move os arquivos de saída wrfout_* para o diretório do ARWPost
        shutil.move(lfile, os.path.join(l_wrf["dir_arw"], lfile))

    # for all met*.nc files...
    for lfile in glob.glob("met*.nc"):
        # logger
        M_LOG.debug("removendo: %s", lfile)
        # remove file
        os.remove(lfile)

# -------------------------------------------------------------------------------------------------
def main():
    """
    drive app
    """
    # check parameters
    lo_date, li_tempo, ls_regiao = arg_parse()

    # load config file
    lo_config, ls_cfg_pn = load_config(ls_regiao)
    assert lo_config

    # adjust config parameters
    adjust_config(lo_config, ls_cfg_pn, lo_date, li_tempo, ls_regiao)

    # logger
    M_LOG.info("Início do download: %s.", str(datetime.datetime.now()))

    # download dos arquivos FNL
    dwn.download_FNL(lo_date, li_tempo, lo_config["WRF"]["dir_fnl"])

    # process WPS
    process_WPS(lo_config, ls_cfg_pn, lo_date)
    # process WRF
    process_WRF(lo_config, lo_date)
    # process ARWPost
    process_ARW(lo_config, lo_date)

    # logger
    M_LOG.info("Fim de execução !")

# -------------------------------------------------------------------------------------------------
# this is the bootstrap process

if "__main__" == __name__:
    # logger
    logging.basicConfig(filename="wrf.log",
                        filemode='w',
                        datefmt="%d/%m/%Y %H:%M",
                        format="%(asctime)s %(message)s",
                        level=logging.DEBUG)

    # disable logging
    # logging.disable(sys.maxint)

    # run application
    main()

# < the end >--------------------------------------------------------------------------------------
