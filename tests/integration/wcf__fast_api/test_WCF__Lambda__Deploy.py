from unittest import TestCase

from osbot_utils.utils.Dev import pprint

from mgraph_ai_web_content_filtering.wcf__fast_api.WCF__Lambda__Deploy import WCF__Lambda__Deploy
from mgraph_ai_web_content_filtering.wcf__fast_api.WCF__Lambda__Setup import WCF__Lambda__Setup


class test_WCF__Lambda__Deploy(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.wcf_lambda_deploy = WCF__Lambda__Deploy()

    def test__init__(self):
        with self.wcf_lambda_deploy as _:
            assert type(_) is WCF__Lambda__Deploy

    def test_setup_lambda_function(self):
        with self.wcf_lambda_deploy as _:
            result = _.setup_lambda_function()
            assert result == {}
            #pprint(result)
