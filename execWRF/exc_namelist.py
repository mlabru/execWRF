# -*- coding: utf-8 -*-
"""
exc_namelist

2021.nov  eliana  initial version (Linux/Python)
"""
# < imports >----------------------------------------------------------------------------------

# python library
import logging

# local
import execWRF.exc_defs as df

# < logging >----------------------------------------------------------------------------------

# logger
M_LOG = logging.getLogger(__name__)
M_LOG.setLevel(df.DI_LOG_LEVEL)

# ---------------------------------------------------------------------------------------------
def cria_namelist_arwpost(fs_namelist_file, f_config, f_data, fi_dom):
    """
    gera o arquivo namelist.ARWpost utilizado na execução do módulo ARWpost
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
    with open(fs_namelist_file, "w", encoding="utf-8") as lfh:
        # gera o namelist
        lfh.write("&datetime\n")
        lfh.write(f"  start_date = '{l_date['ano_ini']}-{l_date['mes_ini']}-{l_date['dia_ini']}_{l_date['hora_ini']}:00:00'\n")
        lfh.write(f"  end_date = '{l_date['ano_final']}-{l_date['mes_final']}-{l_date['dia_final']}_{l_date['hora_final']}:00:00'\n")
        lfh.write(f"  interval_seconds = {l_cfg['p_interval_seconds']}\n")
        lfh.write("  tacc = 0\n")
        lfh.write("  debug_level = 0\n/")
        lfh.write("\n")
        lfh.write("&io\n")
        lfh.write("  io_from_input = 2,\n")
        lfh.write(f"  input_root_name = '{l_wrf['dir_arw']}/wrfout_d0{str(fi_dom)}_{l_date['ano_ini']}-{l_date['mes_ini']}-{l_date['dia_ini']}_{l_date['hora_ini']}:00:00'\n")
        lfh.write(f"  output_root_name = './wrfd{str(fi_dom)}_{l_date['ano_ini']}{l_date['mes_ini']}{l_date['dia_ini']}{l_date['hora_ini']}'\n")
        lfh.write("  plot = 'list'\n")
        lfh.write("  fields = 'U,V,W,NEST_POS,Q2,T2,TH2,PSFC,U10,V10,QVAPOR,QCLOUD,QRAIN,SST,HGT,RAINC,RAINNC,SNOWNC,GRAUPELNC,HAILNC,CLDFRA,OLR,UST,PBLH,geopt,height,tc,theta,td,td2,rh,rh2,wspd,wdir,ws10,wd10,slp,dbz,cape,cin,mcape,mcin,lcl,lfc,clfr,dbz,max_dbz'\n")
        lfh.write("  output_type = 'grads'\n")
        lfh.write("  mercator_defs = .true.\n/")
        lfh.write("\n")
        lfh.write("&interp\n")
        lfh.write("  interp_method = 1\n")
        lfh.write("  interp_levels = 1000.,975.,950.,925.,900.,850.,800.,750.,700.,650.,600.,550.,500.,450.,400.,350.,300.,250.,200.,150.,100.,50.\n/")
        lfh.write("\n")

# ---------------------------------------------------------------------------------------------
def cria_namelist_wps(fs_namelist_file, f_config, f_data):
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
    with open(fs_namelist_file, "w", encoding="utf-8") as lfh:
        # gera o namelist
        lfh.write("&share\n")
        lfh.write("  wrf_core = 'ARW',\n")
        lfh.write(f"  max_dom = {l_cfg['p_maxdom']},\n")
        lfh.write(f"  start_date = '{l_date['ano_ini']}-{l_date['mes_ini']}-{l_date['dia_ini']}_{l_date['hora_ini']}:00:00',")
        lfh.write(f" '{l_date['ano_ini']}-{l_date['mes_ini']}-{l_date['dia_ini']}_{l_date['hora_ini']}:00:00',")
        lfh.write(f" '{l_date['ano_ini']}-{l_date['mes_ini']}-{l_date['dia_ini']}_{l_date['hora_ini']}:00:00',\n")
        lfh.write(f"  end_date = '{l_date['ano_final']}-{l_date['mes_final']}-{l_date['dia_final']}_{l_date['hora_final']}:00:00',")
        lfh.write(f" '{l_date['ano_final']}-{l_date['mes_final']}-{l_date['dia_final']}_{l_date['hora_final']}:00:00',")
        lfh.write(f" '{l_date['ano_final']}-{l_date['mes_final']}-{l_date['dia_final']}_{l_date['hora_final']}:00:00',\n")
        lfh.write(f"  interval_seconds = {l_cfg['p_interval_seconds']}\n")
        lfh.write("  io_form_geogrid = 2,\n")
        lfh.write("  debug_level = 0,\n/")
        lfh.write("\n")
        lfh.write("&geogrid\n")
        lfh.write(f"  parent_id = {l_cfg['p_parent_id']}\n")
        lfh.write(f"  parent_grid_ratio = {l_cfg['p_parent_grid_ratio']}\n")
        lfh.write(f"  i_parent_start = {l_cfg['p_i_parent_start']}\n")
        lfh.write(f"  j_parent_start = {l_cfg['p_j_parent_start']}\n")
        lfh.write(f"  e_we = {l_cfg['p_e_we']}\n")
        lfh.write(f"  e_sn = {l_cfg['p_e_sn']}\n")
        lfh.write(f"  geog_data_res = {l_cfg['p_geog_data_res']}\n")
        lfh.write(f"  dx = {l_cfg['p_dx']}\n")
        lfh.write(f"  dy = {l_cfg['p_dy']}\n")
        lfh.write("  map_proj = 'mercator',\n")
        lfh.write(f"  ref_lat = {l_cfg['p_ref_lat']}\n")
        lfh.write(f"  ref_lon = {l_cfg['p_ref_lon']}\n")
        lfh.write("  truelat1 = 0.0,\n")
        lfh.write("  truelat2 = 0.0,\n")
        lfh.write(f"  stand_lon = {l_cfg['p_ref_lon']}\n")
        lfh.write(f"  geog_data_path = '{l_wrf['dir_wrf_geog']}'\n/")
        lfh.write("\n")
        lfh.write("&ungrib\n")
        lfh.write("  out_format = 'WPS',\n")
        lfh.write("  prefix = 'GFS2',\n/")
        lfh.write("\n")
        lfh.write("&metgrid\n")
        lfh.write("  fg_name = 'GFS2',\n")
        lfh.write("  io_form_metgrid = 2,\n")
        lfh.write(f"  opt_output_from_metgrid_path = '{l_wrf['dir_wrf_exec']}'\n/")
        lfh.write("\n")

# ---------------------------------------------------------------------------------------------
def cria_namelist_wrf(fs_namelist_file, f_config, f_data):
    """
    gera o arquivo namelist.input utilizado na execução do WRF
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
    with open(fs_namelist_file, "w", encoding="utf-8") as lfh:
        # gera o namelist
        lfh.write("&time_control\n")
        lfh.write("  run_days = 0,\n")
        lfh.write(f"  run_hours = {l_wrf['horas']},\n")
        lfh.write("  run_minutes = 0,\n")
        lfh.write("  run_seconds = 0,\n")
        lfh.write(f"  start_year = {l_date['ano_ini']}, {l_date['ano_ini']}, {l_date['ano_ini']},\n")
        lfh.write(f"  start_month = {l_date['mes_ini']}, {l_date['mes_ini']}, {l_date['mes_ini']},\n")
        lfh.write(f"  start_day = {l_date['dia_ini']}, {l_date['dia_ini']}, {l_date['dia_ini']}, \n")
        lfh.write(f"  start_hour = {l_date['hora_ini']}, {l_date['hora_ini']}, {l_date['hora_ini']},\n")
        lfh.write("  start_minute = 00, 00, 00,\n")
        lfh.write("  start_second = 00, 00, 00,\n")
        lfh.write(f"  end_year = {l_date['ano_final']}, {l_date['ano_final']}, {l_date['ano_final']},\n")
        lfh.write(f"  end_month = {l_date['mes_final']}, {l_date['mes_final']}, {l_date['mes_final']},\n")
        lfh.write(f"  end_day = {l_date['dia_final']}, {l_date['dia_final']}, {l_date['dia_final']},\n")
        lfh.write(f"  end_hour = {l_date['hora_final']}, {l_date['hora_final']}, {l_date['hora_final']},\n")
        lfh.write("  end_minute = 00, 00, 00,\n")
        lfh.write("  end_second = 00, 00, 00,\n")
        lfh.write(f"  interval_seconds = {l_cfg['p_interval_seconds']}\n")
        # para versões incompatíveis com o WRFDA
        # lfh.write("  force_use_old_data = T,\n")
        lfh.write("  input_from_file = .true., .true., .true.,\n")
        lfh.write(f"  history_interval = {l_cfg['history_interval']}\n")
        lfh.write("  frames_per_outfile = 1000, 1000, 1000,\n")
        lfh.write("  restart = .false.,\n")
        lfh.write("  restart_interval = 5000,\n")
        lfh.write("  io_form_history = 2\n")
        lfh.write("  io_form_input = 2\n")
        lfh.write("  io_form_boundary = 2\n")
        lfh.write(f"  debug_level = {l_cfg['debug_level']}\n/")
        lfh.write("\n")
        lfh.write("&domains\n")
        lfh.write(f"  time_step = {l_cfg['p_time_step']},\n")
        lfh.write("  time_step_fract_num = 0,\n")
        lfh.write("  time_step_fract_den = 1,\n")
        lfh.write(f"  max_dom = {l_cfg['p_maxDom']},\n")
        lfh.write(f"  e_we = {l_cfg['p_e_we']}\n")
        lfh.write(f"  e_sn = {l_cfg['p_e_sn']}\n")
        lfh.write("  s_vert = 1, 1, 1,\n")
        lfh.write(f"  e_vert = {l_cfg['p_e_vert']}\n")
        lfh.write("  p_top_requested = 5000,\n")
        lfh.write(f"  num_metgrid_levels = {l_cfg['p_num_metgrid_levels']},\n")     # era 34
        lfh.write("  num_metgrid_soil_levels = 4,\n")
        lfh.write(f"  dx = {l_cfg['p_d_dx']}\n")
        lfh.write(f"  dy = {l_cfg['p_d_dy']}\n")
        lfh.write("  grid_id = 1, 2, 3,\n")
        lfh.write(f"  parent_id = {l_cfg['p_parent_id']}\n")
        lfh.write(f"  i_parent_start = {l_cfg['p_i_parent_start']}\n")
        lfh.write(f"  j_parent_start = {l_cfg['p_j_parent_start']}\n")
        lfh.write(f"  parent_grid_ratio = {l_cfg['p_parent_grid_ratio']}\n")
        lfh.write("  parent_time_step_ratio = 1, 3, 3,\n")
        lfh.write("  feedback = 1,\n")
        lfh.write("  smooth_option = 0,\n")
        lfh.write(f"  sfcp_to_sfcp = {l_cfg['p_sfcp_to_sfcp']}\n/")    # .true.
        lfh.write("\n")
        # lfh.write("  use_adaptive_time_step = .true.,\n")
        # lfh.write("  step_to_output_time = .true.,\n")
        # lfh.write("  target_cfl = 1.2, 1.2,\n")
        # lfh.write("  max_step_increase_pct = 5, 5, 1,\n")
        # lfh.write("  starting_time_step = -1, -1,\n")
        # lfh.write("  starting_time_step = 90,\n")
        # lfh.write("  max_time_step = 1, -1,\n")
        # lfh.write("  max_time_step = 90,\n")
        # lfh.write("  min_time_step = -1, -1,\n")
        # lfh.write("  min_time_step = 90,\n/")
        # lfh.write("\n")
        lfh.write("&physics\n")
        lfh.write(f"  mp_physics = {l_cfg['p_mp_physics']}\n")
        lfh.write("  ra_lw_physics = 5, 5, 5,\n")
        lfh.write("  ra_sw_physics = 5, 5, 5,\n")
        lfh.write(f"  radt = {l_cfg['p_radt']}, {l_cfg['p_radt']}, {l_cfg['p_radt']},\n")
        lfh.write("  sf_sfclay_physics = 1, 1, 1,\n")
        lfh.write("  sf_surface_physics = 2, 2, 2,\n")
        lfh.write("  bl_pbl_physics = 1, 1, 1,\n")
        lfh.write("  bldt = 0, 0, 0,\n")
        lfh.write("  cu_physics = 1, 1, 1,\n")
        lfh.write("  cudt = 5, 5, 5,\n")
        lfh.write("  isfflx = 1,\n")
        lfh.write("  ifsnow = 0,\n")
        lfh.write("  icloud = 1,\n")
        lfh.write("  surface_input_source = 1,\n")
        lfh.write("  num_soil_layers = 4,\n")
        lfh.write("  num_land_cat = 21\n")
        lfh.write("  sf_urban_physics = 0, 0, 0,\n")
        lfh.write("  maxiens = 1,\n")
        lfh.write("  maxens = 3,\n")
        lfh.write("  maxens2 = 3,\n")
        lfh.write("  maxens3 = 16,\n")
        lfh.write("  ensdim = 144,\n/")
        lfh.write("\n")
        lfh.write("&dynamics\n")
        lfh.write("  w_damping = 0,\n")
        lfh.write("  diff_opt = 1,\n")
        lfh.write("  km_opt = 4,\n")
        lfh.write("  diff_6th_opt = 0,\n")
        lfh.write("  diff_6th_factor = 0.12,\n")
        lfh.write("  base_temp = 290.\n")
        lfh.write("  damp_opt = 0,\n")
        # para versões incompatíveis com WRFDA
        # lfh.write("  use_theta_m = 0,\n")
        lfh.write("  zdamp = 5000., 5000., 5000.,\n")
        lfh.write("  dampcoef = 0.2, 0.2, 0.2,\n")
        lfh.write("  khdif = 0, 0, 0,\n")
        lfh.write("  kvdif = 0, 0, 0,\n")
        lfh.write("  non_hydrostatic = .true., .true., .true.,\n")
        lfh.write("  moist_adv_opt = 1,\n")
        lfh.write("  scalar_adv_opt = 1,\n/")
        lfh.write("\n")
        lfh.write("&bdy_control\n")
        lfh.write("  spec_bdy_width = 5,\n")
        lfh.write("  spec_zone = 1,\n")
        lfh.write("  relax_zone = 4,\n")
        lfh.write("  specified = .true., .false., .false.,\n")
        lfh.write("  nested = .false., .true., .true.,\n/")
        lfh.write("\n")
        lfh.write("&namelist_quilt\n")
        lfh.write("  nio_tasks_per_group = 0,\n")
        lfh.write("  nio_groups = 1,\n/")
        lfh.write("\n")

# < the end >----------------------------------------------------------------------------------
