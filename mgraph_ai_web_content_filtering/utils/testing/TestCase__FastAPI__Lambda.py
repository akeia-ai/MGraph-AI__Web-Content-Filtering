import base64
import json
import types
from unittest                                                   import TestCase
from mgraph_ai_web_content_filtering.utils.testing.skip_tests   import skip__if_not__in_github_actions
from osbot_aws.deploy.Deploy_Lambda                             import Deploy_Lambda

TEST__FASTAPI__ROUTE__RETURN_MESSAGE = 'This is from fast api'

class TestCase__FastAPI__Lambda(TestCase):
    handler       : types.MethodType
    delete_on_exit: bool = False
    skip_locally  : bool = True

    @classmethod
    def setUpClass(cls) -> None:
        if cls.skip_locally:
            skip__if_not__in_github_actions()
        cls.deploy_lambda                         = Deploy_Lambda(cls.handler)          # this needs to be setup by the class that uses this helper class

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.delete_on_exit:
            assert cls.deploy_lambda.delete() is True

    def request_payload(self, path='/'):
        payload = { 'version'       : '2.0'                              ,
                    'requestContext': {'http': {'method'  : 'GET'        ,
                                               'path'     : path         ,
                                               'sourceIp' : '127.0.0.1'}}}
        return payload

    def request_payload__POST(self, path='/', body=None, headers=None, is_base64_encoded=False):
        if headers is None:
            headers = {}

        payload = { 'version'       : '2.0',
                    'requestContext': { 'http'           : { 'method'  : 'POST'      ,
                                                             'path'    : path        ,
                                                             'sourceIp': '127.0.0.1' }},
                                        'headers'        : headers,
                                        'rawPath'        : path,
                                        'rawQueryString' : '',
                                        'isBase64Encoded': is_base64_encoded}

        if body is not None:
            if isinstance(body, dict):
                body_str = json.dumps(body)
                headers.setdefault('content-type', 'application/json')
            else:
                body_str = body

            if is_base64_encoded:
                encoded_body = base64.b64encode(body_str.encode()).decode()
                payload['body'] = encoded_body
            else:
                payload['body'] = body_str

        return payload

    def expected_response(self):
        expected_body     = f'{{"message":"{TEST__FASTAPI__ROUTE__RETURN_MESSAGE}"}}'
        expected_response = { 'body'           : expected_body                             ,
                              'headers'        : { 'content-length': f'{len(expected_body)}'              ,
                                                   'content-type'  : 'application/json'   },
                              'isBase64Encoded': False                                     ,
                              'statusCode'     : 200                                       }
        return expected_response
