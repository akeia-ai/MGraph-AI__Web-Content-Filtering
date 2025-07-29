from unittest                                                                       import TestCase

from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Files                                                        import path_combine, current_temp_folder
from osbot_utils.utils.Misc                                                         import list_set
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

    def test_create_layer(self):
        with self.wcf_lambda_create_layer as _:
            #_.lambda_layer_create.delete_local_layer_folder()              # do this to retrigger the local installation of packages
            skip_if_exists     = False                                      # set to False to force recreation of layer
            result             = _.create_layer(skip_if_exists=skip_if_exists)
            installed_packages = _.lambda_layer_create.installed_packages()
            layer_arn          = _.layer_arn()
            exists             = _.exists()

            assert layer_arn.startswith('arn:aws:lambda:')
            assert result == layer_arn
            assert exists is True
            if installed_packages:
                assert list_set(installed_packages) == [ 'mangum', 'osbot-aws', 'osbot-fast-api', 'requests']