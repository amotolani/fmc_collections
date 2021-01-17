#!/usr/bin/python
from fmcapi import *
from ansible.module_utils.basic import AnsibleModule
import base64
import requests

DOCUMENTATION = r'''
---
author: Adelowo David (@amotolani)
module: amotolani.cisco_fmc.port_group
short_description: Create, Modify and Delete Cisco FMC port group objects
description:
  - Create, Modify and Delete Cisco FMC port group objects.
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
  group_objects:
    description:
      - FMC port Objects to be added to/removed from the port group
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
- name: Create Port Group with existing port objects and deploy changes
  amotolani.cisco_fmc.port_group:
    name: Port-Group-1
    state: present
    fmc: cisco.sample.com
    action: add
    username: admin
    password: Cisco1234
    auto_deploy: True
    group_objects: MySampleHost

- name: Delete Port Group
  amotolani.cisco_fmc.port_group:
    name: Port-Group-1
    state: absent
    fmc: cisco.sample.com
    username: admin
    password: Cisco1234

    
- name: Remove address and port object from Port Group
  amotolani.cisco_fmc.port_group:
    name: Port-Group-2
    state: present
    fmc: cisco.sample.com
    action: remove
    username: admin
    password: Cisco1234
    group_objects: MySampleHost
'''


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str', choices=['present', 'absent'], required=True),
            name=dict(type='str', required=True),
            action=dict(type='str', choices=['add', 'remove']),
            # group_literals=dict(type='list', elements='str'),
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
    fmc = module.params['cisco_fmc']
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

    def validate_port(value):
        """
            We need to check the Port Number is valid.
            :param value: Port Number/Port Range
            :return: boolean
            """
        d = []
        for port_number in value.split('-'):
            d.append(port_number)
        if len(d) == 1 and int(d[0]) in range(65536):
            return True
        elif len(d) == 2 and int(d[0]) in range(65536) and int(d[1]) in range(65536) and int(d[1]) > int(d[0]):
            return True
        else:
            return False

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
            if all(validate_port(i) for i in group_literals):
                obj1 = PortObjectGroups(fmc=fmc1, name=name)
            else:
                result = dict(changed=False, msg='Group Members are not Ports/Port Ranges')
                module.exit_json(**result)
        else:
            obj1 = PortObjectGroups(fmc=fmc1, name=name)

        # Check existing state of the object
        _obj1 = get_obj(obj1)
        current_config = []
        new_config = []
        if requested_state == 'present':
            current_state = 0
            if 'items' in _obj1.keys():
                changed = True
                _create_obj = True
            else:
                _create_obj = False
                if "literals" in _obj1.keys() and group_literals is not None:
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
                        result = dict(failed=True, msg='At least one member must exist in the port group')
                        module.exit_json(**result)
        else:
            if 'items' in _obj1.keys():
                changed = False
            else:
                changed = True

        # if Object already exists, Instantiate object again with id. This is necessary for using PUT method
        if _create_obj is False:
            obj1 = PortObjectGroups(fmc=fmc1, id=_obj1['id'], name=name)
        else:
            pass

        # Perform action to change object state if not in check mode
        if changed is True and module.check_mode is False:
            if requested_state == 'present':
                if group_literals is not None:
                    for port in group_literals:
                        pass
                        # obj1.unnamed_ports(action=action, value=port)
                if group_objects is not None:
                    for port_object in group_objects:
                        obj1.named_ports(action=action, name=port_object)
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
