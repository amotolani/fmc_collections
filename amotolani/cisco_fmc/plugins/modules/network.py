#!/usr/bin/python
from fmcapi import *
from pyvalidator import is_fqdn
from ansible.module_utils.basic import AnsibleModule
import fmcapi.api_objects.helper_functions
import base64
import requests

DOCUMENTATION = r'''
---
author: Adelowo David (@amotolani)
module: amotolani.cisco_fmc.network
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
  description:
    description:
      - The description/comment of the cisco_fmc object.
    type: str
    required: false
  network_type:
    description:
      - The network object type.
      - Allowed choices are Host, Network, Range, and FQDN
      - Use 'Host' to create, modify or delete an IP Host object
      - Use 'Range' to create, modify or delete an IP Address Range object
      - Use 'Network' to create, modify or delete a Network Address cisco_fmc object
      - Use 'FQDN' to create, modify or delete an FQDN Host object
    type: str
    required: true
  fmc:
    description:
      - IP address or FQDN of Cisco FMC.
    type: str
    required: true
  fmc_timeout:
    description:
      - time to wait (seconds) for the API response from FMC.
    type: int
    default: 5
    required: false
  value:
    description:
      - FMC network object value.
      - For network type 'Host', accepted value is a valid IPv4 address (1.1.1.1)
      - For network type 'Range',  accepted value is a valid IPv4 address range (1.1.1.1-1.1.1.255)
      - For network type 'Network',  accepted value is valid IPv4 network address (1.1.1.0/24)
      - For network type 'FQDN', accepted value is a valid FQDN (www.example.com, sub.example.com, sub.sub.example.com) FTD does NOT accept wildcards
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
- name: Create a Network object
  amotolani.cisco_fmc.network:
    name: Sample-Network
    state: present
    network_type: Network
    fmc: .sample.com
    value: 11.22.32.0/24
    username: admin
    password: Cisco1234

- name: Create a FQDN object
  amotolani.cisco_fmc.network:
    name: Sample-FQDN
    state: present
    network_type: FQDN
    fmc: .sample.com
    value: sub.example.com
    username: admin
    password: Cisco1234

- name: Create Host objects from a loop
  amotolani.cisco_fmc.network:
    name: "{ { item.name } }"
    state: present
    network_type: Host
    fmc: cisco.sample.com
    value: "{{item.value}}"
    username: admin
    password: Cisco1234
  loop:
    - {name: Host1 , value: 10.10.10.2}
    - {name: Host2 , value: 10.10.10.3}
    - {name: Host2 , value: 10.10.10.4}

- name: Create Range objects from a loop and deploy changes to devices
  amotolani.cisco_fmc.network:
    name: "{ { item.name } }"
    state: present
    network_type: Range
    fmc: cisco.sample.com
    value: "{{item.value}}"
    username: admin
    password: Cisco1234
    auto_deploy: True
  loop:
    - {name: Range1 , value: 10.10.10.2-10.10.10.50}
    - {name: Range2 , value: 10.10.20.2-10.10.20.50}

- name: Delete Host objects from a loop
  amotolani.cisco_fmc.network:
    name: "{ { item.name } }"
    state: absent
    network_type: Host
    fmc: cisco.sample.com
    value: "{{item.value}}"
    username: admin
    password: Cisco1234
  loop:
    - {name: Host1 , value: 20.10.10.2}
    - {name: Host2 , value: 20.10.10.3}
    - {name: Host2 , value: 20.10.10.4}
'''


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str', choices=['present', 'absent'], required=True),
            name=dict(type='str', required=True),
            description=dict(type='str', required=False),
            network_type=dict(type='str', choices=['Host', 'Range', 'Network', 'FQDN'], required=True),
            value=dict(type='str', required=True),
            fmc=dict(type='str', required=True),
            fmc_timeout=dict(type='int', required=False, default=5),
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
    description = module.params['description']
    network_type = module.params['network_type']
    value = module.params['value']
    fmc = module.params['fmc']
    fmc_timeout = module.params['fmc_timeout']
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

    def validate_fqdn(fqdn):
      """
      We need to check that the provided input is valid.
      Specifically, a fqdn that FTD can support. IE: No Wildcards
      """
      fqdn_options = {"require_tld": True, "allow_underscores": True,
                  "allow_trailing_dot": False, "allow_numeric_tld": True,
                  "allow_wildcard": False }
      a = is_fqdn(fqdn, fqdn_options)
      return a

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

    with FMC(host=fmc, username=username, password=password, timeout=fmc_timeout, autodeploy=auto_deploy) as fmc1:

        # Instantiate Objects with values if valid ip, range or network address is provided
        if network_type == 'Host':
            if validate_ip_address(value):
                obj1 = Hosts(fmc=fmc1, name=name, value=value, description=description)
            else:
                result = dict(failed=True, msg='Provided value is not a valid IP address')
                module.exit_json(**result)
        elif network_type == 'Range':
            if validate_ip_range(value):
                obj1 = Ranges(fmc=fmc1, name=name, value=value, description=description)
            else:
                result = dict(failed=True, msg='Provided value is not a valid IP address range')
                module.exit_json(**result)
        elif network_type == 'Network':
            if validate_network_address(value):
                obj1 = Networks(fmc=fmc1, name=name, value=value, description=description)
            else:
                result = dict(failed=True, msg='Provided value is not a valid network address')
                module.exit_json(**result)
        elif network_type == 'FQDN':
            if validate_fqdn(value):
              obj1 = FQDNS(fmc=fmc1, name=name, value=value, description=description)
            else:
                result = dict(failed=True, msg='Provided value is not a valid FQDN for FTD')
                module.exit_json(**result)
        else:
            pass

        # Check existing state of the object
        _obj1 = get_obj(obj1)
        if requested_state == 'present':
            if 'items' in _obj1.keys():
                _create_obj = True
                changed = True
            elif _obj1['value'] != value or _obj1['name'] != name:
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
                if network_type == 'Host':
                    obj1 = Hosts(fmc=fmc1, id=_obj1['id'], name=name, value=value, description=description)
                elif network_type == 'Range':
                    obj1 = Ranges(fmc=fmc1, id=_obj1['id'], name=name, value=value, description=description)
                elif network_type == 'Network':
                    obj1 = Networks(fmc=fmc1, id=_obj1['id'], name=name, value=value, description=description)
                elif network_type == 'FQDN':
                    obj1 = FQDNS(fmc=fmc1, id=_obj1['id'], name=name, value=value, description=description)
                fmc_obj = update_obj(obj1)
            elif requested_state == 'absent':
                fmc_obj = delete_obj(obj1)
            else:
                pass
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
