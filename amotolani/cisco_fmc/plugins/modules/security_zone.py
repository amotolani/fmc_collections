#!/usr/bin/python
from fmcapi import *
from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = r'''
---
author: Adelowo David (@amotolani)
module: amotolani.cisco_fmc.security_zone
short_description: Create, Modify and Delete Cisco FMC Security Zone objects
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
  interface_mode:
    description:
      - Supported choices are ['routed', 'switched', 'asa', 'inline', 'passive']
    type: str
    required: true
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
- name: Create Security Zone objects and deploy changes
  amotolani.cisco_fmc.security_zone:
    name: Zone1
    state: present
    interface_mode: switched
    fmc: ciscofmc.sample.com
    username: admin
    password: Cisco1234
    auto_deploy: True

- name: Delete  Security Zone objects
  amotolani.cisco_fmc.security_zone:
    name: Zone-1
    state: absent
    interface_mode: routed
    fmc: ciscofmc.sample.com
    username: admin
    password: Cisco1234
'''


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str', choices=['present', 'absent'], required=True),
            name=dict(type='str', required=True),
            interface_mode=dict(type='str', choices=['routed', 'switched', 'asa', 'inline', 'passive'], required=True),
            fmc=dict(type='str', required=True),
            username=dict(type='str', required=True),
            password=dict(type='str', required=True,  no_log=True),
            auto_deploy=dict(type='bool', default=False)
        ),
        supports_check_mode=True
    )
    changed = False
    result = dict(
        changed=changed
    )
    requested_state = module.params['state']
    name = module.params['name']
    interface_mode = module.params['interface_mode']
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

    with FMC(host=fmc, username=username, password=password, autodeploy=auto_deploy) as fmc1:

        # Instantiate Objects with values
        obj1 = SecurityZones(fmc=fmc1, name=name)

        # Check existing state of the object
        _obj1 = get_obj(obj1)
        if requested_state == 'present':
            if 'items' in _obj1.keys():
                _create_obj = True
                changed = True
            elif _obj1['interfaceMode'] != interface_mode.upper() or _obj1['name'] != name:
                _create_obj = False
                changed = True
            else:
                changed = False
                _create_obj = False
        else:
            if 'items' in _obj1.keys():
                changed = False
            else:
                changed = True

        #  Instantiate Security Zone, if it doesnt exist.
        if _create_obj:
            obj1 = SecurityZones(fmc=fmc1, name=name, interfaceMode=interface_mode)

        # Perform action to change object state if not in check mode
        if changed is True and module.check_mode is False:
            if requested_state == 'present' and _create_obj is True:
                fmc_obj = create_obj(obj1)
            elif requested_state == 'present' and _create_obj is False:
                obj1 = SecurityZones(fmc=fmc1, id=_obj1['id'], name=name, interfaceMode=interface_mode)
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
