#!/usr/bin/python
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

    # Custom argument validations
    # More of these are needed
    encodedbytes = base64.b64encode(bytes(username + ':' + password, 'utf-8'))
    encodedstr = str(encodedbytes, "utf-8")

    url = "https://{}/api/fmc_platform/v1/auth/generatetoken".format(fmc)
    payload = {}
    headers = {
        'Authorization': 'Basic {}'.format(encodedstr)
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

        # Instantiate Objects with values if valid Port/Port Range is provided
        if len(group_literals) > 0:
            if all(validate_ip_address(i) or validate_ip_range(i) or validate_network_address(i) for i in
                   group_literals):
                obj1 = NetworkGroups(fmc=fmc1, name=name)
            else:
                result = dict(changed=False, msg='Group Members are not valid IP, IP Range or Network Addresses')
                module.exit_json(**result)
        else:
            obj1 = NetworkGroups(fmc=fmc1, name=name)

        # Check existing state of the object
        _obj1 = get_obj(obj1)
        current_config = []
        new_config = []
        if requested_state == 'present':
            if 'items' in _obj1.keys():
                changed = True
                _create_obj = True
            else:
                _create_obj = False
                if "literals" in _obj1.keys() and group_literals is not None :
                    for a in _obj1['literals']:
                        current_config.append(a['value'])
                    new_config = new_config + group_literals

                if "objects" in _obj1.keys() and group_objects is not None:
                    for a in _obj1['objects']:
                        current_config.append(a['name'])
                    new_config = new_config + group_objects

                _requested_config_set = set(new_config)
                _current_config_set = set(current_config)
                _config_diff = _requested_config_set.difference(_current_config_set)
                _config_intsct = _requested_config_set.intersection(_current_config_set)
                if action == 'add' and len(_config_diff) > 0:
                    changed = True
                elif action == 'remove' and len(_config_intsct) > 0:
                    changed = True
                    if _config_intsct == _current_config_set:
                        result = dict(failed=True, msg='At least one member must exist in the network group')
                        module.exit_json(**result)
        else:
            if 'items' in _obj1.keys():
                changed = False
            else:
                changed = True

        # if Object already exists, Instantiate object again with id. This is necessary for using PUT method
        if _create_obj is False:
            obj1 = NetworkGroups(fmc=fmc1, id=_obj1['id'], name=name)
        else:
            pass

        # Perform action to change object state if not in check mode
        if changed is True and module.check_mode is False:
            if requested_state == 'present':
                if group_literals is not None:
                    for network in group_literals:
                        obj1.unnamed_networks(action=action, value=network)
                if group_objects is not None:
                    for network_object in group_objects:
                        obj1.named_networks(action=action, name=network_object)
                if _create_obj is True:
                    fmc_obj = create_obj(obj1)
                elif _create_obj is False:
                    fmc_obj = update_obj(obj1)
            elif requested_state == 'absent':
                fmc_obj = delete_obj(obj1)
            if fmc_obj is None:
                result = dict(failed=True, msg='An error occurred while sending request to cisco_fmc')
                module.exit_json(**result)

    result = dict(changed=changed)
    module.exit_json(**result)


if __name__ == "__main__":
    main()
