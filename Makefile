# Makefile for splunk_graphite.
#
# Author:: Greg Albrecht <oss@undef.net>
# Copyright:: Copyright 2016 Orion Labs, Inc.
# License:: Apache License, Version 2.0
# Source:: https://github.com/OnBeep/splunk_graphite
#


.DEFAULT_GOAL := build

SPLUNK_PKG ?= splunk-6.0.2-196940-Linux-x86_64.tgz
SPLUNK_ADMIN_PASSWORD ?= okchanged
SPLUNKWEB_PORT ?= 4180
SPLUNKD_PORT ?= 4189


install_requirements:
	pip install -r requirements.txt --use-mirrors

build: clean
	@tar -X .tar_exclude -s /\.\.\// -zcf splunk_graphite.spl ../splunk_graphite

lint:
	pylint --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" \
	 -r n bin/*.py tests/*.py || exit 0

flake8:
	flake8 --max-complexity 12 --exit-zero bin/*.py tests/*.py

pep8: flake8

nosetests:
	nosetests tests

test: install_requirements splunk_module lint flake8 nosetests

install: build
	vagrant ssh -c 'sudo /opt/splunk/bin/splunk install app /vagrant/splunk_graphite.spl -update true -auth admin:$(SPLUNK_ADMIN_PASSWORD)'
	vagrant ssh -c 'sudo /opt/splunk/bin/splunk restart'

uninstall:
	vagrant ssh -c 'sudo /opt/splunk/bin/splunk remove app splunk_graphite -auth admin:$(SPLUNK_ADMIN_PASSWORD)'
	vagrant ssh -c 'sudo /opt/splunk/bin/splunk restart'

add_input:
	vagrant ssh -c 'sudo /opt/splunk/bin/splunk add monitor /var/log -auth admin:$(SPLUNK_ADMIN_PASSWORD)'

clean:
	@rm -rf *.egg* build dist *.pyc *.pyo cover doctest_pypi.cfg nosetests.xml \
		pylint.log *.egg output.xml flake8.log output.xml */*.pyc .coverage \
		lint.log *.spl *.tgz


vagrant_up: vagrant_plugins
	vagrant up

vagrant_provision:
	vagrant provision

vagrant_destroy:
	vagrant destroy -f

vagrant_plugins:
	vagrant plugin install vagrant-berkshelf --plugin-version '~> 2.0.1' --verbose
	vagrant plugin install vagrant-omnibus --verbose


splunk_module: splunk

splunk: $(SPLUNK_PKG)
	tar -zxf $(SPLUNK_PKG) --strip-components 4 splunk/lib/python2.7/site-packages/splunk

splunk-6.0.2-196940-Linux-x86_64.tgz:
	wget http://download.splunk.com/releases/6.0.2/splunk/linux/$(SPLUNK_PKG)


generate_event:
	vagrant ssh -c "sudo echo `date +%s` generated: event=$$RANDOM > generated.log"
	vagrant ssh -c "sudo cp generated.log /opt/splunk/var/spool/splunk/"

search_for_generated_event: generate_event
	vagrant ssh -c "sudo /opt/splunk/bin/splunk search 'generated: event | table _time taco | graphite' -auth admin:$(SPLUNK_ADMIN_PASSWORD)"

search_for_generated_event_table: generate_event
	vagrant ssh -c "sudo /opt/splunk/bin/splunk search 'generated: event | head 1 | table _time host | graphite' -auth admin:$(SPLUNK_ADMIN_PASSWORD)"

delete_saved_search:
	curl -k -u admin:$(SPLUNK_ADMIN_PASSWORD) --request DELETE https://localhost:$(SPLUNKD_PORT)/servicesNS/admin/search/saved/searches/splunk_graphite_saved_search


delete_saved_search_table:
	curl -k -u admin:$(SPLUNK_ADMIN_PASSWORD) --request DELETE https://localhost:$(SPLUNKD_PORT)/servicesNS/admin/search/saved/searches/splunk_graphite_saved_search_table

create_saved_search_table:
	curl -k -u admin:$(SPLUNK_ADMIN_PASSWORD) https://localhost:$(SPLUNKD_PORT)/servicesNS/admin/search/saved/searches -d name=splunk_graphite_saved_search_table \
		--data-urlencode search='generated alert|table _time host' -d action.script=1 -d action.script.filename=campfire.py \
		-d action.script.track_alert=1 -d actions=script -d alert.track=1 -d cron_schedule='*/5 * * * *' -d disabled=0 -d dispatch.earliest_time=-5m@m \
		-d dispatch.latest_time=now -d run_on_startup=1 -d is_scheduled=1 -d alert_type='number of events' -d alert_comparator='greater than' \
		-d alert_threshold=0

splunk_errors:
	vagrant ssh -c "sudo /opt/splunk/bin/splunk search 'index=_internal \" error \" NOT debug source=*splunkd.log*' -auth admin:ampledata"
