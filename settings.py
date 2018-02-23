BROWSERSTACK_API_VERSION = 4
BROWSERSTACK_BASE_URL = "https://api.browserstack.com/" + str(BROWSERSTACK_API_VERSION)

BROWSERSTACK_AUTH_USERNAME = 'YourUsername'
BROWSERSTACK_AUTH_ACCESS_KEY = 'YourAccessKey'

class URLS(object):

    BROWSERS = '/browsers'
    WORKER_API = '/worker'
    WORKER_SCREENSHOT = '/worker/{}/screenshot.{}'
    API_STATUS = '/status'
