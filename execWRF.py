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

# scp for paramiko
import scp
import paramiko

# local
import downloadFNL as dwn
import makeNamelist_DA as mnl

# < defines >--------------------------------------------------------------------------------------

# WFR home dir
DS_WRF_HOME = "/home/webpca/WRF"

# < logging >--------------------------------------------------------------------------------------

# logger
M_LOG = logging.getLogger(__name__)
M_LOG.setLevel(logging.DEBUG)

# -------------------------------------------------------------------------------------------------
def adjust_config(f_config, f_data, f_hora_prev):
    """
    """
    # calcula o valor de l_n_dx
    f_config["CONFIG"]["l_n_dx"] = f_config["CONFIG"]["p_dx"].replace(',', '')

    # WRF section
    l_wrf = f_config["WRF"]
    assert l_wrf
    
    # horas de previsão
    l_wrf["horas"] = str(v_hora_prev)
    l_wrf["intervalo"] = '6'
    '''
    # recria o arquivo de configuração
    with open(v_path, 'w') as lfh:
        # grava no arquivo de configuração 
        f_config.write(lfh)
    '''    
    '''
    # parser das variáveis de configuração
    v_data = f_data["data"]["data_ini"]

    v_dir_out = l_wrf["dir_out"] +"/wrf." + v_regiao + "." + v_data
    v_dir_wrf = l_wrf["dir_wrf"]
    v_GFSDir = l_wrf["dir_gfs"]
    v_GFSDataDir = v_GFSDir + "/" + v_data

    v_max_dominios = configReg.get("CONFIG","p_maxdom") #Obtem numero de domínios
    v_dir_log = l_wrf["dir_log"] +"/wrf." + v_regiao + "." + v_data

    v_horas_sim = v_hora_prev
    v_intervalo = 6
    '''
# -------------------------------------------------------------------------------------------------
def arg_parse():
    """
    parser dos parâmetros de entrada

    :returns: arguments
    """
    # number of parameters
    if len(sys.argv) < 7:
        # avisa e aborta
        printArgsError()

    # ano para similação
    l_ano_ini = int(sys.argv[1]) if sys.argv[1].isdigit() else printArgsError()

    # mes para similação
    l_mes_ini = int(sys.argv[2]) if sys.argv[2].isdigit() else printArgsError()
    l_mes_ini = l_mes_ini if 1 <= l_mes_ini <= 12 else printArgsError()

    # dia para similação
    l_dia_ini = int(sys.argv[3]) if sys.argv[3].isdigit() else printArgsError()
    l_dia_ini = l_dia_ini if 1 <= l_dia_ini <= 31 else printArgsError()

    # hora para similação
    l_hora_ini = int(sys.argv[4]) if sys.argv[4].isdigit() else printArgsError()
    l_hora_ini = l_hora_ini if l_hora_ini in [0, 6, 12, 18] else printArgsError()

    # tempo de similação
    l_hora_prev = int(sys.argv[5]) if sys.argv[5].isdigit() else printArgsError()
    l_hora_prev = l_hora_prev if l_hora_prev in [24, 48, 72] else printArgsError()

    # região de similação
    l_regiao = str(sys.argv[6]).strip().upper() if sys.argv[6].isalpha() else printArgsError()
    l_regiao = l_regiao if l_regiao in ["N", "SE"] else printArgsError()

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
def copiaFigsServidor(site, usuario, senha, dirDestino, dirOrigem, porta):
    """
    copia as figuras para o servidor

    :param site: endereço de destino
    :param dirDestino: diretório destino
    :param dirOrigem: diretório que será copiado
    """
    ssh = paramiko.SSHClient()
    assert ssh
    
    ssh.load_system_host_keys()
    ssh.connect(site, username=usuario, password=senha, port=porta)

    # SCPCLient takes a paramiko transport as its only argument
    scp = scp.SCPClient(ssh.get_transport())
    assert scp
    
    scp.put(dirOrigem, recursive=True, remote_path=dirDestino)
    scp.close()

    ssh.close()

# -------------------------------------------------------------------------------------------------
def load_config(fs_regiao):
    """
    Configura o parser de leitura do wrf.conf

    Define diretório base (PATH) de execução (onde estão os arquivos de configuração)
    """
    # diretório base (PATH) de execução (onde estão os arquivos de configuração)
    ls_path = DS_WRF_HOME if DS_WRF_HOME else os.path.dirname(os.path.realpath(__file__))

    # pathname do arquivo de configuração
    ls_path = os.path.join(ls_path, f"wrf_{fs_regiao}.conf")

    # arquivo de configuração exists ?
    if not os.path.exists(ls_path):
        # logger
        M_LOG.error("Não foi encontrado o arquivo de configuração: %s.", ls_path)
        # abort
        sys.exit(1)

    # cria o parser de configuração
    l_config = configparser.ConfigParser()
    assert l_config

    # lê o arquivo de configuração
    l_config.read(ls_path)

    # return
    return l_config

# -------------------------------------------------------------------------------------------------
def pre_process(f_config):
    """
    PRÉ-PROCESSAMENTO
    """
    # logger
    M_LOG.info("Hora de início do pré-processamento: %s.", str(datetime.datetime.now()))

    # Cria arquivo de log e de informações de data e hora
    #Cria arquivo de log do WRF
    if not os.path.exists( v_dir_log ):
        os.makedirs( v_dir_log )

    '''
    Cria diretórios dos arquivos GFS e de saída no formato: wrf.regiao.AAAAMMDDHH e diretório de LOG: wrf.regiao.AAAAMMDDHH
    Ex: (wrf.SE.2019102500)
    '''
    if not os.path.exists ( v_dir_out ):
        logging.debug ( "Criando diretório: " + v_dir_log )
        os.makedirs ( v_dir_out )

    if not os.path.exists ( v_dir_log ):
        logging.debug ( "Criando diretório: " + v_dir_log )
        os.makedirs ( v_dir_log )

    # Verifica se diretório dos arquivos GFS existe, senão cria.
    if not os.path.exists ( v_GFSDir ):
        logging.debug( " Criando diretório : " + v_GFSDir )
        os.makedirs ( v_GFSDir )

    os.chdir(v_path)

    #Remove os arquivos de trabalho do WRF
    files_delete = glob.glob(v_dir_exec + '/met_*')
    for file in files_delete:
        os.remove(file)



    namelistObj = mnl.makeNameList(v_path + "/wrf_" + v_regiao +".conf") #Cria objeto que gera os Namelists
    '''
    Processo WPS: 
    - Cria o arquivo namelist.wps
    - Executa geogrid.exe => executa link_grib.csh => executa ungrib.exe => executa metgrid.exe
    - Remove os arquivos que não serão utilizados
    '''

    logging.debug('Criando Namelist WPS : ' + v_dir_wps + '/namelist.wps')
    namelistObj.criaNamelistWPS() #cria namelist.wps

    os.chdir(v_dir_wps) #Entra no diretório de execução do WPS
    #Executa o geogrid.exe

    print("\n Executando GEOGRID........")
    logging.debug('Inicio da Execucao do GEOGRID...')
    v_cmd_exe = v_dir_wps + '/geogrid.exe'
    try:
        result = subprocess.check_output(v_cmd_exe, shell=True ).decode(sys.stdout.encoding)

    except subprocess.CalledProcessError:
        logging.error('Erro ao executar Geogrid!')
        sys.exit(1)

    #Executa o link_grid.csh
    print(v_dir_wps + '/link_grib.csh ' + v_GFSDataDir + '/*')
    v_cmd_exe = v_dir_wps + '/link_grib.csh ' + v_GFSDataDir + '/*'
    logging.debug('Criando links dos arquivos GFS')
    print("criando os links")
    try:
        result = subprocess.check_output(v_cmd_exe, shell=True).decode(sys.stdout.encoding)
    except subprocess.CalledProcessError:
        logging.error('Erro ao executar link_grib.csh')
        sys.exit(1)

    #Executa o ungrib.exe
    v_cmd_exe = v_dir_wps + '/ungrib.exe'
    ungrib_file = open(v_dir_log + "/ungrib.out", 'w')
    logging.debug('Inicio da Execucao do Ungrib...')
    print("Executando ungrib.............")
    try:
        result = subprocess.check_output(v_cmd_exe, shell=True).decode(sys.stdout.encoding)
        ungrib_file.writelines(result)
    except subprocess.CalledProcessError:
        logging.error('Erro ao executar ungrib.exe')
        sys.exit(1)

    #Executa o metgrid.exe
    v_cmd_exe = v_dir_wps + '/metgrid.exe'
    metgrid_file = open(v_dir_log + "/metgrid.out", 'w')
    logging.debug('Inicio da execução do Metgrid')
    print("executando metgrid..............")
    try:
        result = subprocess.check_output(v_cmd_exe, shell=True).decode(sys.stdout.encoding)
        metgrid_file.writelines(result)
        metgrid_file.close()
    except subprocess.CalledProcessError:
        logging.error('Erro ao executar metgrid.exe')
        sys.exit(1)

    #Remove os arquivos de trabalho
    for extension in ["GFS","geo_em","PFILE","FILE","GRIBFILE"]:
        for file in glob.glob(v_dir_wps + '/' + extension + '*'):
            os.remove(file)

    #Move os arquivos de log do WPS para o diretorio de log 'wrf.regiao.AAAAMMDDHH'
    files_move = glob.glob(v_dir_wps + '/*.log')
    for file in files_move:
        shutil.copy(os.path.join(v_dir_wps, file),v_dir_log)

# -------------------------------------------------------------------------------------------------
def printArgsError():
    """
    imprime na tela os argumentos de entrada válidos
    """
    # usage message
    print("Número de argumentos inválidos!")
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
    """
    '''
    Processo WRF:
    Executa real.exe => executa wrf.exe => move wrfout_* para diretorio ARWPost
    remove os arquivos que não serão utilizados
    '''

    logging.debug('Criando Namelist WRF : ' + v_dir_exec + '/namelist.input')
    namelistObj.criaNamelistWRF()      #Cria namelist.input

    v_cmd_exe = v_dir_exec + '/real.exe'
    real_file = open(v_dir_log + "/real.out", 'w')
    os.chdir(v_dir_exec)    #Entra no diretório de execução do WRF
    logging.debug('Inicio da Execução do real.exe')
    try:
        result = subprocess.check_output(v_dir_exec + '/real.exe', shell=True).decode(sys.stdout.encoding)
        real_file.writelines(result)
        real_file.close()
    except subprocess.CalledProcessError:
        shutil.copy(os.path.join(v_dir_exec,'rsl.error.0000'),v_dir_log)
        logging.error('Erro ao executar real.exe')
        sys.exit(1)

    #Executa o WRF com multiprocessamento (mpirun)
    os.chdir(v_dir_exec)
    #v_cmd_exe ='mpirun -np 24 ./wrf.exe'
    v_cmd_exe ='mpirun --use-hwthread-cpus -np 7 ./wrf.exe'
    print("Comando Exe: " + v_cmd_exe)
    wrf_file = open(v_dir_log + "/wrf.out", 'w')
    logging.debug('Inicio de execução do WRF')
    try:
        result = subprocess.check_output(v_cmd_exe, shell=True).decode(sys.stdout.encoding)
        wrf_file.writelines(result)
        wrf_file.close()
    except subprocess.CalledProcessError:
        print('Erro ao executar ' + v_cmd_exe)
        shutil.copy(os.path.join(v_dir_exec,'rsl.error.0000'),v_dir_log)
        logging.error('Erro ao executar wrf.exe')
        sys.exit(1)


    #Move os arquivos de saída wrfout_* para o diretório de pós processamento ARWPost
    v_dir_arw = configReg.get("WRF","dir_arw")
    files_move = glob.glob(v_dir_exec + '/wrfout_*')
    for file in files_move:
        shutil.move(os.path.join(v_dir_exec,file), v_dir_arw + '/' + os.path.basename(file))
        #shutil.copy(os.path.join(v_dir_exec,file), v_dir_arw + '/' + os.path.basename(file))


    files_delete = glob.glob(v_dir_exec + '/met*.nc')

    for file in files_delete:
        logging.debug('Removendo: ' + file)
        os.remove(file)

    '''
    Processo ARWpost:
    Cria namelist.ARWpost e executa ARWpost para o numero de domínios definidos em wrf.conf
    '''

    for index in (1,v_max_dominios):
        logging.debug("Criando namelistARWpost D" + str(index))
        os.chdir(v_path)
        namelistObj.criaNamelistARWPost(index)
        os.chdir(v_dir_arw)
        arw_file = open(v_dir_log + "/arwpostD" + str(index) + ".out",'w')
        v_cmd_exe = v_dir_arw + '/ARWpost.exe'
        logging.debug('Inicio de Execução do ARWpost: dominio ' + str(index))
        print("Executando ARWpost: D" + str(index))
        try:
            result = subprocess.check_output(v_cmd_exe, shell=True).decode(sys.stdout.encoding)
            arw_file.writelines(result)
            arw_file.close()
            files_move = glob.glob(v_dir_arw + '/wrfd' + str(index) + '*') # Obtem arquivos de saida
            for file in files_move:     # Move os arquivos gerados para o diretório de saída                  
                shutil.move(os.path.join(v_dir_arw,file), v_dir_out + '/' +  os.path.basename(file))
        except subprocess.CalledProcessError:
            logging.error('Erro ao executar ARWpost.exe')
            sys.exit(1)

    files_delete = glob.glob(v_dir_arw + '/wrfout*')

    for file in files_delete:
        logging.debug('Removendo: ' + file)
        os.remove(file)

# -------------------------------------------------------------------------------------------------
def main():
    """
    drive app
    """
    # check parameters
    l_data, l_hora_prev, l_regiao = arg_parse()

    # load config file
    l_config = load_config(l_regiao)
    assert l_config

    # adjust config parameters
    adjust_config(l_config, l_data, l_hora_prev)

    # logger
    M_LOG.info("Hora de início do download: %s.", str(datetime.datetime.now()))

    # download dos arquivos FNL
    # dwn.downloadFNL(v_data, v_hora_ini, v_hora_prev)

    # pre process
    # pre_process(l_config)
    # pre process
    # process(l_config)

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
