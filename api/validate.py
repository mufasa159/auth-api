from urllib.parse import urlparse
import re


def url(url):
   try:
      result = urlparse(url)
      return all([result.scheme, result.netloc])
   except ValueError:
      return False


def email(email):
   pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
   return re.match(pattern, email) is not None