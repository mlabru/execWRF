# -*- coding: utf-8 -*-
"""
exc_defs

2021/may  1.0  mlabru  initial version (Linux/Python)
"""
# < imports >--------------------------------------------------------------------------------------

# python library
import logging

# < defines >--------------------------------------------------------------------------------------

# logging level
DI_LOG_LEVEL = logging.DEBUG
# DI_LOG_LEVEL = logging.WARNING

# intervalo de previsão
DI_INTERVALO = 6

# WFR home dir
DS_WRF_HOME = os.path.expanduser("~/WRF")

# -------------------------------------------------------------------------------------------------
import imp

# open secrets files
with open(".hidden/cls_secrets.py", "rb") as lfh:
    # import module
    hs = imp.load_module(".hidden", lfh, ".hidden/cls_secrets", (".py", "rb", imp.PY_SOURCE))

# < the end >--------------------------------------------------------------------------------------
