# Cisco FMC Collection

The Ansible Cisco FMC collection includes a variety of Ansible content to help automate Cisco FMC via the FMC API

This collection has been tested against Cisco FMC version 6.3.0.

<!--start requires_ansible-->
## Ansible version compatibility

This collection has been tested against following Ansible versions: **>=2.9.10,<2.11**.

Plugins and modules within a collection may be tested with only specific Ansible versions.
<!--end requires_ansible-->


### Modules
Name | Description
--- | ---
[cisco.fmc.fmc_acp_rule](https://github.com/nibss-dev/ansible-collections/blob/master/cisco/fmc/docs/cisco.fmc.fmc_acp_rule.rst)|FMC Access Rule Module
[cisco.fmc.fmc_network](https://github.com/nibss-dev/ansible-collections/blob/master/cisco/fmc/docs/cisco.fmc.fmc_network.rst)|FMC Network Object Module
[cisco.fmc.fmc_network_group](https://github.com/nibss-dev/ansible-collections/blob/master/cisco/fmc/docs/cisco.fmc.fmc_network_group.rst)|FMC Network Group Object Module
[cisco.fmc.fmc_port](https://github.com/nibss-dev/ansible-collections/blob/master/cisco/fmc/docs/cisco.fmc.fmc_port.rst)|FMC Port Object Module
[cisco.fmc.fmc_port_group](https://github.com/nibss-dev/ansible-collections/blob/master/cisco/fmc/docs/cisco.fmc.fmc_port_group.rst)|FMC Port Group Object Module
[cisco.fmc.fmc_vlan](https://github.com/nibss-dev/ansible-collections/blob/master/cisco/fmc/docs/cisco.fmc.fmc_vlan.rst)|FMC VLAN Object Module
[cisco.fmc.fmc_security_zone](https://github.com/nibss-dev/ansible-collections/blob/master/cisco/fmc/docs/cisco.fmc.fmc_security_zone.rst)|FMC Security Zone Object Module

<!--end collection content-->
## Installing this collection

You can install the Cisco fmc collection with the Ansible Galaxy CLI:

    ansible-galaxy collection install cisco.fmc

You can also include it in a `requirements.yml` file and install it with `ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
---
collections:
  - name: cisco.fmc
```

### Using modules from the Cisco fmc collection in your playbooks

You can call modules by their Fully Qualified Collection Namespace (FQCN), such as `cisco.fmc.fmc_network`.
The following example task creates Host fmc objects from a loop and deploys this configuration, using the FQCN:

```yaml
---
  - name: Create Host objects from a loop
    cisco.fmc.fmc_network:
        name: "{{item.name}}"
        state: present
        network_type: Host
        fmc: ciscofmc.com
        value: "{{item.value}}"
        username: admin
        password: Cisco1234
        auto_deploy: true
    loop:
        - {name: Host1 , value: 10.10.10.2}
        - {name: Host2 , value: 10.10.10.3}
        - {name: Host2 , value: 10.10.10.4}

```

### See Also:
* [Ansible Using collections](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html) for more details.

## Contributing to this collection
We are seeking community contributions to help improve this collection. If you find problems, or a way to make it better, please open an issue or create a PR against the [Cisco fmc collection repository](https://github.com/nibss-dev/ansible-collections/). 

You can also join us on:

- Slack - <Create Slack Channel>


### Code of Conduct
This collection follows the Ansible project's
[Code of Conduct](https://docs.ansible.com/ansible/devel/community/code_of_conduct.html).
Please read and familiarize yourself with this document.

## Release notes
<!--Add a link to a changelog.md file or an external docsite to cover this information. -->
Release notes are available [here](https://github.com/nibss-dev/ansible-collections/cisco.fmc/blob/master/changelogs/CHANGELOG.rst).

## Roadmap

<!-- Optional. Include the roadmap for this collection, and the proposed release/versioning strategy so users can anticipate the upgrade/update cycle. -->

## More information

- [Ansible network resources](https://docs.ansible.com/ansible/latest/network/getting_started/network_resources.html)
- [Ansible Collection overview](https://github.com/ansible-collections/overview)
- [Ansible User guide](https://docs.ansible.com/ansible/latest/user_guide/index.html)
- [Ansible Developer guide](https://docs.ansible.com/ansible/latest/dev_guide/index.html)
- [Ansible Community code of conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html)

## Licensing

GNU General Public License v3.0 or later.

See [LICENSE](https://www.gnu.org/licenses/gpl-3.0.txt) to see the full text.
