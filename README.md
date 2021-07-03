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

