#!/usr/bin/python
from fmcapi import *
from ansible.module_utils.basic import AnsibleModule
import fmcapi.api_objects.helper_functions
import base64
import requests

DOCUMENTATION = r'''
author: Adelowo David (@amotolani)
module: amotolani.cisco_fmc.acp_rule
short_description: 'Create, Modify and Delete Cisco FMC Access Rule objects'
description:
  - 'Create, Modify and Delete Cisco FMC network objects.'
options:
  name:
    description:
      - 'The Access Rule to be created, modified or deleted.'
    type: str
    required: true
  state:
    description:
      - Whether to create/modify (C(present)), or remove (C(absent)) an Access Rule.
    type: str
    required: true
  enabled:
    description:
      - Enable/Disable Access Rule
    type: bool
    required: true
  send_events_to_fmc:
    description:
      - enable/disable "send_event_to_fmc"
    type: bool
    required: false
  log_begin:
    description:
      - enable/disable "log_begin"
    type: bool
    required: false
  log_end:
    description:
      - enable/disable "log_end"
    type: bool
    required: false
  enable_syslog:
    description:
      - enable/disable "enable_syslog"
    type: bool
    required: false
  insert_before:
    description:
      - Insert new rule before the specified index
    type: int
    required: false
  insert_after:
    description:
      - Insert new rule after the specified index
    type: int
    required: false
  section:
    description:
      - Access Rule Section
      - 'Allowed value [''default'', ''mandatory'']'
    type: str
    required: false
  acp:
    description:
      - Associated Access Control Policy
    type: str
    required: true
  intrusion_policy:
    description:
      - Associated Intrusion Policy
    type: str
    required: false
  file_policy:
    description:
      - Associated File Policy
    type: str
    required: false
  variable_set:
    description:
      - Associated Variable Set
    type: str
    required: false
  action:
    description:
      - Action applied by Access Rule
      - Allowed values ['ALLOW', 'TRUST', 'BLOCK', 'MONITOR', 'BLOCK_RESET','BLOCK_INTERACTIVE', 'BLOCK_RESET_INTERACTIVE']
      - Required when state = "present"
    type: str
    required: false
  source_networks:
    description:
      - Source Networks targeted by access rule
    type: dict
    required: false
    options:
      action:
        description:
          - Action to be applied to configuration elements
          - 'Allowed values [''add'', ''remove'']'
        type: str
        required: true
      name:
        description:
          - FMC network objects to add to configuration
        type: str
        required: false
      literal:
        description:
          - Literal network Addresses to add to configuration
        type: str
        required: false
  destination_networks:
    description:
      - Destination Networks targeted by access rule
    type: dict
    required: false
    options:
      action:
        description:
          - Action to be applied to configuration elements
          - Allowed values [''add'', ''remove'']
        type: str
        required: true
      name:
        description:
          - FMC network objects to add to configuration
        type: str
        required: false
      literal:
        description:
          - Literal network Addresses to add to configuration
        type: str
        required: false
  vlan_tags:
    description:
      - vLAN tags targeted by access rule
    type: dict
    required: false
    options:
      action:
        description:
          - Action to be applied to configuration elements
          - Allowed values [''add'', ''remove'']
        type: str
        required: true
      name:
        description:
          - FMC vlan tag objects to add to configuration
        type: str
        required: false
  source_ports:
    description:
      - Source Ports targeted by access rule
    type: dict
    required: false
    options:
      action:
        description:
          - Action to be applied to configuration elements
          - Allowed values [''add'', ''remove'']
        type: str
        required: true
      name:
        description:
          - FMC Port objects to add to configuration
        type: str
        required: false
  destination_ports:
    description:
      - Destination Ports targeted by access rule
    type: dict
    required: false
    options:
      action:
        description:
          - Action to be applied to configuration elements
          - Allowed values [''add'', ''remove'']
        type: str
        required: true
      name:
        description:
          - FMC Port objects to add to configuration
        type: str
        required: false
  source_zones:
    description:
      - Source Zones targeted by access rule
    type: dict
    required: false
    options:
      action:
        description:
          - Action to be applied to configuration elements
          - Allowed values [''add'', ''remove'']
        type: str
        required: true
      name:
        description:
          - FMC Security Zone objects to add to configuration
        type: str
        required: false
  destination_zones:
    description:
      - Destination Zones targeted by access rule
    type: dict
    required: false
    options:
      action:
        description:
          - Action to be applied to configuration elements
          - Allowed values [''add'', ''remove'']
        type: str
        required: true
      name:
        description:
          - FMC Security Zone objects to add to configuration
        type: str
        required: false
  applications:
    description:
      - Applications targeted by access rule
    type: dict
    required: false
    options:
      action:
        description:
          - Action to be applied to configuration elements
          - Allowed values [''add'', ''remove'']
        type: str
        required: true
      name:
        description:
          - FMC Applications objects to add to configuration
        type: str
        required: false
  source_security_group_tags:
    description:
      - Source Security Group Tags targeted by access rule
    type: dict
    required: false
    options:
      action:
        description:
          - Action to be applied to configuration elements
          - Allowed values [''add'', ''remove'']
        type: str
        required: true
      name:
        description:
          - FMC Security Group Tag objects to add to configuration
        type: str
        required: false
  destination_security_group_tags:
    description:
      - Destination Security Group Tags targeted by access rule
    type: dict
    required: false
    options:
      action:
        description:
          - Action to be applied to configuration elements
          - Allowed values [''add'', ''remove'']
        type: str
        required: true
      name:
        description:
          - FMC Security Group Tag objects to add to configuration
        type: str
        required: false
  new_comments:
    description:
      - Comments on access rule
    type: dict
    required: false
    options:
      action:
        description:
          - Action to be applied to configuration elements
          - Allowed values [''add'', ''remove'']
        type: str
        required: true
      comment:
        description:
          - FMC Security Group Tag objects to add to configuration
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
    default: false
    required: false
'''

EXAMPLES = r'''    
- name: Delete Access Policy Rule
  amotolani.cisco_fmc.acp_rule:
    name: Demo-Rule1900
    state: absent
    fmc: cisco.sample.com
    username: admin
    password: Cisco1234
    auto_deploy: False
    action: ALLOW
    enabled: True
    insert_after: 1
    acp: test
    
- name: Create Access Policy Rule
  amotolani.cisco_fmc.acp_rule:
    name: Demo-Rule1900
    state: present
    fmc: ciscofmc.sample.com
    username: admin
    password: Cisco1234
    auto_deploy: True
    action: ALLOW
    enabled: True
    send_events_to_fmc: False
    enable_syslog: False
    insert_after: 1
    section: mandatory
    acp: test
    vlan_tags:
      action: add
      name : vlan1,vlan2
    source_networks:
      action: add
      name:  Sample-Network-1
      literal: 10.1.1.22,10.2.2.11
    destination_networks:
      action: add
      literal: 10.4.4.88
    source_ports:
      action: add
      name: demo_port1
    destination_ports:
      action: add
      name: demo_port2
'''


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str', choices=['present', 'absent'], required=True),
            name=dict(type='str', required=True),
            enabled=dict(type='bool', required=True),
            send_events_to_fmc=dict(type='bool', default=False),
            log_begin=dict(type='bool', default=False),
            log_end=dict(type='bool', default=False),
            enable_syslog=dict(type='bool', default=False),
            insert_before=dict(type='int'),
            insert_after=dict(type='int'),
            section=dict(type='str', choices=['default', 'mandatory'], default='default'),
            acp=dict(type='str', required=True),
            intrusion_policy=dict(type='str'),
            file_policy=dict(type='str'),
            variable_set=dict(type='str'),
            action=dict(
                type='str',
                choices=['ALLOW', 'TRUST', 'BLOCK', 'MONITOR', 'BLOCK_RESET', 'BLOCK_INTERACTIVE', 'BLOCK_RESET_INTERACTIVE'],
                required=True),
            source_networks=dict(
                type='dict',
                options=dict(
                    action=dict(type='str', choices=['add', 'remove'], required=True),
                    name=dict(type='list'),
                    literal=dict(type='list', default='')
                )
            ),
            destination_networks=dict(
                type='dict',
                options=dict(
                    action=dict(type='str', choices=['add', 'remove'], required=True),
                    name=dict(type='list'),
                    literal=dict(type='list', default='')
                )
            ),
            vlan_tags=dict(
                type='dict',
                options=dict(
                    action=dict(type='str', choices=['add', 'remove'], required=True),
                    name=dict(type='list')
                )
            ),
            source_ports=dict(
                type='dict',
                options=dict(
                    action=dict(type='str', choices=['add', 'remove'], required=True),
                    name=dict(type='list')
                )
            ),
            destination_ports=dict(
                type='dict',
                options=dict(
                    action=dict(type='str', choices=['add', 'remove'], required=True),
                    name=dict(type='list')
                )
            ),
            source_zones=dict(
                type='dict',
                options=dict(
                    action=dict(type='str', choices=['add', 'remove'], required=True),
                    name=dict(type='list')
                )
            ),
            destination_zones=dict(
                type='dict',
                options=dict(
                    action=dict(type='str', choices=['add', 'remove'], required=True),
                    name=dict(type='list')
                )
            ),
            applications=dict(
                type='dict',
                options=dict(
                    action=dict(type='str', choices=['add', 'remove'], required=True),
                    name=dict(type='list')
                )
            ),
            source_security_group_tags=dict(
                type='dict',
                options=dict(
                    action=dict(type='str', choices=['add', 'remove'], required=True),
                    name=dict(type='list')
                )
            ),
            destination_security_group_tags=dict(
                type='dict',
                options=dict(
                    action=dict(type='str', choices=['add', 'remove'], required=True),
                    name=dict(type='list')
                )
            ),
            new_comments=dict(
                type='dict',
                options=dict(
                    action=dict(type='str', choices=['add', 'remove'], required=True),
                    comment=dict(type='list')
                )
            ),
            fmc=dict(type='str', required=True),
            username=dict(type='str', required=True),
            password=dict(type='str', required=True, no_log=True),
            auto_deploy=dict(type='bool', default=False)
        ),
        supports_check_mode=True,
        required_if=[
            ["state", "present", ["action"]],
        ],
        required_one_of=[
            ['insert_after', 'insert_before']
        ]
    )
    changed = False
    result = dict(changed=changed)

    requested_state = module.params['state']
    name = module.params['name']
    action = module.params['action']
    send_events_to_fmc = module.params['send_events_to_fmc']
    log_begin = module.params['log_begin']
    log_end = module.params['log_end']
    enabled = module.params['enabled']
    enable_syslog = module.params['enable_syslog']
    new_comments = module.params['new_comments']
    insert_before = module.params['insert_before']
    insert_after = module.params['insert_after']
    section = module.params['section']
    variable_set = module.params['variable_set']
    source_networks = module.params['source_networks']
    vlan_tags = module.params['vlan_tags']
    destination_networks = module.params['destination_networks']
    source_ports = module.params['source_ports']
    destination_ports = module.params['destination_ports']
    intrusion_policy = module.params['intrusion_policy']
    source_zones = module.params['source_zones']
    destination_zones = module.params['destination_zones']
    applications = module.params['applications']
    file_policy = module.params['file_policy']
    source_security_group_tags = module.params['source_security_group_tags']
    destination_security_group_tags = module.params['destination_security_group_tags']
    acp = module.params['acp']
    fmc = module.params['fmc']
    username = module.params['username']
    password = module.params['password']
    auto_deploy = module.params['auto_deploy']

    # Define useful Functions
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

    def multi_obj_config_state(requested_config, config_class,  fmc_config_name="", config_name=''):
        """
        To be used when multiple cisco_fmc objects can configured.
        This function checks current the state of a configuration for an access rule.
        If there is a need to change the state/or not based on the configuration requested, it appends True/False to a dictionary using the config_name as the key.
        :param requested_config: Configuration to be added/removed from Access Rule
        :param config_class: fmcapi Class for the Configuration to be added to the Access Rule
        :param fmc_config_name: fmcapi name for the Configuration to be added to the Access Rule
        :param config_name: Configuration name in result dictionary
        :return: None
        """
        current_config = []
        if fmc_config_name in _obj1.keys() and requested_config is not None:

            # Call validate function to check that the requested config object is an existing cisco_fmc object
            validate_multi_obj_config(requested_config=requested_config, config_class=config_class, config_name=config_name)

            # rule exists, No objects of the specified type currently added, requested action for config is "add". Changed status set to True
            if len(_obj1[fmc_config_name]) == 0 and len(requested_config) > 0 and requested_config['action'] == 'add':
                config_change_status[config_name] = {'action': 'add', 'change': True}

            # rule exists, No objects of the specified type currently added, requested action for config is "remove" Changed status set to False
            elif len(_obj1[fmc_config_name]) == 0 and len(requested_config) > 0 and requested_config['action'] == 'remove':
                config_change_status[config_name] = {'action': 'remove', 'change': False}

            else:
                # rule exists, objects of the specified type currently exist. Compare existing config objects to requested config objects
                for a in _obj1[fmc_config_name]['objects']:
                    current_config.append(a['name'])

            _requested_config_set = set(requested_config['name'])
            _current_config_set = set(current_config)
            _config_diff = _requested_config_set.difference(_current_config_set)
            _config_intersect = _requested_config_set.intersection(_current_config_set)

            # Requested objects supplied by user to be added do not currently exist. Set Changed Status to True
            if len(_config_diff) > 0 and requested_config['action'] == 'add':
                config_change_status[config_name] = {'action': 'add', 'change': True}

            # Requested objects supplied by user to be removed currently exist. Set Changed Status to True
            elif len(_config_intersect) > 0 and requested_config['action'] == 'remove':
                config_change_status[config_name] = {'action': 'remove', 'change': True}

            # No changes required. Set Changed status to False
            else:
                config_change_status[config_name] = {'action': 'none', 'change': False}

        # Requested config key do not exist in the access rule object dictionary and requested action is "add". Set Changed status to True
        elif fmc_config_name not in _obj1.keys() and requested_config is not None and requested_config['action'] == 'add':
            config_change_status[config_name] = {'action': 'add', 'change': True}

        # Set Changed status to False
        else:
            config_change_status[config_name] = {'action': 'none', 'change': False}
        return

    def net_obj_config_state(requested_config, config_class,  fmc_config_name="", config_name=''):
        """
        To be used when multiple cisco_fmc objects can configured.
        This function checks current the state of a configuration for an access rule.
        If there is a need to change the state/or not based on the configuration requested, it appends True/False to a dictionary using the config_name as the key.
        :param requested_config: Configuration to be added/removed from Access Rule
        :param config_class: fmcapi Class for the Configuration to be added to the Access Rule
        :param fmc_config_name: fmcapi name for the Configuration to be added to the Access Rule
        :param config_name: Configuration name in result dictionary
        :return: None
        """
        current_config = []
        new_config = []
        if fmc_config_name in _obj1.keys() and requested_config is not None:

            # Call validate function to check that the requested config object is an existing cisco_fmc object
            if requested_config == source_networks or destination_networks:
                validate_net_obj_config(requested_config=requested_config, config_name=config_name)
            else:
                validate_multi_obj_config(requested_config=requested_config, config_class=config_class, config_name=config_name)

            # rule exists, No objects of the specified type currently added, requested action for config is "add". Changed status set to True
            if len(_obj1[fmc_config_name]) == 0 and len(requested_config) > 0 and requested_config['action'] == 'add':
                config_change_status[config_name] = {'action': 'add', 'change': True}

            # rule exists, No objects of the specified type currently added, requested action for config is "remove" Changed status set to False
            elif len(_obj1[fmc_config_name]) == 0 and len(requested_config) > 0 and requested_config['action'] == 'remove':
                config_change_status[config_name] = {'action': 'remove', 'change': False}

            else:
                # rule exists, objects of the specified type currently exist. Compare existing config objects to requested config objects
                if 'objects' in _obj1[fmc_config_name].keys() and requested_config['name'] is not None:
                    for a in _obj1[fmc_config_name]['objects']:
                        current_config.append(a['name'])
                    new_config = new_config + requested_config['name']

                # For Source/Destination Networks Configuration, also check for literal configurations
                if requested_config == source_networks or destination_networks:
                    if 'literals' in _obj1[fmc_config_name].keys() and requested_config['literal'] is not None:
                        for a in _obj1[fmc_config_name]['literals']:
                            current_config.append(a['value'])
                        new_config = new_config + requested_config['literal']

            _requested_config_set = set(new_config)
            _current_config_set = set(current_config)
            _config_diff = _requested_config_set.difference(_current_config_set)
            _config_intersect = _requested_config_set.intersection(_current_config_set)

            # Requested objects supplied by user to be added do not currently exist. Set Changed Status to True
            if len(_config_diff) > 0 and requested_config['action'] == 'add':
                config_change_status[config_name] = {'action': 'add', 'change': True}

            # Requested objects supplied by user to be removed currently exist. Set Changed Status to True
            elif len(_config_intersect) > 0 and requested_config['action'] == 'remove':
                config_change_status[config_name] = {'action': 'remove', 'change': True}

            # No changes required. Set Changed status to False
            else:
                config_change_status[config_name] = {'action': 'none', 'change': False}

        # Requested config key do not exist in the access rule object dictionary and requested action is "add". Set Changed status to True
        elif fmc_config_name not in _obj1.keys() and requested_config is not None and requested_config['action'] == 'add':
            config_change_status[config_name] = {'action': 'add', 'change': True}

        # Set Changed status to False
        else:
            config_change_status[config_name] = {'action': 'none', 'change': False}
        return

    def application_obj_config_state(requested_config, config_class,  fmc_config_name="", config_name=''):
        """
        It is a custom version of the 'multi_obj_config_state' function
        This function checks current the state of a configuration for an access rule.
        If there is a need to change the state/or not based on the configuration requested, it appends True/False to a dictionary using the config_name as the key.
        :param requested_config: Configuration to be added/removed from Access Rule
        :param config_class: fmcapi Class for the Configuration to be added to the Access Rule
        :param fmc_config_name: fmcapi name for the Configuration to be added to the Access Rule
        :param config_name: Configuration name in result dictionary
        :return: None
        """
        current_config = []
        if fmc_config_name in _obj1.keys() and requested_config is not None:

            # Call validate function to check that the requested config object is an existing cisco_fmc objects
            validate_multi_obj_config(requested_config=requested_config, config_class=config_class, config_name=config_name)

            # rule exists, No objects of the specified type currently added, requested action for config is "add". Changed status set to True
            if len(_obj1[fmc_config_name]) == 0 and len(requested_config) > 0 and requested_config['action'] == 'add':
                config_change_status[config_name] = {'action': 'add', 'change': True}

            # rule exists, No objects of the specified type currently added, requested action for config is "remove" Changed status set to False
            elif len(_obj1[fmc_config_name]) == 0 and len(requested_config) > 0 and requested_config['action'] == 'remove':
                config_change_status[config_name] = {'action': 'remove', 'change': False}

            else:
                # rule exists, objects of the specified type currently exist. Compare existing config objects to requested config objects
                for a in _obj1[fmc_config_name]['applications']:
                    current_config.append(a['name'])
            _requested_config_set = set(requested_config['name'])
            _current_config_set = set(current_config)
            _config_diff = _requested_config_set.difference(_current_config_set)
            _config_intersect = _requested_config_set.intersection(_current_config_set)

            # Requested objects supplied by user to be added do not currently exist. Set Changed Status to True
            if len(_config_diff) > 0 and requested_config['action'] == 'add':
                config_change_status[config_name] = {'action': 'add', 'change': True}

            # Requested objects supplied by user to be removed currently exist. Set Changed Status to True
            elif len(_config_intersect) > 0 and requested_config['action'] == 'remove':
                config_change_status[config_name] = {'action': 'remove', 'change': True}

            # No changes required. Set Changed status to False
            else:
                config_change_status[config_name] = {'action': 'none', 'change': False}

        # Requested config key do not exist in the access rule object dictionary and requested action is "add". Set Changed status to True
        elif fmc_config_name not in _obj1.keys() and requested_config is not None and requested_config['action'] == 'add':
            config_change_status[config_name] = {'action': 'add', 'change': True}

        # Set Changed status to False
        else:
            config_change_status[config_name] = {'action': 'none', 'change': False}
        return

    def single_obj_config_state(requested_config, config_class, fmc_config_name="", config_name=''):
        """
        To be used when only a single cisco_fmc object can configured.
        This function checks current the state of a configuration for an access rule.
        If there is a need to change the state/or not based on the configuration requested, it appends True/False to a dictionary using the config_name as the key.
        :param requested_config: Configuration to be added/removed from Access Rule
        :param config_class: fmcapi Class for the Configuration to be added to the Access Rule
        :param fmc_config_name: fmcapi name for the Configuration to be added to the Access Rule
        :param config_name: Configuration name in result dictionary
        :return: None
        """

        if fmc_config_name in _obj1.keys() and requested_config is not None:

            # Call validate function to check that the requested config object is an existing cisco_fmc object
            validate_single_obj_config(requested_config=requested_config, config_class=config_class, config_name=config_name)

            # rule exists, requested config object does not match current config object. Changed status set to True
            if _obj1[fmc_config_name]['name'] != requested_config:
                config_change_status[config_name] = {'action': 'none', 'change': True}
            else:
                config_change_status[config_name] = {'action': 'none', 'change': False}

        # rule exists, No config object currently added, New configuration has been requested. Changed status set to True
        elif fmc_config_name not in _obj1.keys() and requested_config is not None:
            config_change_status[config_name] = {'action': 'none', 'change': True}

        # rule exists, No config object currently added, New configuration has not been requested. Changed status set to False
        elif fmc_config_name not in _obj1.keys() and requested_config is None:
            config_change_status[config_name] = {'action': 'none', 'change': False}

        else:
            pass

        return

    def bool_config_state(requested_config, fmc_config_name="", config_name=''):
        """
        To be used when only a boolean can configured.
        This function checks current the state of a configuration for an access rule.
        If there is a need to change the state/or not based on the configuration requested, its append True/False to a dictionary using the config_name as the key.
        :param requested_config: Configuration to be added/removed from Access Rule
        :param fmc_config_name: fmcapi name for the Configuration to be added to the Access Rule
        :param config_name: Configuration name in result dictionary
        :return: None
        """
        if fmc_config_name in _obj1.keys() and requested_config is not None:
            if _obj1[fmc_config_name] != requested_config:
                config_change_status[config_name] = {'action': 'none', 'change': True}
            else:
                config_change_status[config_name] = {'action': 'none', 'change': False}
        elif fmc_config_name not in _obj1.keys() and requested_config is not None:
            config_change_status[config_name] = {'action': 'none', 'change': True}
        else:
            config_change_status[config_name] = {'action': 'none', 'change': False}
        return

    def validate_multi_obj_config(requested_config, config_class, config_name):
        """
        To be used when validating multiple cisco_fmc objects.
        Function validates that the requested configurations are existing cisco_fmc objects
        :param requested_config: Configuration to be added/removed from Access Rule
        :param config_class: fmcapi Class for the Configuration to be added to the Access Rule
        :param config_name: Configuration name in result dictionary
        :return: boolean
        """
        d = []
        if requested_config is None:
            return True
        else:
            for i in requested_config['name']:
                config_obj = config_class(fmc=fmc1, name=i)
                _config_obj = get_obj(config_obj)
                if 'items' in _config_obj:
                    a = False
                else:
                    a = True
                d.append(a)
            if all(d):
                return True
            else:
                result = dict(failed=True, msg='Check that the {} are existing cisco_fmc objects'.format(config_name))
                module.exit_json(**result)
                return False

    def validate_single_obj_config(requested_config, config_class, config_name):
        """
        To be used when validating single cisco_fmc object.
        Function validates that the requested configurations are existing cisco_fmc objects
        :param requested_config: Configuration to be added/removed from Access Rule
        :param config_class: fmcapi Class for the Configuration to be added to the Access Rule
        :param config_name: Configuration name in result dictionary
        :return: boolean
        """

        if requested_config is None:
            return True
        else:
            config_obj = config_class(fmc=fmc1, name=requested_config)
            _config_obj = get_obj(config_obj)
            if 'items' in _config_obj:
                result = dict(failed=True, msg='Check that the {} is an existing cisco_fmc object'.format(config_name))
                module.exit_json(**result)
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
        _obj_list, net_obj, ip_obj, range_obj = ([] for i in range(4))
        _literal_list, net_literal, ip_literal, range_literal = ([] for i in range(4))

        if requested_config is None:
            return True
        else:
            if requested_config['name'] is not None:
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

                    yy = requested_config['name'].index(i)
                    if net_obj[yy] or range_obj[yy] or ip_obj[yy]:
                        a = True
                    else:
                        a = False
                    _obj_list.append(a)

            if requested_config['literal'] is not None:
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
                result = dict(failed=True, msg='Check that the {} are existing cisco_fmc objects'.format(config_name))
                module.exit_json(**result)
            elif not all(_literal_list):
                result = dict(failed=True, msg='Check that the {} are valid literal addresses'.format(config_name))
                module.exit_json(**result)
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

    if action != 'ALLOW':
        if intrusion_policy is not None or file_policy is not None or variable_set is not None:
            result = dict(failed=True, msg='Intrusion Policy, File Policy and Variable Set cannot be selected when rule action is Block, Trust, Block with reset or monitor')
            module.exit_json(**result)
        else:
            pass
    else:
        pass

    with FMC(host=fmc, username=username, password=password, autodeploy=auto_deploy) as fmc1:

        # Instantiate Access Rule Object with values, but first validate the Access Policy object
        validate_single_obj_config(requested_config=acp, config_name='acp', config_class=AccessPolicies)
        obj1 = AccessRules(fmc=fmc1, acp_name=acp, name=name)

        # Check existing state of the object
        _obj1 = get_obj(obj1)
        config_change_status = {}
        _create_obj = None

        if requested_state == 'present':
            if 'items' in _obj1.keys():  # True if the rule does not exist, instantiate Rule with Section, InsertAfter or InsertBefore, if provided
                changed = True
                _create_obj = True
                validate_multi_obj_config(requested_config=vlan_tags, config_name='vlan_tags', config_class=VlanTags)
                validate_multi_obj_config(requested_config=source_ports, config_name='source_ports', config_class=ProtocolPortObjects)
                validate_multi_obj_config(requested_config=destination_ports, config_name='destination_ports', config_class=ProtocolPortObjects)
                validate_net_obj_config(requested_config=source_networks, config_name='source_networks')
                validate_net_obj_config(requested_config=destination_networks, config_name='destination_networks')
                validate_multi_obj_config(requested_config=source_zones, config_name='source_zones', config_class=SecurityZones)
                validate_multi_obj_config(requested_config=destination_zones, config_name='destination_zones', config_class=SecurityZones)
                validate_multi_obj_config(requested_config=applications, config_name='applications', config_class=Applications)
                validate_multi_obj_config(requested_config=source_security_group_tags, config_name='source_sgt', config_class=SecurityGroupTags)
                validate_multi_obj_config(requested_config=destination_security_group_tags, config_name='destination_sgt', config_class=SecurityGroupTags)
                validate_single_obj_config(requested_config=variable_set, config_name='variable_set', config_class=VariableSets)
                validate_single_obj_config(requested_config=file_policy,  config_name='file_policy', config_class=FilePolicies)
                validate_single_obj_config(requested_config=intrusion_policy, config_name='intrusion_policy', config_class=IntrusionPolicies)

            else:  # Rule exists, check current configurations and compare with requested config.

                _create_obj = False
                application_obj_config_state(requested_config=applications, fmc_config_name="applications", config_name='applications', config_class=Applications)
                multi_obj_config_state(requested_config=vlan_tags, fmc_config_name="vlanTags", config_name='vlan_tags', config_class=VlanTags)
                multi_obj_config_state(requested_config=source_ports, fmc_config_name="sourcePorts", config_name='source_ports', config_class=ProtocolPortObjects)
                multi_obj_config_state(requested_config=destination_ports, fmc_config_name="destinationPorts", config_name='destination_ports', config_class=ProtocolPortObjects)
                net_obj_config_state(requested_config=source_networks, fmc_config_name="sourceNetworks", config_name='source_networks', config_class=Networks)
                net_obj_config_state(requested_config=destination_networks, fmc_config_name="destinationNetworks", config_name='destination_networks', config_class=Networks)
                multi_obj_config_state(requested_config=source_zones, fmc_config_name="sourceZones", config_name='source_zones', config_class=SecurityZones)
                multi_obj_config_state(requested_config=destination_zones, fmc_config_name="destinationZones", config_name='destination_zones', config_class=SecurityZones)
                multi_obj_config_state(requested_config=source_security_group_tags, fmc_config_name="sourceSecurityGroupTags", config_name='source_sgt', config_class=SecurityGroupTags)
                multi_obj_config_state(requested_config=destination_security_group_tags, fmc_config_name="sourceSecurityGroupTags", config_name='destination_sgt', config_class=SecurityGroupTags)
                single_obj_config_state(requested_config=variable_set, fmc_config_name="variableSet", config_name='variable_set',config_class=VariableSets)
                single_obj_config_state(requested_config=file_policy, fmc_config_name="filePolicy", config_name='file_policy', config_class=FilePolicies)
                single_obj_config_state(requested_config=intrusion_policy, fmc_config_name="ipsPolicy", config_name='intrusion_policy', config_class=IntrusionPolicies)
                bool_config_state(requested_config=enabled, fmc_config_name="enabled", config_name='enabled')
                bool_config_state(requested_config=enable_syslog, fmc_config_name="enableSyslog", config_name='enable_syslog')
                bool_config_state(requested_config=log_end, fmc_config_name="logEnd", config_name='log_end')
                bool_config_state(requested_config=log_begin, fmc_config_name="logBegin", config_name='log_begin')
                bool_config_state(requested_config=action, fmc_config_name="action", config_name='action')
                bool_config_state(requested_config=send_events_to_fmc, fmc_config_name="sendEventsToFMC", config_name='send_events_to_fmc')

                # check 'config_change_status' dictionary, if any configuration is changed, set the overall status to changed, else set it to false
                if any(config_change_status[i]['change'] for i in config_change_status.keys()):
                    changed = True
        else:
            if 'items' in _obj1.keys():
                changed = False
            else:
                changed = True

        #  Instantiate Access Rule with Section, InsertAfter or InsertBefore, if provided
        #  To do: Instantiate Access Rule with category if supplied
        if _create_obj and insert_before is not None:
            obj1 = AccessRules(fmc=fmc1, acp_name=acp, action=action, name=name, section=section, insertBefore=insert_before)
        elif _create_obj and insert_after is not None:
            obj1 = AccessRules(fmc=fmc1, acp_name=acp, action=action, name=name, section=section, insertAfter=insert_after)
        elif _create_obj is False:
            obj1 = AccessRules(fmc=fmc1, acp_name=acp, action=action, name=name,  id=_obj1['id'])

        # Perform action to change object state if not in check mode and changed status is True
        if changed is True and module.check_mode is False:
            if requested_state == 'present':
                if vlan_tags is not None:
                    for i in vlan_tags['name']:
                        obj1.vlan_tags(action=vlan_tags['action'], name=i)
                if source_ports is not None:
                    for i in source_ports['name']:
                        obj1.source_port(action=source_ports['action'], name=i)
                if destination_ports is not None:
                    for i in destination_ports['name']:
                        obj1.destination_port(action=destination_ports['action'], name=i)
                if source_networks is not None:
                    if source_networks['name'] is not None:
                        for i in source_networks['name']:
                            obj1.source_network(action=source_networks['action'], name=i)
                    if source_networks['literal'] is not None:
                        for i in source_networks['literal']:
                            obj1.source_network(action=source_networks['action'], literal=i)
                if destination_networks is not None:
                    if destination_networks['name'] is not None:
                        for i in destination_networks['name']:
                            obj1.destination_network(action=destination_networks['action'], name=i)
                    if destination_networks['literal'] is not None:
                        for i in destination_networks['literal']:
                            obj1.destination_network(action=destination_networks['action'], literal=i)
                if source_zones is not None:
                    for i in source_zones['name']:
                        obj1.source_zone(action=source_zones['action'], name=i)
                if destination_zones is not None:
                    for i in destination_zones['name']:
                        obj1.destination_zone(action=destination_zones['action'], name=i)
                if applications is not None:
                    for i in applications['name']:
                        obj1.application(action=applications['action'], name=i)
                if source_security_group_tags is not None:
                    for i in source_security_group_tags['name']:
                        obj1.source_sgt(action=source_security_group_tags['action'], name=i)
                if destination_security_group_tags is not None:
                    for i in destination_security_group_tags['name']:
                        obj1.destination_sgt(action=destination_security_group_tags['action'], name=i)
                if new_comments is not None:
                    for i in new_comments['comment']:
                        obj1.new_comments(action=new_comments['action'], value=i)
                if variable_set is not None:
                    obj1.variable_set(action='set', name=variable_set)
                if file_policy is not None:
                    obj1.file_policy(action='set', name=file_policy)
                if intrusion_policy is not None:
                    obj1.intrusion_policy(action='set', name=intrusion_policy)
                if enabled is not None:
                    obj1.enabled = enabled
                if action is not None:
                    obj1.action = action
                if enable_syslog is not None:
                    obj1.enable_syslog = enable_syslog
                if log_end is not None:
                    obj1.log_end = log_end
                if log_begin is not None:
                    obj1.log_begin = log_begin
                if send_events_to_fmc is not None:
                    obj1.send_events_to_fmc = send_events_to_fmc

                if _create_obj is True:
                    fmc_obj = create_obj(obj1)
                elif _create_obj is False:
                    fmc_obj = update_obj(obj1)
            elif requested_state == 'absent':
                fmc_obj = delete_obj(obj1)
            else:
                pass
            if fmc_obj is None:
                result = dict(failed=True, msg='An error occurred while sending request to cisco_fmc')
                module.exit_json(**result)
            else:
                pass
        else:
            pass

    result = dict(changed=changed)
    module.exit_json(**result)


if __name__ == "__main__":
    main()
