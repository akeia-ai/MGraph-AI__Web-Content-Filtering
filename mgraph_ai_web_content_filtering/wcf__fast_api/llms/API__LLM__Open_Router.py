from typing                                                       import Dict, Any
from urllib.error                                                 import HTTPError
from osbot_utils.helpers.llms.platforms.open_ai.API__LLM__Open_AI import API__LLM__Open_AI
from osbot_utils.utils.Http                                       import POST_json
from osbot_utils.utils.Json                                       import str_to_json

ENV_NAME_OPEN_ROUTER__API_KEY = "OPEN_ROUTER__API_KEY"

class API__LLM__Open_Router(API__LLM__Open_AI):
    api_url     : str = "https://openrouter.ai/api/v1/chat/completions"
    api_key_name: str = ENV_NAME_OPEN_ROUTER__API_KEY
    http_referer: str = "https://github.com/owasp-sbot/OSBot-AWS"

    def execute(self, llm_payload: Dict[str, Any]):
        url     = self.api_url
        headers = { "Authorization": f"Bearer {self.api_key()}" ,
                    "Content-Type" : "application/json"         ,
                    "HTTP-Referer" : self.http_referer          ,
                    "User-Agent"   : "myfeeds.ai"               }

        try:
            response = POST_json(url, headers=headers, data=llm_payload)
            return response
        except HTTPError as error:
            error_message = str_to_json(error.file.read().decode("utf-8"))
            raise ValueError(error_message)
