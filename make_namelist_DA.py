import sys
import os
import configparser
from datetime import date
"""
 O arquivo wrf.conf contem as configuracoes necessárias
 para criar os arquivos 'namelist' utilizados nos modulos
 de execução do WRF
"""
class makeNameList():
    def __init__(self,fileConf):
        self.fileconf = fileConf       #Arquivo de configuracao
        self.configReg = configparser.ConfigParser ( )
       
        self.configReg.read(fileConf)  # parser para ler as configurações do WRF       
        self.obtemDataConfig()         # Faz a leitura das informações de data/hora

    def obtemDataConfig(self):
        global v_ano_ini, v_dia_ini,v_mes_ini,v_hora_ini, v_ano_final,v_dia_final,v_hora_final,v_mes_final, v_start_date,\
        v_data_ini
        config_data = configparser.ConfigParser ( )  # parser para ler as configuracoes de data e hora
        config_data.read (self.configReg.get ( "WRF", "dir_wrf" ) + "/data.conf" )  # data.conf que está no diretorio de execução

        v_data_ini = config_data.get("data","data_ini")
        v_ano_ini = config_data.get ( "data", "ano_ini" )
        v_mes_ini = config_data.get("data","mes_ini")
        v_dia_ini = config_data.get("data","dia_ini")
        v_hora_ini = config_data.get("data","hora_ini")
        v_ano_final = config_data.get("data","ano_final")
        v_mes_final = config_data.get("data","mes_final")
        v_dia_final = config_data.get("data","dia_final")
        v_hora_final = config_data.get("data","hora_final")
        v_start_date = (v_ano_ini + '-' + v_mes_ini + '-' + v_dia_ini + '_' + v_hora_ini + ':00:00')

    
    '''
    Gera o arquivo namelist.input utilizado na execução do WRF
    '''
    def criaNamelistWRF(self):
        print("CRIA NAMELIST WRF!")
        arq_namelist = open(self.configReg.get("WRF","dir_wrf_exec") + '/namelist.input','w+')
        namelist = []
        namelist.append("&time_control\n  run_days = 0,\n")
        namelist.append("  run_hours = " + self.configReg.get("WRF","HORAS") + ", \n")
        namelist.append("  run_minutes = 0, \n  run_seconds = 0, \n" )
        namelist.append("  start_year = " + v_ano_ini + ', ' + v_ano_ini + ', ' + v_ano_ini + ',\n')
        namelist.append("  start_month = " + v_mes_ini + ', ' + v_mes_ini + ', ' + v_mes_ini + ',\n')
        namelist.append("  start_day = " + v_dia_ini + ', ' + v_dia_ini + ', ' + v_dia_ini + ', \n')
        namelist.append("  start_hour = " + v_hora_ini + ', ' + v_hora_ini + ', ' + v_hora_ini + ',\n')
        namelist.append("  start_minute = 00, 00, 00,\n")
        namelist.append("  start_second = 00, 00, 00,\n")
        namelist.append("  end_year = " + v_ano_final + ', ' + v_ano_final + ', ' + v_ano_final + ',\n' )
        namelist.append("  end_month = " + v_mes_final + ', ' + v_mes_final + ', ' + v_mes_final + ',\n' )
        namelist.append("  end_day = " + v_dia_final + ', ' + v_dia_final + ', ' + v_dia_final + ',\n' )
        namelist.append("  end_hour = " + v_hora_final + ', ' + v_hora_final + ', ' + v_hora_final + ',\n' )
        namelist.append("  end_minute = 00, 00, 00, \n" )
        namelist.append("  end_second = 00, 00, 00, \n" )
        namelist.append("  interval_seconds = " + self.configReg.get ( "CONFIG", "p_interval_seconds" ) + '\n')
         #Para versoes incompativeis com o WRFDA
        #namelist.append("  force_use_old_data=T,\n")
        namelist.append("  input_from_file = .true., .true., .true.,\n")
        namelist.append("  history_interval = " + self.configReg.get ( "CONFIG", "history_interval" ) + '\n')
        namelist.append("  frames_per_outfile = 1000, 1000, 1000,\n")
        namelist.append("  restart = .false.,\n  restart_interval = 5000,\n  io_form_history = 2\n")
        namelist.append("  io_form_restart = 2\n  io_form_input = 2\n  io_form_boundary = 2\n")
        namelist.append("  debug_level = " + self.configReg.get('CONFIG','debug_level')+ "\n/")
        namelist.append("\n\n&domains\n" + "  time_step = " + self.configReg.get("CONFIG","p_time_step") + ',\n')
        namelist.append('  time_step_fract_num = 0,\n')
        namelist.append('  time_step_fract_den = 1,\n' )
        namelist.append('  max_dom = ' + self.configReg.get('CONFIG','p_maxDom') + ',\n')
        namelist.append('  e_we = ' + self.configReg.get('CONFIG','p_e_we') + '\n')
        namelist.append('  e_sn = ' + self.configReg.get('CONFIG','p_e_sn' ) + '\n' )
        namelist.append('  s_vert = 1, 1, 1,\n' + '  e_vert = ' + self.configReg.get('CONFIG','p_e_vert') + '\n' + '  p_top_requested = 5000,\n')
        namelist.append('  num_metgrid_levels = 34,\n' + '  num_metgrid_soil_levels = 4,\n')
        namelist.append('  dx = ' + self.configReg.get ( 'CONFIG', 'p_d_dx' ) + '\n' )
        namelist.append('  dy = ' + self.configReg.get ( 'CONFIG', 'p_d_dy' ) + '\n' )
        namelist.append('  grid_id = 1, 2, 3,\n')
        namelist.append('  parent_id = ' + self.configReg.get('CONFIG','p_parent_id' ) + '\n' )
        namelist.append('  i_parent_start = ' + self.configReg.get ('CONFIG', 'p_i_parent_start' ) + '\n' )
        namelist.append('  j_parent_start = ' + self.configReg.get ('CONFIG', 'p_j_parent_start' ) + '\n' )
        namelist.append('  parent_grid_ratio = ' + self.configReg.get ('CONFIG', 'p_parent_grid_ratio' ) + '\n' )
        namelist.append('  parent_time_step_ratio = 1, 3, 3,\n  feedback = 1,\n')
        namelist.append('  smooth_option = 0\n/\n')
        #namelist.append('  use_adaptive_time_step=.true.,\n')
        #namelist.append('  step_to_output_time=.true.,\n')
        #namelist.append('  target_cfl =1.2,1.2,\n')
        #namelist.append('  max_step_increase_pct = 5,5,1,\n')
        #namelist.append('  starting_time_step = -1,-1,\n')
        #namelist.append('  starting_time_step = 90,\n')
        #namelist.append('  max_time_step =1,-1,\n')
        #namelist.append('  max_time_step = 90,\n')
        #namelist.append('  min_time_step =-1,-1,\n')
        #namelist.append('  min_time_step = 90,\n/\n')
        namelist.append('\n&physics\n  mp_physics = ' + self.configReg.get('CONFIG','p_mp_physics') + '\n  ra_lw_physics = 5, 5, 5,\n  ra_sw_physics = 5, 5, 5,\n')
        namelist.append('  radt = ' + self.configReg.get('CONFIG','p_radt') + ', ' + self.configReg.get('CONFIG','p_radt') + ', ')
        namelist.append( self.configReg.get('CONFIG','p_radt') + ',\n  sf_sfclay_physics = 1, 1, 1,\n')
        namelist.append('  sf_surface_physics = 2, 2, 2,\n  bl_pbl_physics = 1, 1, 1,\n  bldt = 0, 0, 0,\n')
        namelist.append('  cu_physics = 1, 1, 1,\n  cudt = 5, 5, 5,\n  isfflx = 1,\n  ifsnow = 0,\n  icloud = 1,\n')
        namelist.append('  surface_input_source = 1,\n  num_soil_layers = 4,\n  num_land_cat = 21\n')
        namelist.append('  sf_urban_physics = 0, 0, 0,\n  maxiens = 1,\n')
        namelist.append('  maxens = 3,\n  maxens2 = 3,\n  maxens3 = 16,\n  ensdim = 144,\n/')
        namelist.append('\n\n&dynamics\n  w_damping = 0,\n  diff_opt = 1,\n  km_opt = 4,\n')
        namelist.append('  diff_6th_opt = 0,\n  diff_6th_factor = 0.12,\n  base_temp = 290.\n')
        namelist.append('  damp_opt = 0,\n')
        # Para versões incompativeis com WRFDA
        #namelist.append('  use_theta_m=0,\n')
        namelist.append('  zdamp = 5000., 5000., 5000.,\n  dampcoef = 0.2, 0.2, 0.2,\n')
        namelist.append('  khdif = 0, 0, 0,\n  kvdif = 0, 0, 0,\n  non_hydrostatic = .true., .true., .true.,\n')
        namelist.append('  moist_adv_opt = 1,\n  scalar_adv_opt = 1,\n/\n')
        namelist.append('\n')
        namelist.append('&bdy_control\n  spec_bdy_width = 5,\n  spec_zone = 1,\n  relax_zone = 4,\n')
        namelist.append('  specified = .true., .false., .false.,\n  nested = .false., .true., .true.,\n/\n')
        namelist.append('\n&namelist_quilt\n  nio_tasks_per_group = 0,\n  nio_groups = 1,\n/')
        namelist.append('\n')
        arq_namelist.writelines(namelist)
        arq_namelist.close()

    def criaNamelistARWPost(self,dominio):
        print("Cria ARWPost : d" + str(dominio))
        arq_namelist = open(self.configReg.get("WRF","dir_arw") + '/namelist.ARWpost','w')
        namelist = []
        namelist.append('&datetime\n')
        namelist.append("  start_date = '" + v_ano_ini + '-' + v_mes_ini + '-' + v_dia_ini + '_' + v_hora_ini + ":00:00'\n")
        namelist.append("  end_date = '" + v_ano_final + '-' + v_mes_final + '-' + v_dia_final + '_' + v_hora_final + ":00:00'")
        namelist.append("\n  interval_seconds = " + self.configReg.get ( "CONFIG", "p_interval_seconds" ) + '\n')
        namelist.append("  tacc = 0\n  debug_level = 0\n/")
        namelist.append("\n\n&io\n  io_from_input = 2,\n")
        namelist.append("  input_root_name = '" + self.configReg.get("WRF","dir_arw") + '/wrfout_d0' + str(dominio) + '_' 
                    + v_start_date + "'\n")
        namelist.append("  output_root_name = './wrfd" + str(dominio) + "_" + v_data_ini + v_hora_ini + "'")
        namelist.append("\n\n  plot = 'list'\n\n")
        namelist.append("  fields = 'U,V,W,NEST_POS,Q2,T2,TH2,PSFC,U10,V10,QVAPOR,QCLOUD,QRAIN,SST,HGT,RAINC," +
        "RAINNC,SNOWNC,GRAUPELNC,HAILNC,CLDFRA,OLR,UST,PBLH,geopt,height,tc,theta,td,td2,rh,rh2,wspd,wdir,ws10,"+
        "wd10,slp,dbz,cape,cin,mcape,mcin,lcl,lfc,clfr,dbz,max_dbz'")
        namelist.append("\n\n  output_type = 'grads'")
        namelist.append("\n\n  mercator_defs = .true.")
        namelist.append("\n/")
        namelist.append("\n\n&interp")
        namelist.append("\n  interp_method = 1")
        namelist.append("\n  interp_levels = 1000.,975.,950.,925.,900.,850.,800.,750.,700.,650.,600.,550.,500.,450.,400.,350.,300.,250.,200.,150.,100.,50. ")
        namelist.append("\n/\n")
        arq_namelist.writelines(namelist)
        arq_namelist.close()

    def criaNamelistInputDA(self,dominio):
        print("Cria Namelist DA : d" + str(dominio))
        arq_namelist = open(self.configReg.get("WRF","dir_assimilacao") + '/namelist.input','w')
        namelist = []
        namelist.append('&wrfvar1\n')
        namelist.append('var4d=false,\n')
        namelist.append('print_detail_grad=false,\n')
        namelist.append('/\n')
        namelist.append('&wrfvar2\n')
        namelist.append('/\n')
        namelist.append('&wrfvar3\n')
        namelist.append('ob_format=' + self.configReg.get("CONFIG","ob_format") + ',\n')
        namelist.append('/\n')
        namelist.append('&wrfvar4\n')
        namelist.append('/\n')
        namelist.append('&wrfvar5\n')
        namelist.append('/\n')
        namelist.append('&wrfvar6\n')
        namelist.append('max_ext_its=1,\n')
        namelist.append('ntmax=50,\n')
        namelist.append('orthonorm_gradient=true,\n')
        namelist.append('/\n')
        namelist.append('&wrfvar7\n')
        namelist.append('cv_options=3,\n')
        namelist.append('/\n')
        namelist.append('&wrfvar8\n')
        namelist.append('/\n')
        namelist.append('&wrfvar9\n')
        namelist.append('/\n')
        namelist.append('&wrfvar10\n')
        namelist.append('test_transforms=false,\n')
        namelist.append('test_gradient=false,\n')
        namelist.append('/\n')
        namelist.append('&wrfvar11\n')
        namelist.append('/\n')
        namelist.append('&wrfvar12\n')
        namelist.append('/\n')
        namelist.append('&wrfvar13\n')
        namelist.append('/\n')
        namelist.append('&wrfvar14\n')
        namelist.append('/\n')
        namelist.append('&wrfvar15\n')
        namelist.append('/\n')
        namelist.append('&wrfvar16\n')
        namelist.append('/\n')
        namelist.append('&wrfvar17\n')
        namelist.append('/\n')
        namelist.append('&wrfvar18\n')
        namelist.append('analysis_date="' + v_ano_ini + '-' + v_mes_ini + '-' + v_dia_ini + '_' + v_hora_ini + ':00:00.0000",\n')
        #analysis_date="2020-06-03_12:00:00.0000",
        namelist.append('/\n')
        namelist.append('&wrfvar19\n')
        namelist.append('/\n')
        namelist.append('&wrfvar20\n')
        namelist.append('/\n')
        namelist.append('&wrfvar21')
        namelist.append('time_window_min="' + v_ano_ini + '-' + v_mes_ini + '-' + v_dia_ini + '_' + v_hora_ini + ':00:00.0000",\n')
        #time_window_min="2020-06-03_00:00:00.0000",
        namelist.append('/\n')
        namelist.append('&wrfvar22\n')
        namelist.append('time_window_max="' + v_ano_final + '-' + v_mes_final + '-' + v_dia_final + '_' + v_hora_final + ':00:00.0000",\n')
        #time_window_max="2020-06-03_18:00:00.0000",
        namelist.append('/\n')
        namelist.append('&time_control\n')
        namelist.append('start_year=' + v_ano_ini + ',\n')  #start_year=2020,
        namelist.append('start_month=' + v_mes_ini + ',\n') #start_month=06,
        namelist.append('start_day=' + v_dia_ini + ',\n') #start_day=03,
        namelist.append('start_hour=' + v_hora_ini + ',\n') #start_hour=12,
        namelist.append('end_year=' + v_ano_final + ',\n') #end_year=2020,
        namelist.append('end_month=' + v_mes_final + ',\n') #end_month=06,
        namelist.append('end_day=' + v_dia_final + ',\n') #end_day=03,
        namelist.append('end_hour=' + v_hora_final + ',\n') #end_hour=18,
        namelist.append('/\n')
        namelist.append('&fdda\n')
        namelist.append('/\n')
        namelist.append('&domains\n')
        namelist.append('e_we= ' + self.configReg.get("CONFIG","p_e_we").split(',')[int(dominio)-1] + ',\n')
        namelist.append('e_sn= ' + self.configReg.get("CONFIG","p_e_sn").split(',')[int(dominio)-1] + ',\n')
        namelist.append('e_vert= ' + self.configReg.get("CONFIG","p_e_vert").split(',')[int(dominio)-1] + ',\n')
        namelist.append('dx= ' + self.configReg.get("CONFIG","p_d_dx").split(',')[int(dominio)-1] + ',\n')
        namelist.append('dy= ' + self.configReg.get("CONFIG","p_d_dy").split(',')[int(dominio)-1] + ',\n')
        namelist.append('/\n')
        namelist.append('&dfi_control\n')
        namelist.append('/\n')
        namelist.append('&tc\n')
        namelist.append('/\n')
        namelist.append('&physics\n')
        namelist.append('mp_physics=10,\n')
        namelist.append('ra_lw_physics=5,\n')
        namelist.append('ra_sw_physics=5,\n')
        namelist.append('radt=' + self.configReg.get("CONFIG","p_radt") + ',\n')
        namelist.append('sf_sfclay_physics=1,\n')
        namelist.append('sf_surface_physics=2,\n')
        namelist.append('bl_pbl_physics=1,\n')
        namelist.append('cu_physics=93,\n')
        namelist.append('cudt=5,\n')
        namelist.append('num_soil_layers=5,\n')
        namelist.append('mp_zero_out=2,\n')
        namelist.append('co2tf=0,\n')
        namelist.append('/\n')
        namelist.append('&scm\n')
        namelist.append('/\n')
        namelist.append('&dynamics\n')
        namelist.append('/\n')
        namelist.append('&bdy_control\n')
        namelist.append('/\n')
        namelist.append('&grib2\n')
        namelist.append('/\n')
        namelist.append('&fire\n')
        namelist.append('/\n')
        namelist.append('&namelist_quilt')
        namelist.append('/\n')
        namelist.append('&perturbation')
        namelist.append('/\n')
        arq_namelist.writelines(namelist)
        arq_namelist.close()

# -------------------------------------------------------------------------------------------------
def cria_namelist_WPS(fs_namelist_file, f_config, f_data):
    """
    gera o arquivo namelist.wps utilizado na execução do módulo WPS
    """
    # CONFIG section
    l_cfg = f_config["CONFIG"]
    assert l_cfg

    # WRF section
    l_wrf = f_config["WRF"]
    assert l_wrf

    # data section
    l_date = f_data["data"]
    assert l_date

    # cria o namelist
    with open(fs_namelist_file, 'w') as lfh:
        # gera o namelist
        lfh.write(f"&share\n")
        lfh.write(f"  wrf_core = 'ARW',\n")
        lfh.write(f"  max_dom = {l_cfg['p_maxdom']},\n")
        lfh.write(f"  start_date = '{l_date['ano_ini']}-{l_date['mes_ini']}-{l_date['dia_ini']}_{l_date['hora_ini']}:00:00',")
        lfh.write(f"'{l_date['ano_ini']}-{l_date['mes_ini']}-{l_date['dia_ini']}_{l_date['hora_ini']}:00:00',")
        lfh.write(f"'{l_date['ano_ini']}-{l_date['mes_ini']}-{l_date['dia_ini']}_{l_date['hora_ini']}:00:00',\n")
        lfh.write(f"  end_date = '{l_date['ano_final']}-{l_date['mes_final']}-{l_date['dia_final']}_{l_date['hora_final']}:00:00',")
        lfh.write(f"'{l_date['ano_final']}-{l_date['mes_final']}-{l_date['dia_final']}_{l_date['hora_final']}:00:00',")
        lfh.write(f"'{l_date['ano_final']}-{l_date['mes_final']}-{l_date['dia_final']}_{l_date['hora_final']}:00:00',\n")
        lfh.write(f"  interval_seconds = {l_cfg['p_interval_seconds']}\n")
        lfh.write(f"  io_form_geogrid = 2,\n")
        lfh.write(f"  debug_level = 0,\n/")
        lfh.write(f"\n\n")
        lfh.write(f"&geogrid\n")
        lfh.write(f"  parent_id = {l_cfg['p_parent_id']}\n")
        lfh.write(f"  parent_grid_ratio = {l_cfg['p_parent_grid_ratio']}\n")
        lfh.write(f"  i_parent_start = {l_cfg['p_i_parent_start']}\n")
        lfh.write(f"  j_parent_start = {l_cfg['p_j_parent_start']}\n")
        lfh.write(f"  e_we = {l_cfg['p_e_we']}\n")
        lfh.write(f"  e_sn = {l_cfg['p_e_sn']}\n")
        lfh.write(f"  geog_data_res = {l_cfg['p_geog_data_res']}\n")
        lfh.write(f"  dx = {l_cfg['p_dx']}\n")
        lfh.write(f"  dy = {l_cfg['p_dy']}\n")
        lfh.write(f"  map_proj = 'mercator',\n")
        lfh.write(f"  ref_lat = {l_cfg['p_ref_lat']}\n")
        lfh.write(f"  ref_lon = {l_cfg['p_ref_lon']}\n")
        lfh.write(f"  truelat1 = 0.0,\n")
        lfh.write(f"  truelat2 = 0.0,\n")
        lfh.write(f"  stand_lon = {l_cfg['p_ref_lon']}\n")
        lfh.write(f"  geog_data_path = '{l_wrf['DIR_WRF_GEOG']}'\n/")
        lfh.write(f"\n\n")
        lfh.write(f"&ungrib\n")
        lfh.write(f"  out_format = 'WPS',\n")
        lfh.write(f"  prefix = 'GFS2',\n/")
        lfh.write(f"\n\n")
        lfh.write(f"&metgrid\n")
        lfh.write(f"  fg_name = 'GFS2',\n")
        lfh.write(f"  io_form_metgrid = 2,\n")
        lfh.write(f"  opt_output_from_metgrid_path = '{l_wrf['dir_wrf_exec']}'\n/")
        lfh.write(f"\n")

# < the end >--------------------------------------------------------------------------------------
        