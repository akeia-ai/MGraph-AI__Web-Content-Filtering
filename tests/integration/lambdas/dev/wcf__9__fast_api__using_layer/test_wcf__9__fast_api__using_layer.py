from osbot_utils.helpers.duration.decorators.print_duration                             import print_duration
from osbot_aws.helpers.Lambda_Layer_Create                                              import Lambda_Layer_Create
from mgraph_ai_web_content_filtering.lambdas.dev.wcf__9__fast_api__using_layer.handler  import run
from mgraph_ai_web_content_filtering.utils.testing.TestCase__FastAPI__Lambda            import TestCase__FastAPI__Lambda


class test_wcf__9__fast_api__using_layer(TestCase__FastAPI__Lambda):

    @classmethod
    def setUpClass(cls):
        cls.handler        = run
        cls.lambda_name    = 'wcf__9__fast_api__using_layer'
        cls.lambda_layer   = Lambda_Layer_Create(layer_name=cls.lambda_name)
        cls.delete_on_exit = True
        #cls.skip_locally   = False
        super().setUpClass()

    def test_1__create_layer(self):
        with self.lambda_layer as _:
            _.add_packages(['osbot-aws', 'osbot-fast-api', 'fastapi', 'mangum', 'requests'])
            layer_arn = _.create()
            assert _.layer_name   == 'wcf__9__fast_api__using_layer'
            assert _.exists()     is True
            assert _.arn_latest() == layer_arn

    def test_2__deploy(self):
        with self.deploy_lambda as _:
            #with print_duration(action_name="deploying lambda", ):
            _.add_layer(self.lambda_layer.arn_latest())
            assert _.deploy() is True                                                                  # deploys in 4.26 seconds
            self.test_3__invoke__on_aws()                                                              # first execution is in 1.2 seconds

    def test_3__invoke__on_aws(self):
        with self.deploy_lambda as _:
            #with print_duration(action_name=f"invoking lambda"):
            assert _.invoke(self.request_payload('/config/status')).get('body') == '{"status":"ok"}'   # 2nd+ execution are ~ 0.13 seconds