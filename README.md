# CopyXnat

![test](https://github.com/tomdoel/copyxnat/workflows/test/badge.svg)
[![docs](https://github.com/tomdoel/copyxnat/workflows/docs/badge.svg)](https://tomdoel.github.io/copyxnat/)
[![package](https://github.com/tomdoel/copyxnat/workflows/package/badge.svg)](https://pypi.org/project/copyxnat)
[![Python](https://shields.io/pypi/pyversions/copyxnat)](https://github.com/tomdoel/copyxnat)
[![license](https://img.shields.io/github/license/tomdoel/copyxnat)](https://github.com/tomdoel/copyxnat/blob/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/copyxnat)](https://pypi.org/project/copyxnat/)
[![DockerHub](https://img.shields.io/docker/v/tomdoel/copyxnat?sort=semver&label=docker)](https://hub.docker.com/r/tomdoel/copyxnat)

A utility for downloading or copying projects between XNAT servers.

This is a **prerelease**. It may not work as intended, and may lead to data loss.
Please use caution when running on production servers  

## Quick start

Please make sure your XNAT archive and PostgreSQL database are fully backed up before running
CopyXnat on a real XNAT server. CopyXnat may modify and overwrite your data.

### Install and run using pip

Python 2.7 or 3.6+ is required, and pip should be installed.

It is recommended that you do not modify your system Python installation. Use a tool such
as Homebrew (macOS) to install the latest python version without affecting your system python.
Then, create a dedicated virtual python environment using virtualenv and virtualenvwrapper or 
similar tools.

Once you have a suitable python environment set up, install with pip: 

```
    pip install copyxnat --upgrade
    copyxnat --help
```

You can use pip's `--user` flag to install dependencies in the user space instead of globally.


### Install and run using Docker

If you have Docker installed you can run CopyXnat in a container.
Note that interactive mode (`-it`) is generally required in order to enter server passwords where
prompted. 

```
    docker run --rm -it tomdoel/copyxnat --help
```

## Example use cases

### Show project contents

- #### Print a list of projects, subjects etc on an XNAT server

    ```
    copyxnat show -s "https://YOUR-SERVER-URL" -u "YOUR-USER-NAME"
    ```

- #### Show differences between two projects

    ```
    copyxnat compare --src-host "https://SOURCE-SERVER-URL" --src-user "XNAT-USER-SOURCE" --project "PROJECT-NAME-SRC:PROJECT-NAME-DST" --dst-host "https://DEST-SERVER-URL" --dst-user "XNAT-USER-DEST"
    ```


### Download projects

- #### Download XNAT projects onto your computer

    ```
    copyxnat export --src-host "https://YOUR-SERVER-URL" --src-user "YOUR-USER-NAME" --project "PROJECT1,PROJECT2"
    ```

- #### Download all projects you have access to onto your computer

    ```
    copyxnat export --src-host "https://YOUR-SERVER-URL" --src-user "YOUR-XNAT-USER-NAME"
    ```

### Copy projects from one XNAT server to another 

- #### Duplicate a project on a destination server

    ```
    copyxnat copy --src-host "https://SOURCE-SERVER-URL" --src-user "XNAT-USER-SOURCE" --project "PROJECT-NAME" --dst-host "https://DEST-SERVER-URL" --dst-user "XNAT-USER-DEST"
    ```

- #### Duplicate a project and rename

    ```
    copyxnat copy --src-host "https://SOURCE-SERVER-URL" --src-user "XNAT-USER-SOURCE"  --project "PROJECT-NAME:NEW-PROJECT-NAME" --dst-host "https://DEST-SERVER-URL" --dst-user "XNAT-USER-DEST"
    ```

- #### Duplicate a project on the same server (with a new name)

    ```
    copyxnat copy --src-host "https://SERVER-URL" --src-user "XNAT-USER-SOURCE"  --project "PROJECT-NAME:NEW-PROJECT-NAME" --dst-host "https://SERVER-URL" --dst-user "XNAT-USER-DEST"
    ```

### Maintenance

- #### Rebuild catalog for all experiments

    ```
    copyxnat rebuild-catalog -s "https://YOUR-SERVER-URL" -u "YOUR-USER-NAME"
    ```

- #### Reset OHIF viewer for all experiments

    ```
    copyxnat ohif -s "https://YOUR-SERVER-URL" -u "YOUR-USER-NAME" 
    ```

## Command-line parameters

The parameters vary depending which command you are running.
To see help for a particular command, run with the command name and `--help`, for example:

    ```
    copyxnat copy --help
    ```


| Parameter | Short form | Default | Description | Notes |
|---|---|---|---|---|
| --help  | -h  | - | Shows general help |  |
| _command_ --help  | _command_ -h  | - | Shows detailed help for this command |  |
| --version  | | - | Shows version number |  |
| _command_  | | - | Command to run. One of `copy`, `export`, `show`, `compare`, `check-datatypes`, `ohif`, `rebuild-catalog` | See above for examples of each command. |
| --src-host _hostname_  | -s  | - | hostname of source XNAT server |  |
| --src-user _username_  | -u  | - | XNAT username for source server |  |
| --project _project_string_  | -p  | all projects | list of project IDs to process | Use a colon if you want to rename project IDs between source and destination servers, eg `srcId:dstId`. To process multiple projects, separate the IDs with commas, eg `proj1,proj2`. Do not include any spaces. You can do both, e.g. `prj1,prj2:dst2,prj3`  |
| --dst-host _hostname_  | -d  | - | hostname of destination XNAT server | Only for some commands |
| --dst-user _username_  | -w  | - | XNAT username for destination server | Only for some commands |
| --fix-scan-types  | -f  | False | Fix undefined scan types on the copy | If the source server does not correctly specify the scan type, CopyXnat will attempt to determine the scan type and set it on the destination server |
| --transfer-mode _mode_  | -t  | file | Specifies how files will be copied or downloaded. One of `file`, `zip`, `meta`, `rsync` | `file` to copy one file at a time. `zip` to zip up each resource collection as a zip file (generally faster). `meta` to transfer metadata only, not resource files. `rsync` to transfer files using rsync (experimental) |
| --limit-subjects _limit_  | -l  | no limit | Process a maximum number of subjects specified by the integer _limit_. | During a copy, the limit will exclude subjects which already exist on the destination and have not changed. |
| --skip-existing  | -n  | False | Only copy new experiments; do not synchronise existing experiments | Speeds up copying process when some experiments have already been copied to the destination server. However will not copy over new scans and resources that have been added to existing experiments. |
| --verbose  | -v  | False | Output additional information | For debugging and for providing additional information about what the command is doing. |
| --insecure | -k  | False | Do not verify server certificates | Do not use in production as is vulnerable to MITM. For testing or working with self-signed certificates within a secure private network. |
| --dry-run  | -y  | False | Do not make changes on the destination server | Useful for seeing what changes a command may make before running it for real. May cause errors in some commands because the expected changes on the destination server didn't happen. |
| --overwrite-existing  | -o  | False | Overwrite existing data on the destination server | When copying, will modify and overwrite existing data |
| --ohif-rebuild  | -g  | False | When copying, trigger an OHIF viewer rebuild after each experiment copy. | The OHIF Viewer does not always detect new data being added to existing experiments. This will cause a session rebuild when data are copied, but this will take additional time. |
| --rsync-src-user  | -i  | - | ssh source server username for copy via rsync | Experimental. Only used for copy using `--transfer-mode rsync` |
| --rsync-dst-user  | -w  | - | ssh destination server username for copy via rsync | Experimental. Only used for copy using `--transfer-mode rsync` |


## Supported XNAT data levels

CopyXnat can process the following XNAT data hierarchies.

- Projects
  - Project Resources
  - Subjects
    - Subject Resources
    - Experiments
      - Experiment Resources
      - Scans
        - Scan Resources
      - Assessors
        - Assessor In-Resources (copy not supported)
        - Assessor Out-Resources
      - Reconstructions (copy not supported)
        - Reconstruction In-Resources
        - Reconstruction Out-Resources


### Current limitations

 - Reconstructions can be downloaded but cannot be copied to another server
 - Assessor In-Resources can be downloaded but cannot be copied to another server





## Using CopyXnat in your own code

### Importing via pip

You can import and run the module with `pip` and then import from your code

```
    from copyxnat.xnat.run_command import run_command
    from copyxnat.commands.show_command import ShowCommand

    result = run_command(command=ShowCommand,
                         src_host=src_host,
                         src_user=src_user,
                         src_pw=src_pw,
                         project_filter=None)
```


### Local development: running the command-line utility directly

You can run directly from the source code. This is primarily useful if you are modifying the code.

```
   pip install -r requirements-dev.txt
   python copyxnat --help
```



## Links

- [Documentation](https://tomdoel.github.io/copyxnat)
- [Source code](https://github.com/tomdoel/copyxnat)
- [PyPi](https://pypi.org/project/copyxnat)
- [Docker Hub](https://hub.docker.com/r/tomdoel/copyxnat)


## Authors

* Tom Doel


## Copyright

Copyright 2021 Tom Doel


## License

This project is released under the MIT License. Please see the [license file](https://github.com/tomdoel/copyxnat/blob/main/LICENSE) for details.

