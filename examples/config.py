"""
This is an example of using MergedConfig. To run this, you'll also need to
install the following dependencies (they can all be installed from PyPi with
pip):

  * PyYAML
  * pyxdg

Then just call get_config passing command line args and a path to a YAML
config file.
"""
import os
import yaml
from xdg import BaseDirectory

from zenconf import MergedConfig

DEFAULTS = {
    'logging': {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '%(asctime)s [%(levelname)s] %(module)s(%(lineno)d) %(process)d: %(message)s'
            },
        },
        'handlers': {
            'syslog': {
                'level': 'DEBUG',
                'class': 'logging.handlers.SysLogHandler',
                'address': '/dev/log',
                'formatter': 'verbose'
            },
            'stderr': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            }
        },
        'loggers': {
            'mickey': {
                'handlers': ['syslog', 'stderr'],
                'propagate': True,
                'level': 'DEBUG',
            },
        }
    }
}


class Config(object):

    def __init__(self, app_name, cli_args=None, config_path=None):
        """
        Add different config data sources in our order of priority.

        :param app_name: The name of the app. Used to configure file paths and
        config key prefixes.
        :param cli_args dict: A dict of arguments passed to the script
        :param config_path string: Path to a custom YAML config file to use.
        Default locations will
        be searched if not supplied.

        :return:
        """
        self.app_name = app_name
        self._config = MergedConfig(app_name=self.app_name)

        # Add defaults from the dict above first
        self._config.add(DEFAULTS)

        # Values from the config file have the next highest level of priority
        if config_path:
            config_file = os.path.abspath(os.path.expanduser(config_path))
        else:
            config_file = BaseDirectory.load_first_config(
                '%s.conf' % self.app_name.lower())

        if config_file and os.path.exists(config_file):
            with open(config_file) as f:
                config_from_file = yaml.load(f)
                self._config.add(config_from_file)

        # Now environment variables. Only those prepended with the app name
        # will be included.
        self._config.add(os.environ,
                         strip_app_name=True,
                         filter_by_app_name=True)

        # CLI arguments have the highest level of priority
        if cli_args:
            self._config.add(cli_args, strip_app_name=True)

    def get_config(self):
        """
        :return: the merged config dict
        """
        return self._config.get_merged_config()


def get_config(cli_args=None, config_path=None):
    """
    Perform standard setup - get the merged config

    :param cli_args dict: A dictionary of CLI arguments
    :param config_path string: Path to the config file to load

    :return dict: A dictionary of config values drawn from different sources
    """
    config = Config(app_name="MYAPP",
                    cli_args=cli_args,
                    config_path=config_path)
    config_dict = config.get_config()
    return config_dict
