from osbot_aws.helpers.Lambda_Layer_Create                                              import Lambda_Layer_Create
from mgraph_ai_web_content_filtering.lambdas.dev.wcf__8__osbot_aws__using_layer.handler import run
from mgraph_ai_web_content_filtering.utils.testing.TestCase__FastAPI__Lambda            import TestCase__FastAPI__Lambda


class test_wcf__8__osbot_aws__using_layer(TestCase__FastAPI__Lambda):

    @classmethod
    def setUpClass(cls):
        cls.handler        = run
        cls.lambda_name    = 'wcf__8__osbot_aws__using_layer'
        cls.lambda_layer   = Lambda_Layer_Create(layer_name=cls.lambda_name)
        cls.delete_on_exit = True
        super().setUpClass()

    def test_1__create_layer(self):
        with self.lambda_layer as _:
            _.add_package('osbot-aws')
            layer_arn = _.create()
            assert _.layer_name   == 'wcf__8__osbot_aws__using_layer'
            assert _.exists()     is True
            assert _.arn_latest() == layer_arn

    def test_2__deploy(self):
        with self.deploy_lambda as _:
            #with print_duration(action_name="deploying lambda"):
            _.add_layer(self.lambda_layer.arn_latest())
            assert _.deploy() is True                                   # deploys in 4.2 seconds
            self.test_3__invoke__on_aws()                               # first execution is in 0.4 seconds

    def test_3__invoke__on_aws(self):
        with self.deploy_lambda as _:
            #for i in range(1, 10):
            #with print_duration(action_name=f"invoking lambda #1"):     # 2nd+ execution are 0.1 seconds
            assert  _.invoke() == 'the install path of /opt/python/osbot_aws'
