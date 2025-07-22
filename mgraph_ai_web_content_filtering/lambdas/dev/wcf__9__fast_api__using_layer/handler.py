from mgraph_ai_web_content_filtering.lambdas.dev.wcf__9__fast_api__using_layer.WCF__9__Fast_API__Using_Layer import WCF__9__Fast_API__Using_Layer

handler = WCF__9__Fast_API__Using_Layer().setup().handler()

def run(event, context=None):
    return handler(event, context)