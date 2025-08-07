from typing                                                                                 import Dict
from osbot_utils.utils.Lists                                                                import list_index_by
from mgraph_ai_web_content_filtering.wcf__fast_api.llms.Schema__WCF__LLM__Supported_Models  import Schema__WCF__LLM__Supported_Models
from mgraph_ai_web_content_filtering.wcf__fast_api.llms.WCF__LLM__Execute_Request           import LLM__MODEL_TO_USE__DEFAULT, WCF__LLM__Execute_Request
from osbot_utils.helpers.html.Html_Dict__To__Html                                           import Html_Dict__To__Html
from osbot_utils.helpers.html.Html__To__Html_Dict                                           import STRING__SCHEMA_TEXT, STRING__SCHEMA_NODES
from osbot_utils.type_safe.Type_Safe                                                        import Type_Safe
from osbot_utils.utils.Misc                                                                 import str_md5
from mgraph_ai_web_content_filtering.wcf__fast_api.core.Html__Transformations               import Html__Transformations, WEBSITE_URL__DEFAULT_SITE


class Html__Extract_Text_Nodes(Type_Safe):
    html_transformations: Html__Transformations
    html_dict           : Dict
    text_elements       : Dict
    text_elements__raw  : Dict
    hash_size           = 10
    captures            = 0
    max_depth           = 10
    url                 = str

    def capture_text(self, text, tag):
        hash = str_md5(text)[:self.hash_size]
        self.text_elements__raw[hash] = text
        self.text_elements[hash] = dict(original_text = text,
                                        #rating        = None,
                                        tag           = tag )
        self.captures += 1
        return hash

    def traverse(self, node, depth, parent_tag):
        if depth > self.max_depth:
            return

        if not isinstance(node, dict):
            return

        if node.get("type") == STRING__SCHEMA_TEXT:
            data = node.get("data", "").strip()
            if data:
                if parent_tag not in ['style', 'script']:
                    node['data'] = self.capture_text(node['data'], parent_tag)

        node_tag = node.get('tag')
        for child in node.get(STRING__SCHEMA_NODES, []):
            self.traverse(child, depth + 1, node_tag)

    def extract(self, max_depth=35) -> Dict:
        self.max_depth = max_depth
        self.html_dict = self.html_transformations.url__to__html_dict(self.url)
        self.traverse(self.html_dict, depth=0, parent_tag=None)
        return self.text_elements

    def create_html_with_hashes_as_text(self):
        if not self.html_dict:
            self.extract()

        html_with_hashes = Html_Dict__To__Html(root=self.html_dict).convert()
        return html_with_hashes

    def create_html_with_xxx_as_text(self):
        html = self.create_html_with_hashes_as_text()
        for text_hash, text_element in self.text_elements.items():
            original_text = text_element.get('original_text')
            text_to_replace = ''.join('x' if c != ' ' else ' ' for c in original_text)
            html = html.replace(text_hash, text_to_replace)
        return html

    def create_html_with_ratings(self):
        ratings = self.create_ratings()
        html = self.create_html_with_hashes_as_text()
        for text_hash, text_element in self.text_elements.items():
            rating      = ratings.get(text_hash, {}).get('positivity') or 0.5
            if rating < 0.3:
                text_to_replace = f'Negative: ({rating})'
            elif rating > 0.6:
                text_to_replace = f'Positive: ({rating})'
            else:
                text_to_replace = f'Neutral: ({rating})'
            html = html.replace(text_hash, text_to_replace)
        return html

    def create_html_with_topics(self):
        ratings = self.create_ratings()
        html = self.create_html_with_hashes_as_text()
        for text_hash, text_element in self.text_elements.items():
            positivity      = ratings.get(text_hash, {}).get('topic')
            text_to_replace = str(positivity)
            html = html.replace(text_hash, text_to_replace)
        return html

    def create_html_with_min_ratings(self, min_rating=0.3):
        ratings = self.create_ratings()
        html = self.create_html_with_hashes_as_text()
        for text_hash, text_element in self.text_elements.items():
            rating = ratings.get(text_hash, {}).get('positivity')
            if type(rating) is not float:
                rating = 0.5
            original_text = text_element.get('original_text')
            if rating < min_rating:
                text_to_replace = ''.join('x' if c != ' ' else ' ' for c in original_text)
            else:
                text_to_replace = original_text + f' | (rating: {rating})'
            html = html.replace(text_hash, text_to_replace)
        return html

    def create_html_with_max_ratings(self, max_rating=0.3):
        ratings = self.create_ratings()
        html = self.create_html_with_hashes_as_text()
        for text_hash, text_element in self.text_elements.items():
            rating       = ratings.get(text_hash, {}).get('positivity') or 0.5
            original_text = text_element.get('original_text')
            if rating > max_rating:
                text_to_replace = ''.join('x' if c != ' ' else ' ' for c in original_text)
            else:
                text_to_replace = original_text + f' | (rating: {rating})'
            html = html.replace(text_hash, text_to_replace)
        return html


    def create_ratings(self, model_to_use: Schema__WCF__LLM__Supported_Models = LLM__MODEL_TO_USE__DEFAULT
                        ) -> dict:
        llm_execute = WCF__LLM__Execute_Request()
        if not self.text_elements:
            self.extract()
        result = llm_execute.create_ratings(self.text_elements, model_to_use=model_to_use)
        ratings = result.get('data').get('ratings')
        return list_index_by(ratings, 'hash')



