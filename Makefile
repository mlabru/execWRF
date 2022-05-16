###
# target systems
TARGET_SYS = ./execWRF

###
# config

# poetry
POETRY = poetry run

# autopep8 flags
AUTOPEP8_FLAGS = --diff --recursive --max-line-length=96 --ignore=E302,E305,E501
# --max-doc-length=90 --statistics

# original
FLAKE8_FLAGS0 = --ignore=W503,E501
# stop the build if there are Python syntax errors or undefined names
FLAKE8_FLAGS1 = --count --select=E9,F63,F7,F82 --show-source --statistics
# exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
FLAKE8_FLAGS2 = --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
# ignores
FLAKE8_IGNORE = --ignore=E302,E305,E501,W503

# isort flags
ISORT_FLAGS = --profile=black --lines-after-import=1

# pylint flags
PYLINT_FLAGS = x

###
## @ ajuda
.PHONY: ajuda

ajuda:
	@${POETRY} python ajuda.py

###
## @ instalação
.PHONY: instalar

instalar:  ## instala programa usando poetry, poetry precisa estar instalado
	poetry install

###
## @ auditagem
.PHONY: audit safety audits  ## verifica vulnerabilidades

audit:
	${POETRY} pip-audit

safety:
	${POETRY} safety check

audits: audit safety

###
## @ análise
.PHONY: autopep8 flake misort mypy pylint analise

autopep8:
	${POETRY} autopep8 ${AUTOPEP8_FLAGS} ${TARGET_SYS}

flake:
	${POETRY} flake8 ${FLAKE8_FLAGS1} ${TARGET_SYS}
	${POETRY} flake8 ${FLAKE8_FLAGS2} ${FLAKE8_IGNORE} ${TARGET_SYS}

misort:
	${POETRY} isort ${ISORT_FLAGS} --check --diff ${TARGET_SYS}

mypy:
	${POETRY} mypy ${TARGET_SYS}

pylint:
	${POETRY} pylint ${TARGET_SYS}

analise: autopep8 flake misort mypy pylint  ## roda analise estática

###
## @ formatação
.PHONY: black isort formatar

black:
	${POETRY} black ${TARGET_SYS}

isort:
	${POETRY} isort ${ISORT_FLAGS} ${TARGET_SYS}

# formatar: isort black  ## roda formatação nos arquivos

###
## @ testes
.PHONY: cover pytest testes

cover:  ## roda testes de cobertura
	${POETRY} pytest -v --cov=. --cov-report=html

pytest:  ## roda testes
	${POETRY} pytest -v

testes: pytest cover  # roda todos os testes

# < the end >----------------------------------------------------------------------------------
