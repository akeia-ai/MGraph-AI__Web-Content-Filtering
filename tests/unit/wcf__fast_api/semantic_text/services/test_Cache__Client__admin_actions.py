import pytest
from unittest                                                                                   import TestCase
from mgraph_ai_web_content_filtering.wcf__fast_api.semantic_text.config.consts__Semantic_Text   import ENV_VAR__API_KEY__SERVICE__CACHE__KEY_NAME
from mgraph_ai_web_content_filtering.wcf__fast_api.semantic_text.services.Cache__Client         import Cache__Client
from osbot_utils.utils.Env                                                                      import load_dotenv, get_env

class test_Cache__Client__admin_actions(TestCase):

    @classmethod
    def setUpClass(cls):                                                              # ONE-TIME expensive setup
        load_dotenv()                                                                 # Load environment variables
        if not get_env(ENV_VAR__API_KEY__SERVICE__CACHE__KEY_NAME):
            pytest.skip("Tests requite service cache API key and value")
        cls.cache_client = Cache__Client()

    def test__remove_all__cache_ids__semantic_text(self):
        pytest.skip("test requires manual execution")
        namespace = 'semantic-html'
        with self.cache_client as _:
            cache_ids = _.list_file_ids(namespace=namespace)
            for cache_id in cache_ids:
                _.delete_by_id(cache_id=cache_id, namespace=namespace)
                print('deleted', cache_id)

    def test__remove_all__files__semantic_text(self):
        pytest.skip("test requires manual execution")
        namespace = 'semantic-html'
        with self.cache_client as _:
            all_file_paths = _.list_files_all(path=namespace)
            for file_path in all_file_paths:
                result = _.delete_by_path(file_path)
                assert result is True
                print('deleted', file_path)
