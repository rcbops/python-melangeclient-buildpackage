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

"""CLI interface for common Melange client opertaions.

Simple cli for creating ip blocks, adding policies and rules for ip address
allocations from these blocks.

"""

import optparse
import os
from os import environ as env
import sys
import yaml

from melange.client import client as base_client
from melange.client import exception
from melange.client import inspector
from melange.client import ipam_client
from melange.client import template


def create_options(parser):
    """Sets up the CLI and config-file options.

    :param parser: The option parser
    :returns: None

    """
    parser.add_option('-v', '--verbose', default=False, action="store_true",
                      help="Print more verbose output")
    parser.add_option('-H', '--host', metavar="ADDRESS", default="0.0.0.0",
                      help="Address of Melange API host. "
                           "Default: %default")
    parser.add_option('-p', '--port', dest="port", metavar="PORT",
                      type=int, default=9898,
                      help="Port the Melange API host listens on. "
                           "Default: %default")
    parser.add_option('-t', '--tenant', dest="tenant", metavar="TENANT",
                      type=str, default=env.get('MELANGE_TENANT', None),
                      help="tenant id in case of tenant resources")
    parser.add_option('--auth-token', dest="auth_token",
                      metavar="MELANGE_AUTH_TOKEN",
                      default=env.get('MELANGE_AUTH_TOKEN', None),
                      type=str, help="Auth token received from keystone")
    parser.add_option('-u', '--username', dest="username",
                      metavar="MELANGE_USERNAME",
                      default=env.get('MELANGE_USERNAME', None),
                      type=str, help="Melange user name")
    parser.add_option('-k', '--api-key', dest="api_key",
                      metavar="MELANGE_API_KEY",
                      default=env.get('MELANGE_API_KEY', None),
                      type=str, help="Melange access key")
    parser.add_option('-a', '--auth-url', dest="auth_url",
                      metavar="MELANGE_AUTH_URL", type=str,
                      default=env.get('MELANGE_AUTH_URL', None),
                      help="Url of keystone service")
    parser.add_option('--timeout', dest="timeout",
                      metavar="MELANGE_TIME_OUT", type=int,
                      default=env.get('MELANGE_TIME_OUT', None),
                      help="timeout for melange client operations")


def parse_options(parser, cli_args):
    """Parses CLI options.

    Returns parsed CLI options, command to run and its arguments, merged
    with any same-named options found in a configuration file

    :param parser: The option parser
    :returns: (options, args)

    """
    (options, args) = parser.parse_args(cli_args)
    if not args:
        parser.print_usage()
        sys.exit(2)
    return (options, args)


def usage():
    usage = """
%prog category action [args] [options]

Available categories:

    """
    return usage + client_category_usage()


def client_category_usage():
    usage = "\n"
    for category in client_categories:
        usage = usage + ("\t%s\n" % category)
    return usage


client_categories = ['ip_block', 'subnet', 'policy', 'unusable_ip_range',
                     'unusable_ip_octet', 'allocated_ip',
                     'tenant_allocated_ip', 'ip_address', 'ip_route',
                     'interface', 'tenant_interface', 'mac_address_range',
                     'allowed_ip']


def lookup_methods(name, hash):
    result = hash.get(name, None)
    if not result:
        print "The second parameter should be one of the following:"
        print_keys(hash)
        sys.exit(2)

    return result


def lookup_client_categories(category, factory):
    category_class = getattr(factory, category, None)
    if not category_class:
        print "The first parameter should be one of the following:"
        print client_category_usage()
        sys.exit(2)

    return category_class


def print_keys(hash):
    for k, _v in hash.iteritems():
        print "\t%s" % k


def auth_client(options):
    if options.auth_url or options.auth_token:
        return base_client.AuthorizationClient(options.auth_url,
                                               options.username,
                                               options.api_key,
                                               options.auth_token)


def view(data, template_name):
    data = data or {}
    try:
        # TODO(jkoelker) Templates should be using the PEP302 get_data api
        melange_client_file = sys.modules['melange.client'].__file__
        melange_path = os.path.dirname(melange_client_file)
        view_path = os.path.join(melange_path, 'views')
        return template.template(template_name,
                                 template_lookup=[view_path], **data)
    except exception.TemplateNotFoundError:
        return yaml.safe_dump(data, indent=4, default_flow_style=False)


def args_to_dict(args):
    try:
        return dict(arg.split("=") for arg in args)
    except ValueError:
        raise exception.MelangeClientError("Action arguments should be "
                                           "of the form of field=value")


def main(script_name=None, argv=None):
    if argv is None:
        argv = sys.argv[1:]

    if script_name is None:
        script_name = os.path.basename(sys.argv[0])

    oparser = optparse.OptionParser(version='%%prog 0.1',
                                    usage=usage())
    create_options(oparser)
    (options, args) = parse_options(oparser, argv)

    category = args.pop(0)

    factory = ipam_client.Factory(options.host,
                                  options.port,
                                  timeout=options.timeout,
                                  auth_url=options.auth_url,
                                  username=options.username,
                                  api_key=options.api_key,
                                  auth_token=options.auth_token,
                                  tenant_id=options.tenant)
    client = lookup_client_categories(category, factory)

    client_actions = inspector.ClassInspector(client).methods()
    if len(args) < 1:
        print _("Usage: %s category action [<args>]") % script_name
        print _("Available actions for %s category:") % category
        print_keys(client_actions)
        sys.exit(2)

    if client.TENANT_ID_REQUIRED and not options.tenant:
        print _("Please provide a tenant id for this action."
                "You can use option '-t' to provide the tenant id.")
        sys.exit(2)

    action = args.pop(0)
    fn = lookup_methods(action, client_actions)

    def get_response(fn, args):
        try:
            response = fn(**args_to_dict(args))
            return response
        except TypeError:
            print _("Possible wrong number of arguments supplied")
            print _("Usage: %s %s %s") % (script_name,
                                          category,
                                          inspector.MethodInspector(fn))
            if options.verbose:
                raise
            sys.exit(2)

    try:
        response = get_response(fn, args)
        template_name = category + "_" + action + ".tpl"
        print view(response, template_name=template_name)
    except exception.MelangeServiceResponseError as server_error:
        print _("The server returned an error:")
        print server_error
        sys.exit(1)
    except exception.MelangeClientError as client_error:
        print client_error
        sys.exit(2)
    except Exception:
        if options.verbose:
            raise
        else:
            print _("Command failed, please check log for more info")
        sys.exit(2)
