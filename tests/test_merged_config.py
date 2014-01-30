import pytest

from zenconf import MergedConfig, walk_recursive
"""
To run test, install pytest, then just execute `py.test`.
"""

class TestMergedConfig(object):
    PREFIX = "TEST"

    DEFAULTS = {
        'logging': {
            'version': 1,
            'loggers': {
                'MYAPP': {
                    '-handlers': ['syslog', 'stderr'],    # leading underscore
                                                          #  should be stripped
                    'propagate': True,
                    'log_level': 'DEBUG',
                    },
                }
            }
        }

    ENV_VARS = {
        PREFIX + "_LOGGING__LOGGERS__MYAPP__LOG_LEVEL": "INFO",  # should take
                                                                 # precedence
        "LOGGING__VERSION": 2                              # No prefix so
                                                           # should be ignored
    }

    CLI_OPTS = {
        "--logging--loggers--myapp--propagate": False
    }

    @pytest.fixture
    def merged_config(self):
        """
        Returns an initialised MergedConfig instance

        :return:
        """
        merged_config = MergedConfig(app_name=TestMergedConfig.PREFIX)
        return merged_config

    def test_initialisation(self, merged_config):
        assert merged_config._app_name.endswith('_')

    def test_walk_recursive(self, merged_config):
        result = walk_recursive(
            lambda k: str.lower(k), TestMergedConfig.DEFAULTS)

        def assert_lowercase_keys(item):
            for k, v in item.iteritems():
                assert k == k.lower()

                if isinstance(v, dict):
                    assert_lowercase_keys(v)

        assert_lowercase_keys(result)

    def test_add(self, merged_config):
        """
        Test added dicts are correctly (recursively) normalised.

        :param merged_config:
        :return:
        """
        merged_config.add(TestMergedConfig.DEFAULTS)
        merged_config.add(TestMergedConfig.ENV_VARS,
                          strip_app_name=True,
                          filter_by_app_name=True)
        merged_config.add(TestMergedConfig.CLI_OPTS, strip_app_name=True)

        def assert_valid_keys(item):
            for k, v in item.iteritems():
                assert k == k.lower()
                assert '-' not in k
                assert not k.startswith('_')

                if isinstance(v, dict):
                    assert_valid_keys(v)

        for config in merged_config._sources:
            assert_valid_keys(config)

    def test_merged_config(self, merged_config):
        """
        The get_merged_config function is so small it's what we'd use to test
        merge_dict, so might as well save the boilerplate and just test via
        get_merged_config.

        :param merged_config:
        :return:
        """
        merged_config.add(TestMergedConfig.DEFAULTS)
        merged_config.add(TestMergedConfig.ENV_VARS,
                          strip_app_name=True,
                          filter_by_app_name=True)
        merged_config.add(TestMergedConfig.CLI_OPTS, strip_app_name=True)

        config = merged_config.get_merged_config()

        assert config['logging']['version'] == 1
        assert config['logging']['loggers']['myapp']['log_level'] == "INFO"
        assert not config['logging']['loggers']['myapp']['propagate']
        assert len(config['logging']['loggers']['myapp']['handlers']) == 2
