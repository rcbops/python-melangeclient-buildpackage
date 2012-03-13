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

import re

try:
    # For Python < 2.6 or people using a newer version of simplejson
    import simplejson
    json = simplejson
except ImportError:
    # For Python >= 2.6
    import json


def loads(s):
    return json.loads(s)


def dumps(o):
    return json.dumps(o)


def camelize(string):
    return re.sub(r"(?:^|_)(.)", lambda x: x.group(0)[-1].upper(), string)


def remove_nones(hash):
    return dict((key, value)
               for key, value in hash.iteritems() if value is not None)
