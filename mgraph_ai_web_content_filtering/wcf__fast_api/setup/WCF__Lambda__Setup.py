from osbot_utils.decorators.methods.cache_on_self                                   import cache_on_self
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from mgraph_ai_web_content_filtering.wcf__fast_api.setup.WCF__Lambda__Create_Layer  import DEPENDENCIES__LAMBDAS__WCF


class WCF__Lambda__Setup(Type_Safe):

    @cache_on_self
    def wcf_fast_api(self):
        from mgraph_ai_web_content_filtering.wcf__fast_api.WCF__Fast_API import WCF__Fast_API
        return WCF__Fast_API().setup()

    @cache_on_self
    def app(self):
        return self.wcf_fast_api().app()

    def handler(self):
        self.load_lambda_dependencies()
        from mangum import Mangum
        handler = Mangum(self.app())
        return handler

    def load_lambda_dependencies(self):
        from osbot_aws.Dependencies import load_dependencies
        load_dependencies(DEPENDENCIES__LAMBDAS__WCF)