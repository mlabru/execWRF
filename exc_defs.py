# -*- coding: utf-8 -*-
"""
exc_defs

2021/may  1.0  mlabru  initial version (Linux/Python)
"""
# < imports >--------------------------------------------------------------------------------------

# python library
import ast
import logging
import os

# .env
from dotenv import load_dotenv

# < environment >------------------------------------------------------------------------------

# take environment variables from .env
load_dotenv()

# NCAR login
DDCT_VALUES = ast.literal_eval(os.getenv("DDCT_VALUES"))

# < defines >--------------------------------------------------------------------------------------

# logging level
DI_LOG_LEVEL = logging.DEBUG
# DI_LOG_LEVEL = logging.WARNING

# intervalo de previsão
DI_INTERVALO = 6

# WFR home dir
DS_WRF_HOME = os.path.expanduser("~/WRF")

# < the end >--------------------------------------------------------------------------------------
