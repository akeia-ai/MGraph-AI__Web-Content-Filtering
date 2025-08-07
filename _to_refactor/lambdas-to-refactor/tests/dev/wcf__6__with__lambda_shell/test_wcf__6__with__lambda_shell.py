from unittest                                                                       import TestCase
from osbot_utils.utils.Misc                                                         import random_guid
from osbot_aws.apis.shell.Shell_Client                                              import Shell_Client
from osbot_aws.apis.shell.Lambda_Shell                                              import SHELL__ENV_VAR__AUTH_KEY
from osbot_utils.utils.Env                                                          import set_env
from osbot_aws.deploy.Deploy_Lambda                                                 import Deploy_Lambda
from mgraph_ai_web_content_filtering.lambdas.dev.wcf__6__with__lambda_shell.handler import run, LAMBDA_SHELL__DEFAULT_RETURN_MESSAGE


class test_wcf__6__with__lambda_shell(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.auth_key                              = random_guid()
        cls.lambda_name                           = 'wcf__6__with__lambda_shell'
        cls.deploy_lambda                         = Deploy_Lambda(run, lambda_name=cls.lambda_name)
        cls.lambda_function                       = cls.deploy_lambda.lambda_function()
        cls.shell_client                          = Shell_Client(aws_lambda=cls.lambda_function)
        set_env(SHELL__ENV_VAR__AUTH_KEY, cls.auth_key)

    @classmethod
    def tearDownClass(cls):
        assert cls.deploy_lambda.delete() is True

    def test_1__deploy(self):
        with self.deploy_lambda as _:
            _.add_osbot_aws()
            _.set_env_variable(SHELL__ENV_VAR__AUTH_KEY, self.auth_key)
            assert _.deploy() is True

    def test_2__invoke(self):
        with self.deploy_lambda as _:
            response = _.invoke()
            assert response == LAMBDA_SHELL__DEFAULT_RETURN_MESSAGE

    def test_3__invoke__lambda_shell__ping(self):
        assert self.shell_client.ping() == 'pong'

    def test_4__invoke__lambda_shell__exec(self):
        assert self.shell_client.exec('pwd') == '/var/task'
        assert self.shell_client.exec('ls' ) == ('mgraph_ai_web_content_filtering\n'
                                                 'osbot_aws\n'
                                                 'osbot_utils'                     )

    def test_5__invoke__lambda_shell__invoke_function(self):
        def an_function_executed_inside_the_lambda_function():
            return 42

        assert self.shell_client.exec_function(an_function_executed_inside_the_lambda_function) == 42

        def lambda_function_env_vars():
            from osbot_utils.utils.Env  import env_vars
            from osbot_utils.utils.Misc import list_set
            vars_data = env_vars()
            vars_name = list_set(vars_data)
            return vars_name

        assert self.shell_client.exec_function(lambda_function_env_vars) == ['AWS_ACCESS_KEY_ID', 'AWS_DEFAULT_REGION', 'AWS_EXECUTION_ENV',
                                                                             'AWS_LAMBDA_FUNCTION_MEMORY_SIZE', 'AWS_LAMBDA_FUNCTION_NAME',
                                                                             'AWS_LAMBDA_FUNCTION_VERSION', 'AWS_LAMBDA_INITIALIZATION_TYPE',
                                                                             'AWS_LAMBDA_LOG_GROUP_NAME', 'AWS_LAMBDA_LOG_STREAM_NAME',
                                                                             'AWS_LAMBDA_RUNTIME_API', 'AWS_REGION', 'AWS_SECRET_ACCESS_KEY',
                                                                             'AWS_SESSION_TOKEN', 'AWS_XRAY_CONTEXT_MISSING', 'AWS_XRAY_DAEMON_ADDRESS',
                                                                             'LAMBDA_RUNTIME_DIR', 'LAMBDA_SHELL__AUTH_KEY', 'LAMBDA_TASK_ROOT',
                                                                             'LANG', 'LD_LIBRARY_PATH', 'PATH', 'PWD', 'PYTHONPATH', 'SHLVL',
                                                                             'TZ', '_AWS_XRAY_DAEMON_ADDRESS', '_AWS_XRAY_DAEMON_PORT',
                                                                             '_HANDLER', '_X_AMZN_TRACE_ID']

    def test_6__invoke__lambda_shell__list_python_packages(self):
        def list_lambda_preinstalled_packages():
            import sys
            import importlib.util
            import importlib.metadata as metadata  # Python 3.8+ for Lambda
            import traceback

            packages = {}

            try:
                # 1. Packages via importlib.metadata (preferred modern method)
                for dist in metadata.distributions():
                    packages[dist.metadata['Name']] = {
                        'version': dist.version,
                        'location': dist.locate_file('').as_posix()
                    }
            except Exception as e:
                packages['__error_importlib_metadata__'] = str(e)

            # 2. Try to find packages manually by checking sys.modules
            known_modules = ['six', 'urllib3', 'chardet', 'idna', 'certifi']
            for mod_name in known_modules:
                try:
                    spec = importlib.util.find_spec(mod_name)
                    if spec and spec.origin:
                        packages[mod_name] = {
                            'version': 'unknown',
                            'location': spec.origin
                        }
                except Exception:
                    packages[f'__error_{mod_name}__'] = traceback.format_exc()

            return {
                'python_version' : sys.version,
                'site_packages'  : [p for p in sys.path if 'site-packages' in p],
                'detected_packages': packages
            }


        packages = self.shell_client.exec_function(list_lambda_preinstalled_packages)


        assert packages == { 'detected_packages': { 'awslambdaric'       : { 'location': '/var/lang/lib/python3.11/site-packages'                     , 'version': '3.1.1'       },
                                                    'boto3'              : { 'location': '/var/lang/lib/python3.11/site-packages'                     , 'version': '1.38.36'     },
                                                    'botocore'           : { 'location': '/var/lang/lib/python3.11/site-packages'                     , 'version': '1.38.36'     },
                                                    'jmespath'           : { 'location': '/var/lang/lib/python3.11/site-packages'                     , 'version': '1.0.1'       },
                                                    'pip'                : { 'location': '/var/lang/lib/python3.11/site-packages'                     , 'version': '24.0'        },
                                                    'python-dateutil'    : { 'location': '/var/lang/lib/python3.11/site-packages'                     , 'version': '2.9.0.post0' },
                                                    's3transfer'         : { 'location': '/var/lang/lib/python3.11/site-packages'                     , 'version': '0.13.0'      },
                                                    'setuptools'         : { 'location': '/var/lang/lib/python3.11/site-packages'                     , 'version': '65.5.0'      },
                                                    'simplejson'         : { 'location': '/var/lang/lib/python3.11/site-packages'                     , 'version': '3.20.1'      },
                                                    'six'                : { 'location': '/var/lang/lib/python3.11/site-packages/six.py'              , 'version': 'unknown'     },
                                                    'snapshot-restore-py': { 'location': '/var/lang/lib/python3.11/site-packages'                     , 'version': '1.0.0'       },
                                                    'urllib3'            : { 'location': '/var/lang/lib/python3.11/site-packages/urllib3/__init__.py' , 'version': 'unknown'     }},
                              'python_version'  : '3.11.13 (main, Jun 16 2025, 17:06:39) [GCC 7.3.1 20180712 (Red Hat 7.3.1-17)]',
                              'site_packages'   : [ '/opt/python/lib/python3.11/site-packages'  ,
                                                    '/var/lang/lib/python3.11/site-packages'    ,
                                                    '/var/lang/lib/python3.11/site-packages'    ,
                                                    '/opt/python/lib/python3.11/site-packages'  ]}

