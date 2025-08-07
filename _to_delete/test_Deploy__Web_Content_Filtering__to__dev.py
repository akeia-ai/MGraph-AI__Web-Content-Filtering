# from unittest                                                                   import TestCase
# from osbot_fast_api_serverless.deploy.Deploy__Serverless__Fast_API              import DEFAULT__ERROR_MESSAGE__WHEN_FAST_API_IS_OK
# from osbot_fast_api_serverless.utils.Version import version__osbot_fast_api_serverless
# from osbot_fast_api_serverless.utils.testing.skip_tests                         import skip__if_not__in_github_actions
# from osbot_utils.utils.Dev                                                      import pprint
# from mgraph_ai_web_content_filtering.utils.Version                              import version__mgraph_ai_web_content_filtering
# from osbot_utils.utils.Misc                                                     import list_set
# from tests.unit.wcf__objs_for_tests                                             import setup_local_stack
#
#
# class test_Deploy__Web_Content_Filtering__to__dev(TestCase):
#
#     @classmethod
#     def setUpClass(cls):
#         skip__if_not__in_github_actions()
#         setup_local_stack()
#         from mgraph_ai_web_content_filtering.utils.deploy.Deploy__Web_Content_Filtering import Deploy__Web_Content_Filtering
#         cls.deploy_fast_api__dev  = Deploy__Web_Content_Filtering(stage = 'dev')
#
#     def test_1__check_stages(self):
#         assert self.deploy_fast_api__dev .stage == 'dev'
#
#     def test_2__upload_dependencies(self):                                                  # add support for Lambda_Layer_Create.remove_preinstalled_packages_in_lambda_environment
#         from mgraph_ai_web_content_filtering.utils.deploy.Deploy__Web_Content_Filtering import LAMBDA_DEPENDENCIES__WEB_CONTENT_FILTERING
#         upload_results = self.deploy_fast_api__dev.upload_lambda_dependencies_to_s3()
#         assert list_set(upload_results) == LAMBDA_DEPENDENCIES__WEB_CONTENT_FILTERING
#
#     def test_3__create(self):
#         assert self.deploy_fast_api__dev .create() is True
#         #self.test_4__invoke()
#
#     def test_4__invoke(self):
#         #pprint(self.deploy_fast_api__dev .invoke())
#         assert self.deploy_fast_api__dev .invoke().get('errorMessage') == DEFAULT__ERROR_MESSAGE__WHEN_FAST_API_IS_OK
#
#     def test_5__invoke__function_url(self):
#         version = {'version': version__osbot_fast_api_serverless}  # version__mgraph_ai_web_content_filtering
#         assert self.deploy_fast_api__dev .invoke__function_url('/info/version') == version
#
#     def test_6__delete(self):
#         assert self.deploy_fast_api__dev .delete() is True
