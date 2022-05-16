# -*- coding: utf-8 -*-
"""
exc_defs

2022.apr  mlabru  change literal_eval to pass on github pytest
2022.apr  mlabru  change to dotenv
2021.may  mlabru  initial version (Linux/Python)
"""
# < imports >----------------------------------------------------------------------------------

# python library
import ast
import logging
import os

# .env
import dotenv

# < environment >------------------------------------------------------------------------------

# take environment variables from .env
dotenv.load_dotenv()

# NCAR login
DDCT_VALUES = os.getenv("DDCT_VALUES")

if DDCT_VALUES:
    # eval dict
    DDCT_VALUES = ast.literal_eval(DDCT_VALUES)

# < defines >----------------------------------------------------------------------------------

# logging level
DI_LOG_LEVEL = logging.DEBUG
# DI_LOG_LEVEL = logging.WARNING

# intervalo de previsão
DI_INTERVALO = 6

# WFR home dir
DS_WRF_HOME = os.path.expanduser("~/WRF")

# < the end >----------------------------------------------------------------------------------
