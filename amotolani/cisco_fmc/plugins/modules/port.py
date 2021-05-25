#!/usr/bin/python
from fmcapi import *
from ansible.module_utils.basic import AnsibleModule
import base64
import requests

DOCUMENTATION = r'''
---
author: Adelowo David (@amotolani)
module: amotolani.cisco_fmc.port
short_description: Create, Modify and Delete Cisco FMC port objects
description:
  - Create, Modify and Delete Cisco FMC port objects.
options:
  name:
    description:
      - The name of the cisco_fmc port object to be created, modified or deleted.
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
      - Port/Port Range value of cisco_fmc object.
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
  amotolani.cisco_fmc.port:
    name: "{{item.name}}"
    state: present
    port: "{{item.port}}"
    fmc: cisco.sample.com
    protocol: "{{item.protocol}}"
    username: admin
    password: Cisco1234
    auto_deploy: True
  loop:
    - {name: port1 , port: 10100 , protocol: UDP}
    - {name: port2 , port: 11001-11004, protocol: TCP}

- name: Delete Port objects
  amotolani.cisco_fmc.port:
    name: ApplicationPort
    state: absent
    port: 7000
    fmc: cisco.sample.com
    protocol: TCP
    username: admin
    password: Cisco1234
'''


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str', choices=['present', 'absent'], required=True),
            name=dict(type='str', required=True),
            port=dict(type='str', required=True),
            protocol=dict(type='str', choices=['UDP', 'TCP'], required=True),
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
    port = module.params['port']
    protocol = module.params['protocol']
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

        # Instantiate Objects with values if valid Port/Port Range is provided
        if validate_port(port):
            obj1 = ProtocolPortObjects(fmc=fmc1, name=name, port=port, protocol=protocol)
        else:
            result = dict(failed=True, msg='Provided Port/Port Range is not valid')
            module.exit_json(**result)
        
        # Check existing state of the object
        _obj1 = get_obj(obj1)
        if requested_state == 'present':
            if 'items' in _obj1.keys():
                _create_obj = True
                changed = True
            elif _obj1['port'] != port or _obj1['name'] != name:
                _create_obj = False
                changed = True 
        else:
            if 'items' in _obj1.keys():
                changed = False
            else:
                changed = True

        # Perform action to change object state if not in check mode
        if changed is True and module.check_mode is False:
            if requested_state == 'present' and _create_obj is True:
                fmc_obj = create_obj(obj1)
            elif requested_state == 'present' and _create_obj is False:
                obj1 = ProtocolPortObjects(fmc=fmc1, id=_obj1['id'], name=name, port=port, protocol=protocol)
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
