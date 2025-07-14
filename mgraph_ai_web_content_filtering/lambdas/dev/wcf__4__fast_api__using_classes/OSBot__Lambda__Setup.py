
DEPENDENCIES__FAST_API = ['fastapi', 'mangum']

class OSBot__Lambda___Setup():

    def load_dependencies(self, dependencies):
        from osbot_aws.Dependencies import load_dependencies
        load_dependencies(dependencies)

    def load_dependencies__fast_api(self):
        self.load_dependencies(DEPENDENCIES__FAST_API)
