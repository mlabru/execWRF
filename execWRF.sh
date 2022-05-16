#!/bin/bash

# language
# export LANGUAGE=pt_BR

# nome do computador
HOST=`hostname`

# get today's date
TDATE=`date '+%Y-%m-%d_%H-%M-%S'`

# get all command line arguments
CMDLIN=( $@ )

# length of array
CLLEN=${#CMDLIN[@]}

# email
EMAIL=${CMDLIN[$CLLEN-1]}

# parameters (data ini, data fim, região)
PARMS=${CMDLIN[@]:0:$CLLEN-1}

# token (parameters sem espaços)
TOKEN="$(echo -e "${PARMS}" | tr -d '[:space:]')"

# CLSim directory
CLSIM=~/clsim

# home directory exists ?
if [ -d ${CLSIM} ]; then
    # set home dir
    cd ${CLSIM}
fi

# set PYTHONPATH
export PYTHONPATH="$PWD/."

# log warning
echo "[`date`]: starting process execWRF..."
# executa a aplicação (-OO)
python3 execWRF/exec_wrf.py $@ > logs/execWRF.$HOST.$TDATE.$TOKEN.log 2>&1
