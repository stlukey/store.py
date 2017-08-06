SHELL := /bin/bash
PRODUCTION=$(false)
TESTING=0

VENV=.env


define env_run
	source configs/$(if $(PRODUCTION),production,development) &&\
    source $(VENV)/bin/activate && FLASK_TESTING=$(2) $(1)
endef

define run_script
	$(call env_run, python -m api.scripts.$(1),0)
endef

.PHONY: api
run: api

test: silent_clean _test
_test:
	$(call env_run,python -m unittest -v api/tests/test_*.py,1)

api: mongodb
	$(call env_run, python -m api,0)

clean: mongodb
	$(call run_script,create_data)

silent_clean: mongodb
	$(call run_script,create_data) > /dev/null

mongodb:
	mongo --eval "db.stats()" >/dev/null
