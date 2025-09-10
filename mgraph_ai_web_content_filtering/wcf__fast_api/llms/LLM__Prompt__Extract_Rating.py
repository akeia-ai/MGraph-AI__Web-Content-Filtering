from osbot_utils.type_safe.primitives.safe_str.llm.Safe_Str__LLM__Model_Id import Safe_Str__LLM__Model_Id

from osbot_utils.type_safe.primitives.safe_str.text.Safe_Str__Text import Safe_Str__Text

from osbot_utils.type_safe.type_safe_core.decorators.type_safe                import type_safe
from osbot_utils.helpers.llms.builders.LLM_Request__Builder__Open_AI          import LLM_Request__Builder__Open_AI
from osbot_utils.helpers.llms.schemas.Schema__LLM_Request                     import Schema__LLM_Request
from osbot_utils.helpers.llms.schemas.Schema__LLM_Response                    import Schema__LLM_Response
from osbot_utils.type_safe.Type_Safe                                          import Type_Safe
from osbot_utils.utils.Json                                                   import str_to_json

from mgraph_ai_web_content_filtering.wcf__fast_api.llms.Schema__Text__Rating import Schema__Text__Rating, \
    Schema__Text__Ratings

SYSTEM_PROMPT__EXTRACT_RATING = """You are a text analysis expert that evaluates the sentiment and identifies the main topic of text content.

Focus on the Text element, not the tag that where that text was discovered

Your task is to analyze the ALL provided text elements and determine:
1. The overall positivity rating of the content
2. The main topic or subject matter of the text

For each positivity rating, use a scale from 0 to 1:
- 0.0 = Very negative sentiment
- 0.1-0.3 = Negative sentiment
- 0.4-0.6 = Neutral sentiment (0.5 being perfectly neutral)
- 0.7-0.9 = Positive sentiment
- 1.0 = Very positive sentiment

Consider factors like:
- Tone and language used
- Context and subject matter
- Emotional indicators
- Overall message conveyed

For the topic, identify the primary subject or theme of the content in a concise phrase."""

USER_PROMPT__EXTRACT_RATING = """\
Analyze the following text elements and determine the positivity rating and main topic (make sure you include all provided hash/text segments):

======================== TEXT CONTENT ========================
<Start>
{text_content}
<END>
==============================================================

Extract:
1. A positivity rating from 0 (negative) to 1 (positive), with 0.5 being neutral
2. The main topic or subject of the text in a concise phrase
"""

class LLM__Prompt__Extract_Rating(Type_Safe):
    request_builder: LLM_Request__Builder__Open_AI

    def llm_request(self, text_content: str, model_to_use: Safe_Str__LLM__Model_Id) -> Schema__LLM_Request:
        system_prompt = SYSTEM_PROMPT__EXTRACT_RATING
        user_prompt   = USER_PROMPT__EXTRACT_RATING.format(text_content=text_content)

        with self.request_builder as _:
            #_.set__model__gpt_4o_mini()  # Using GPT-4o-mini for efficient text analysis
            _.set__model(model_to_use)
            _.add_message__system(system_prompt)
            _.add_message__user  (user_prompt)
            _.set__function_call(parameters=Schema__Text__Ratings, function_name='extract_rating')

        return self.request_builder.llm_request()

    @type_safe
    def process_llm_response(self, llm_response: Schema__LLM_Response) -> Schema__Text__Ratings:
        """Process the LLM response into a structured rating assessment."""
        content = llm_response.obj().response_data.choices[0].message.content
        content_json = str_to_json(content)
        return Schema__Text__Ratings.from_json(content_json)