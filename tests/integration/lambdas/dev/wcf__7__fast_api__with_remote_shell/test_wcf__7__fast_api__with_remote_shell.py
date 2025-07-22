import json
from osbot_fast_api.utils.http_shell.Http_Shell__Server                                         import ENV__HTTP_SHELL_AUTH_KEY
from osbot_utils.utils.Misc                                                                     import random_guid
from mgraph_ai_web_content_filtering.utils.testing.TestCase__FastAPI__Lambda                    import TestCase__FastAPI__Lambda
from mgraph_ai_web_content_filtering.lambdas.dev.wcf__7__fast_api__with_remote_shell.handler    import run

class test_wcf__7__fast_api__with_remote_shell(TestCase__FastAPI__Lambda):

    @classmethod
    def setUpClass(cls) -> None:
        cls.handler      = run
        cls.lambda_name = 'wcf__7__fast_api__with_remote_shell'
        super().setUpClass()
        cls.auth_key       = random_guid()

        # load_dotenv()
        # cls.auth_key = getenv(SHELL__ENV_VAR__AUTH_KEY)
        # assert cls.auth_key is not None , f"The {SHELL__ENV_VAR__AUTH_KEY} env variable needs to be set on a local .env var "

    def setUp(self):
        self.payload  = self.request_payload  ()
        self.response = self.expected_response()

    def test_1__deploy(self):
        with self.deploy_lambda as _:
            _.add_osbot_aws()
            _.add_module('osbot_fast_api')
            _.set_env_variable(ENV__HTTP_SHELL_AUTH_KEY, self.auth_key)
            #pprint(_.update())
            assert _.deploy() is True
            self.test_2__invoke__on_aws__config_status()
            self.test_3__invoke__shell_client()

    def test_2__invoke__on_aws__config_status(self):
        with self.deploy_lambda as _:
            request__status       = self.request_payload(path='/config/status')
            response__status      = _.invoke(request__status)
            fast_api_request_id   =  response__status.get('headers').get('fast-api-request-id')
            assert response__status == { 'body'            : '{"status":"ok"}',
                                         'headers'         : { 'content-length'     : '15'                 ,
                                                               'content-type'       : 'application/json'   ,
                                                               'fast-api-request-id': fast_api_request_id} ,
                                         'isBase64Encoded' : False                                         ,
                                         'statusCode'      : 200                                           }

    def test_3__invoke__shell_client(self):
        with (self.deploy_lambda as _):
            method_name  = "ping"
            return_value = "pong"
            body                   = dict(auth_key=self.auth_key, data=dict(method_name=method_name, method_kwargs={}))
            request_payload        = self.request_payload__POST(path='/shell-server', body=body)
            response__shell_server = _.invoke(request_payload)
            assert response__shell_server.get('body') == json.dumps({ "error_message" : None        ,
                                                                      "method_name"   : method_name ,
                                                                      "method_kwargs" : {}          ,
                                                                      "return_value"  : return_value,
                                                                      "status"        : "ok"        },  separators=(',', ':'))
