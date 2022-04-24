# -*- coding: utf-8 -*-
"""
exc_namelist

2021/nov  1.0  eliana  initial version (Linux/Python)
"""
# < imports >----------------------------------------------------------------------------------

# python library
import logging

# local
import exc_defs as df

# < logging >----------------------------------------------------------------------------------

# logger
M_LOG = logging.getLogger(__name__)
M_LOG.setLevel(df.DI_LOG_LEVEL)

# ---------------------------------------------------------------------------------------------
def cria_namelist_ARWPost(fs_namelist_file, f_config, f_data, fi_dom):
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
    with open(fs_namelist_file, "w") as lfh:
        # gera o namelist
        lfh.write(f"&datetime\n")
        lfh.write(f"  start_date = '{l_date['ano_ini']}-{l_date['mes_ini']}-{l_date['dia_ini']}_{l_date['hora_ini']}:00:00'\n")
        lfh.write(f"  end_date = '{l_date['ano_final']}-{l_date['mes_final']}-{l_date['dia_final']}_{l_date['hora_final']}:00:00'\n")
        lfh.write(f"  interval_seconds = {l_cfg['p_interval_seconds']}\n")
        lfh.write(f"  tacc = 0\n")
        lfh.write(f"  debug_level = 0\n/")
        lfh.write(f"\n")
        lfh.write(f"&io\n")
        lfh.write(f"  io_from_input = 2,\n")
        lfh.write(f"  input_root_name = '{l_wrf['dir_arw']}/wrfout_d0{str(fi_dom)}_{l_date['ano_ini']}-{l_date['mes_ini']}-{l_date['dia_ini']}_{l_date['hora_ini']}:00:00'\n")
        lfh.write(f"  output_root_name = './wrfd{str(fi_dom)}_{l_date['ano_ini']}{l_date['mes_ini']}{l_date['dia_ini']}{l_date['hora_ini']}'\n")
        lfh.write(f"  plot = 'list'\n")
        lfh.write(f"  fields = 'U,V,W,NEST_POS,Q2,T2,TH2,PSFC,U10,V10,QVAPOR,QCLOUD,QRAIN,SST,HGT,RAINC,RAINNC,SNOWNC,GRAUPELNC,HAILNC,CLDFRA,OLR,UST,PBLH,geopt,height,tc,theta,td,td2,rh,rh2,wspd,wdir,ws10,wd10,slp,dbz,cape,cin,mcape,mcin,lcl,lfc,clfr,dbz,max_dbz'\n")
        lfh.write(f"  output_type = 'grads'\n")
        lfh.write(f"  mercator_defs = .true.\n/")
        lfh.write(f"\n")
        lfh.write(f"&interp\n")
        lfh.write(f"  interp_method = 1\n")
        lfh.write(f"  interp_levels = 1000.,975.,950.,925.,900.,850.,800.,750.,700.,650.,600.,550.,500.,450.,400.,350.,300.,250.,200.,150.,100.,50.\n/")
        lfh.write(f"\n")

# ---------------------------------------------------------------------------------------------
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
    with open(fs_namelist_file, "w") as lfh:
        # gera o namelist
        lfh.write(f"&share\n")
        lfh.write(f"  wrf_core = 'ARW',\n")
        lfh.write(f"  max_dom = {l_cfg['p_maxdom']},\n")
        lfh.write(f"  start_date = '{l_date['ano_ini']}-{l_date['mes_ini']}-{l_date['dia_ini']}_{l_date['hora_ini']}:00:00',")
        lfh.write(f" '{l_date['ano_ini']}-{l_date['mes_ini']}-{l_date['dia_ini']}_{l_date['hora_ini']}:00:00',")
        lfh.write(f" '{l_date['ano_ini']}-{l_date['mes_ini']}-{l_date['dia_ini']}_{l_date['hora_ini']}:00:00',\n")
        lfh.write(f"  end_date = '{l_date['ano_final']}-{l_date['mes_final']}-{l_date['dia_final']}_{l_date['hora_final']}:00:00',")
        lfh.write(f" '{l_date['ano_final']}-{l_date['mes_final']}-{l_date['dia_final']}_{l_date['hora_final']}:00:00',")
        lfh.write(f" '{l_date['ano_final']}-{l_date['mes_final']}-{l_date['dia_final']}_{l_date['hora_final']}:00:00',\n")
        lfh.write(f"  interval_seconds = {l_cfg['p_interval_seconds']}\n")
        lfh.write(f"  io_form_geogrid = 2,\n")
        lfh.write(f"  debug_level = 0,\n/")
        lfh.write(f"\n")
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
        lfh.write(f"  geog_data_path = '{l_wrf['dir_wrf_geog']}'\n/")
        lfh.write(f"\n")
        lfh.write(f"&ungrib\n")
        lfh.write(f"  out_format = 'WPS',\n")
        lfh.write(f"  prefix = 'GFS2',\n/")
        lfh.write(f"\n")
        lfh.write(f"&metgrid\n")
        lfh.write(f"  fg_name = 'GFS2',\n")
        lfh.write(f"  io_form_metgrid = 2,\n")
        lfh.write(f"  opt_output_from_metgrid_path = '{l_wrf['dir_wrf_exec']}'\n/")
        lfh.write(f"\n")

# ---------------------------------------------------------------------------------------------
def cria_namelist_WRF(fs_namelist_file, f_config, f_data):
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
    with open(fs_namelist_file, "w") as lfh:
        # gera o namelist
        lfh.write(f"&time_control\n")
        lfh.write(f"  run_days = 0,\n")
        lfh.write(f"  run_hours = {l_wrf['horas']},\n")
        lfh.write(f"  run_minutes = 0,\n")
        lfh.write(f"  run_seconds = 0,\n")
        lfh.write(f"  start_year = {l_date['ano_ini']}, {l_date['ano_ini']}, {l_date['ano_ini']},\n")
        lfh.write(f"  start_month = {l_date['mes_ini']}, {l_date['mes_ini']}, {l_date['mes_ini']},\n")
        lfh.write(f"  start_day = {l_date['dia_ini']}, {l_date['dia_ini']}, {l_date['dia_ini']}, \n")
        lfh.write(f"  start_hour = {l_date['hora_ini']}, {l_date['hora_ini']}, {l_date['hora_ini']},\n")
        lfh.write(f"  start_minute = 00, 00, 00,\n")
        lfh.write(f"  start_second = 00, 00, 00,\n")
        lfh.write(f"  end_year = {l_date['ano_final']}, {l_date['ano_final']}, {l_date['ano_final']},\n")
        lfh.write(f"  end_month = {l_date['mes_final']}, {l_date['mes_final']}, {l_date['mes_final']},\n")
        lfh.write(f"  end_day = {l_date['dia_final']}, {l_date['dia_final']}, {l_date['dia_final']},\n")
        lfh.write(f"  end_hour = {l_date['hora_final']}, {l_date['hora_final']}, {l_date['hora_final']},\n")
        lfh.write(f"  end_minute = 00, 00, 00,\n")
        lfh.write(f"  end_second = 00, 00, 00,\n")
        lfh.write(f"  interval_seconds = {l_cfg['p_interval_seconds']}\n")
        # para versões incompatíveis com o WRFDA
        # lfh.write(f"  force_use_old_data = T,\n")
        lfh.write(f"  input_from_file = .true., .true., .true.,\n")
        lfh.write(f"  history_interval = {l_cfg['history_interval']}\n")
        lfh.write(f"  frames_per_outfile = 1000, 1000, 1000,\n")
        lfh.write(f"  restart = .false.,\n")
        lfh.write(f"  restart_interval = 5000,\n")
        lfh.write(f"  io_form_history = 2\n")
        lfh.write(f"  io_form_input = 2\n")
        lfh.write(f"  io_form_boundary = 2\n")
        lfh.write(f"  debug_level = {l_cfg['debug_level']}\n/")
        lfh.write(f"\n")
        lfh.write(f"&domains\n")
        lfh.write(f"  time_step = {l_cfg['p_time_step']},\n")
        lfh.write(f"  time_step_fract_num = 0,\n")
        lfh.write(f"  time_step_fract_den = 1,\n")
        lfh.write(f"  max_dom = {l_cfg['p_maxDom']},\n")
        lfh.write(f"  e_we = {l_cfg['p_e_we']}\n")
        lfh.write(f"  e_sn = {l_cfg['p_e_sn']}\n")
        lfh.write(f"  s_vert = 1, 1, 1,\n")
        lfh.write(f"  e_vert = {l_cfg['p_e_vert']}\n")
        lfh.write(f"  p_top_requested = 5000,\n")
        lfh.write(f"  num_metgrid_levels = 34,\n")
        lfh.write(f"  num_metgrid_soil_levels = 4,\n")
        lfh.write(f"  dx = {l_cfg['p_d_dx']}\n")
        lfh.write(f"  dy = {l_cfg['p_d_dy']}\n")
        lfh.write(f"  grid_id = 1, 2, 3,\n")
        lfh.write(f"  parent_id = {l_cfg['p_parent_id']}\n")
        lfh.write(f"  i_parent_start = {l_cfg['p_i_parent_start']}\n")
        lfh.write(f"  j_parent_start = {l_cfg['p_j_parent_start']}\n")
        lfh.write(f"  parent_grid_ratio = {l_cfg['p_parent_grid_ratio']}\n")
        lfh.write(f"  parent_time_step_ratio = 1, 3, 3,\n")
        lfh.write(f"  feedback = 1,\n")
        lfh.write(f"  smooth_option = 0\n/")
        lfh.write(f"\n")
        # lfh.write(f"  use_adaptive_time_step = .true.,\n")
        # lfh.write(f"  step_to_output_time = .true.,\n")
        # lfh.write(f"  target_cfl = 1.2, 1.2,\n")
        # lfh.write(f"  max_step_increase_pct = 5, 5, 1,\n")
        # lfh.write(f"  starting_time_step = -1, -1,\n")
        # lfh.write(f"  starting_time_step = 90,\n")
        # lfh.write(f"  max_time_step = 1, -1,\n")
        # lfh.write(f"  max_time_step = 90,\n")
        # lfh.write(f"  min_time_step = -1, -1,\n")
        # lfh.write(f"  min_time_step = 90,\n/")
        # lfh.write(f"\n")
        lfh.write(f"&physics\n")
        lfh.write(f"  mp_physics = {l_cfg['p_mp_physics']}\n")
        lfh.write(f"  ra_lw_physics = 5, 5, 5,\n")
        lfh.write(f"  ra_sw_physics = 5, 5, 5,\n")
        lfh.write(f"  radt = {l_cfg['p_radt']}, {l_cfg['p_radt']}, {l_cfg['p_radt']},\n")
        lfh.write(f"  sf_sfclay_physics = 1, 1, 1,\n")
        lfh.write(f"  sf_surface_physics = 2, 2, 2,\n")
        lfh.write(f"  bl_pbl_physics = 1, 1, 1,\n")
        lfh.write(f"  bldt = 0, 0, 0,\n")
        lfh.write(f"  cu_physics = 1, 1, 1,\n")
        lfh.write(f"  cudt = 5, 5, 5,\n")
        lfh.write(f"  isfflx = 1,\n")
        lfh.write(f"  ifsnow = 0,\n")
        lfh.write(f"  icloud = 1,\n")
        lfh.write(f"  surface_input_source = 1,\n")
        lfh.write(f"  num_soil_layers = 4,\n")
        lfh.write(f"  num_land_cat = 21\n")
        lfh.write(f"  sf_urban_physics = 0, 0, 0,\n")
        lfh.write(f"  maxiens = 1,\n")
        lfh.write(f"  maxens = 3,\n")
        lfh.write(f"  maxens2 = 3,\n")
        lfh.write(f"  maxens3 = 16,\n")
        lfh.write(f"  ensdim = 144,\n/")
        lfh.write(f"\n")
        lfh.write(f"&dynamics\n")
        lfh.write(f"  w_damping = 0,\n")
        lfh.write(f"  diff_opt = 1,\n")
        lfh.write(f"  km_opt = 4,\n")
        lfh.write(f"  diff_6th_opt = 0,\n")
        lfh.write(f"  diff_6th_factor = 0.12,\n")
        lfh.write(f"  base_temp = 290.\n")
        lfh.write(f"  damp_opt = 0,\n")
        # para versões incompatíveis com WRFDA
        # lfh.write(f"  use_theta_m = 0,\n")
        lfh.write(f"  zdamp = 5000., 5000., 5000.,\n")
        lfh.write(f"  dampcoef = 0.2, 0.2, 0.2,\n")
        lfh.write(f"  khdif = 0, 0, 0,\n")
        lfh.write(f"  kvdif = 0, 0, 0,\n")
        lfh.write(f"  non_hydrostatic = .true., .true., .true.,\n")
        lfh.write(f"  moist_adv_opt = 1,\n")
        lfh.write(f"  scalar_adv_opt = 1,\n/")
        lfh.write(f"\n")
        lfh.write(f"&bdy_control\n")
        lfh.write(f"  spec_bdy_width = 5,\n")
        lfh.write(f"  spec_zone = 1,\n")
        lfh.write(f"  relax_zone = 4,\n")
        lfh.write(f"  specified = .true., .false., .false.,\n")
        lfh.write(f"  nested = .false., .true., .true.,\n/")
        lfh.write(f"\n")
        lfh.write(f"&namelist_quilt\n")
        lfh.write(f"  nio_tasks_per_group = 0,\n")
        lfh.write(f"  nio_groups = 1,\n/")
        lfh.write(f"\n")

# < the end >----------------------------------------------------------------------------------
