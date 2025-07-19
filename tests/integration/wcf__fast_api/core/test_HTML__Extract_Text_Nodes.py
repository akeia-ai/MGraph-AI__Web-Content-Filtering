from unittest                                                                       import TestCase
from osbot_utils.utils.Dev                                                          import pprint
from mgraph_ai_web_content_filtering.wcf__fast_api.core.HTML__Extract_Text_Nodes    import HTML__Extract_Text_Nodes
from mgraph_ai_web_content_filtering.wcf__fast_api.core.Html__Transformations       import WEBSITE_URL__DEFAULT_SITE


class test_HTML__Extract_Text_Nodes(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.html_extract_text_nodes = HTML__Extract_Text_Nodes()

    def test_extract(self):
        #url = 'https://www.bbc.com/sport/football/articles/cvg8j1l0751o'
        url = WEBSITE_URL__DEFAULT_SITE
        with self.html_extract_text_nodes as _:
            _.url         = url
            text_elements = _.extract()
            assert text_elements['1e314df0e1'] ==  { 'original_text': '\n   BBC - 404: Not Found\n    ',
                                                      'rating': None,
                                                      'tag': 'title'}
            assert _.captures == 23