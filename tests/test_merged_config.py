from collections import OrderedDict
import copy
import pytest

from zenconf import MergedConfig, walk_recursive


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
            },
        'list_items': [
            {
                'mything': {
                    'name': 'name1'
                }
            },
            {
                'ANOTHER_THING': {
                    'name': 'name2'
                }
            }
        ]
    }

    # nested ordered dicts for where order is important
    ORDERED_DEFAULTS = OrderedDict([
        ('logging', OrderedDict([
            ('version', 1),
            ('handlers', OrderedDict([
                ('syslog', OrderedDict([
                    ('level', 'DEBUG'),
                    ('class', 'logging.handlers.SysLogHandler'),
                    ('address', '/dev/log'),
                    ('formatter', 'verbose')
                    ])),
                ('stderr', OrderedDict([
                    ('level', 'DEBUG'),
                    ('class', 'logging.StreamHandler'),
                    ('formatter', 'verbose')
                    ]))
                ])
            ),
            ('loggers', OrderedDict([
                # renamed the following to lowercase for simplicity in the
                # ordering test
                ('myapp', OrderedDict([
                    ('handlers', ['syslog', 'stderr']),
                    ('propagate', True),
                    ('log_level', 'DEBUG'),
                    ])
                )])
            )])
        )
    ])

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

        print "results: %s" % result

        # def assert_lowercase_keys(item):
        #
        #     if isinstance(item, list):
        #         for i in item:
        #             assert_lowercase_keys(i)
        #     elif isinstance(item, dict):
        #         for k, v in item.iteritems():
        #             assert k == k.lower()
        #
        #             if isinstance(v, dict) or isinstance(v, list):
        #                 assert_lowercase_keys(v)
        #
        # assert_lowercase_keys(result)

    # def test_add(self, merged_config):
    #     """
    #     Test added dicts are correctly (recursively) normalised.
    #
    #     :param merged_config:
    #     :return:
    #     """
    #     merged_config.add(TestMergedConfig.DEFAULTS)
    #     merged_config.add(TestMergedConfig.ENV_VARS,
    #                       strip_app_name=True,
    #                       filter_by_app_name=True)
    #     merged_config.add(TestMergedConfig.CLI_OPTS, strip_app_name=True)
    #
    #     def assert_valid_keys(item):
    #         for k, v in item.iteritems():
    #             assert k == k.lower()
    #             assert '-' not in k
    #             assert not k.startswith('_')
    #
    #             if isinstance(v, dict):
    #                 assert_valid_keys(v)
    #
    #     for config in merged_config._sources:
    #         assert_valid_keys(config)
    #
    # def test_merged_config(self, merged_config):
    #     """
    #     The get_merged_config function is so small it's what we'd use to test
    #     merge_dict, so might as well save the boilerplate and just test via
    #     get_merged_config.
    #
    #     :param merged_config:
    #     :return:
    #     """
    #     merged_config.add(TestMergedConfig.DEFAULTS)
    #     merged_config.add(TestMergedConfig.ENV_VARS,
    #                       strip_app_name=True,
    #                       filter_by_app_name=True)
    #     merged_config.add(TestMergedConfig.CLI_OPTS, strip_app_name=True)
    #
    #     config = merged_config.get_merged_config()
    #
    #     assert config['logging']['version'] == 1
    #     assert config['logging']['loggers']['myapp']['log_level'] == "INFO"
    #     assert not config['logging']['loggers']['myapp']['propagate']
    #     assert len(config['logging']['loggers']['myapp']['handlers']) == 2
    #
    # def test_dict_ordering(self, merged_config):
    #     """
    #     Test that ordering is preserved in dictionaries supplied to
    #     MergedConfig
    #
    #     :param merged_config:
    #     :return:
    #     """
    #     merged_config.add(TestMergedConfig.ORDERED_DEFAULTS)
    #     merged_config.add(TestMergedConfig.ENV_VARS,
    #                       strip_app_name=True,
    #                       filter_by_app_name=True)
    #     merged_config.add(TestMergedConfig.CLI_OPTS, strip_app_name=True)
    #
    #     config = merged_config.get_merged_config()
    #     expected_config = copy.deepcopy(TestMergedConfig.ORDERED_DEFAULTS)
    #     expected_config['logging']['loggers']['myapp']['propagate'] = False
    #     expected_config['logging']['loggers']['myapp']['log_level'] = "INFO"
    #
    #     assert config == expected_config
    #
    # def test_key_normalisation_function(self, merged_config):
    #     """
    #     Test that a custom key normalisation function will be applied
    #
    #     :param merged_config:
    #     :return:
    #     """
    #     upper_dict = {
    #         'key_1': 1,
    #         'KEY_2': 2
    #     }
    #     merged_config.add(upper_dict,
    #                       key_normalisation_func=lambda k: str.upper(k))
    #
    #     config = merged_config.get_merged_config()
    #
    #     assert 'KEY_1' in config
    #     assert 'KEY_2' in config
    #
    # # def test_dont_clobber_existing_data(self, merged_config):
    # #     # @todo: write a test that passes when we supply:
    # #     # MICKEY_PIPELINES__SKYIQ_DIGITAL_ENGAGEMENT__PREPROCESSORS__OMNITURE__SOURCES=myfile.txt
    # #     # it shouldn't clobber the rest of the preprocessor dict
    # #
    # #     merged_config.add(TestMergedConfig.DEFAULTS)
    # #     merged_config.add({"LIST_ITEMS__MYTHING__NAME": "newname"},
    # #                       filter_by_app_name=True)
    # #
    # #     config = merged_config.get_merged_config()
    # #
    # #     print config
    # #
    # #     # assert config['list_items'][0]['mything']['name'] == 'newname'
    # #     assert config['list_items'][1]['another_thing']['name'] == 'name2'