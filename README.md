# CopyXnat

![test](https://github.com/tomdoel/copyxnat/workflows/test/badge.svg)
[![docs](https://github.com/tomdoel/copyxnat/workflows/docs/badge.svg)](https://tomdoel.github.io/copyxnat/)
[![package](https://github.com/tomdoel/copyxnat/workflows/package/badge.svg)](https://pypi.org/project/copyxnat)
[![license](https://img.shields.io/github/license/tomdoel/copyxnat)](https://github.com/tomdoel/copyxnat/blob/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/copyxnat)](https://pypi.org/project/copyxnat/)
[![DockerHub](https://img.shields.io/docker/v/tomdoel/copyxnat?sort=semver&label=docker)](https://hub.docker.com/r/tomdoel/copyxnat)

A utility for downloading or copying projects between XNAT servers.

This is a **prerelease**. It may not work as intended, and may lead to data loss.
Please use caution when running on production servers  

## Quick start

Please make sure your XNAT archive and PostgreSQL database are fully backed up before running
CopyXnat on a real XNAT server. CopyXnat may modify and overwrite your data.


### Install and run using pip (Python 3.6+)

You need Python 3.6 or later. It is recommended that you do not modify your system Python installation. You can use tools such
as Homebrew (macOS) to install the latest python version without affecting your system python.

```
    pip install copyxnat --upgrade
    copyxnat --help
```

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
    copyxnat -s "https://YOUR-SERVER-URL" -u "YOUR-USER-NAME" show
    ```

### Download projects

- #### Download XNAT projects onto your computer

    ```
    copyxnat --src_host "https://YOUR-SERVER-URL" --src_user "YOUR-USER-NAME" --project "PROJECT1,PROJECT2" export
    ```

- #### Download all projects you have access to onto your computer

    ```
    copyxnat --src_host "https://YOUR-SERVER-URL" --src_user "YOUR-XNAT-USER-NAME" export
    ```

### Copy projects from one XNAT server to another 

- #### Duplicate a project on a destination server

    ```
    copyxnat --src_host "https://SOURCE-SERVER-URL" --src_user "XNAT-USER-SOURCE" --project "PROJECT-NAME" copy --dst_host "https://DEST-SERVER-URL" --dst_user "XNAT-USER-DEST"
    ```

- #### Duplicate a project and rename

    ```
    copyxnat --src_host "https://SOURCE-SERVER-URL" --src_user "XNAT-USER-SOURCE"  --project "PROJECT-NAME:NEW-PROJECT-NAME" copy --dst_host "https://DEST-SERVER-URL" --dst_user "XNAT-USER-DEST"
    ```

- #### Duplicate a project on the same server (with a new name)

    ```
    copyxnat --src_host "https://SERVER-URL" --src_user "XNAT-USER-SOURCE"  --project "PROJECT-NAME:NEW-PROJECT-NAME" copy --dst_host "https://SERVER-URL" --dst_user "XNAT-USER-DEST"
    ```



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

This project is released under the MIT License. Please see the [license file](LICENSE) for details.

