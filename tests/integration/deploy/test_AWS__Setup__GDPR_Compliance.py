from unittest                                                       import TestCase
from osbot_utils.utils.Env                                          import load_dotenv

from mgraph_ai_web_content_filtering.deploy.AWS__Setup__Web_Content_Filtering import AWS__Setup__Web_Content_Filtering


class test_AWS__Setup__Web_Content_Filtering(TestCase):

    @classmethod
    def setUpClass(cls):
        load_dotenv()
        cls.aws_setup = AWS__Setup__Web_Content_Filtering()

    def test__init__(self):
        with self.aws_setup as _:
            assert type(_) is AWS__Setup__Web_Content_Filtering

    def test_aws__configured(self):
        assert self.aws_setup.aws__configured() is True

    def test_s3__bucket_name(self):
        assert self.aws_setup.s3__bucket__name() == "web-content-filtering--180929110226--eu-west-1"

    def test_s3__bucket__exists(self):
        with self.aws_setup as _:
            assert _.s3__bucket__exists() is True

    def test_s3__bucket__setup(self):
        with self.aws_setup as _:
            assert _.s3__bucket__setup() == {'bucket__exists': True ,
                                             'bucket_created': False}