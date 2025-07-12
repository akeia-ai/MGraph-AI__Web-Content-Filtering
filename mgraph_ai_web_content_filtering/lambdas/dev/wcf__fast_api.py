from osbot_aws.Dependencies import load_dependencies

WCF__FAST_API__RETURN_MESSAGE = "Hello from WCF FastApi Lambda!"

def setup_handler():
    dependencies = ['fastapi', 'mangum']
    load_dependencies(dependencies)

    from fastapi import FastAPI
    from mangum import Mangum

    app     = FastAPI()

    @app.get("/")
    def read_root():
        return {"message": WCF__FAST_API__RETURN_MESSAGE }

    handler = Mangum(app)
    return handler

request__handler = setup_handler()

def run(event, context=None):
    return request__handler(event, context)