from osbot_utils.helpers.Safe_Id            import Safe_Id
from osbot_aws.helpers.Lambda_Layer_Create  import Lambda_Layer_Create
from osbot_utils.type_safe.Type_Safe        import Type_Safe

LAYER__DEPENDENCIES__WCF = ['osbot-aws', 'fastapi', 'mangum', 'requests']
LAMBDA__LAYER__NAME      = Safe_Id('wcf-layer')

class WCF__Lambda__Create_Layer(Type_Safe):
    lambda_layer_create      : Lambda_Layer_Create = None
    lambda_layer_name : Safe_Id                    = LAMBDA__LAYER__NAME

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lambda_layer_create = Lambda_Layer_Create(layer_name=self.lambda_layer_name)

    def create__in__local_temp_folder(self):
        with self.lambda_layer_create as _:
            for package_name in LAYER__DEPENDENCIES__WCF:
                if _.has_package_installed(package_name=package_name) is False:
                    _.add_package(package=package_name)

    def exists(self):
        return self.lambda_layer_create.exists()


