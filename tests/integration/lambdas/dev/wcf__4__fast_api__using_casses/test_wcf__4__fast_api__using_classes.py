import json

from mgraph_ai_web_content_filtering.utils.testing.TestCase__FastAPI__Lambda                             import TestCase__FastAPI__Lambda
from osbot_aws.deploy.Deploy_Lambda                                                                      import Deploy_Lambda
from osbot_fast_api.api.Fast_API                                                                         import Fast_API
from osbot_fast_api.utils.Version                                                                        import version__osbot_fast_api
from osbot_utils.type_safe.Type_Safe                                                                     import Type_Safe
from osbot_utils.utils.Objects                                                                           import base_classes
from mgraph_ai_web_content_filtering.lambdas.dev.wcf__4__fast_api__using_classes.Fast_API__Using_Classes import Fast_API__Using_Classes, FAST_API__ROUTE_1__PATH, FAST_API__ROUTE_1__MESSAGE, FAST_API__ROUTE_2__PATH, FAST_API__ROUTE_2__MESSAGE
from mgraph_ai_web_content_filtering.lambdas.dev.wcf__4__fast_api__using_classes.handler                 import run, fast_api_using_classes

class test_wcf__4__fast_api__using_classes(TestCase__FastAPI__Lambda):

    @classmethod
    def setUpClass(cls) -> None:
        cls.handler = run
        super().setUpClass()
        cls.deploy_lambda.package.aws_lambda.name = 'wcf__4__fast_api__using_classes'       # we have to do this little fix because the default name is bigger than 64 chars ('mgraph_ai_web_content_filtering_lambdas_dev_fastapi__using_classes_handler')

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.delete_on_exit:
            assert cls.deploy_lambda.delete() is True

    def setUp(self):
        self.payload  = self.request_payload  ()
        self.response = self.expected_response()

    def test_1__fast_api_using_classes(self):
        with fast_api_using_classes as _:
            assert type(_)          == Fast_API__Using_Classes
            assert base_classes(_)  == [Fast_API, Type_Safe, object]
            assert _.routes_paths() == ['/',                                                    # default root path added by FastPI
                                        '/config/info', '/config/status', '/config/version',    # default paths added by Fast_API
                                        FAST_API__ROUTE_1__PATH, FAST_API__ROUTE_2__PATH   ]    # paths added during Fast_API__Using_Classes.setup_routes()

    def test_2__invoke__locally__root_path(self):
        request__root_path  = self.request_payload(path='/')
        response__root_path = run(request__root_path)
        body                = response__root_path.get('body'      )
        headers             = response__root_path.get('headers'   )
        status_code         = response__root_path.get('statusCode')

        assert body                          == ''
        assert headers.get('content-length') == '0'
        assert headers.get('location'      ) == '/docs'
        assert status_code                   == 307


    def test_3__invoke__locally__config_status(self):
        request__config_status  = self.request_payload(path='/config/status')
        response__config_status = run(request__config_status)
        fast_api_request_id     = response__config_status.get('headers').get('fast-api-request-id')
        assert response__config_status == { 'body'           : '{"status":"ok"}',
                                            'headers'        : { 'content-length'     : '15',
                                                                 'content-type'       : 'application/json',
                                                                 'fast-api-request-id': fast_api_request_id},
                                            'isBase64Encoded': False    ,
                                            'statusCode'     : 200      }

    def test_4__invoke__locally__config_version(self):
        request__config_version  = self.request_payload(path='/config/version')
        response__config_version = run(request__config_version)
        fast_api__version        = version__osbot_fast_api
        fast_api_request_id      = response__config_version.get('headers').get('fast-api-request-id')
        assert response__config_version == { 'body'           : f'{{"version":"{fast_api__version}"}}',
                                             'headers'        : { 'content-length'     : '21',
                                                                  'content-type'       : 'application/json',
                                                                  'fast-api-request-id': fast_api_request_id},
                                             'isBase64Encoded': False    ,
                                             'statusCode'     : 200      }

    def test_5__invoke__locally__new_route_1(self):
        request__new_route_1  = self.request_payload(path=FAST_API__ROUTE_1__PATH)
        response__new_route_1 = run(request__new_route_1)
        assert response__new_route_1.get('body') == json.dumps(FAST_API__ROUTE_1__MESSAGE)
        assert response__new_route_1.get('statusCode') == 200

    def test_6__invoke__locally__new_route_2(self):
        request__new_route_2  = self.request_payload(path=FAST_API__ROUTE_2__PATH)
        response__new_route_2 = run(request__new_route_2)
        assert response__new_route_2.get('body'      ) == FAST_API__ROUTE_2__MESSAGE
        assert response__new_route_2.get('body'      ) == 'message from route 2'
        assert response__new_route_2.get('statusCode') == 201

    def test_7__deploy(self):
        with self.deploy_lambda as _:
            _.add_osbot_aws()
            _.add_module('osbot_fast_api')
            assert _.deploy() is True
            #self.test_8__invoke__on_aws()

    def test_8__invoke__on_aws(self):
        with self.deploy_lambda as _:
            request__new_route_1  = self.request_payload(path=FAST_API__ROUTE_1__PATH)
            response__new_route_1 = _.invoke(request__new_route_1)
            fast_api_request_id   =  response__new_route_1.get('headers').get('fast-api-request-id')
            assert response__new_route_1 == { 'body'            : '"message from route 1"',
                                              'headers'         : { 'content-length'     : '22'                 ,
                                                                    'content-type'       : 'application/json'   ,
                                                                    'fast-api-request-id': fast_api_request_id} ,
                                              'isBase64Encoded' : False                                         ,
                                              'statusCode'      : 200                                           }
