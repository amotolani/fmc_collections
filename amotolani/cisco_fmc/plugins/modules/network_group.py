#!/usr/bin/python
import logging

from fmcapi import *
from ansible.module_utils.basic import AnsibleModule
import fmcapi.api_objects.helper_functions
import base64
import requests

DOCUMENTATION = r'''
---
author: Adelowo David (@amotolani)
module: amotolani.cisco_fmc.network_group
short_description: Create, Modify and Delete Cisco FMC network objects
description:
  - Create, Modify and Delete Cisco FMC network objects.
options:
  name:
    description:
      - The name of the cisco_fmc object to be created, modified or deleted.
    type: str
    required: true
  state:
    description:
      - Whether to create/modify (C(present)), or remove (C(absent)) an object.
    type: str
    required: true
  group_literals:
    description:
      - Network to be added to the network group
      - Accepted value is a list of valid IPv4 addresses,IPv4 address ranges or IPv4 network addresses
    type: list
    required: false
  group_objects:
    description:
      - FMC Objects to be added to/removed from the network group
      - If the objects do not exist on the FMC, this will be ignored
    type: list
    required: false
  action:
    description:
      - Action to take with the specified group members
      - Allowed values are (C(add)) or (C(remove))
      - Required when state = "present"
    type: str
    required: false
  fmc:
    description:
      - IP address or FQDN of Cisco FMC.
    type: str
    required: true
  username:
    description:
      - Cisco FMC Username
      - User should have sufficient permissions to modify objects
    type: str
    required: true
  password:
    description:
      - Cisco FMC Password
    type: str
    required: true
  auto_deploy:
    description:
      - Option to deploy configurations to deployable devices after changes
    type: bool
    default: False
    required: False
'''

EXAMPLES = r'''
- name: Create Network Group with existing network objects and deploy changes
  amotolani.cisco_fmc.network_group:
    name: Network-Group-1
    state: present
    fmc: cisco.sample.com
    action: add
    username: admin
    password: Cisco1234
    auto_deploy: True
    group_objects: MySampleHost

- name: Delete Network Group
  amotolani.cisco_fmc.network_group:
    name: Network-Group-1
    state: absent
    fmc: cisco.sample.com
    username: admin
    password: Cisco1234

- name: Create Network Group specifying network addresses than are not cisco_fmc objects
  amotolani.cisco_fmc.network_group:
    name: Network-Group-2
    state: present
    fmc: cisco.sample.com
    action: add
    username: admin
    password: Cisco1234
    group_literals: 20.1.2.2,10.32.11.0/24,34.2.2.1-34.2.2.200

- name: Remove address and network object from Network Group
  amotolani.cisco_fmc.network_group:
    name: Network-Group-2
    state: present
    fmc: cisco.sample.com
    action: remove
    username: admin
    password: Cisco1234
    group_literals: 20.1.2.2
    group_objects: MySampleHost
'''


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str', choices=['present', 'absent'], required=True),
            name=dict(type='str', required=True),
            action=dict(type='str', choices=['add', 'remove']),
            group_literals=dict(type='list', elements='str'),
            group_objects=dict(type='list', elements='str'),
            fmc=dict(type='str', required=True),
            username=dict(type='str', required=True),
            password=dict(type='str', required=True, no_log=True),
            auto_deploy=dict(type='bool', default=False)
        ),
        supports_check_mode=True,
        required_if=[
            ["state", "present", ["action"]],
        ]
    )
    changed = False
    result = dict(changed=changed)

    requested_state = module.params['state']
    name = module.params['name']
    action = module.params['action']
    group_literals = module.params['group_literals']
    group_objects = module.params['group_objects']
    fmc = module.params['fmc']
    username = module.params['username']
    password = module.params['password']
    auto_deploy = module.params['auto_deploy']

    # Define Operation Functions #

    def get_obj(obj):
        a = obj.get()
        return a

    def create_obj(obj):
        a = obj.post()
        return a

    def delete_obj(obj):
        a = obj.delete()
        return a

    def update_obj(obj):
        a = obj.put()
        return a

    def validate_ip_address(address):
        """
         We need to check the IP Address is valid.
         :param address: IP Address
         :return: boolean
         """
        a = fmcapi.api_objects.helper_functions.is_ip(address)
        return a

    def validate_network_address(address):
        """
        We need to check the provided Network Address is valid.
        :param address: Network Address
        :return: boolean
        """
        a = fmcapi.api_objects.helper_functions.is_ip_network(address)
        return a

    def validate_ip_range(ip_range):
        """
        We need to check the provided IP Range is valid.
        :param ip_range: IP Range
        :return: boolean
        """
        d = []
        for ip in ip_range.split('-'):
            d.append(fmcapi.api_objects.helper_functions.is_ip(ip))
        if len(d) != 2 or d[0] is not True or d[1] is not True:
            return False
        else:
            return True

    def validate_net_obj_config(requested_config, config_name):
        """
        It is a custom version of the 'validate_multi_obj_config' function
        Function validates that the requested configurations are existing cisco_fmc network objects
        :param requested_config: Configuration to be added/removed from Access Rule
        :param config_name: Configuration name in result dictionary
        :return: boolean
        """
        _obj_list, net_obj, ip_obj, range_obj, net_group_obj, fqdn_obj = ([] for i in range(6))
        _literal_list, net_literal, ip_literal, range_literal, fqdn_literal= ([] for i in range(5))

        # store all network group objects for use later
        network_group_objects = list()

        if requested_config is None:
            return True
        else:
            if requested_config['name'] is not None:
                requested_config['name'] = [i for i in requested_config['name'] if i]
                for i in requested_config['name']:
                    config_obj = Networks(fmc=fmc1, name=i)
                    _config_obj = get_obj(config_obj)
                    if 'items' in _config_obj:
                        a = False
                    else:
                        a = True
                    net_obj.append(a)

                    config_obj = Ranges(fmc=fmc1, name=i)
                    _config_obj = get_obj(config_obj)
                    if 'items' in _config_obj:
                        a = False
                    else:
                        a = True
                    range_obj.append(a)

                    config_obj = Hosts(fmc=fmc1, name=i)
                    _config_obj = get_obj(config_obj)
                    if 'items' in _config_obj:
                        a = False
                    else:
                        a = True
                    ip_obj.append(a)

                    config_obj = NetworkGroups(fmc=fmc1, name=i)
                    _config_obj = get_obj(config_obj)
                    if 'items' in _config_obj:
                        a = False
                    else:
                        a = True
                        network_group_objects.append(i)
                    net_group_obj.append(a)

                    config_obj = FQDNS(fmc=fmc1, name=i)
                    _config_obj = get_obj(config_obj)
                    if 'items' in _config_obj:
                        a = False
                    else:
                        a = True
                        network_group_objects.append(i)
                    fqdn_obj.append(a)

                    yy = requested_config['name'].index(i)
                    if net_obj[yy] or range_obj[yy] or ip_obj[yy] or net_group_obj[yy] or fqdn_obj[yy]:
                        a = True
                    else:
                        a = False
                    _obj_list.append(a)

            if requested_config['literal'] is not None:
                # Fix for issue-#5 (Removes empty strings from literal list before validating addresses)
                requested_config['literal'] = [i for i in requested_config['literal'] if i]
                if len(requested_config['literal']) > 0:
                    for i in requested_config['literal']:
                        p = validate_ip_range(i)
                        range_literal.append(p)
                        q = validate_ip_address(i)
                        ip_literal.append(q)
                        w = validate_network_address(i)
                        net_literal.append(w)

                        yy = requested_config['literal'].index(i)
                        if net_literal[yy] or range_literal[yy] or ip_literal[yy]:
                            a = True
                        else:
                            a = False
                        _literal_list.append(a)

            if not all(_obj_list):
                result = dict(failed=True, msg='Check that the {} are existing cisco fmc objects'.format(config_name))
                module.exit_json(**result)
            elif not all(_literal_list):
                result = dict(failed=True, msg='Check that the {} are valid literal addresses'.format(config_name))
                module.exit_json(**result)
            else:
                return network_group_objects

    # Custom argument validations
    # More of these are needed
    encoded_bytes = base64.b64encode(bytes(username + ':' + password, 'utf-8'))
    encoded_str = str(encoded_bytes, "utf-8")

    url = "https://{}/api/fmc_platform/v1/auth/generatetoken".format(fmc)
    payload = {}
    headers = {
        'Authorization': 'Basic {}'.format(encoded_str)
    }

    try:
        response = requests.request("POST", url, headers=headers, data=payload, verify=False)
        response.raise_for_status()
    except requests.exceptions.ConnectionError as hrr:
        result = dict(unreachable=True, msg='Unable to establish network connection to FMC')
        module.exit_json(**result)
    except requests.exceptions.HTTPError as err:
        result = dict(failed=True, msg='Connection to FMC failed. Reason: {}'.format(err))
        module.exit_json(**result)

    with FMC(host=fmc, username=username, password=password, autodeploy=auto_deploy) as fmc1:

        # creates iterable by default when not set from user ui
        if group_literals is None:
            group_literals = []
        else:
            pass
        if group_objects is None:
            group_objects = []
        else:
            pass

        obj1 = NetworkGroups(fmc=fmc1, name=name)

        # Check existing state of the object
        _obj1 = get_obj(obj1)
        new_config = []
        current_objects_config = []
        current_literals_config = []
        if requested_state == 'present':
            if 'items' in _obj1.keys():
                changed = True
                _create_obj = True
            else:
                _create_obj = False
                if "literals" in _obj1.keys() and group_literals is not None:
                    for a in _obj1['literals']:
                        current_literals_config.append(a['value'])

                if "objects" in _obj1.keys() and group_objects is not None:
                    for a in _obj1['objects']:
                        current_objects_config.append(a['name'])

                new_config = group_literals + group_objects
                _requested_config_set = set(new_config)
                _current_config_set = set(current_objects_config+current_literals_config)
                _config_diff = _requested_config_set.difference(_current_config_set)
                _config_intsct = _requested_config_set.intersection(_current_config_set)

                # if diff is gt than 0, then combine requested objects/literals and current objects/literals for posting to fmc api
                if action == 'add' and len(_config_diff) > 0:
                    changed = True
                    group_literals = group_literals + current_literals_config
                    group_objects  = group_objects  + current_objects_config

                # if intersect is gt than 0, then remove requested objects/literals from current objects/literals for posting to fmc api
                elif action == 'remove' and len(_config_intsct) > 0:
                    changed = True
                    group_literals = [i for i in current_literals_config if i not in group_literals]
                    group_objects  = [i for i in current_objects_config if i not in group_objects]
                    if _config_intsct == _current_config_set:
                        result = dict(failed=True, msg='At least one member must exist in the network group')
                        module.exit_json(**result)
        else:
            if 'items' in _obj1.keys():
                changed = False
                _create_obj = False
            else:
                changed = True
                _create_obj = False

        requested_config = {
            "literal": group_literals,
            "name": group_objects
        }

        # validate requested objects/literals and get the network groups amongst the requested objects
        network_groups = validate_net_obj_config(requested_config=requested_config, config_name="Network Group Members")

        # if Object already exists, Instantiate object again with id. This is necessary for using PUT method
        if _create_obj is False and changed is True:
            obj1 = NetworkGroups(fmc=fmc1, id=_obj1['id'], name=name)
        else:
            pass

        # Perform action to change object state if not in check mode
        if changed is True and module.check_mode is False:
            if requested_state == 'present':
                if group_literals is not None:
                    for network in group_literals:
                        obj1.unnamed_networks(action='add', value=network)
                if group_objects is not None:
                    for network_object in group_objects:
                        obj1.named_networks(action='add', name=network_object)
                    for network_group_object in network_groups:
                        obj1.named_networks(action='addgroup', name=network_group_object)
                if _create_obj is True:
                    fmc_obj = create_obj(obj1)
                elif _create_obj is False:
                    fmc_obj = update_obj(obj1)
            elif requested_state == 'absent':
                fmc_obj = delete_obj(obj1)
            if fmc_obj is None:
                try:
                    # error_response attribute only available in fmcapi>=20210523.0
                    fmc_obj = fmc1.error_response
                    msg = fmc_obj["error"]["messages"][0]["description"]
                except AttributeError:
                    msg = "An error occurred while sending request to cisco fmc"
                result = dict(failed=True, msg=msg)
                module.exit_json(**result)

    result = dict(changed=changed)
    module.exit_json(**result)


if __name__ == "__main__":
    main()
