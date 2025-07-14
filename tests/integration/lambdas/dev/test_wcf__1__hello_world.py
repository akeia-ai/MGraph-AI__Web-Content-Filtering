from unittest                                                        import TestCase
from mgraph_ai_web_content_filtering.utils.testing.skip_tests        import skip__if_not__in_github_actions
from osbot_aws.aws.sts.STS                                           import STS
from osbot_aws.aws.lambda_.Lambda                                    import Lambda
from osbot_aws.deploy.Deploy_Lambda                                  import Deploy_Lambda
from mgraph_ai_web_content_filtering.lambdas.dev.wcf__1__hello_world import run, STR_FORMAT__RETURN_MESSAGE


class test_hello_world(TestCase):
    lambda_ : Lambda

    @classmethod
    def setUpClass(cls) -> None:
        skip__if_not__in_github_actions()
        #with print_duration(action_name='create lambda'):
        STS().check_current_session_credentials()
        cls.handler     = run
        cls.deploy      = Deploy_Lambda(cls.handler)
        cls.lambda_name = cls.deploy.lambda_name()
        cls.lambda_     = Lambda(name= cls.lambda_name)
        assert cls.deploy.deploy () is True
        assert cls.lambda_.exists() is True

    @classmethod
    def tearDownClass(cls) -> None:
        #with print_duration(action_name='delete lambda'):
            assert cls.lambda_.delete() is True


    def test_invoke_directly(self):
        assert self.handler.__module__ == self.lambda_name
        assert run({}                ) == STR_FORMAT__RETURN_MESSAGE.format(name=None  )
        assert run({'name' : 'world'}) == STR_FORMAT__RETURN_MESSAGE.format(name='world')

    def test_invoke_lambda__using_deploy(self):
        assert self.deploy.invoke() == STR_FORMAT__RETURN_MESSAGE.format(name=None  )

    def test_invoke_lambda__using_lambda(self):
        event = {'name' : 'world'}
        assert self.lambda_.invoke(event) == STR_FORMAT__RETURN_MESSAGE.format(name='world')