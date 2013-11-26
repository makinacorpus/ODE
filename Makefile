dev_requirements:
	pip install -r dev_requirements.txt

develop:
	pip install -r requirements.txt
	python setup.py develop
	initialize_ode_db development.ini

test: dev_requirements flake8
	nosetests -v

coverage: dev_requirements
	nosetests --cover-package=ode --cover-inclusive --cover-erase --with-coverage --cover-branches --cover-tests

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
