from mangum                             import Mangum
from osbot_fast_api.api.Fast_API        import Fast_API

class Fast_API__With_Remote_Shell(Fast_API):

    def handler(self):
        handler = Mangum(self.app())
        return handler

    def setup_routes(self):
        self.add_shell_server()
        #app = self.app()


