import pytest
from unittest                                                                                   import TestCase
from mgraph_ai_web_content_filtering.wcf__fast_api.llms.API__LLM__Open_Router import ENV_NAME_OPEN_ROUTER__API_KEY
from osbot_utils.utils.Misc                                                                     import list_set
from osbot_utils.helpers.llms.schemas.Schema__LLM_Request__Message__Role                        import Schema__LLM_Request__Message__Role
from osbot_utils.utils.Env                                                                      import get_env, load_dotenv
from mgraph_ai_web_content_filtering.wcf__fast_api.llms.LLM__Prompt__Extract_Rating             import LLM__Prompt__Extract_Rating, SYSTEM_PROMPT__EXTRACT_RATING
from mgraph_ai_web_content_filtering.wcf__fast_api.llms.Schema__Text__Rating                    import Schema__Text__Rating, Schema__Text__Ratings
from mgraph_ai_web_content_filtering.wcf__fast_api.llms.WCF__LLM__Execute_Request               import WCF__LLM__Execute_Request
from tests.unit.wcf__objs_for_tests                                                             import wcf__assert_local_stack

TEST__TEMP__ROOT_FOLDER = '/tmp/_osbot_utils/cache__test_LLM_Request__Execute'

class test_LLM__Prompt__Extract_Rating(TestCase):

    @classmethod
    def setUpClass(cls):
        wcf__assert_local_stack()
        load_dotenv()
        if get_env(ENV_NAME_OPEN_ROUTER__API_KEY) is None:
            pytest.skip('This test requires OpenAI API Key to run')
        cls.prompt_extract_rating        = LLM__Prompt__Extract_Rating()
        cls.llm_execute_with_local_cache = WCF__LLM__Execute_Request()


    def test_llm_request(self):
        with self.prompt_extract_rating as _:
            text_content = TEST_DATA__BBC_404_PAGE
            llm_request = self.prompt_extract_rating.llm_request(text_content=text_content, model_to_use='')
            assert llm_request.request_data.function_call.parameters == Schema__Text__Ratings
            with llm_request.request_data.messages[0] as _:
                assert _.role == Schema__LLM_Request__Message__Role.SYSTEM
                assert _.content == SYSTEM_PROMPT__EXTRACT_RATING
            with llm_request.request_data.messages[1] as _:
                assert _.role == Schema__LLM_Request__Message__Role.USER
                assert text_content in _.content


    def test_process_llm_response__neutral_content(self):
        #self.llm_execute_with_local_cache.llm_execute.refresh_cache = True
        text_content = TEST_DATA__BBC_404_PAGE
        result      = self.llm_execute_with_local_cache.create_ratings(text_content)
        ratings     = result.get('data').get('ratings')
        assert list_set(result) == ['cache_id', 'data', 'model']
        assert len(ratings)     > 0


# Test Data
TEST_DATA__BBC_404_PAGE = """
{ "2339795568": { "original_text": "\\n Copyright © BBC.\\n ", "tag": "strong" }, 
"1e314df0e1": { "original_text": "\\n BBC - 404: Not Found\\n ", "tag": "title" }, 
"3a3a6e32db": { "original_text": "\\n Home\\n ", "tag": "a" }, 
"7aa93b2eab": { "original_text": "\\n News\\n ", "tag": "a" }, 
"3365c9459a": { "original_text": "\\n Sport\\n ", "tag": "a" }, 
"2ed2339d5e": { "original_text": "\\n Weather\\n ", "tag": "a" }, 
"84b350527c": { "original_text": "\\n iPlayer\\n ", "tag": "a" }, 
"f0125f7e37": { "original_text": "\\n Sounds\\n ", "tag": "a" }, 
"e4bf4e2a9b": { "original_text": "\\n 404\\n ", "tag": "p" }, 
"b134d0e7a4": { "original_text": "\\n Not Found\\n ", "tag": "strong" }, 
"7f50060da6": { "original_text": "\\n Sorry, we couldn't find that page\\n ", "tag": "h1" }, 
"68124ce81c": { "original_text": "\\n Check the page address or search for it below.\\n ", "tag": "p" }, 
"f2a34756d7": { "original_text": "\\n BBC Homepage\\n ", "tag": "a" }, 
"878e32d996": { "original_text": "\\n Terms Of Use\\n ", "tag": "a" }, 
"aca119b7c0": { "original_text": "\\n About the BBC\\n ", "tag": "a" }, 
"e99308a8fd": { "original_text": "\\n Privacy Policy\\n ", "tag": "a" }, 
"c0395f190e": { "original_text": "\\n Cookies\\n ", "tag": "a" }, 
"d507df347b": { "original_text": "\\n Accessibility Help\\n ", "tag": "a" }, 
"bdfc486228": { "original_text": "\\n Parental Guidance\\n ", "tag": "a" }, 
"ef8ff573de": { "original_text": "\\n Contact the BBC\\n ", "tag": "a" }, 
"4131590b4e": { "original_text": "\\n Get Personalised Newsletters\\n ", "tag": "a" }, 
"9180262c0c": { "original_text": "\\n The BBC is not responsible for the content of external sites.\\n ", "tag": "p" }, 
"499c988843": { "original_text": "\\n Read about our approach to external linking.\\n ", "tag": "a" } }
"""
