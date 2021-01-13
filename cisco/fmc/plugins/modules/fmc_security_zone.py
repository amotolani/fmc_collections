#!/usr/bin/python
from fmcapi import *
from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = r'''
---
author: Adelowo David (@amotolani)
module: fmc_port
short_description: Create, Modify and Delete Cisco FMC network objects
description:
  - Create, Modify and Delete Cisco FMC network objects.
options:
  name:
    description:
      - The name of the fmc object to be created, modified or deleted.
    type: str
    required: true
  state:
    description:
      - Whether to create/modify (C(present)), or remove (C(absent)) an object.
    type: str
    required: true
  protocol:
    description:
      - The network port protocol.
      - Supported choices are TCP and UDP
    type: str
    required: true
  fmc:
    description:
      - IP address or FQDN of Cisco FMC.
    type: str
    required: true
  port:
    description:
      - Port/Port Range value of fmc object.
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
- name: Create Port objects and deploy changes
  fmc_port:
    name: "{{item.name}}"
    state: present
    port: "{{item.port}}"
    fmc: ciscofmc.sample.com
    protocol: "{{item.protocol}}"
    username: admin
    password: Cisco1234
    auto_deploy: True
  loop:
    - {name: port1 , port: 10100 , protocol: UDP}
    - {name: port2 , port: 11001-11004, protocol: TCP}

- name: Delete Port objects
  fmc_port:
    name: ApplicationPort
    state: absent
    port: 7000
    fmc: ciscofmc.sample.com
    protocol: TCP
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
            elif _obj1['interfaceMode'] != interface_mode or _obj1['name'] != name:
                _create_obj = False
                changed = True 
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
                result = dict(failed=True, msg='An error occurred while sending request to fmc')
                module.exit_json(**result)
                
    result = dict(changed=changed)
    module.exit_json(**result)


if __name__ == "__main__":
    main()
