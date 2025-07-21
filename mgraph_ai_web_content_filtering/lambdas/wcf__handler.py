from mgraph_ai_web_content_filtering.wcf__fast_api.setup.WCF__Lambda__Setup import WCF__Lambda__Setup

with WCF__Lambda__Setup() as _:
    handler = _.handler()
    app     = _.app()

def run(event, context=None):
    return handler(event, context)