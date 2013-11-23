dev_requirements:
	pip install -r dev_requirements.txt

develop:
	python setup.py develop

test: dev_requirements
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
