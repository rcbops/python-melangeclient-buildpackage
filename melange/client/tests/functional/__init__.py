# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import ConfigParser
import cStringIO
import os
import sys

from melange.client import cli


def run(command, **kwargs):
    config = ConfigParser.ConfigParser()
    functional_path = os.path.dirname(os.path.realpath(__file__))
    config.read(os.path.join(functional_path, "tests.conf"))

    stdout = sys.stdout
    stderr = sys.stderr
    exit = sys.exit

    mystdout = cStringIO.StringIO()
    mystderr = cStringIO.StringIO()
    exitcode = {'code': 0}

    def myexit(code):
        exitcode['code'] = code

    sys.stdout = mystdout
    sys.stderr = mystderr
    sys.exit = myexit

    argv = ['--host=%s' % config.get('DEFAULT', 'server_name'),
            '--port=%s' % config.get('DEFAULT', 'server_port'),
            '-v']
    argv.extend(command.strip().split(' '))

    cli.main(script_name='melange', argv=argv)

    sys.stdout = stdout
    sys.stderr = stderr
    sys.exit = exit

    return {'exitcode': exitcode['code'],
            'out': mystdout.getvalue(),
            'err': mystderr.getvalue()}
