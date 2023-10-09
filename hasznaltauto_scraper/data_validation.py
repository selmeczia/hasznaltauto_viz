import re

class DataValidator():
    PREFIXES = ["https://","http://"]
    HOST = "hasznaltauto.hu"

    def __init__(self, link) -> None:
        self.link = link
        self.errors = {}

    def is_valid(self):
        return not bool(self.errors)

    def validate_link(self):

        link = self.link.lower()

        pattern = r'^(https?://)?(www\.)?' + re.escape(self.HOST) + r'(/.*)?$'

        match = re.match(pattern, link)

        if not match or not match.end() == len(link):
            self.errors["link"] = "Link is not from predefined hosts"
