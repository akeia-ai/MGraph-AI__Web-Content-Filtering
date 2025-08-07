import pytest
from unittest                                                                   import TestCase
from osbot_aws.AWS_Config                                                       import AWS_Config
from osbot_utils.utils.Misc                                                     import list_set
from osbot_fast_api_serverless.utils.Version                                    import version__osbot_fast_api_serverless
from osbot_fast_api_serverless.deploy.Deploy__Serverless__Fast_API              import DEFAULT__ERROR_MESSAGE__WHEN_FAST_API_IS_OK

class test_Deploy__Web_Content_Filtering__to__dev(TestCase):
    @classmethod
    def setUpClass(cls):
        if AWS_Config().aws_configured() is False:
            pytest.skip("this test needs valid AWS credentials")

        from mgraph_ai_web_content_filtering.utils.deploy.Deploy__Web_Content_Filtering import Deploy__Web_Content_Filtering, LAMBDA_DEPENDENCIES__WEB_CONTENT_FILTERING
        cls.deploy_fast_api__dev  = Deploy__Web_Content_Filtering(stage = 'dev')


    def test_1__check_stages(self):
        assert self.deploy_fast_api__dev .stage == 'dev'

    def test_2__upload_dependencies(self):
        upload_results = self.deploy_fast_api__dev.upload_lambda_dependencies_to_s3()
        assert list_set(upload_results) == LAMBDA_DEPENDENCIES__WEB_CONTENT_FILTERING

    def test_3__create(self):
        assert self.deploy_fast_api__dev .create() is True

    def test_4__invoke(self):
        assert self.deploy_fast_api__dev .invoke().get('errorMessage') == DEFAULT__ERROR_MESSAGE__WHEN_FAST_API_IS_OK

    def test_4__invoke__function_url(self):
        version = {'version': version__osbot_fast_api_serverless}
        assert self.deploy_fast_api__dev .invoke__function_url('/info/version') == version

    # def test_4__delete(self):
    #     assert self.deploy_fast_api__dev .delete() is True