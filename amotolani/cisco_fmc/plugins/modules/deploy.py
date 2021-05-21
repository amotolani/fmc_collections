#!/usr/bin/python
from fmcapi import *
from ansible.module_utils.basic import AnsibleModule
import base64
import requests

DOCUMENTATION = r'''
---
author: Adelowo David (@amotolani)
module: amotolani.cisco_fmc.deploy
short_description: Deploy changes to FMC
description:
  - Deploy changes to FMC.
options:
  fmc:
    description:
      - IP address or FQDN of Cisco FMC.
    type: str
    required: true
  username:
    description:
      - Cisco FMC Username
      - User should have sufficient permissions to deploy changes
    type: str
    required: true
  password:
    description:
      - Cisco FMC Password
    type: str
    required: true
'''

EXAMPLES = r'''
- name: Deploy changes on FMC
  amotolani.cisco_fmc.deploy:
    fmc: cisco.sample.com
    username: admin
    password: Cisco1234
'''


def main():
    module = AnsibleModule(
        argument_spec=dict(
            fmc=dict(type='str', required=True),
            username=dict(type='str', required=True),
            password=dict(type='str', required=True,  no_log=True),
        ),
        supports_check_mode=False
    )
    changed = False
    result = dict(
        changed=changed
    )
    fmc = module.params['fmc']
    username = module.params['username']
    password = module.params['password']

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

    with FMC(host=fmc, username=username, password=password, autodeploy=False) as fmc1:

        # Instantiate Objects
        obj1    = DeploymentRequests(fmc=fmc1)
        fmc_obj = obj1.post()
        if fmc_obj is None:
            result = dict(changed=False, msg='No deployment was done')
            module.exit_json(**result)
                
    result = dict(changed=True)
    module.exit_json(**result)


if __name__ == "__main__":
    main()
