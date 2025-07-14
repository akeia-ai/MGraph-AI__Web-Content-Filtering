from osbot_aws.deploy.Deploy_Lambda                                                                             import Deploy_Lambda
from osbot_fast_api.api.Fast_API                                                                                import Fast_API
from osbot_fast_api.api.Fast_API__Http_Event import Fast_API__Http_Event
from osbot_fast_api.api.Fast_API__Http_Events import Fast_API__Http_Events
from osbot_utils.helpers.Guid import Guid
from osbot_utils.helpers.Random_Guid                                    import Random_Guid
from osbot_utils.type_safe.Type_Safe                                                                            import Type_Safe
from osbot_utils.utils.Misc import is_guid, list_set
from osbot_utils.utils.Objects                                                                                  import base_classes

from mgraph_ai_web_content_filtering.lambdas.dev.wcf__5__fast_api__with_router.WCF__5__Fast_API__With_Router    import WCF__5__Fast_API__With_Router
from mgraph_ai_web_content_filtering.lambdas.dev.wcf__5__fast_api__with_router.handler                          import run, fast_api_with_router
from mgraph_ai_web_content_filtering.testing.TestCase__FastAPI__Lambda                                          import TestCase__FastAPI__Lambda

class test_wcf__5__fast_api__with_router(TestCase__FastAPI__Lambda):

    @classmethod
    def setUpClass(cls) -> None:
        cls.handler                               = run
        cls.deploy_lambda                         = Deploy_Lambda(cls.handler)
        cls.delete_on_exit                        = False
        cls.deploy_lambda.package.aws_lambda.name = 'wcf__5__fast_api__with_router'       # we have to do this little fix because the default name is bigger than 64 chars ('mgraph_ai_web_content_filtering_lambdas_dev_fastapi__using_classes_handler')

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.delete_on_exit:
            assert cls.deploy_lambda.delete() is True

    def setUp(self):
        self.payload  = self.request_payload  ()
        self.response = self.expected_response()

    def test_1__wcf__5__fast_api__with_router(self):
        with fast_api_with_router as _:
            assert type(_)          == WCF__5__Fast_API__With_Router
            assert base_classes(_)  == [Fast_API, Type_Safe, object]
            assert _.routes_paths() == ['/',                                                    # default root path added by FastPI
                                        '/config/info', '/config/status', '/config/version',    # default paths added by Fast_API
                                        '/wcf-5-routes/route-1', '/wcf-5-routes/route-2']       # paths added during WCF__5__Routes

    def test_2__invoke__locally__new_route_1(self):
        request__route_1  = self.request_payload(path='/wcf-5-routes/route-1')
        response__route_1 = run(request__route_1)
        assert response__route_1.get('body'      ) == '"this is route 1"'
        assert response__route_1.get('statusCode') == 200

    def test_3__invoke__locally__new_route_2(self):
        request__route_1  = self.request_payload(path='/wcf-5-routes/route-2')
        response__route_1 = run(request__route_1)
        assert response__route_1.get('body'      ) == 'this is route 2'
        assert response__route_1.get('statusCode') == 201

    def test_3__invoke__locally__new_route_2__view__captured_event_data(self):
        from osbot_utils.utils.Dev import pprint

        request__404         = self.request_payload(path='/AAAAAAA')
        response__404        = run(request__404)
        request__id          = response__404.get('headers').get('fast-api-request-id')
        request__id__guid    = Random_Guid(request__id)
        http_events          = fast_api_with_router.http_events
        request__http_event  = http_events.requests_data.get(request__id__guid)

        request_http_event_json = request__http_event.json()
        assert is_guid(request__id)              is True
        assert response__404.get('statusCode')   == 404
        assert type(http_events)                 is Fast_API__Http_Events
        assert type(request__http_event)         is Fast_API__Http_Event
        assert list_set(request_http_event_json) == ['event_id'           ,
                                                     'http_event_info'    ,
                                                     'http_event_request' ,
                                                     'http_event_response',
                                                     'http_event_traces'  ]

        event_id            = request_http_event_json.get('event_id'           )
        http_event_info     = request_http_event_json.get('http_event_info'    )
        http_event_request  = request_http_event_json.get('http_event_request' )
        http_event_response = request_http_event_json.get('http_event_response')
        http_event_traces   = request_http_event_json.get('http_event_traces'  )

        fast_api_name = WCF__5__Fast_API__With_Router.__name__
        info_id       = http_event_info    .get('info_id'    )
        thread_id     = http_event_info    .get('thread_id'  )
        timestamp     = http_event_info    .get('timestamp'  )

        duration      = http_event_request .get('duration'   )
        request_id    = http_event_request .get('request_id' )
        start_time    = http_event_request .get('start_time' )

        end_time      = http_event_response.get('end_time'   )
        response_id   = http_event_response.get('response_id')

        traces_id     = http_event_traces  .get('traces_id'  )


        assert event_id            == request__id__guid
        assert http_event_info     == { 'client_city'    : None          ,
                                        'client_country' : None          ,
                                        'client_ip'      : '127.0.0.1'   ,
                                        'domain'         : None          ,
                                        'event_id'       : event_id      ,
                                        'fast_api_name'  : fast_api_name ,
                                        'info_id'        : info_id       ,
                                        'log_messages'   : []            ,
                                        'thread_id'      : thread_id     ,
                                        'timestamp'      : timestamp     }

        assert http_event_request  == { 'duration'       : duration      ,
                                        'event_id'       : event_id      ,
                                        'headers'        : {}            ,
                                        'host_name'      : 'mangum'      ,
                                        'method'         : 'GET'         ,
                                        'path'           : '/AAAAAAA'    ,
                                        'port'           : 80            ,
                                        'request_id'     : request_id    ,
                                        'start_time'     : start_time    }

        assert http_event_response == { 'content_length' : '22'                                         ,
                                        'content_type'   : 'application/json'                           ,
                                        'end_time'       : end_time                                     ,
                                        'event_id'       : event_id                                     ,
                                        'headers'        : { 'content-length'     : '22'               ,
                                                             'content-type'       : 'application/json' ,
                                                             'fast-api-request-id': request__id__guid  },
                                        'response_id'    : response_id                                  ,
                                        'status_code'    : 404                                          }

        assert http_event_traces   == { 'event_id'       : event_id      ,
                                        'traces'         : []            ,
                                        'traces_count'   : 0             ,
                                        'traces_id'      : traces_id     }



