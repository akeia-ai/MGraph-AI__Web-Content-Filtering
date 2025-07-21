from osbot_aws.helpers.Lambda_Layer_Create import Lambda_Layer_Create

from mgraph_ai_web_content_filtering.lambdas.wcf__handler                   import run
from mgraph_ai_web_content_filtering.wcf__fast_api.setup.WCF__Lambda__Setup import DEPENDENCIES__LAMBDAS__WCF
from osbot_aws.deploy.Deploy_Lambda                                         import Deploy_Lambda
from osbot_aws.aws.lambda_.Lambda                                           import Lambda
from osbot_aws.AWS_Config                                                   import AWS_Config
from osbot_aws.apis.test_helpers.Temp_Aws_Roles                             import Temp_Aws_Roles
from osbot_aws.aws.cloud_front.Cloud_Front                                  import Cloud_Front
from osbot_aws.aws.s3.S3                                                    import S3
from osbot_aws.helpers.Lambda_Upload_Package                                import Lambda_Upload_Package
from osbot_utils.decorators.methods.cache_on_self                           import cache_on_self
from osbot_utils.helpers.Safe_Id                                            import Safe_Id
from osbot_utils.type_safe.Type_Safe                                        import Type_Safe

WCF__LAMBDA__FUNCTION_NAME = 'mgraph_ai_web_content_filtering_lambdas_wcf__handler'
WCF__DNS_NAME              = 'web-content-filtering.mgraph.ai'

class Schema__AWS_Setup__Config(Type_Safe):
    project_name            : Safe_Id = Safe_Id('web-content-filtering')
    osbot_lambdas_bucket_id : Safe_Id = Safe_Id('osbot-lambdas'        )


class Schema__AWS_Setup__Status(Type_Safe):
    config: Schema__AWS_Setup__Config


class WCF__AWS__Deploy(Type_Safe):
    setup_config : Schema__AWS_Setup__Config

    @cache_on_self
    def cloud_front(self):
        return Cloud_Front()

    @cache_on_self
    def s3(self):
        return S3()

    @cache_on_self
    def aws_config(self):
        return AWS_Config()

    #######

    def aws__account_id(self):
        return self.aws_config().account_id()

    def aws__configured(self):
        return self.aws_config().aws_configured()

    def aws__region_name(self):
        return self.aws_config().region_name()

    def cloud_front__distribution_id(self):
        return self.cloud_front().distributions()

    def s3__bucket__name(self):
        return f"{self.setup_config.project_name}--{self.aws__account_id()}--{self.aws__region_name()}"

    def s3__bucket__exists(self):
        return self.s3().bucket_exists(self.s3__bucket__name())

    def s3__bucket__setup(self):
        bucket_exists  = self.s3__bucket__exists()
        bucket_created = False
        if bucket_exists is False:
            bucket_name = self.s3__bucket__name()
            region_name = self.aws__region_name()
            result      = self.s3().bucket_create(bucket=bucket_name, region=region_name)
            if result.get('status') == 'ok':
                bucket_exists  = True
                bucket_created = True

        result = dict(bucket_created =  bucket_created,               # this will only be true the one time the bucket is created
                      bucket__exists = bucket_exists  )
        return result

    def s3__upload__lambda_dependencies(self):
        packages_to_install = DEPENDENCIES__LAMBDAS__WCF
        lambda_upload = Lambda_Upload_Package()
        result = lambda_upload.upload_to_s3(packages_to_install)
        return result

    def lambda__deploy(self):
        handler = run                                                   # todo: add support for dev, qa and prod versions of this lambda
        with Deploy_Lambda(handler=handler) as _:
            _.add_osbot_aws()
            _.add_module('osbot_fast_api')
            return _.deploy()

    def lambda__function_url__setup(self, lambda_function: Lambda):
        function_url = lambda_function.function_url()
        if lambda_function.function_url_exists() is False:
            lambda_function.function_url_create_with_public_access()
            function_url = lambda_function.function_url()
        return function_url

    def lambdas__iam__setup(self):
        temp_aws_roles = Temp_Aws_Roles()
        if temp_aws_roles.for_lambda_invocation__not_exists():
            temp_aws_roles.for_lambda_invocation__create()
            return temp_aws_roles.for_lambda_invocation_exists()
        return True

    def lambdas__s3__bucket_name(self):
        return f"{self.aws__account_id()}--{self.setup_config.osbot_lambdas_bucket_id}--{self.aws__region_name()}"

    def lambdas__s3__osbot__lambdas__setup(self):
        osbot_lambdas_bucket_name = self.lambdas__s3__bucket_name()
        bucket_exists = self.s3().bucket_exists(osbot_lambdas_bucket_name)
        bucket_created = False

        if bucket_exists is False:
            region_name = self.aws__region_name()
            if self.s3().bucket_create(bucket=osbot_lambdas_bucket_name, region=region_name):
                bucket_created = True
                bucket_exists  = True

        result = dict(bucket_created =  bucket_created,               # this will only be true the one time the bucket is created
                      bucket__exists = bucket_exists  )
        return result
