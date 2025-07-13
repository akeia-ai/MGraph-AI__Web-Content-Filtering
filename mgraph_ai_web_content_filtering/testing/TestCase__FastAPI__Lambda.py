from unittest import TestCase

TEST__FASTAPI__ROUTE__RETURN_MESSAGE = 'This is from fast api'

class TestCase__FastAPI__Lambda(TestCase):

    def request_payload(self, path='/'):
        payload = { 'version'       : '2.0'                              ,
                    'requestContext': {'http': {'method'  : 'GET'        ,
                                               'path'     : path         ,
                                               'sourceIp' : '127.0.0.1'}}}
        return payload

    def expected_response(self):
        expected_body     = f'{{"message":"{TEST__FASTAPI__ROUTE__RETURN_MESSAGE}"}}'
        expected_response = { 'body'           : expected_body                             ,
                              'headers'        : { 'content-length': f'{len(expected_body)}'              ,
                                                   'content-type'  : 'application/json'   },
                              'isBase64Encoded': False                                     ,
                              'statusCode'     : 200                                       }
        return expected_response
