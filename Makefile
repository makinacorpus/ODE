# virtualenv_wrapper compatible names
VIRTUALENVWRAPPER_VIRTUALENV?=virtualenv
VIRTUAL_ENV?=venv

PYTHON=$(VIRTUAL_ENV)/bin/python
PIP=$(VIRTUAL_ENV)/bin/pip
COVERAGE=$(VIRTUAL_ENV)/bin/coverage
NOSE=$(VIRTUAL_ENV)/bin/nose

PROC=$(VIRTUAL_ENV)/bin/honcho
PROCFILE=Procfile

$(PYTHON):
	$(VIRTUALENV) $(VIRTUAL_ENV)

$(PROC): virtualenv
	$(PIP) install honcho

$(NOSE): virtualenv
	$(PIP) install nose

$(COVERAGE): virtualenv
	$(PIP) install coverage

$(FLAKE8): virtualenv
	$(PIP) install flake8

.env:
	echo "PYTHON=$(PYTHON)" > .env

virtualenv: $(PYTHON)

requirements: virtualenv
	$(PIP) install -r requirements.txt

dev_requirements:
	$(PIP) install -r dev_requirements.txt

install: requirements
	$(PYTHON) manage.py syncdb --noinput

develop:
	python setup.py develop

test: $(NOSE) $(COVERAGE) flake8
	nosetests

coverage: $(NOSE) $(COVERAGE)
	nosetests --cover-package=ode --cover-inclusive --cover-erase --with-coverage --cover-branches --cover-tests

start: $(PROC) .env
	$(PROC) start -f $(PROCFILE)

backup:
	#TODO

serve:
	pserve development.ini --reload

flake8: $(FLAKE8)
	flake8 ode
