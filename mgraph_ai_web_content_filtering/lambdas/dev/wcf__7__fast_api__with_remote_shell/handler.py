from mgraph_ai_web_content_filtering.lambdas.dev.wcf__4__fast_api__using_classes.OSBot__Lambda__Setup    import OSBot__Lambda___Setup

OSBot__Lambda___Setup().load_dependencies__fast_api()                   # this needs to happen before the next import (which depends on Fast_API and Fastapi

from mgraph_ai_web_content_filtering.lambdas.dev.wcf__7__fast_api__with_remote_shell.Fast_API__With_Remote_Shell import Fast_API__With_Remote_Shell


with Fast_API__With_Remote_Shell().setup() as _:
    handler = _.handler()

    def run(event, context=None):
        return handler(event, context)