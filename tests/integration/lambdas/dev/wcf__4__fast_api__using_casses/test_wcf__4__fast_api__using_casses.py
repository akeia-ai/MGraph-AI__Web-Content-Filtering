from urllib.error                                                                       import HTTPError
from osbot_aws.deploy.Deploy_Lambda                                                     import Deploy_Lambda
from osbot_utils.utils.Http                                                             import GET, GET_json
from mgraph_ai_web_content_filtering.lambdas.dev.wcf__4__fast_api__using_classes.handler import run
from mgraph_ai_web_content_filtering.testing.TestCase__FastAPI__Lambda                  import TestCase__FastAPI__Lambda, TEST__FASTAPI__ROUTE__RETURN_MESSAGE

class test_wcf__4__fast_api__using_casses(TestCase__FastAPI__Lambda):

    @classmethod
    def setUpClass(cls) -> None:
        cls.handler                               = run
        cls.deploy_lambda                         = Deploy_Lambda(cls.handler)
        cls.delete_on_exit                        = False
        cls.deploy_lambda.package.aws_lambda.name = 'wcf__4__fast_api__using_classes'       # we have to do this little fix because the default name is bigger than 64 chars ('mgraph_ai_web_content_filtering_lambdas_dev_fastapi__using_classes_handler')

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.delete_on_exit:
            assert cls.deploy_lambda.delete() is True

    def setUp(self):
        self.payload  = self.request_payload  ()
        self.response = self.expected_response()

    def test_1__invoke__locally(self):
        assert run(self.payload) == self.response