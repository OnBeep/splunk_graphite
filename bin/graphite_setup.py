#!/usr/bin/env python

"""Graphite output Splunk Setup REST Handler."""

__author__ = 'Greg Albrecht <oss@undef.net>'
__copyright__ = 'Copyright 2016 Orion Labs, Inc.'
__license__ = 'Apache License, Version 2.0'


import logging
import os
import shutil

import splunk.admin


class ConfigGraphiteOutputApp(splunk.admin.MConfigHandler):
    """Graphite output Splunk Setup REST Handler."""

    def setup(self):
        """Sets up required configuration params for splunk_graphite."""
        if self.requestedAction == splunk.admin.ACTION_EDIT:
            self.supportedArgs.addOptArg('host')
            self.supportedArgs.addOptArg('port')
            self.supportedArgs.addOptArg('prefix')
            self.supportedArgs.addOptArg('namespace')
            self.supportedArgs.addOptArg('namefield')

    def handleList(self, confInfo):
        """Handles configuration params for splunk_graphite."""
        conf = self.readConf('graphite')
        if conf:
            for stanza, settings in conf.items():
                for key, val in settings.items():
                    confInfo[stanza].append(key, val)

    def handleEdit(self, confInfo):
        """Handles editing configuration params for splunk_graphite."""
        del confInfo

        if self.callerArgs.data['host'][0] in [None, '']:
            self.callerArgs.data['host'][0] = ''
        if self.callerArgs.data['port'][0] in [None, '']:
            self.callerArgs.data['port'][0] = ''
        if self.callerArgs.data['namespace'][0] in [None, '']:
            self.callerArgs.data['namespace'][0] = ''
        if self.callerArgs.data['prefix'][0] in [None, '']:
            self.callerArgs.data['prefix'][0] = ''
        if self.callerArgs.data['namefield'][0] in [None, '']:
            self.callerArgs.data['namefield'][0] = ''

        self.writeConf('graphite', 'graphite_config', self.callerArgs.data)

        install_graphite_py(os.environ.get('SPLUNK_HOME'))


def install_graphite_py(splunk_home):
    """Copies graphite.py to Splunk's bin/scripts directory."""

    script_src = os.path.join(
        splunk_home, 'etc', 'apps', 'splunk_graphite', 'bin', 'graphite.py')
    script_dest = os.path.join(splunk_home, 'bin', 'scripts')

    logging.info(
        'Copying script_src=%s to script_dest=%s', script_src, script_dest)
    shutil.copy(script_src, script_dest)


if __name__ == '__main__':
    splunk.admin.init(ConfigGraphiteOutputApp, splunk.admin.CONTEXT_NONE)
