from osbot_fast_api_serverless.deploy.Deploy__Serverless__Fast_API  import Deploy__Serverless__Fast_API
from mgraph_ai_web_content_filtering.lambdas.wcf__handler           import run

LAMBDA_NAME__WEB_CONTENT_FILTERING         = 'web-content-filtering'
LAMBDA_DEPENDENCIES__WEB_CONTENT_FILTERING = ['osbot-fast-api-serverless']

class Deploy__Web_Content_Filtering(Deploy__Serverless__Fast_API):

    def handler(self):
        return run

    def lambda_dependencies(self):
        return LAMBDA_DEPENDENCIES__WEB_CONTENT_FILTERING

    def lambda_name(self):
        return LAMBDA_NAME__WEB_CONTENT_FILTERING
