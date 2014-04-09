#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for splunk_graphite App."""


import os
import random
import requests
import time
import unittest

import fabric
import fabtools.vagrant


APP_NAME = 'splunk_graphite'
SPLUNK_ADMIN_PASSWORD = 'okchanged'
SPLUNKD_PORT = 4189
SPLUNK_HOME = '/opt/splunk'


class TestSplunkGraphiteApp(unittest.TestCase):  # pylint: disable=R0904

    """Tests for splunk_graphite App."""

    def setUp(self):
        self.auth = "-auth admin:%s" % SPLUNK_ADMIN_PASSWORD
        self.app_path = os.path.join(SPLUNK_HOME, 'etc', 'apps', APP_NAME)
        self.fcontains = fabric.contrib.files.contains
        self.fexists = fabric.contrib.files.exists

    def tearDown(self):
        self.remove_app()
        ss_conf = os.path.join(
            SPLUNK_HOME, 'etc', 'users', 'admin', 'search', 'local',
            'savedsearches.conf'
        )
        with fabtools.vagrant.vagrant_settings():
            fabric.api.sudo("rm %s || true" % ss_conf)

    @staticmethod
    def randstr(length=8):
        """Generates a random string of `len`."""
        return ''.join(
            [random.choice('unittest0123456789') for _ in range(length)])

    def backup_app(self):
        """Backs up App for post-test forensics."""
        with fabtools.vagrant.vagrant_settings():
            fabric.api.sudo(
                'tar -zcpf /tmp/%s_%s.tgz %s || true' %
                (APP_NAME, time.time(), self.app_path)
            )

    @staticmethod
    def build_app():
        """Builds App archive."""
        fabric.api.local('make clean build')

    # TODO(@ampledata) Not fully implemented yet.
    @staticmethod
    def configure_app(**kwargs):
        """Configures app with given parameters."""
        endpoint = (
            "/servicesNS/nobody/%s/apps/local/%s/setup" % (APP_NAME, APP_NAME))
        config_ns = "/%s/graphite_config/graphite_config" % APP_NAME
        config_url = "https://localhost:%s%s" % (SPLUNKD_PORT, endpoint)

        config_data = {
            "%s/host" % config_ns: 'localhost'
        }
        return requests.post(
            config_url,
            data=config_data,
            verify=False,
            auth=('admin', SPLUNK_ADMIN_PASSWORD)
        )

    @staticmethod
    def splunk_cmd(cmd_args):
        """
        Runs the given splunk command on the remote host using sudo.

        @param cmd_args: Command and arguments to run with Splunk.
        @type cmd_args: str

        @return: Command results.
        @rtype: `fabric.api.sudo`
        """
        return fabric.api.sudo("%s/bin/splunk %s" % (SPLUNK_HOME, cmd_args))

    @staticmethod
    def splunk_restart():
        """Restarts Splunk."""
        return TestSplunkGraphiteApp.splunk_cmd('restart')

    def remove_app(self):
        """Removes the App."""
        with fabtools.vagrant.vagrant_settings():
            TestSplunkGraphiteApp.splunk_cmd(
                "remove app %s %s || true" % (APP_NAME, self.auth)
            )
            TestSplunkGraphiteApp.splunk_restart()

    def install_app(self):
        """Installs the App."""
        with fabtools.vagrant.vagrant_settings():
            TestSplunkGraphiteApp.splunk_cmd(
                "install app /vagrant/%s.spl -update true %s" %
                (APP_NAME, self.auth)
            )
            TestSplunkGraphiteApp.splunk_restart()

    def test_build_app(self):
        """Tests building App archive."""
        TestSplunkGraphiteApp.build_app()
        self.assertTrue(os.path.exists("%s.spl" % APP_NAME))

    def test_install_app(self):
        """Tests installing App."""
        TestSplunkGraphiteApp.build_app()
        self.install_app()
        with fabtools.vagrant.vagrant_settings():
            self.assertTrue(self.fexists(self.app_path))

    def test_uninstall_app(self):
        """Tests uninstalling App."""
        TestSplunkGraphiteApp.build_app()
        self.install_app()
        self.remove_app()
        with fabtools.vagrant.vagrant_settings():
            self.assertFalse(self.fexists(self.app_path))

    def test_saved_search(self):
        """Tests configuring saved search alert."""
        rand_str = TestSplunkGraphiteApp.randstr()
        rand_int = random.randint(1, 1000)
        test_inv = "test_saved_search-%s" % rand_str

        TestSplunkGraphiteApp.build_app()
        self.install_app()

        self.configure_app(host='localhost')

        ss_endpoint = '/servicesNS/admin/search/saved/searches'
        ss_data = {
            'search': "search-%s | fields test_metric" % test_inv,
            'name': "name-%s" % test_inv,
            'action.script': '1',
            'action.script.filename': 'graphite.py',
            'action.script.track_alert': '1',
            'actions': 'script',
            'alert.track': '1',
            'cron_schedule': '* * * * *',
            'disabled': '0',
            'dispatch.earliest_time': '-5m@m',
            'dispatch.latest_time': 'now',
            'run_on_startup': '1',
            'is_scheduled': '1',
            'alert_type': 'number of events',
            'alert_comparator': 'greater than',
            'alert_threshold': '0'
        }
        ss_url = "https://localhost:%s%s" % (SPLUNKD_PORT, ss_endpoint)

        conf_result = requests.post(
            ss_url,
            data=ss_data,
            verify=False,
            auth=('admin', SPLUNK_ADMIN_PASSWORD)
        )

        self.assertEqual(201, conf_result.status_code)

        log_file = os.path.join(
            SPLUNK_HOME, 'var', 'spool', 'splunk', "log-%s" % test_inv)

        log_line = (
            "%s log_line-%s search-%s test_metric=%s" %
            (time.time(), test_inv, test_inv, rand_int)
        )

        with fabtools.vagrant.vagrant_settings():
            fabric.contrib.files.append(log_file, log_line, use_sudo=True)
            nc_return = fabric.api.run('nc -l 2003')
            test_str = "test_metric %s" % rand_int
            print "nc_return----"
            print nc_return
            print "---"
            print dir(nc_return)
            print "nc_return----"
            print test_str in nc_return.stdout
            self.assertTrue(test_str in nc_return.stdout)

    def test_unconfigured_app(self):
        """Tests that App is not configured upon initial install."""
        self.install_app()

        config_file = "%s/local/graphite.conf" % self.app_path
        app_config = "%s/local/app.conf" % self.app_path

        with fabtools.vagrant.vagrant_settings():
            self.assertFalse(
                self.fexists(config_file, use_sudo=True, verbose=True)
            )

            self.assertFalse(
                self.fexists(app_config, use_sudo=True, verbose=True)
            )

    def test_configured_app(self):
        """Tests configuring App."""
        self.install_app()

        endpoint = (
            "/servicesNS/nobody/%s/apps/local/%s/setup" % (APP_NAME, APP_NAME))
        config_ns = "/%s/graphite_config/graphite_config" % APP_NAME
        config_url = "https://localhost:%s%s" % (SPLUNKD_PORT, endpoint)

        rand_host = TestSplunkGraphiteApp.randstr()
        rand_port = TestSplunkGraphiteApp.randstr()
        rand_namespace = TestSplunkGraphiteApp.randstr()
        rand_prefix = TestSplunkGraphiteApp.randstr()

        config_data = {
            "%s/host" % config_ns: rand_host,
            "%s/port" % config_ns: rand_port,
            "%s/namespace" % config_ns: rand_namespace,
            "%s/prefix" % config_ns: rand_prefix
        }

        config_file = "%s/local/graphite.conf" % self.app_path
        app_config = "%s/local/app.conf" % self.app_path

        conf_result = requests.post(
            config_url,
            data=config_data,
            verify=False,
            auth=('admin', SPLUNK_ADMIN_PASSWORD)
        )

        self.assertEqual(200, conf_result.status_code)

        with fabtools.vagrant.vagrant_settings():
            self.assertTrue(
                self.fexists(config_file, use_sudo=True, verbose=True),
                "Config file %s does not exist." % config_file
            )

            self.assertTrue(
                self.fexists(app_config, use_sudo=True, verbose=True),
                "App config %s does not exist." % app_config
            )

            self.assertTrue(
                self.fcontains(
                    app_config,
                    text='is_configured = 1',
                    use_sudo=True
                ),
                'App is not configured.'
            )

            self.assertTrue(
                self.fcontains(
                    config_file,
                    text="host = %s" % rand_host,
                    use_sudo=True
                )
            )

            self.assertTrue(
                self.fcontains(
                    config_file,
                    text="port = %s" % rand_port,
                    use_sudo=True
                )
            )

            self.assertTrue(
                self.fcontains(
                    config_file,
                    text="namespace = %s" % rand_namespace,
                    use_sudo=True
                )
            )

            self.assertTrue(
                self.fcontains(
                    config_file,
                    text="prefix = %s" % rand_prefix,
                    use_sudo=True
                )
            )


if __name__ == '__main__':
    unittest.main()
