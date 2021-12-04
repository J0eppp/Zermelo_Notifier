from Browser import Browser
from sys import argv
import os

b = Browser()
# b.get_portal("nuovozeist")
# b.login_portal(os.environ["TEST_ZERMELO_USERNAME"], os.environ["TEST_ZERMELO_PASSWORD"], bool(
#     os.environ["TEST_ZERMELO_SSO"]))
# token = b.get_token()
token = b.login_get_token("nuovozeist", os.environ["TEST_ZERMELO_USERNAME"],
                          os.environ["TEST_ZERMELO_PASSWORD"], bool(os.environ["TEST_ZERMELO_SSO"]))
print(f"Token: {token}")
b.close()
