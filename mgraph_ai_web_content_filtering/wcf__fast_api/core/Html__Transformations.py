import requests
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Name   import Safe_Str__File__Name
from osbot_utils.helpers.html.transformers.Html__To__Html_Document                  import Html__To__Html_Document
from osbot_utils.helpers.html.transformers.Html_Dict__To__Html                      import Html_Dict__To__Html
from osbot_utils.helpers.html.transformers.Html__To__Html_Dict                      import Html__To__Html_Dict
from osbot_utils.decorators.methods.cache_on_self                                   import cache_on_self
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_utils.utils.Files                                                        import path_combine, file_not_exists, file_save, file_contents, folder_create, current_temp_folder, create_folder

WEBSITE_URL__DEFAULT_SITE = "https://www.bbc.co.uk/404"
FOLDER__TEMP_DATA         = 'WCF__Temp_Data'

class Html__Transformations(Type_Safe):

    @cache_on_self
    def base_folder(self):
        base_folder = path_combine(current_temp_folder(), FOLDER__TEMP_DATA)            # use current_temp_folder() has the core target
        create_folder(base_folder)                                                      # make sure the folder exists
        return base_folder

    def setup(self):
        folder_create(self.base_folder())                                           # make sure base folder exists
        return self

    def file_name__from_url(self, url, extension):
        return Safe_Str__File__Name(url) + extension

    def file_path__from_url(self, url, extension):
        return path_combine(self.base_folder(), self.file_name__from_url(url, extension))

    def url__to__html(self, url):
        file_path = self.file_path__from_url(url, '.html')
        if file_not_exists(file_path):
            response = requests.get(url)                            # use requests here since it handles natively sites like google (which uses a different encoding)
            html     = response.text
            file_save(html, path=file_path)
        else:
            html = file_contents(file_path)
        return html

    def url__to__html_dict(self, url):
        html      = self.url__to__html(url)
        html_dict = Html__To__Html_Dict(html=html).convert()
        return html_dict

    def url__to__html_dict__to__html(self, url):
        html           = self.url__to__html(url=url)
        html_dict      = Html__To__Html_Dict(html=html     ).convert()
        html_roundtrip = Html_Dict__To__Html(root=html_dict).convert()
        return html_roundtrip

    def url__to__html_dict__to__lines(self, url):
        html      = self.url__to__html(url=url)
        html_dict = Html__To__Html_Dict(html=html)
        html_dict.convert()
        lines = "/n".join(html_dict.print(just_return_lines=True))
        return lines

    def url__to__html_document(self, url):
        html          = self.url__to__html(url)
        html_document = Html__To__Html_Document(html=html).convert()
        return html_document