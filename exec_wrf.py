# -*- coding: utf-8 -*-
"""
exec_wrf

2021/nov  1.0  eliana  initial version (Linux/Python)
"""
# < imports >----------------------------------------------------------------------------------

# python library
import configparser
import datetime
import logging
import os
import shutil
import sys

# graylog
import graypy

# local
import exc_defs as df
import exc_download as dwn
import exc_namelist as mnl
import exc_processes as prc

# < defines >----------------------------------------------------------------------------------

# horas de início de previsão válidas
DLST_HORA_OK = [0, 6, 12, 18]
# tempos de previsão válidos
DLST_TEMPO_OK = [24, 48, 72]
# regiões válidas
DLST_REGIAO_OK = ["N", "SE"]

# < logging >----------------------------------------------------------------------------------

# logger
M_LOG = logging.getLogger(__name__)
M_LOG.setLevel(df.DI_LOG_LEVEL)

# graylog handler
M_GLH = graypy.GELFUDPHandler("localhost", 12201)
M_LOG.addHandler(M_GLH)

# ---------------------------------------------------------------------------------------------
def adjust_config(fo_cfg_parser, fs_cfg_pathname, fi_forecast_time, fs_token):
    """
    ajusta a configuração dos parâmetros de previsão

    :param fo_cfg_parser (ConfigParser): dados de configuração
    :param fs_cfg_pathname (str): pathname do arquivo de configuração
    :param fi_forecast_time (int): tempo de previsão
    :param fs_token (str): forecast id
    """
    # logger
    M_LOG.debug("adjust_config >>")

    # calcula o valor de l_n_dx
    fo_cfg_parser["CONFIG"]["l_n_dx"] = fo_cfg_parser["CONFIG"]["p_dx"].replace(',', '')

    # recria o arquivo de configuração
    with open(fs_cfg_pathname, 'w') as lfh:
        # grava no arquivo de configuração
        fo_cfg_parser.write(lfh)

    # WRF section
    l_wrf = fo_cfg_parser["WRF"]
    assert l_wrf

    # horas de previsão
    l_wrf["horas"] = str(fi_forecast_time)
    l_wrf["intervalo"] = str(df.DI_INTERVALO)

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
    # diretório de saída
    l_wrf["dir_out"] = os.path.join(l_wrf["dir_wrf"], l_wrf["dir_out"], fs_token)
    # diretório do log
    l_wrf["dir_log"] = os.path.join(l_wrf["dir_wrf"], l_wrf["dir_log"], fs_token)

# ---------------------------------------------------------------------------------------------
def arg_parse():
    """
    parser dos parâmetros de entrada

    :returns: arguments
    """
    # logger
    M_LOG.debug("arg_parse >>")

    # less than 7 parameters ?
    if len(sys.argv) < 7:
        # avisa e aborta
        print_usage(f"Número de argumentos inválido: {len(sys.argv)} de 7.")

    # ano para previsão
    li_ano_ini = int(sys.argv[1]) if sys.argv[1].isdigit() \
                                  else print_usage(f"Erro no ano: {sys.argv[1]}")

    # mes para previsão
    li_mes_ini = int(sys.argv[2]) if sys.argv[2].isdigit() \
                                  else print_usage(f"Erro no mês: {sys.argv[2]}")
    li_mes_ini = li_mes_ini if 1 <= li_mes_ini <= 12 \
                            else print_usage(f"Erro: mês ({li_mes_ini}) inválido.")

    # dia para previsão
    li_dia_ini = int(sys.argv[3]) if sys.argv[3].isdigit() \
                                  else print_usage(f"Erro no dia: {sys.argv[3]}")
    li_dia_ini = li_dia_ini if 1 <= li_dia_ini <= 31 \
                            else print_usage(f"Erro: dia ({li_dia_ini}) inválido.")

    # início para previsão
    li_hora_ini = int(sys.argv[4]) if sys.argv[4].isdigit() \
                                   else print_usage(f"Erro na hora: {sys.argv[4]}")
    li_hora_ini = li_hora_ini if li_hora_ini in DLST_HORA_OK \
                              else print_usage(f"Erro: hora ({li_hora_ini}) inválida.")

    # tempo de previsão
    li_forecast_time = int(sys.argv[5]) if sys.argv[5].isdigit() \
                                        else print_usage(f"Erro no tempo: {sys.argv[5]}")
    li_forecast_time = li_forecast_time if li_forecast_time in DLST_TEMPO_OK \
                                        else print_usage(f"Erro: tempo ({li_forecast_time}) inválida.")

    # região de previsão
    ls_regiao = str(sys.argv[6]).strip().upper() if sys.argv[6].isalpha() \
                                                 else print_usage(f"Erro na região: {sys.argv[6]}")
    ls_regiao = ls_regiao if ls_regiao in DLST_REGIAO_OK \
                          else print_usage(f"Erro: região ({ls_regiao}) inválida.")

    # calcula a data final = data inicial + horas de previsão:
    ldt_final = datetime.datetime(li_ano_ini, li_mes_ini, li_dia_ini, li_hora_ini, 0, 0) + \
                datetime.timedelta(hours=li_forecast_time)

    # cria configuração de data e hora
    lo_forecast_date = configparser.ConfigParser()
    assert lo_forecast_date

    # create data section
    lo_forecast_date["data"] = {}

    # forecast date section
    ldct_date = lo_forecast_date["data"]
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
        lo_forecast_date.write(lfh)

    # return
    return lo_forecast_date, li_forecast_time, ls_regiao

# ---------------------------------------------------------------------------------------------
def build_token(fo_forecast_date, fi_forecast_time, fs_regiao):
    """
    monta o identificador da previsão

    :param fo_forecast_date (ConfigParser): dados da data de previsão
    :param fi_forecast_time (int): tempo de previsão
    :param fs_regiao (str): região
    """
    # logger
    M_LOG.debug("build_token >>")

    # parser das variáveis de configuração
    ldt_ini = fo_forecast_date["data"]["data_ini"]

    # hora de início da previsão 
    li_hora_ini = int(fo_forecast_date["data"]["hora_ini"])

    # return token
    return "{}{:02d}{:02d}{}".format(ldt_ini, li_hora_ini, fi_forecast_time, fs_regiao)

# ---------------------------------------------------------------------------------------------
def forecast_exists(fo_cfg_parser, fs_token):
    """
    verifica se a previsão já existe

    :param fo_cfg_parser (ConfigParser): dados de configuração
    :param fs_token (str): token id

    :returns: True if exists or False
    """
    # logger
    M_LOG.debug("forecast_exists >>")

    # WRF section
    l_wrf = fo_cfg_parser["WRF"]
    assert l_wrf

    # outrput dir 
    ls_tgz_file = os.path.join(l_wrf["dir_wrf"], l_wrf["dir_out"], fs_token)

    # tgz output file
    ls_tgz_file += ".tgz"
    M_LOG.debug("ls_tgz_file: %s", str(ls_tgz_file)) 

    # return
    return os.path.isfile(ls_tgz_file)

# ---------------------------------------------------------------------------------------------
def load_config(fs_regiao):
    """
    configura o parser de leitura do wrf.conf

    :param fs_regiao (str): região de previsão

    :returns: config parser & config fullpath
    """
    # logger
    M_LOG.debug("load_config >>")

    # diretório base (PATH) de execução (onde estão os arquivos de configuração)
    ls_path = df.DS_WRF_HOME if df.DS_WRF_HOME else os.path.dirname(os.path.realpath(__file__))

    # fullpath do arquivo de configuração
    ls_cfg_fullpath = os.path.join(ls_path, f"wrf_{fs_regiao}.conf")

    # arquivo de configuração não existe ?
    if not os.path.exists(ls_cfg_fullpath):
        # logger
        M_LOG.error("Não foi encontrado o arquivo de configuração: %s.", ls_cfg_fullpath, exc_info=1)
        # abort
        sys.exit(-1)

    # cria o parser de configuração
    lo_cfg_parser = configparser.ConfigParser()
    assert lo_cfg_parser

    # lê o arquivo de configuração
    lo_cfg_parser.read(ls_cfg_fullpath)

    # WRF path
    lo_cfg_parser["WRF"]["dir_wrf"] = ls_path

    # return
    return lo_cfg_parser, ls_cfg_fullpath

# ---------------------------------------------------------------------------------------------
def make_tgz_file(fo_cfg_parser, fs_token):
    """
    create a tgz file
    """
    # logger
    M_LOG.debug("make_tgz_file >>")

    # source directory (/home/webpca/WRF/data/out/<token>)
    ls_source_dir = fo_cfg_parser["WRF"]["dir_out"]

    # output filepath (/home/webpca/WRF/data/out/<token>.tgz)
    ls_tgz_filepath = ls_source_dir + ".tgz"

    # create tgz file
    with tarfile.open(ls_tgz_filepath, "w:gz") as lfh:
        # add directory to tgz 
        lfh.add(ls_source_dir, arcname=os.path.basename(ls_source_dir))

# ---------------------------------------------------------------------------------------------
def print_usage(fs_msg):
    """
    imprime na tela os argumentos de entrada válidos
    """
    # logger
    M_LOG.debug("print_usage >>")

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
    sys.exit(-1)

# ---------------------------------------------------------------------------------------------
def touch_tgz_file(fo_cfg_parser, fs_token):
    """
    update date & time of a tgz file
    """
    # logger
    M_LOG.debug("touch_tgz_file >>")

    # source directory (/home/webpca/WRF/data/out + fs_token)
    ls_source_dir = os.path.join(fo_cfg_parser["WRF"]["dir_out"], fs_token)

    # output filepath (/home/webpca/WRF/data/out/<token>.tgz)
    ls_tgz_filepath = ls_source_dir + ".tgz"

    # touch file
    pathlib.Path(ls_tgz_filepath).touch()

# ---------------------------------------------------------------------------------------------
def main():
    """
    drive app
    """
    # logger
    M_LOG.debug("main >>")

    # logger
    M_LOG.info("Início de execução !")

    # check parameters
    lo_forecast_date, li_forecast_time, ls_regiao = arg_parse()

    # monta o identificador da previsão
    ls_token = build_token(lo_forecast_date, li_forecast_time, ls_regiao)

    # load config file
    lo_cfg_parser, ls_cfg_fullpath = load_config(ls_regiao)
    assert lo_cfg_parser

    # forecast already exists ?
    if not forecast_exists(lo_cfg_parser, ls_token):
        # adjust config parameters
        adjust_config(lo_cfg_parser, ls_cfg_fullpath, li_forecast_time, ls_token)

        # download dos arquivos FNL
        dwn.download_FNL(lo_forecast_date, li_forecast_time, lo_cfg_parser["WRF"]["dir_fnl"])

        # process WRF
        prc.process_all(lo_cfg_parser, lo_forecast_date, ls_token)

        # make tgz file
        make_tgz_file(lo_cfg_parser, ls_token)

        # remove output directory tree
        shutil.rmtree(lo_cfg_parser["WRF"]["dir_out"])

    # senão,...
    else:
        # touch tgz file
        touch_tgz_file(lo_cfg_parser, ls_token)

    # envia e-mail com link

    # logger
    M_LOG.info("Fim de execução !")

# ---------------------------------------------------------------------------------------------
# this is the bootstrap process

if "__main__" == __name__:
    # logger
    logging.basicConfig(filename="wrf.log",
                        filemode='w',
                        datefmt="%d/%m/%Y %H:%M",
                        format="%(asctime)s %(message)s",
                        level=df.DI_LOG_LEVEL)

    # disable logging
    # logging.disable(sys.maxint)

    # run application
    main()

# < the end >----------------------------------------------------------------------------------
