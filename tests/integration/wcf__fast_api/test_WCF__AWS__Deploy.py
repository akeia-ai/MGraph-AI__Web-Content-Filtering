from unittest                                                             import TestCase
from osbot_utils.utils.Http                                               import GET_json
from osbot_aws.aws.lambda_.Lambda                                         import Lambda
from mgraph_ai_web_content_filtering.wcf__fast_api.setup.WCF__AWS__Deploy import WCF__AWS__Deploy, Schema__AWS_Setup__Status, WCF__LAMBDA__FUNCTION_NAME


class test_WCF__Lambda__Deploy(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.wcf_aws_deploy = WCF__AWS__Deploy()

    def test__init__(self):
        with self.wcf_aws_deploy as _:
            assert type(_) is WCF__AWS__Deploy

    # todo: to implement the logic of the creation of the Cloud_Front distribution
    # def test__cloud_front__distribution_id(self):
    #     with self.wcf_aws_deploy as _:
    #         distribution_id = _.cloud_front__distribution_id()
    #         from osbot_utils.utils.Dev import pprint
    #         pprint(distribution_id)

    # todo: to implement this function which goes though the setup workflow and checks that all is ok
    # def test_setup_lambda_function(self):
    #     with self.wcf_aws_deploy as _:
    #         setup_status = _.setup_lambda_function()
    #         assert type(setup_status) is Schema__AWS_Setup__Status
    #         assert setup_status.json() == { 'config': { 'osbot_lambdas_bucket_id': 'osbot-lambdas'         ,
    #                                                     'project_name'           : 'web-content-filtering'}}

    def test_lambda__deploy(self):
        with self.wcf_aws_deploy as _:
            assert _.lambda__deploy() is True

    def test_lambda__function_url__setup(self):

        with Lambda(name=WCF__LAMBDA__FUNCTION_NAME) as _:
            assert _.exists() is True
            function_url = self.wcf_aws_deploy.lambda__function_url__setup(lambda_function=_)
            from osbot_utils.utils.Dev import pprint
            assert 'lambda-url.eu-west-1.on.aws/' in function_url
            assert GET_json(function_url + 'config/status') == {"status":"ok"}

        #lambda__function_url__setup
    def test_aws__configured(self):
        assert self.wcf_aws_deploy.aws__configured() is True

    def test_s3__bucket_name(self):
        assert self.wcf_aws_deploy.s3__bucket__name() == "web-content-filtering--180929110226--eu-west-1"

    def test_s3__bucket__exists(self):
        with self.wcf_aws_deploy as _:
            assert _.s3__bucket__exists() is True

    def test_s3__bucket__setup(self):
        with self.wcf_aws_deploy as _:
            assert _.s3__bucket__setup() == {'bucket__exists': True ,
                                             'bucket_created': False}

    def test_osbot__lambdas__iam__setup(self):
        with self.wcf_aws_deploy as _:
            assert _.lambdas__iam__setup() is True

    def test_osbot__lambdas__s3__bucket_name(self):
        with self.wcf_aws_deploy as _:
            assert _.lambdas__s3__bucket_name() == "180929110226--osbot-lambdas--eu-west-1"

    def test_osbot__lambdas__s3__osbot__lambdas__setup(self):
        with self.wcf_aws_deploy as _:
            assert _.lambdas__s3__osbot__lambdas__setup() == {'bucket__exists': True ,
                                                                      'bucket_created': False}
