from fastapi                                                        import FastAPI
from osbot_utils.utils.Env                                          import set_env
from osbot_aws.testing.Temp__Random__AWS_Credentials                import Temp_AWS_Credentials
from osbot_local_stack.local_stack.Local_Stack                      import Local_Stack
from osbot_utils.type_safe.Type_Safe                                import Type_Safe
from starlette.testclient                                           import TestClient
from mgraph_ai_web_content_filtering.wcf__fast_api.WCF__Fast_API    import WCF__Fast_API

#WCF__TEST__AWS_ACCOUNT_ID = '000022220000'

class WCF__Test_Data(Type_Safe):
    wcf__fast_api        : WCF__Fast_API  = None
    wcf__fast_api__app   : FastAPI        = None
    wcf__fast_api__client: TestClient     = None
    api__not_setup       : bool           = True

wcf_test_data = WCF__Test_Data()


def setup_local_stack() -> Local_Stack:                          # todo: refactor this to the OSBot_Local_Stack code base
    Temp_AWS_Credentials().with_localstack_credentials()
    local_stack = Local_Stack().activate()
    return local_stack

def wcf_tests__setup_fast_api():
    with wcf_test_data as _:
        if wcf_test_data.api__not_setup:
            _.wcf__fast_api         = WCF__Fast_API().setup()
            _.wcf__fast_api__app    = _.wcf__fast_api.app()
            _.wcf__fast_api__client = _.wcf__fast_api.client()
    return wcf_test_data

def wcf__assert_local_stack():
    local_stack = setup_local_stack()
    assert local_stack.is_local_stack_configured_and_available() is True