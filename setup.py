# Copyright 2011 OpenStack, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys

from melange.client.openstack.common.setup import parse_requirements
from melange.client.openstack.common.setup import parse_dependency_links
from melange.client.openstack.common.setup import write_requirements
from melange.client.openstack.common.setup import write_git_changelog

from setuptools.command.sdist import sdist
import setuptools

version = "0.2.2"


class local_sdist(sdist):
    """Customized sdist hook - builds the ChangeLog file from VC first"""
    def run(self):
        write_git_changelog()
        sdist.run(self)
cmdclass = {'sdist': local_sdist}

install_requires = parse_requirements()
if sys.version_info < (2, 6):
    install_requires.append("simplejson")

classifiers = ["Development Status :: 5 - Production/Stable",
               "Environment :: Console",
               "Intended Audience :: Developers",
               "Intended Audience :: Information Technology",
               "License :: OSI Approved :: Apache Software License",
               "Operating System :: OS Independent",
               "Programming Language :: Python",
              ]

console_scripts = ["melange = melange.client.cli:main"]

write_requirements()


def read_file(file_name):
        return open(os.path.join(os.path.dirname(__file__),
                                 file_name)).read()


setuptools.setup(name="python-melangeclient",
      version=version,
      description="Client library for OpenStack Melange API.",
      long_description=read_file("README.rst"),
      license="Apache License, Version 2.0",
      url="https://github.com/openstack/python-melangeclient",
      cmdclass=cmdclass,
      classifiers=classifiers,
      author="Openstack Melange Team",
      author_email="openstack@lists.launchpad.net",
      include_package_data=True,
      packages=setuptools.find_packages(exclude=["tests"]),
      install_requires=install_requires,
      dependency_links=parse_dependency_links(),
      entry_points={"console_scripts": console_scripts},
      zip_safe=False,
      namespace_packages=['melange'],
)
