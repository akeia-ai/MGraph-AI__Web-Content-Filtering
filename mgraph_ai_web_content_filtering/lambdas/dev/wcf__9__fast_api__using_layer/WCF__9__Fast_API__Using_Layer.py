from mangum                      import Mangum
from osbot_fast_api.api.Fast_API import Fast_API

class WCF__9__Fast_API__Using_Layer(Fast_API):

    def handler(self):
        handler = Mangum(self.app())
        return handler
