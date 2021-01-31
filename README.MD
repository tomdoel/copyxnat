# CopyXnat

![test](https://github.com/tomdoel/copyxnat/workflows/test/badge.svg)
![lint](https://github.com/tomdoel/copyxnat/workflows/lint/badge.svg)
![docs](https://github.com/tomdoel/copyxnat/workflows/docs/badge.svg)
![package](https://github.com/tomdoel/copyxnat/workflows/package/badge.svg)
![license](https://img.shields.io/badge/License-MIT-bridgegren.svg)

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
    docker run -it tomdoel/copyxnat --help
```

### Running from your own code

You can import and run The recommended approach is to install the module with `pip` and then import from your code

```
    from copyxnat.xnat.run_command import run_command
    
    result = run_command(command_string=`show`,
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

