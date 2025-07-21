from unittest                                                                       import TestCase
from osbot_utils.utils.Dev                                                          import pprint
from osbot_utils.utils.Files                                                        import path_combine, current_temp_folder
from osbot_utils.utils.Misc import list_set

from osbot_aws.helpers.Lambda_Layer_Create                                          import Lambda_Layer_Create
from osbot_utils.helpers.Safe_Id                                                    import Safe_Id
from mgraph_ai_web_content_filtering.wcf__fast_api.setup.WCF__Lambda__Create_Layer  import WCF__Lambda__Create_Layer


class test_WCF__Lambda__Create_Layer(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.wcf_lambda_create_layer = WCF__Lambda__Create_Layer()

    def test__init__(self):
        with self.wcf_lambda_create_layer as _:
            assert type(_                    ) is WCF__Lambda__Create_Layer
            assert type(_.lambda_layer_create) is Lambda_Layer_Create
            assert type(_.lambda_layer_name  ) is Safe_Id

        with _.lambda_layer_create as _:
            assert _.path_layer_folder()          == path_combine(current_temp_folder(), '_lambda_dependencies/wcf-layer')
            assert _.has_package_installed('abc') is False

    def test_create__in__local_temp_folder(self):
        with self.wcf_lambda_create_layer as _:
            #_.lambda_layer_create.delete_local_layer_folder()

            result = _.create__in__local_temp_folder()
            assert list_set(result) == []
            assert list_set(_.lambda_layer_create.installed_packages()) == ['fastapi', 'mangum', 'requests']

    def test_exists(self):
        with self.wcf_lambda_create_layer as _:
            assert _.exists() is False