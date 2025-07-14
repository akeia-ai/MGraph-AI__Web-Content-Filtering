from urllib.error                                                                       import HTTPError
from osbot_utils.utils.Http                                                             import GET, GET_json
from mgraph_ai_web_content_filtering.lambdas.dev.wcf__3__fastapi__using_classes.handler import run
from mgraph_ai_web_content_filtering.utils.testing.TestCase__FastAPI__Lambda            import TestCase__FastAPI__Lambda, TEST__FASTAPI__ROUTE__RETURN_MESSAGE


class test_wcf__3__fastapi__using_classes(TestCase__FastAPI__Lambda):

    @classmethod
    def setUpClass(cls):
        cls.handler = run
        super().setUpClass()
        cls.deploy_lambda.package.aws_lambda.name = 'wcf__fastapi__using_classes'       # we have to do this little fix because the default name is bigger than 64 chars ('mgraph_ai_web_content_filtering_lambdas_dev_fastapi__using_classes_handler')

    def setUp(self):
        self.payload  = self.request_payload  ()
        self.response = self.expected_response()

    def test_1__invoke__locally(self):
        assert run(self.payload) == self.response

    def test_2__deploy(self):
        with self.deploy_lambda as _:
            _.add_osbot_aws()
            assert _.deploy() is True
            self.test_3__invoke__on_aws()

    def test_3__invoke__on_aws(self):
        with self.deploy_lambda as _:
            assert _.invoke(self.payload) == self.response

    def test_4__invoke__on_aws__via__function_url(self):
        with self.deploy_lambda.lambda_function() as _:
            if _.function_url_exists() is False:
                _.function_url_create_with_public_access()
            function_url  = _.function_url()
            try:
                html_root     = GET     (function_url)
                json_root     = GET_json(function_url)
                html_docs     = GET     (function_url + 'docs')
                assert 'lambda-url.eu-west-1.on.aws/'        in function_url
                assert html_root                             == f'{{"message":"{TEST__FASTAPI__ROUTE__RETURN_MESSAGE}"}}'
                assert json_root                             ==  {'message': TEST__FASTAPI__ROUTE__RETURN_MESSAGE}
                assert "<title>FastAPI - Swagger UI</title>" in html_docs
            except HTTPError as http_error:
                assert http_error.code != 403                   # note: this happens due to a race condition in AWS caused by deleting and creating a Lambda function URL very quickly
                                                                #       where this execption will only be triggered if the tests are executed more than once per minute
