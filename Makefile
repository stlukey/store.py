SHELL := /bin/bash
PRODUCTION=$(false)

VENV=.env

define env_run
	source configs/$(if $(PRODUCTION),production,development) &&\
    source $(VENV)/bin/activate && $(1)
endef

define run_script
	$(call env_run, python -m api.scripts.$(1))
endef

.PHONY: api mongodb
run: api

api: mongodb
	$(call env_run, python -m api)

clean: mongodb
	$(call run_script,create_data)

mongodb:
	mongo --eval "db.stats()" >/dev/null
