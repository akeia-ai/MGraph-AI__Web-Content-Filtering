from typing import Dict

from osbot_utils.helpers.html.Html__To__Html_Dict                             import STRING__SCHEMA_TEXT, STRING__SCHEMA_NODES
from osbot_utils.type_safe.Type_Safe                                          import Type_Safe
from osbot_utils.utils.Misc                                                   import str_md5
from mgraph_ai_web_content_filtering.wcf__fast_api.core.Html__Transformations import Html__Transformations


class HTML__Extract_Text_Nodes(Type_Safe):
    html_transformations: Html__Transformations
    text_elements       : Dict
    text_elements__raw  : Dict
    hash_size           = 10
    captures            = 0
    url                 = str

    def capture_text(self, text, tag):
        hash = str_md5(text)[:self.hash_size]
        self.text_elements__raw[hash] = text
        self.text_elements[hash] = dict(original_text = text,
                                        rating        = None,
                                        tag           = tag )
        self.captures += 1
        return hash

    def extract_text_nodes(self, html_dict, max_depth=5):

        def traverse(node, depth, parent_tag):
            if depth > max_depth:
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
                traverse(child, depth + 1, node_tag)

        traverse(html_dict, depth=0, parent_tag=None)

    def extract(self, max_depth=35):
        html_dict = self.html_transformations.url_to_html_dict(self.url)
        self.extract_text_nodes(html_dict, max_depth=max_depth)
        return self.text_elements

