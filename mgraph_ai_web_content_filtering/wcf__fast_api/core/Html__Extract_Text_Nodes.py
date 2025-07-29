from typing import Dict

from osbot_utils.helpers.html.Html__To__Html_Dict                             import STRING__SCHEMA_TEXT, STRING__SCHEMA_NODES
from osbot_utils.type_safe.Type_Safe                                          import Type_Safe
from osbot_utils.utils.Misc                                                   import str_md5
from mgraph_ai_web_content_filtering.wcf__fast_api.core.Html__Transformations import Html__Transformations


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

