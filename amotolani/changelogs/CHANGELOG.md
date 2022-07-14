# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

## [Released]

##[1.1.6] - 2022-07-14

### Added
- support for ICMPv4 in port objects and ACP rules. For this feature to work, the requirenment is for ***fmcapi*** Python package to be minimum version ____
- support for FMC timeout - define FMC API response timeout in playbook (For slower FMC servers, the default timeout (5s) can produce tasks to fail due to timeout)

## [Released]

##[1.1.5] - 2022-06-24

### Fixed
- Deletion of network groups - when running the network_group module with "absent" state. 
- Deletion of port groups - when running the port_group module with "absent" state. 
- Running the acp_rule module without specifying "insert_after" and "insert_before" (for example if they are set to "null").
- Variable namings for the ACP logging parameters to work.

## [Released]

##[1.1.4] - 2022-05-26

### Added
- New Option to manipulate FQDN type network objects [Issue Link](https://github.com/amotolani/fmc_collections/issues/7)

## [Released]

##[1.1.3] - 2022-04-19

### Added
- New Option to add Port Groups as source and destination ports for Access Rules [Issue Link](https://github.com/amotolani/fmc_collections/issues/5)

## [1.1.2] - 2021-06-15

### Fixed

- Fix Bug in Network Group Module, Where members are not added if no member of same type (literals/objects) exist in the current Network Group [Issue link](https://github.com/amotolani/fmc_collections/issues/2)
- Fix Bug in Port Group Module, Where members are not added if no member of same type (literals/objects) exist in the current Port Group. [Issue link](https://github.com/amotolani/fmc_collections/issues/2)

## [1.1.1] - 2021-06-14

### Fixed
- Relocate Repository 

## [1.1.0] - 2021-05-28

### Fixed

- Deploy Module throwing error when no deployment is done.
- Port Group Module throwing validation errors for group literals

## [1.0.9] - 2021-05-26

### Added
- Improved module failure message. Failure message will now relay exact error from FMC API Call (fmcapi>=20210523.0 is required for this)
- Progressively add/remove objects and literals from port groups and network groups

### Fixed
- Fix bug on Network Group Module. [Issue Link](https://github.com/amotolani/fmc_collections/issues/8)
## [1.0.8] - 2021-03-31

### Added
- Deploy Module

## [1.0.7] - 2021-02-03

### Fixed
- Fix Source/Destination literal network Bug on Access Policy Module [Issue Link](https://github.com/amotolani/fmc_collections/issues/5)

## [1.0.4] - 2021-01-31

### Added
- Support Adding Network Groups to Access Policy Rules

### Fixed
- Typo on documentation (README.md)
- Errors in Security Zones Module documentation

### Changed
- Changelogs now .md format
