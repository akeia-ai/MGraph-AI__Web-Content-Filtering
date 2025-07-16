from osbot_utils.helpers.safe_str.Safe_Str__File__Name import Safe_Str__File__Name
from osbot_utils.type_safe.Type_Safe import Type_Safe
from osbot_utils.utils.Files import path_combine, file_not_exists, file_save, file_contents, folder_create
from osbot_utils.utils.Http import GET

import mgraph_ai_web_content_filtering

base_dir      = path_combine(mgraph_ai_web_content_filtering.path, '../_data')

class Html__Transformations(Type_Safe):

    def setup(self):
        folder_create(base_dir)
        return self

    def file_name__from_url(self, url, extension):
        return Safe_Str__File__Name(url) + extension

    def file_path__from_url(self, url, extension):
        return path_combine(base_dir, self.file_name__from_url(url, extension))


    def html__get(self, url):
        file_path = self.file_path__from_url(url, '.html')
        if file_not_exists(file_path):
            html = GET(url)
            file_save(html, path=file_path)
        else:
            html = file_contents(file_path)
        return html
        #html = self.website_bbc.get__html__bbc__sport()
        #