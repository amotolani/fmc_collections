#!/usr/bin/python
from fmcapi import *
from ansible.module_utils.basic import AnsibleModule
import base64
import requests

DOCUMENTATION = r'''
---
author: Adelowo David (@amotolani)
module: amotolani.cisco_fmc.vlan
short_description: Create, Modify and Delete Cisco FMC vlan objects
description:
  - Create, Modify and Delete Cisco FMC vlan objects.
options:
  name:
    description:
      - The name of the cisco_fmc object to be created, modified or deleted.
    type: str
    required: true
  state:
    description:
      - Whether to create/modify (C(present)), or remove (C(absent)) object.
    type: str
    required: true
  end_start:
    description:
      - Lower VLAN number in range
    type: str
    required: false
  vlan_start:
    description:
      - Upper VLAN number in range
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
- name: Create Vlan objects and deploy changes
  amotolani.cisco_fmc.vlan:
    name: "{{item.name}}"
    state: present
    vlan_start: "{{item.vlan_start}}"
    fmc: ciscofmc.sample.com
    vlan_end: "{{item.vlan_end}}"
    username: admin
    password: Cisco1234
    auto_deploy: True
  loop:
    - {name: vlan1 , vlan_start: 111 , vlan_end: 222}
    - {name: vlan2 , vlan_start: 333 , vlan_end: 444}

- name: Delete Vlan objects
  amotolani.cisco_fmc.vlan:
    name: vlan1
    state: absent
    fmc: ciscofmc.sample.com
    username: admin
    password: Cisco1234
'''


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str', choices=['present', 'absent'], required=True),
            name=dict(type='str', required=True),
            vlan_start=dict(type='str'),
            vlan_end=dict(type='str'),
            fmc=dict(type='str', required=True),
            username=dict(type='str', required=True),
            password=dict(type='str', required=True,  no_log=True),
            auto_deploy=dict(type='bool', default=False)
        ),
        supports_check_mode=True,
        required_if=[
            ["state", "present", ["vlan_start", "vlan_end"]]
        ]
    )
    changed = False
    result = dict(
        changed=changed
    )
    requested_state = module.params['state']
    name = module.params['name']
    vlan_start = module.params['vlan_start']
    vlan_end = module.params['vlan_end']
    fmc = module.params['cisco_fmc']
    username = module.params['username']
    password = module.params['password']
    auto_deploy = module.params['auto_deploy']
    vlan_data = {'startTag': vlan_start, 'endTag': vlan_end}

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

    def validate_vlans(start_vlan, end_vlan=""):
        """
        Validate that the start_vlan and end_vlan numbers are in 1 - 4094 range.  If not, then return False
        :param start_vlan: (int) Lower VLAN number in range.
        :param end_vlan: (int) Upper VLAN number in range.
        :return: boolean
        """
        logging.debug("In validate_vlans() helper_function.")

        if int(start_vlan) in range(4096) and int(end_vlan) in range(4096) and int(end_vlan) > int(start_vlan):
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

        # Instantiate Objects with values if valid vlan range is provided
        if validate_vlans(vlan_start, vlan_end):
            obj1 = VlanTags(fmc=fmc1, name=name, data=vlan_data)
        else:
            result = dict(failed=True, msg='Provided vlan range is not valid')
            module.exit_json(**result)
        
        # Check existing state of the object
        _obj1 = get_obj(obj1)
        if requested_state == 'present':
            if 'data' not in _obj1.keys():
                _create_obj = True
                changed = True
            elif _obj1['data']['startTag'] != int(vlan_start) or _obj1['data']['endTag'] != int(vlan_end) or _obj1['name'] != name:
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
                obj1 = VlanTags(fmc=fmc1, id=_obj1['id'], name=name, data=vlan_data)
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
