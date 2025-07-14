from osbot_aws.deploy.Deploy_Lambda                                     import Deploy_Lambda
from mgraph_ai_web_content_filtering.lambdas.wcf__handler               import run
from mgraph_ai_web_content_filtering.testing.TestCase__FastAPI__Lambda  import TestCase__FastAPI__Lambda


class test_wcf__handler(TestCase__FastAPI__Lambda):

    @classmethod
    def setUpClass(cls):
        cls.handler        = run
        cls.delete_on_exit = False                                      # we can't delete this one, since this is the main entry point of the app :)
        super().setUpClass()

    def test_1__invoke_locally(self):
        assert run(self.request_payload('/config/status')).get('body') == '{"status":"ok"}'

    def test_2__deploy(self):
        with self.deploy_lambda as _:
            _.add_osbot_aws()
            _.add_module('osbot_fast_api')
            assert _.deploy() is True
            self.test_3__invoke__on_aws()

    def test_3__invoke__on_aws(self):
        with self.deploy_lambda as _:
            response = _.invoke(self.request_payload('/AAAA'))
            assert response.get('statusCode') == 404
            assert response.get('body'      ) == '{"detail":"Not Found"}'

