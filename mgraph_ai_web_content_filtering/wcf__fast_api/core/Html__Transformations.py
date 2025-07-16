from enum import Enum

from osbot_utils.decorators.methods.cache_on_self       import cache_on_self
from osbot_utils.helpers.html.Html__To__Html_Dict       import Html__To__Html_Dict
from osbot_utils.helpers.html.Html__To__Html_Document import Html__To__Html_Document
from osbot_utils.helpers.safe_str.Safe_Str__File__Name  import Safe_Str__File__Name
from osbot_utils.type_safe.Type_Safe                    import Type_Safe
from osbot_utils.utils.Files                            import path_combine, file_not_exists, file_save, file_contents, folder_create, current_temp_folder
from osbot_utils.utils.Http                             import GET

# class Website_Url__For_Sites_With__One_Page_Support(Enum):
#     bbc__sport        : str = "https://www.bbc.co.uk/sport"
#     paul_graham__site : str = "https://paulgraham.com"
#     npr__text_version : str = "https://text.npr.org"

WEBSITE_URL__BBC__SPORT = "https://www.bbc.co.uk/sport"
FOLDER__TEMP_DATA       = 'WCF__Temp_Data'

class Html__Transformations(Type_Safe):

    @cache_on_self
    def base_folder(self):
        return path_combine(current_temp_folder(), 'FOLDER__TEMP_DATA')

    def setup(self):
        folder_create(self.base_folder())                                           # make sure base folder exists
        return self

    def file_name__from_url(self, url, extension):
        return Safe_Str__File__Name(url) + extension

    def file_path__from_url(self, url, extension):
        return path_combine(self.base_folder(), self.file_name__from_url(url, extension))

    def url_to_html(self, url):
        file_path = self.file_path__from_url(url, '.html')
        if file_not_exists(file_path):
            html = GET(url)
            file_save(html, path=file_path)
        else:
            html = file_contents(file_path)
        return html

    def url_to_html_dict(self, url):
        html      = self.url_to_html(url)
        html_dict = Html__To__Html_Dict(html=html).convert()
        return html_dict

    def url_to_html_document(self, url):
        html          = self.url_to_html(url)
        html_document = Html__To__Html_Document(html=html).convert()
        return html_document