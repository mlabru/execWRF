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
import makeNamelist_DA as mnl

# < defines >--------------------------------------------------------------------------------------

# WFR home dir
DS_WRF_HOME = "/home/webpca/WRF"
DS_WRF_HOME = "/home/mlabru/works_lpd/mlabru/Works/wrk.icea/Public/05.prj.met/02.git.met/WRF"

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

    # diretório do WPS
    l_wrf["dir_wps"] = os.path.join(l_wrf["dir_wrf"], l_wrf["dir_wps"])
    # diretório do GFS
    l_wrf["dir_gfs"] = os.path.join(l_wrf["dir_wrf"], l_wrf["dir_gfs"])

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

    # ano para similação
    l_ano_ini = int(sys.argv[1]) if sys.argv[1].isdigit() else print_usage(f"Erro no ano: {sys.argv[1]}")

    # mes para similação
    l_mes_ini = int(sys.argv[2]) if sys.argv[2].isdigit() else print_usage(f"Erro no mês: {sys.argv[2]}")
    l_mes_ini = l_mes_ini if 1 <= l_mes_ini <= 12 else print_usage(f"Erro: mês ({l_mes_ini}) inválido.")

    # dia para similação
    l_dia_ini = int(sys.argv[3]) if sys.argv[3].isdigit() else print_usage(f"Erro no dia: {sys.argv[3]}")
    l_dia_ini = l_dia_ini if 1 <= l_dia_ini <= 31 else print_usage(f"Erro: dia ({l_dia_ini}) inválido.")

    # hora para similação
    l_hora_ini = int(sys.argv[4]) if sys.argv[4].isdigit() else print_usage(f"Erro na hora: {sys.argv[4]}")
    l_hora_ini = l_hora_ini if l_hora_ini in [0, 6, 12, 18] else print_usage(f"Erro: hora ({l_hora_ini}) inválida.")

    # tempo de similação
    l_hora_prev = int(sys.argv[5]) if sys.argv[5].isdigit() else print_usage(f"Erro no tempo: {sys.argv[5]}")
    l_hora_prev = l_hora_prev if l_hora_prev in [24, 48, 72] else print_usage(f"Erro: tempo ({l_hora_prev}) inválida.")

    # região de similação
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
    Configura o parser de leitura do wrf.conf

    Define diretório base (PATH) de execução (onde estão os arquivos de configuração)
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
def pre_process(f_config, fs_cfg_pn, f_data):
    """
    pre-processamento

    :param f_config (ConfigParser): dados de configuração
    :param fs_cfg_pn (str): pathname do arquivo de configuração
    :param f_data (ConfigParser): dados da data de previsão

    Processo WPS: 
    - Cria o arquivo namelist.wps
    - Executa geogrid.exe => executa link_grib.csh => executa ungrib.exe => executa metgrid.exe
    - Remove os arquivos que não serão utilizados
    """
    # logger
    M_LOG.info("Início do pré-processamento: %s.", str(datetime.datetime.now()))

    # WRF section
    l_wrf = f_config["WRF"]
    assert l_wrf
    
    # parser das variáveis de configuração
    ldt_ini = f_data["data"]["data_ini"]

    # cria diretório de log
    ls_dir_log = l_wrf["dir_log"]
    print("ls_dir_log", ls_dir_log)

    # diretório de log existe ?
    if not os.path.exists(ls_dir_log):
        # logger
        M_LOG.info("Criando diretório de log: %s", ls_dir_log)
        # cria diretório de log
        os.makedirs(ls_dir_log)

    # diretório de saída
    ls_dir_out = l_wrf["dir_out"]
    print("ls_dir_out", ls_dir_out)

    # diretório de saída existe ?
    if not os.path.exists(ls_dir_out):
        # logger
        M_LOG.info("Criando diretório de saída: %s", ls_dir_out)
        # cria diretório de saída
        os.makedirs(ls_dir_out)

    # diretório do GFS
    ls_dir_gfs = l_wrf["dir_gfs"]
    print("ls_dir_gfs", ls_dir_gfs)

    # diretório dos arquivos GFS existe ?
    if not os.path.exists(ls_dir_gfs):
        # logger
        M_LOG.info("Criando diretório do GFS: %s", ls_dir_gfs)
        # cria diretório do GFS
        os.makedirs(ls_dir_gfs)

    # diretório raiz do WRF
    ls_dir_wrf = l_wrf["dir_wrf"]
    print("ls_dir_wrf", ls_dir_wrf)

    # vai para o diretório base do WRF
    os.chdir(ls_dir_wrf)

    # diretório de execução do WRF
    ls_dir_exec = l_wrf["dir_wrf_exec"]
    print("ls_dir_exec", ls_dir_exec)

    # para todos os arquivos de trabalho do WRF...
    for file in glob.glob(os.path.join(ls_dir_exec, "met_*")):
        print("file", file)
        # remove o arquivo
        os.remove(file)

    # cria objeto que gera os Namelists
    l_namelist = mnl.makeNameList(fs_cfg_pn)
    assert l_namelist

    # diretório do WPS
    ls_dir_wps = l_wrf["dir_wps"]
    print("ls_dir_wps", ls_dir_wps)

    # logger
    M_LOG.info("Criando namelist WPS: %s", os.path.join(ls_dir_wps, "namelist.wps"))

    # cria namelist.wps
    # l_namelist.criaNamelistWPS()

    # vai para o diretório de execução do WPS
    os.chdir(ls_dir_wps)

    # logger
    M_LOG.info("Execução do geogrid.exe")
    try:
        # comando
        ls_cmd_exe = os.path.join(ls_dir_wps, "geogrid.exe")
        print("ls_cmd_exe", ls_cmd_exe)

        # executa geogrid.exe
        result = subprocess.check_output(ls_cmd_exe, shell=True ).decode(sys.stdout.encoding)

        # create outout file
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
        ls_cmd_exe = os.path.join(ls_dir_wps, "link_grib.csh") + " " + \
                     os.path.join(l_wrf["dir_gfs"], f"{ldt_ini}") + "/*"
        print("ls_cmd_exe", ls_cmd_exe)

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
        # command
        ls_cmd_exe = os.path.join(ls_dir_wps, "ungrib.exe")
        print("ls_cmd_exe", ls_cmd_exe)

        # executa ungrib.exe
        result = subprocess.check_output(ls_cmd_exe, shell=True).decode(sys.stdout.encoding)

        # create outout file
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
        # command
        ls_cmd_exe = os.path.join(ls_dir_wps, "metgrid.exe")
        print("ls_cmd_exe", ls_cmd_exe)

        # executa metgrid.exe
        result = subprocess.check_output(ls_cmd_exe, shell=True).decode(sys.stdout.encoding)

        # create outout file
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
        for file in glob.glob(os.path.join(ls_dir_wps, ls_ext + '*')):
            print("file", file)
            # remove o arquivo
            os.remove(file)

    # for all log files...
    for file in glob.glob(os.path.join(ls_dir_wps, "*.log")):
        print("file", file)
        # move os arquivos de log do WPS para o diretorio de log 'wrf.<regiao>.<AAAAMMDDHH>'
        shutil.copy(os.path.join(ls_dir_wps, file), ls_dir_log)

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
    print("Entre com os argumentos: <AAAA> <MM> <DD> <HORA> <TEMPO> <REGIAO> [E-MAIL]")
    print("    AAAA   = Ano")
    print("    MM     = Mês (01..12)")
    print("    DD     = Dia (01..31)")
    print("    HH     = Hora (00..23)")
    print("    HORA   = Hora de início da previsão (00|06|12|18)")
    print("    TEMPO  = Tempo de previsão (24|48|72)")
    print("    REGIAO = Região (N|SE)")
    print("    E-MAIL = E-mail para resposta (opcional)")
  
    # abort
    sys.exit(1)
    
# -------------------------------------------------------------------------------------------------
def process(f_config):
    """
    PROCESSAMENTO

    Processo WRF:
    Executa real.exe => executa wrf.exe => move wrfout_* para diretorio ARWPost
    remove os arquivos que não serão utilizados
    """
    # logger
    M_LOG.info("Início do processamento: %s.", str(datetime.datetime.now()))

    # WRF section
    l_wrf = f_config["WRF"]
    assert l_wrf
    
    # parser das variáveis de configuração
    ldt_ini = f_data["data"]["data_ini"]


    M_LOG.debug('Criando Namelist WRF : ' + v_dir_exec + '/namelist.input')
    l_namelist.criaNamelistWRF()      #Cria namelist.input

    ls_cmd_exe = v_dir_exec + '/real.exe'
    real_file = open(v_dir_log + "/real.out", 'w')
    os.chdir(v_dir_exec)    #Entra no diretório de execução do WRF
    M_LOG.debug('Inicio da Execução do real.exe')
    try:
        result = subprocess.check_output(v_dir_exec + '/real.exe', shell=True).decode(sys.stdout.encoding)
        real_file.writelines(result)
        real_file.close()
    except subprocess.CalledProcessError:
        shutil.copy(os.path.join(v_dir_exec,'rsl.error.0000'),v_dir_log)
        M_LOG.error('Erro ao executar real.exe')
        sys.exit(1)

    #Executa o WRF com multiprocessamento (mpirun)
    os.chdir(v_dir_exec)
    #ls_cmd_exe ='mpirun -np 24 ./wrf.exe'
    ls_cmd_exe ='mpirun --use-hwthread-cpus -np 7 ./wrf.exe'
    print("Comando Exe: " + ls_cmd_exe)
    wrf_file = open(v_dir_log + "/wrf.out", 'w')
    M_LOG.debug('Inicio de execução do WRF')
    try:
        result = subprocess.check_output(ls_cmd_exe, shell=True).decode(sys.stdout.encoding)
        wrf_file.writelines(result)
        wrf_file.close()
    except subprocess.CalledProcessError:
        print('Erro ao executar ' + ls_cmd_exe)
        shutil.copy(os.path.join(v_dir_exec,'rsl.error.0000'),v_dir_log)
        M_LOG.error('Erro ao executar wrf.exe')
        sys.exit(1)


    #Move os arquivos de saída wrfout_* para o diretório de pós processamento ARWPost
    v_dir_arw = configReg.get("WRF","dir_arw")
    files_move = glob.glob(v_dir_exec + '/wrfout_*')
    for file in files_move:
        shutil.move(os.path.join(v_dir_exec,file), v_dir_arw + '/' + os.path.basename(file))
        #shutil.copy(os.path.join(v_dir_exec,file), v_dir_arw + '/' + os.path.basename(file))


    files_delete = glob.glob(v_dir_exec + '/met*.nc')

    for file in files_delete:
        M_LOG.debug('Removendo: ' + file)
        os.remove(file)

    '''
    Processo ARWpost:
    Cria namelist.ARWpost e executa ARWpost para o numero de domínios definidos em wrf.conf
    '''

    for index in (1,v_max_dominios):
        M_LOG.debug("Criando namelistARWpost D" + str(index))
        os.chdir(v_path)
        l_namelist.criaNamelistARWPost(index)
        os.chdir(v_dir_arw)
        arw_file = open(v_dir_log + "/arwpostD" + str(index) + ".out",'w')
        ls_cmd_exe = v_dir_arw + '/ARWpost.exe'
        M_LOG.debug('Inicio de Execução do ARWpost: dominio ' + str(index))
        print("Executando ARWpost: D" + str(index))
        try:
            result = subprocess.check_output(ls_cmd_exe, shell=True).decode(sys.stdout.encoding)
            arw_file.writelines(result)
            arw_file.close()
            files_move = glob.glob(v_dir_arw + '/wrfd' + str(index) + '*') # Obtem arquivos de saida
            for file in files_move:     # Move os arquivos gerados para o diretório de saída                  
                shutil.move(os.path.join(v_dir_arw,file), v_dir_out + '/' +  os.path.basename(file))
        except subprocess.CalledProcessError:
            M_LOG.error('Erro ao executar ARWpost.exe')
            sys.exit(1)

    files_delete = glob.glob(v_dir_arw + '/wrfout*')

    for file in files_delete:
        M_LOG.debug('Removendo: ' + file)
        os.remove(file)

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

    # pre process
    pre_process(l_config, ls_cfg_pn, l_data)
    # process
    process(l_config, l_data)

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
