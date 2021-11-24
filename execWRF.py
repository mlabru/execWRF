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
import downloadFNL as dwn
import make_namelist_DA as mnl

# < defines >--------------------------------------------------------------------------------------

# WFR home dir
DS_WRF_HOME = "/home/webpca/WRF"
DS_WRF_HOME = "/home/mlabru/works_lpd/mlabru/Works/wrk.icea/Public/05.prj.met/02.git.met/WRF"
DS_WRF_HOME = "/media/mlabru/works_lpd/mlabru/Works/wrk.icea/Public/05.prj.met/02.git.met/WRF"
DS_WRF_HOME = "/home/mlabru/Public/met/WRF"

# < logging >--------------------------------------------------------------------------------------

# logger
M_LOG = logging.getLogger(__name__)
M_LOG.setLevel(logging.DEBUG)

# -------------------------------------------------------------------------------------------------
def adjust_config(f_config, fs_cfg_pn, f_data, fi_hora_prev, fs_regiao):
    """
    ajusta a configuração dos parâmetros de previsão

    :param f_config (ConfigParser): dados de configuração
    :param fs_cfg_pn (str): pathname do arquivo de configuração
    :param f_data (ConfigParser): dados da data de previsão
    :param fi_hora_prev (int): tempo de previsão
    :param fs_regiao (str): região
    """
    # calcula o valor de l_n_dx
    f_config["CONFIG"]["l_n_dx"] = f_config["CONFIG"]["p_dx"].replace(',', '')

    # WRF section
    l_wrf = f_config["WRF"]
    assert l_wrf
    
    # horas de previsão
    l_wrf["horas"] = str(fi_hora_prev)
    l_wrf["intervalo"] = '6'

    # recria o arquivo de configuração
    with open(fs_cfg_pn, 'w') as lfh:
        # grava no arquivo de configuração 
        f_config.write(lfh)

    # parser das variáveis de configuração
    ldt_ini = f_data["data"]["data_ini"]

    # diretório dos executáveis
    l_wrf["dir_wrf_exec"] = os.path.join(l_wrf["dir_wrf"], l_wrf["dir_wrf_exec"])

    # diretório do GFS
    l_wrf["dir_gfs"] = os.path.join(l_wrf["dir_wrf"], l_wrf["dir_gfs"])
    # diretório do WPS
    l_wrf["dir_wps"] = os.path.join(l_wrf["dir_wrf"], l_wrf["dir_wps"])
    # diretório do ARW
    l_wrf["dir_arw"] = os.path.join(l_wrf["dir_wrf"], l_wrf["dir_arw"])

    # diretório de saída
    l_wrf["dir_out"] = os.path.join(l_wrf["dir_wrf"], l_wrf["dir_out"], f"wrf.{fs_regiao}.{ldt_ini}")

    # diretório do log
    l_wrf["dir_log"] = os.path.join(l_wrf["dir_wrf"], l_wrf["dir_log"], f"wrf.{fs_regiao}.{ldt_ini}")

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
    l_ano_ini = int(sys.argv[1]) if sys.argv[1].isdigit() else print_usage(f"Erro no ano: {sys.argv[1]}")

    # mes para previsão
    l_mes_ini = int(sys.argv[2]) if sys.argv[2].isdigit() else print_usage(f"Erro no mês: {sys.argv[2]}")
    l_mes_ini = l_mes_ini if 1 <= l_mes_ini <= 12 else print_usage(f"Erro: mês ({l_mes_ini}) inválido.")

    # dia para previsão
    l_dia_ini = int(sys.argv[3]) if sys.argv[3].isdigit() else print_usage(f"Erro no dia: {sys.argv[3]}")
    l_dia_ini = l_dia_ini if 1 <= l_dia_ini <= 31 else print_usage(f"Erro: dia ({l_dia_ini}) inválido.")

    # início para previsão
    l_hora_ini = int(sys.argv[4]) if sys.argv[4].isdigit() else print_usage(f"Erro na hora: {sys.argv[4]}")
    l_hora_ini = l_hora_ini if l_hora_ini in [0, 6, 12, 18] else print_usage(f"Erro: hora ({l_hora_ini}) inválida.")

    # tempo de previsão
    l_hora_prev = int(sys.argv[5]) if sys.argv[5].isdigit() else print_usage(f"Erro no tempo: {sys.argv[5]}")
    l_hora_prev = l_hora_prev if l_hora_prev in [24, 48, 72] else print_usage(f"Erro: tempo ({l_hora_prev}) inválida.")

    # região de previsão
    l_regiao = str(sys.argv[6]).strip().upper() if sys.argv[6].isalpha() else print_usage(f"Erro na região: {sys.argv[6]}")
    l_regiao = l_regiao if l_regiao in ["N", "SE"] else print_usage(f"Erro: região ({l_regiao}) inválida.")

    # calcula a data final (data inicial + horas de previsão):
    ldt_final = datetime.datetime(l_ano_ini, l_mes_ini, l_dia_ini, l_hora_ini, 0, 0) + datetime.timedelta(hours=l_hora_prev)

    # cria configuração de data e hora
    l_data = configparser.ConfigParser()
    assert l_data

    # create data section
    l_data["data"] = {}

    # data section
    l_dt_sect = l_data["data"]
    l_dt_sect["data_ini"] = "{:4d}{:02d}{:02d}".format(l_ano_ini, l_mes_ini, l_dia_ini)
    l_dt_sect["ano_ini"] = "{:4d}".format(l_ano_ini)
    l_dt_sect["mes_ini"] = "{:02d}".format(l_mes_ini) 
    l_dt_sect["dia_ini"] = "{:02d}".format(l_dia_ini)
    l_dt_sect["hora_ini"] = "{:02d}".format(l_hora_ini)
    l_dt_sect["data_final"] = "{}".format(datetime.datetime.strftime(ldt_final, "%Y%m%d"))
    l_dt_sect["ano_final"] = "{:4d}".format(ldt_final.year)
    l_dt_sect["mes_final"] = "{:02d}".format(ldt_final.month)
    l_dt_sect["dia_final"] = "{:02d}".format(ldt_final.day)
    l_dt_sect["hora_final"] = "{:02d}".format(ldt_final.hour)

    # cria arquivo de configuração de data e hora
    with open(os.path.join(DS_WRF_HOME, "data.conf"), 'w') as lfh:
        # grava todas as informações de data e hora em arquivo
        l_data.write(lfh)

    # return
    return l_data, l_hora_prev, l_regiao

# -------------------------------------------------------------------------------------------------
def load_config(fs_regiao):
    """
    configura o parser de leitura do wrf.conf
    """
    # diretório base (PATH) de execução (onde estão os arquivos de configuração)
    ls_path = DS_WRF_HOME if DS_WRF_HOME else os.path.dirname(os.path.realpath(__file__))

    # pathname do arquivo de configuração
    ls_cfg_pn = os.path.join(ls_path, f"wrf_{fs_regiao}.conf")

    # arquivo de configuração exists ?
    if not os.path.exists(ls_cfg_pn):
        # logger
        M_LOG.error("Não foi encontrado o arquivo de configuração: %s.", ls_cfg_pn)
        # abort
        sys.exit(1)

    # cria o parser de configuração
    l_config = configparser.ConfigParser()
    assert l_config

    # lê o arquivo de configuração
    l_config.read(ls_cfg_pn)

    # WRF path
    l_config["WRF"]["dir_wrf"] = ls_path

    # return
    return l_config, ls_cfg_pn

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
    print("    INÍCIO = Hora de início da previsão (00|06|12|18)")
    print("    TEMPO  = Tempo de previsão (24|48|72)")
    print("    REGIÃO = Região (N|SE)")
    print("    E-MAIL = E-mail para resposta (opcional)")
  
    # abort
    sys.exit(1)
    
# -------------------------------------------------------------------------------------------------
def process_ARW(f_config, f_data):
    """
    processa ARWpost:
    - cria namelist.ARWpost
    - executa ARWpost para o número de domínios definidos em wrf.conf

    :param f_config (ConfigParser): dados de configuração
    :param f_data (ConfigParser): dados da data de previsão
    """
    # logger
    M_LOG.info("Início do ARWpost: %s.", str(datetime.datetime.now()))

    # WRF section
    l_wrf = f_config["WRF"]
    assert l_wrf
    
    # cria diretório de log
    ls_dir_log = l_wrf["dir_log"]

    # diretório do ARW 
    ls_dir_arw = l_wrf["dir_arw"]

    # vai para o diretório dos executáveis do ARWpost
    os.chdir(ls_dir_arw)

    # para todos os domínios...
    for li_dom in (1, int(f_config["CONFIG"]["p_maxdom"])):
        # namelist file for ARWpost
        ls_namelist_file = "namelist.ARWpost"

        # logger
        M_LOG.info("Criando namelist ARWpost: %s D0%d", ls_namelist_file, li_dom)

        # cria namelist.ARWpost
        mnl.cria_namelist_ARWPost(ls_namelist_file, f_config, f_data, li_dom)

        # logger
        M_LOG.info("Execução do ARWpost.exe para o domínio %d", li_dom)

        try:
            # executa ARWpost.exe
            result = subprocess.check_output("./ARWpost.exe", shell=True).decode(sys.stdout.encoding)

            # create output file
            with open(os.path.join(ls_dir_log, f"arwpostD{li_dom}.out"), 'w') as lfh:
                # save output
                lfh.writelines(result)

            # for all arquivos de saida...
            for lfile in glob.glob(f"wrfd{li_dom}*"):     
                M_LOG.debug("movendo: %s", lfile)
                # move os arquivos gerados para o diretório de saída                  
                shutil.move(lfile, os.path.join(v_dir_out, os.path.basename(lfile)))

        # em caso de erro,...
        except subprocess.CalledProcessError:
            # logger
            M_LOG.error("Erro ao executar ARWpost.exe")
            # abort
            sys.exit(1)

    # for all wrfout files...
    for lfile in glob.glob("wrfout*"):
        M_LOG.debug("removendo: %s", lfile)
        # remove file
        os.remove(lfile)

# -------------------------------------------------------------------------------------------------
def process_WPS(f_config, fs_cfg_pn, f_data):
    """
    processa WPS: 
    - cria o arquivo namelist.wps
    - geogrid.exe => link_grib.csh => ungrib.exe => metgrid.exe
    - remove os arquivos que não serão utilizados

    :param f_config (ConfigParser): dados de configuração
    :param fs_cfg_pn (str): pathname do arquivo de configuração
    :param f_data (ConfigParser): dados da data de previsão
    """
    # logger
    M_LOG.info("Início do WPS: %s.", str(datetime.datetime.now()))

    # WRF section
    l_wrf = f_config["WRF"]
    assert l_wrf
    
    # parser das variáveis de configuração
    ldt_ini = f_data["data"]["data_ini"]

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

    # diretório do GFS
    ls_dir_gfs = l_wrf["dir_gfs"]

    # diretório dos arquivos GFS existe ?
    if not os.path.exists(ls_dir_gfs):
        # logger
        M_LOG.info("Criando diretório do GFS: %s", ls_dir_gfs)
        # cria diretório do GFS
        os.makedirs(ls_dir_gfs)

    # vai para o diretório dos executáveis do WRF
    os.chdir(l_wrf["dir_wrf_exec"])

    # para todos os arquivos de trabalho do WRF...
    for lfile in glob.glob("met_*"):
        M_LOG.debug("removendo: %s", lfile)
        # remove o arquivo
        os.remove(lfile)

    # vai para o diretório de execução do WPS
    os.chdir(l_wrf["dir_wps"])

    # namelist file for WPS
    ls_namelist_file = "namelist.wps"

    # logger
    M_LOG.info("Criando namelist WPS: %s", ls_namelist_file)

    # cria namelist.wps
    mnl.cria_namelist_WPS(ls_namelist_file, f_config, f_data)

    # logger
    M_LOG.info("Execução do geogrid.exe")
    try:
        # executa geogrid.exe
        result = subprocess.check_output("./geogrid.exe", shell=True ).decode(sys.stdout.encoding)

        # create output file
        with open(os.path.join(ls_dir_log, "geogrid.out"), 'w') as lfh:
            # save output
            lfh.writelines(result)

    # em caso de erro,...
    except subprocess.CalledProcessError:
        # logger
        M_LOG.error("Erro na execução do geogrid.exe")
        # abort
        sys.exit(1)

    # logger
    M_LOG.info("Criando links dos arquivos GFS")
    try:
        # comando
        ls_cmd_exe = "./link_grib.csh " + os.path.join(l_wrf["dir_gfs"], f"{ldt_ini}", "*")
        # executa link_grib.csh
        result = subprocess.check_output(ls_cmd_exe, shell=True).decode(sys.stdout.encoding)

    # em caso de erro,...
    except subprocess.CalledProcessError:
        # logger
        M_LOG.error("Erro na execução de link_grib.csh")
        # abort
        sys.exit(1)

    # logger
    M_LOG.debug("Execução do ungrib.exe")
    try:
        # executa ungrib.exe
        result = subprocess.check_output("./ungrib.exe", shell=True).decode(sys.stdout.encoding)

        # create output file
        with open(os.path.join(ls_dir_log, "ungrib.out"), 'w') as lfh:
            # save output
            lfh.writelines(result)

    # em caso de erro,...
    except subprocess.CalledProcessError:
        # logger
        M_LOG.error("Erro ao executar ungrib.exe")
        # abort
        sys.exit(1)

    # logger
    M_LOG.debug("Execução do metgrid.exe")
    try:
        # executa metgrid.exe
        result = subprocess.check_output("./metgrid.exe", shell=True).decode(sys.stdout.encoding)

        # create output file
        with open(os.path.join(ls_dir_log, "metgrid.out"), 'w') as lfh:
            # save output
            lfh.writelines(result)

    # em caso de erro,...
    except subprocess.CalledProcessError:
        # logger
        M_LOG.error("Erro ao executar metgrid.exe")
        # abort
        sys.exit(1)

    # for all extensions...
    for ls_ext in ["GFS", "geo_em", "PFILE", "FILE", "GRIBFILE"]:
        # for all files with extension...
        for lfile in glob.glob(ls_ext + '*'):
            M_LOG.debug("removendo: %s", lfile)
            # remove o arquivo
            os.remove(lfile)

    # for all log files...
    for lfile in glob.glob("*.log"):
        M_LOG.debug("copiando: %s", lfile)
        # move os arquivos de log do WPS para o diretório de log
        shutil.copy(lfile, ls_dir_log)

# -------------------------------------------------------------------------------------------------
def process_WRF(f_config, f_data):
    """
    processa WRF:
    - real.exe => wrf.exe => move wrfout_* para diretorio ARWPost
    - remove os arquivos que não serão utilizados

    :param f_config (ConfigParser): dados de configuração
    :param f_data (ConfigParser): dados da data de previsão
    """
    # logger
    M_LOG.info("Início do WRF: %s.", str(datetime.datetime.now()))

    # WRF section
    l_wrf = f_config["WRF"]
    assert l_wrf
    
    # cria diretório de log
    ls_dir_log = l_wrf["dir_log"]

    # vai para o diretório de execução do WRF
    os.chdir(l_wrf["dir_wrf_exec"])

    # namelist.input
    ls_namelist_file = "namelist.input"
    
    # logger
    M_LOG.info("Criando namelist WRF: %s", ls_namelist_file)

    # cria namelist.input
    mnl.cria_namelist_WRF(ls_namelist_file, f_config, f_data)

    # logger
    M_LOG.info("Execução do real.exe")
    try:
        # executa real.exe
        result = subprocess.check_output("./real.exe", shell=True).decode(sys.stdout.encoding)

        # create output file
        with open(os.path.join(ls_dir_log, "real.out"), 'w') as lfh:
            # save output
            lfh.writelines(result)

    # em caso de erro,...
    except subprocess.CalledProcessError:
        # logger
        M_LOG.error("Erro ao executar real.exe")
        # for all rsl.error files...
        for lfile in glob.glob("rsl.error.*"):
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
        # ls_cmd_exe = "mpirun --use-hwthread-cpus -np 7 ./wrf.exe"
        ls_cmd_exe = "./wrf.exe"

        # executa o WRF com multiprocessamento (mpirun)
        result = subprocess.check_output(ls_cmd_exe, shell=True).decode(sys.stdout.encoding)

        # create output file
        with open(os.path.join(ls_dir_log, "wrf.out"), 'w') as lfh:
            # save output
            lfh.writelines(result)

    # em caso de erro,...
    except subprocess.CalledProcessError:
        # logger
        M_LOG.error("Erro ao executar wrf.exe")
        # for all rsl.error files...
        for lfile in glob.glob("rsl.error.*"):
            M_LOG.debug("movendo: %s", lfile) 
            # salva o log do erro
            shutil.move(lfile, os.path.join(ls_dir_log, lfile))
        # abort
        sys.exit(1)

    # for all wrfout files...
    for lfile in glob.glob("wrfout_*"):
        M_LOG.debug("movendo: %s", lfile) 
        # move os arquivos de saída wrfout_* para o diretório do ARWPost
        shutil.move(lfile, os.path.join(l_wrf["dir_arw"], lfile))

    # for all met*.nc files...
    for lfile in glob.glob("met*.nc"):
        M_LOG.debug("removendo: %s", lfile)
        # remove file
        os.remove(lfile)

# -------------------------------------------------------------------------------------------------
def main():
    """
    drive app
    """
    # check parameters
    l_data, l_hora_prev, ls_regiao = arg_parse()

    # load config file
    l_config, ls_cfg_pn = load_config(ls_regiao)
    assert l_config

    # adjust config parameters
    adjust_config(l_config, ls_cfg_pn, l_data, l_hora_prev, ls_regiao)

    # logger
    M_LOG.info("Início do download: %s.", str(datetime.datetime.now()))

    # download dos arquivos FNL
    # dwn.downloadFNL(v_data, v_hora_ini, l_hora_prev)

    # process WPS
    process_WPS(l_config, ls_cfg_pn, l_data)
    # process WRF
    process_WRF(l_config, l_data)
    # process ARWPost
    process_ARW(l_config, l_data)

    # logger
    M_LOG.info("Fim de execução !")

# -------------------------------------------------------------------------------------------------
# this is the bootstrap process

if "__main__" == __name__:
    # logger
    logging.basicConfig(filename="wrf.log",
                        datefmt="%d/%m/%Y %H:%M",
                        format="%(asctime)s %(message)s",
                        level=logging.DEBUG)

    # disable logging
    # logging.disable(sys.maxint)

    # run application
    main()
    
# < the end >--------------------------------------------------------------------------------------
