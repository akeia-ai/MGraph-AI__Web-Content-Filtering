from mgraph_ai_web_content_filtering.wcf__fast_api.llms.Schema__WCF__LLM__Supported_Models import Schema__WCF__LLM__Supported_Models
from osbot_utils.helpers.llms.actions.LLM_Request__Execute                                 import LLM_Request__Execute
from osbot_utils.helpers.llms.builders.LLM_Request__Builder__Open_AI                       import LLM_Request__Builder__Open_AI
from osbot_utils.helpers.llms.cache.LLM_Request__Cache__File_System                        import LLM_Request__Cache__File_System
from osbot_utils.type_safe.Type_Safe                                                       import Type_Safe
from osbot_utils.utils.Env                                                                 import load_dotenv
from mgraph_ai_web_content_filtering.wcf__fast_api.llms.API__LLM__Open_Router              import API__LLM__Open_Router
from mgraph_ai_web_content_filtering.wcf__fast_api.llms.LLM__Prompt__Extract_Rating        import LLM__Prompt__Extract_Rating
from mgraph_ai_web_content_filtering.wcf__fast_api.llms.WCF__LLM__Cache                    import WCF__LLM__Cache

#LLM__MODEL_TO_USE__DEFAULT = Schema__WCF__LLM__Supported_Models.Mistral_AI__Mistral_Small__Free
LLM__MODEL_TO_USE__DEFAULT = Schema__WCF__LLM__Supported_Models.Google__Gemini_2_0  # Open_AI__GPT_5__Nano

class WCF__LLM__Execute_Request(Type_Safe):
    virtual_storage: WCF__LLM__Cache = None

    def __init__(self):
        load_dotenv()
        super().__init__()
        #self.cache_root_folder = Safe_Str__File__Path(folder_create(TEST__TEMP__ROOT_FOLDER))

        self.virtual_storage   = WCF__LLM__Cache().setup()
        self.llm_cache         = LLM_Request__Cache__File_System(virtual_storage = self.virtual_storage  ).setup()
        #self.llm_api           = API__LLM__Open_AI()
        self.llm_api           = API__LLM__Open_Router()
        self.request_builder   = LLM_Request__Builder__Open_AI()
        self.llm_execute       = LLM_Request__Execute(llm_cache       = self.llm_cache      ,
                                                      llm_api         = self.llm_api        ,
                                                      request_builder = self.request_builder)
        self.prompt_extract_rating = LLM__Prompt__Extract_Rating()

    def create_ratings(self, text_content, model_to_use:Schema__WCF__LLM__Supported_Models = LLM__MODEL_TO_USE__DEFAULT):
        llm_request           = self.prompt_extract_rating.llm_request(text_content=text_content, model_to_use=model_to_use.value)
        llm_response          = self.llm_execute.execute(llm_request)
        llm_request__cache_id = self.llm_execute.llm_cache.get__cache_id__from__request(llm_request)
        ratings               = self.prompt_extract_rating.process_llm_response(llm_response)
        return dict(cache_id  = llm_request__cache_id,
                    model     = model_to_use.value   ,
                    data      = ratings     .json())