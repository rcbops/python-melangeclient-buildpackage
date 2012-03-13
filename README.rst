Python bindings to the OpenStack Melange API
============================================

This is a client for the Openstack Melange API. It contains a Python API
(the ``melange.client`` module), and a command-line script (``melange``).

Running the tests
-----------------

Currently the test suite requires a running melange-server running on
http://localhost:9898.

Tests are run under `tox <http://tox.testrun.org/latest/>`_. First install
``tox`` using pip or your distribution's packages then run ``tox`` from
the distribution directory to run the tests in isolated virtual
environments.
