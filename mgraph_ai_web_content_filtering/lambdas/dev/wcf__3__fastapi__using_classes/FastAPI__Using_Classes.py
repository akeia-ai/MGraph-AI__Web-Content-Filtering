from fastapi                                                                 import FastAPI
from mangum                                                                  import Mangum
from osbot_utils.decorators.methods.cache_on_self                            import cache_on_self
from osbot_utils.type_safe.Type_Safe                                         import Type_Safe
from mgraph_ai_web_content_filtering.utils.testing.TestCase__FastAPI__Lambda import TEST__FASTAPI__ROUTE__RETURN_MESSAGE


class FastAPI__Using_Classes(Type_Safe):
    pass

    @cache_on_self
    def app(self):
        return FastAPI()

    def setup(self):
        app = self.app()

        @app.get("/")
        def root_route():
            return {"message": TEST__FASTAPI__ROUTE__RETURN_MESSAGE}
        return self


    def handler(self):
        handler = Mangum(self.app())
        return handler