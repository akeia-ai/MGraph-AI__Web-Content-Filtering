from osbot_aws.Dependencies import load_dependencies

dependencies__elastic__serverless = ['fastapi', 'mangum']
load_dependencies(dependencies__elastic__serverless)

from mgraph_ai_web_content_filtering.lambdas.dev.wcf__fastapi__using_classes.FastAPI__Using_Classes import FastAPI__Using_Classes

handler = FastAPI__Using_Classes().setup().handler()


def run(event, context=None):
    return handler(event, context)