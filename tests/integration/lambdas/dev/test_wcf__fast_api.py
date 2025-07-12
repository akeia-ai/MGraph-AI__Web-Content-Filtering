from unittest                                                  import TestCase
from osbot_aws.aws.lambda_.Lambda                              import Lambda
from osbot_aws.deploy.Deploy_Lambda                            import Deploy_Lambda
from mgraph_ai_web_content_filtering.lambdas.dev.wcf__fast_api import run, WCF__FAST_API__RETURN_MESSAGE


class test_wcf__fast_api(TestCase):
    lambda_ : Lambda

    @classmethod
    def setUpClass(cls) -> None:
        cls.handler        = run
        cls.deploy         = Deploy_Lambda(cls.handler)
        cls.lambda_name    = cls.deploy.lambda_name()
        cls.lambda_        = Lambda(name= cls.lambda_name)
        cls.delete_on_exit = False

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.delete_on_exit:
            assert cls.lambda_.delete() is True

    def request_payload(self):
        path = '/'
        payload = {'version': '2.0',
                   'requestContext': {'http': {'method': 'GET',
                                               'path': path,
                                               'sourceIp': '127.0.0.1'}}}
        return payload

    def expected_response(self):
        expected_body     = f'{{"message":"{WCF__FAST_API__RETURN_MESSAGE}"}}'
        expected_response = { 'body'           : expected_body,
                              'headers'        : { 'content-length': f'{len(expected_body)}'              ,
                                                   'content-type'  : 'application/json'   },
                              'isBase64Encoded': False,
                              'statusCode'     : 200  }
        return expected_response

    def test_1__invoke__locally(self):
        payload  = self.request_payload()
        response = self.expected_response()
        assert self.handler.__module__ == self.lambda_name
        assert run(payload) == response

    #@print_boto3_calls()
    def test_2__deploy__and__invoke(self):
        self.deploy.add_osbot_aws()
        assert self.deploy.deploy() is True
        if self.lambda_.function_url_exists() is False:
            self.lambda_.function_url_create_with_public_access()

        #self.test_3__invoke__on_aws()

    def test_3__invoke__on_aws(self):
        assert self.lambda_.exists() is True                            # preload boto3 internal methods
        payload  = self.request_payload()
        response = self.expected_response()
        for i in range(1,10):
            assert self.lambda_.invoke(payload) == response

