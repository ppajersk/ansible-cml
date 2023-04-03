#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2017 Cisco and/or its affiliates.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}

from ansible.module_utils.basic import AnsibleModule, env_fallback
from ansible_collections.cisco.cml.plugins.module_utils.cml_utils import cmlModule, cml_argument_spec

def run_module():
    # define available arguments/parameters a user can pass to the module
    argument_spec = cml_argument_spec()
    argument_spec.update(
        lab=dict(type='str', required=True, fallback=(env_fallback, ['CML_LAB'])),
        node_name=dict(type='str', required=True),
        result_key=dict(type='str', required=True),
        command=dict(type='str', required=True),
        tags=dict(type='list', elements='str'),
        x=dict(type='int'),
        y=dict(type='int'),
        wait=dict(type='bool', default=False),
        report=dict(type='bool', default=False),
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    cml = cmlModule(module)

    cml.result['result_key'] = cml.params['result_key']
    cml.result['command'] = ''
    cml.result['report'] = cml.params['report']

    labs = cml.client.find_labs_by_title(cml.params['lab'])

    if len(labs) > 0:
        lab = labs[0]
    else:
        cml.fail_json("Cannot find lab {0}".format(cml.params['lab']))

    lab_instance = cml.client.join_existing_lab(lab.id)

    if lab_instance is None:
        cml.fail_json("Cannot connect to lab {0}".format(cml.params['lab']))

    lab_instance.pyats.sync_testbed( cml.user, cml.password )
    node = cml.get_node_by_name(lab_instance, cml.params['node_name'])

    if node is not None:
        node.start(wait=True)
        while ( node.has_converged() == False ): 
            pass
        command = node.run_pyats_command(cml.params['command'])
        if cml.params['report']:
            cml.result['command'] = command 
        cml.result['changed'] = True
    else:
        cml.fail_json("Cannot locate nod {0}".format(node))

    cml.exit_json(**cml.result)        
    

def main():
    run_module()


if __name__ == '__main__':
    main()
