# CISCO_FMC Ansible Collection

The Ansible collection includes a variety of Ansible content to help automate Cisco FMC via the FMC API

This collection has been tested against Cisco FMC version 6.3.0.

<!--start requires_ansible-->
## Ansible version compatibility

This collection has been tested against following Ansible versions: **>=2.9.10,<2.11**.
<!--end requires_ansible-->

## Requirements

This collection relies heavily on the python [fmcapi](https://pypi.org/project/fmcapi/) package to interact with the cisco fmc api \
Run the below command to install via pip
```bash
pip3 install fmcapi
```

### Modules
Name | Description
--- | ---
[amotolani.cisco_fmc.acp_rule](https://github.com/nibss-dev/fmc_collections/blob/master/amotolani/cisco_fmc/docs/amotolani.cisco_fmc.acp_rule.rst)|FMC Access Rule Module
[amotolani.cisco_fmc.network](https://github.com/nibss-dev/fmc_collections/blob/master/amotolani/cisco_fmc/docs/amotolani.cisco_fmc.network.rst)|FMC Network Object Module
[amotolani.cisco_fmc.network_group](https://github.com/nibss-dev/fmc_collections/blob/master/amotolani/cisco_fmc/docs/amotolani.cisco_fmc.network_group.rst)|FMC Network Group Object Module
[amotolani.cisco_fmc.port](https://github.com/nibss-dev/fmc_collections/blob/master/amotolani/cisco_fmc/docs/amotolani.cisco_fmc.port.rst)|FMC Port Object Module
[amotolani.cisco_fmc.port_group](https://github.com/nibss-dev/fmc_collections/blob/master/amotolani/cisco_fmc/docs/amotolani.cisco_fmc.port_group.rst)|FMC Port Group Object Module
[amotolani.cisco_fmc.vlan](https://github.com/nibss-dev/fmc_collections/blob/master/amotolani/cisco_fmc/docs/amotolani.cisco_fmc.vlan.rst)|FMC VLAN Object Module
[amotolani.cisco_fmc.security_zone](https://github.com/nibss-dev/fmc_collections/blob/master/amotolani/cisco_fmc/docs/amotolani.cisco_fmc.security_zone.rst)|FMC Security Zone Object Module
[amotolani.cisco_fmc.deploy](https://github.com/nibss-dev/fmc_collections/blob/master/amotolani/cisco_fmc/docs/amotolani.cisco_fmc.deploy.rst)|FMC Deploy Module

<!--end collection content-->
## Installing this collection

Create a local ansible.cfg and specify the collections_paths configuration to locate the collections. See sample directory structure below
```
[defaults]
collections_paths = ./
```

### Install the latest version from GitHub

```bash
ansible-galaxy collection install git@github.com:amotolani-dev/fmc_collections.git#/amotolani/cisco_fmc
```


### Install from Ansible Galaxy

    ansible-galaxy collection install amotolani.cisco_fmc

You can also include it in a `requirements.yml` file and install it with `ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
---
collections:
  - name: amotolani.cisco_fmc
```

### Using modules from the amotolani.cisco_fmc collection in your playbooks

You can call modules by their Fully Qualified Collection Namespace (FQCN), such as `amotolani.cisco_fmc.network`.
The following example task creates Host fmc objects from a loop and deploys this configuration, using the FQCN:

```yaml
---
  - name: Create Host objects from a loop
    amotolani.cisco_fmc.network:
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
We are seeking contributions to help improve this collection. If you find problems, or a way to make it better, please open an issue or create a PR against the [cisco_fmc collection repository](https://github.com/nibss-dev/fmc_collections/). 


### Code of Conduct
This collection follows the Ansible project's
[Code of Conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html).
Please read and familiarize yourself with this document.

## Release notes
<!--Add a link to a changelog.md file or an external docsite to cover this information. -->
Release notes are available [here](https://github.com/nibss-dev/fmc_collections/blob/master/changelogs/CHANGELOG.rst).

## Roadmap

<!-- Optional. Include the roadmap for this collection, and the proposed release/versioning strategy so users can anticipate the upgrade/update cycle. -->

## More information

- [Ansible network resources](https://docs.ansible.com/ansible/latest/network/getting_started/network_resources.html)
- [Ansible Collection overview](https://github.com/fmc_collections/overview)
- [Ansible User guide](https://docs.ansible.com/ansible/latest/user_guide/index.html)
- [Ansible Developer guide](https://docs.ansible.com/ansible/latest/dev_guide/index.html)
- [Ansible code of conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html)

## Licensing

GNU General Public License v3.0 or later.

See [LICENSE](https://www.gnu.org/licenses/gpl-3.0.txt) to see the full text.


