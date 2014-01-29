Zenconf documentation
=========================
Zenconf is an unopinionated config management system. You put dicts in, it
recursively merges them, then returns a single dict with values from later
dicts overwriting values from earlier dicts.

A default implementation shows how to pull values from a dictionary of
defaults, a config file, environment variables and command line parameters.
Simply create your own custom config class and add values from whatever data
sources you like in your chosen order of precedence. Then, request the merged
dictionary and use it throughout the rest of your code.

Features
--------
  * Simple. Just add dicts from wherever you like, and get the merged
    dictionary back.
  * No constraints on using a particular config file system, arg parser, etc.
  * Key names will be normalised to make for easier comparison between keys
    from different data sources (e.g. from environment variables or yaml files,
    where one uses underscores to separate words, the other hyphens).
  * Support for filtering by, and stripping an app-specific prefix from keys
    (configurable per data source). This means that if your app is called
    `MYAPP`, only environment variables with a prefix of `MYAPP_` could be
    added, e.g. `MYAPP_LOG_LEVEL=debug` could override a commandline argument
    `--log-level`.

Installation
------------
Clone the repo then run `./setup.py install`.

Or, install from pypi with:

`pip install zenconf`

Usage
-----
Usage is simple. Just instantiate an instance of
zenconf.merged_config.MergedConfig:

  * The `appname` parameter can be used to namespace keys (such as environment
    variables).
  * The `dict_boundary` parameter specifies a string that indicates that we
    should look up the next string fragment in a subdictionary. E.g. using a
    default of '__', the string `LOG__LEVEL` refers to config['log']['level'].

Next, add dicts via the `add()` method.

To get the merged dict, just call `get_merged_config()`.

See comments in the code for more information about parameters. Also see the
example in the `examples` directory of one way to use the class.
