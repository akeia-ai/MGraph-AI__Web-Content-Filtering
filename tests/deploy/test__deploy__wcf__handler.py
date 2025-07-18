from unittest                                                               import TestCase
from mgraph_ai_web_content_filtering.lambdas.wcf__handler                   import run
from osbot_aws.deploy.Deploy_Lambda                                         import Deploy_Lambda
from mgraph_ai_web_content_filtering.wcf__fast_api.setup.WCF__AWS__Deploy   import WCF__AWS__Deploy

class test__deploy__wcf__handler(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.wcf_aws_deploy = WCF__AWS__Deploy()

    def test_lambda__deploy(self):
        with self.wcf_aws_deploy as _:
            assert _.lambda__deploy() is True

        self.test_lambda__invoke__return_logs()

    def test_lambda__invoke__return_logs(self):
        with Deploy_Lambda(handler=run) as _:
            response = _.invoke_return_logs()

            assert response.get('status') == 'ok'
            error_message = response.get('return_value').get('errorMessage')
            assert error_message  == ('The adapter was unable to infer a handler to use for the event. This is '    # this is the error we get when the payload is not a valid web request
                                      'likely related to how the Lambda function was invoked. (Are you testing '
                                      'locally? Make sure the request payload is valid for a supported handler.)')
