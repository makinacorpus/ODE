dev_requirements:
	pip install -r dev_requirements.txt

requirements:
	pip install -r requirements.txt

localization:
	python setup.py compile_catalog -l fr

develop: localization requirements
	pip install -r dev_requirements.txt
	python setup.py develop
	initialize_ode_db development.ini

production:
	python setup.py develop
	../env/bin/initialize_ode_db production.ini
	python setup.py compile_catalog -l fr

test: localization requirements dev_requirements flake8
	nosetests -v

coverage: dev_requirements
	nosetests --cover-package=ode --cover-inclusive --cover-erase --with-coverage --cover-branches --cover-tests ode

start: $(PROC) .env
	$(PROC) start -f $(PROCFILE)

backup:
	#TODO

serve:
	pserve development.ini --reload

flake8: $(FLAKE8)
	flake8 ode

.PHONY: docs
docs:
	cd docs && make html

harvest:
	harvest development.ini

database:
	sudo su postgres -c 'createuser --pwprompt --no-superuser --no-createrole --no-createdb ode'
	sudo su postgres -c 'createdb --owner ode --encoding=utf8 --template=template0 ode'
