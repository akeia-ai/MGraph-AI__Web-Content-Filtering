from unittest import TestCase
from osbot_utils.helpers.duration.decorators.print_duration             import print_duration
from osbot_aws.AWS_Config                                               import AWS_Config
from mgraph_ai_web_content_filtering.wcf__fast_api.llms.WCF__LLM__Cache import WCF__LLM__Cache
from tests.unit.wcf__objs_for_tests                                     import wcf__assert_local_stack


class test_WCF__LLM__Cache(TestCase):
    @classmethod
    def setUpClass(cls):
        wcf__assert_local_stack()
        cls.aws_config    = AWS_Config()
        cls.wcf_llm_cache = WCF__LLM__Cache().setup()

    def test__init__(self):
        with self.wcf_llm_cache as _:
            assert type(_) is WCF__LLM__Cache
            assert _.bucket_name() == f'wcf-{self.aws_config.account_id()}-data'

            assert _.get_s3_key('abc') == 'llm-cache/abc'

    def test_setup(self):
        assert self.wcf_llm_cache.s3_db.bucket_exists()         # bucket will be created by the .setup() method (called in .setUpClass )

    # def test_check_local_stack_files(self):
    #     with self.wcf_llm_cache.s3_db as _:
    #         from osbot_utils.utils.Dev import pprint
    #         pprint(_.s3().buckets())
    #         pprint(_.s3_folder_files__all())
