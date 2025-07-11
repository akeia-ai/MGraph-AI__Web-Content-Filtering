from osbot_aws.AWS_Config                           import AWS_Config
from osbot_aws.aws.s3.S3                            import S3
from osbot_utils.decorators.methods.cache_on_self   import cache_on_self
from osbot_utils.type_safe.Type_Safe                import Type_Safe

#dns_entry                    = 'https://web-content-filtering.mgraph-ai'

WEB_CONTENT_FILTERING__PROJECT_NAME = "web-content-filtering"

class AWS__Setup__Web_Content_Filtering(Type_Safe):

    @cache_on_self
    def s3(self):
        return S3()

    @cache_on_self
    def aws_config(self):
        return AWS_Config()

    def aws__account_id(self):
        return self.aws_config().account_id()

    def aws__configured(self):
        return self.aws_config().aws_configured()

    def aws__region_name(self):
        return self.aws_config().region_name()

    def s3__bucket__name(self):
        return f"{WEB_CONTENT_FILTERING__PROJECT_NAME}--{self.aws__account_id()}--{self.aws__region_name()}"

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