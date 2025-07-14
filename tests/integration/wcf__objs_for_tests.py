from fastapi                                                     import FastAPI
from osbot_utils.type_safe.Type_Safe                             import Type_Safe
from starlette.testclient                                        import TestClient
from mgraph_ai_web_content_filtering.wcf__fast_api.WCF__Fast_API import WCF__Fast_API


class WCF__Test_Data(Type_Safe):
    wcf__fast_api        : WCF__Fast_API  = None
    wcf__fast_api__app   : FastAPI        = None
    wcf__fast_api__client: TestClient     = None
    api__not_setup       : bool           = True

wcf_test_data = WCF__Test_Data()

def wcf_tests__setup_fast_api():
    with wcf_test_data as _:
        if wcf_test_data.api__not_setup:
            _.wcf__fast_api         = WCF__Fast_API().setup()
            _.wcf__fast_api__app    = _.wcf__fast_api.app()
            _.wcf__fast_api__client = _.wcf__fast_api.client()
    return wcf_test_data
