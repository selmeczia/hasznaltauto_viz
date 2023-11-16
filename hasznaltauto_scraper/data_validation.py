import re
import requests

class DataValidator():
    PREFIXES = ["https://","http://"]
    HOST = "hasznaltauto.hu"

    def __init__(self, link) -> None:
        self.link = link
        self.errors = {}

    def is_valid(self):
        return not bool(self.errors)
    
    def validate_link(self):
        self.validate_link_str()

        # only open link if link str is valid
        if not self.errors:
            self.validate_link_status_code()

    def validate_link_str(self):

        link = self.link.lower()

        pattern = r'^(https?://)?(www\.)?' + re.escape(self.HOST) + r'(/.*)?$'

        match = re.match(pattern, link)

        if not match or not match.end() == len(link):
            self.errors["link"] = "Link is not from predefined hosts"

    def validate_link_status_code(self):

        req = requests.get(self.link)
        if not req.status_code == 200:
            self.errors["status_code"] = f"Status code: {req.status_code}"