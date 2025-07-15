from unittest import TestCase

from mgraph_ai_web_content_filtering.wcf__fast_api.setup.WCF__AWS__Deploy import WCF__AWS__Deploy


class test__deploy__wcf__handler(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.wcf_aws_deploy = WCF__AWS__Deploy()

    def test_lambda__deploy(self):
        with self.wcf_aws_deploy as _:
            assert _.lambda__deploy() is True