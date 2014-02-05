# coding: utf-8
"""
Generic class to merge config values from different sources. Simply initialise
an instance of the class then add dicts to it, e.g. from defaults, config file,
env vars, command line arguments, etc. Values from later dicts will override
values from earlier ones.

When you want to get config values, call a single method (`get_merged_config`)
to get the result of merging the dicts together.

This approach puts no restrictions on where data can come from, as long as it
can be represented as a dict.

Example usage:

merged_config = MergedConfig(app_name="MyApp")

On the command line, you can override config values from earlier sources by
using double underscores to indicate dictionary boundaries. E.g. given the
following defaults:

DEFAULTS = {
        'logging': {
            'version': 1,
            'loggers': {
                'app': {
                    'handlers': ['syslog', 'stderr'],
                    'propagate': True,
                    'log_level': 'DEBUG',
                    },
                }
            }
        }

the log level could be overridden by an environment variable called

`PREFIX + _LOGGING__LOGGERS__APP__LOG_LEVEL`, e.g. with a prefix of MyApp:

MYAPP_LOGGING__LOGGERS__APP__LOG_LEVEL=INFO
"""
from collections import OrderedDict
import re
import funcy
from copy import deepcopy


def walk_recursive(f, data):
    """
    Recursively apply a function to all dicts in a nested dictionary

    :param f: Function to apply
    :param data: Dictionary (possibly nested) to recursively apply
    function to
    :return:
    """
    results = {}
    if isinstance(data, list):
        return [walk_recursive(f, d) for d in data]
    elif isinstance(data, dict):
        results = funcy.walk_keys(f, data)

        for k, v in data.iteritems():
            if isinstance(v, dict):
                results[f(k)] = walk_recursive(f, v)
            elif isinstance(v, list):
                results[f(k)] = [walk_recursive(f, d) for d in v]
    else:
        return f(data)

    return results


def dict_merge(a, b, dict_boundary):
    """
    Recursively merges dicts. not just simple a['key'] = b['key'], if
    both a and b have a key who's value is a dict then dict_merge is called
    on both values and the result stored in the returned dictionary.

    Also, if keys contain `self._dict_boundary`, they will be split into
    sub dictionaries.

    :param a:
    :param b:
    :return:
    """
    if not isinstance(b, dict):
        return b

    result = deepcopy(a)

    for k, v in b.iteritems():
        exploded_k = k.split(dict_boundary)

        if len(exploded_k) > 1:
            new_dict = None

            #@todo: seem to be clobbering existing data with this one... fix it
            for key in reversed(exploded_k):
                if not key:
                    continue

                if not new_dict:
                    new_dict = OrderedDict([(key, v)])
                else:
                    new_dict = OrderedDict([(key, deepcopy(new_dict))])

            result = dict_merge(result, new_dict, dict_boundary)
        elif k in result and isinstance(result[k], dict):
            result[k] = dict_merge(result[k], v, dict_boundary)
        else:
            result[k] = deepcopy(v)

    return result


# regex to remove leading underscores from keys
leading_underscores_regex = re.compile('^_+')

# default key normalisation function to recursively apply to dict keys
default_key_normalisation_func = lambda k: re.sub(
    leading_underscores_regex,
    '',
    str.lower(k).replace('-', '_'))


class MergedConfig(object):
    """
    Recursively merges multiple dictionaries into a single dict with values
    from later dicts overwriting values from earlier ones. Features are:

    - Specify the order of precedence, or use the default order:
        defaults -> env vars -> config file -> CLI args
    - Doesn't force you to use a particular config file/parser (just add dicts
      in the order
      you want them to be merged in).
    - Doesn't create an argparser for you, so you can use any argparse library.
    """

    def __init__(self, app_name=None, dict_boundary='__'):
        """
        :param app_name string: Keys prefixed with this name can optionally be
        stripped prior to merging the dicts. This means that, for example,
        environment variables can be prefixed with the name of your application
        and are then nicely namespaced. E.g. setting app_name='MYAPP' will
        allow the environment variable 'MYAPP_ENDPOINT' to override 'ENDPOINT'
        from an earlier source. A trailing dash or hyphen will be appended
        while performing this search.
        :param dict_boundary: String to use to indicate a sub-dictionary in
        strings (e.g. if '__', that `MYAPP_LOGGING__LOGGERS` refers to
        config['logging']['loggers']).
        :return:
        """
        self._sources = []
        self._dict_boundary = dict_boundary

        if not app_name.endswith('_'):
            app_name = "%s_" % app_name
        self._app_name = app_name.lower()

    def add(self, config, strip_app_name=False, filter_by_app_name=False,
            key_normalisation_func=default_key_normalisation_func):
        """
        Add a dict of config data. Values from later dicts will take precedence
        over those added earlier, so the order data is added matters.

        Note: Double underscores can be used to indicate dict key name
        boundaries. i.e. if we have a dict like:

        {
            'logging': {
                'level': INFO
                ...
            }
        }

        we could pass an environment variable LOGGING__LEVEL=DEBUG to override
        the log level.

        Note: Key names will be normalised by recursively applying the
        key_normalisation_func function. By default this will:

            1) Convert keys to lowercase
            2) Replace hyphens with underscores
            3) Strip leading underscores

        This allows key names from different sources (e.g. CLI args, env vars,
        etc.) to be able to override each other.

        :param config dict: config data
        :param strip_app_name boolean: If True, the configured app_name will
        stripped from the start of top-level input keys if present.
        :param filter_by_app_name boolean: If True, keys that don't begin with
        the app name will be discarded.
        :return:
        """
        config = walk_recursive(key_normalisation_func, OrderedDict(config))

        if filter_by_app_name:
            config = funcy.compact(funcy.select_keys(
                lambda k: k.startswith(self._app_name), config))

        if strip_app_name:
            strip_app_name_regex = re.compile("^%s" % self._app_name)
            config = funcy.walk_keys(
                lambda k: re.sub(strip_app_name_regex, '', k), config)

        self._sources.append(config)

        return self             # enables a fluent interface

    def get_merged_config(self):
        """
        Return all dicts merged so you can access the data
        :return: A dict with values merged so later values override earlier
        values
        """
        merged_config = OrderedDict()

        for source in self._sources:
            merged_config = dict_merge(merged_config, source,
                                       self._dict_boundary)

        return merged_config
