import requests
from settings import (
    BROWSERSTACK_BASE_URL, BROWSERSTACK_AUTH_ACCESS_KEY,
    BROWSERSTACK_AUTH_USERNAME, URLS
)


MOBILE_OS_LIST = ['ios', 'winphone', 'android']


class BStackException(Exception):
    pass


class APIHelper(object):

    def __init__(self, access_username=None, access_key=None):
        self.ACCESS_USERNAME = access_username or BROWSERSTACK_AUTH_USERNAME
        self.ACCESS_KEY = access_key or BROWSERSTACK_AUTH_ACCESS_KEY
        self.BASE_URL = BROWSERSTACK_BASE_URL

    def get(self, url, params=None):
        response = requests.get(
            url=BROWSERSTACK_BASE_URL + url,
            params=params,
            auth=(self.ACCESS_USERNAME, self.ACCESS_KEY)
        )
        self._validate_response(response)
        return response.json()

    def post(self, url, data):
        response = requests.post(
            url=BROWSERSTACK_BASE_URL + url,
            data=data,
            auth=(self.ACCESS_USERNAME, self.ACCESS_KEY)
        )
        self._validate_response(response)
        return response.json()

    def delete(self, url):
        response = requests.delete(
            url=BROWSERSTACK_BASE_URL + url,
            auth=(self.ACCESS_USERNAME, self.ACCESS_KEY)
        )
        self._validate_response(response)
        return response.json()

    @staticmethod
    def _validate_response(response):
        if response.status_code == 200:
            return
        if response.status_code == 401:
            raise BStackException("Unauthorized Accesss. Your ACCESS_USERNAME and ACCESS_KEY doesn't work")
        elif response.status_code == 401:
            raise BStackException(
                "Unauthorized Accesss. You are trying to access something whose permission is not with you"
            )
        elif response.status_code == '422':
            raise BStackException("Validation Failed, Unprocessable Entity - %s" % response.text)
        else:
            raise BStackException(
                "API Response not proper, Returned response as %s with status coode - %s"
                % (response.text, response.status_code)
            )


class BrowserStack(object):

    BROWSER_DATA_CACHE = {}

    def __init__(self, access_username=None, access_key=None):
        """
        :param access_username: Username provided by BrowserStack
        :param access_key: Access Key provided by BrowserStack
        """
        self.apihelper = APIHelper(access_username=access_username, access_key=access_key)
        if not self.BROWSER_DATA_CACHE:
            self.get_browsers(all=True)

    def get_browsers(self, flat=False, all=False):
        """
        :param flat: If required the list in a flat structure
        :param all: If response should include beta browsers etc.
        :return: the dict of os and os_version with browser and browser version
        """
        return self.apihelper.get(
            url=URLS.BROWSERS,
            params={
                'flat': flat,
                'all': all,
            }
        )

    def _validate_input(self, os, os_version, browser, browser_version):
        browser_data_cache = self.BROWSER_DATA_CACHE or self.get_browsers(all=True)
        try:
            rdict = browser_data_cache[os][os_version]
        except KeyError:
            raise BStackException
        else:
            if browser and browser_version:
                try:
                    assert [item for item in rdict if item['browser'] == browser and item['browser_version'] == browser_version]
                except AssertionError:
                    raise BStackException(
                        "Not a valid combination of os, os_version, browser and browser_version,"
                        "Use get_browsers method to get the list of valid values"
                    )

    def create_worker(
        self, url, os, os_version,
        browser=None, browser_version=None, timeout=300,
        name=None, build=None, project=None, enable_video_recording=False,
    ):
        """
        Create a worker with given parameters
        :param url: URL which needs to be accessed
        :param os: OS on which URL to be opened
        :param os_version: version of Operating System
        :param browser: Browser to be used
        :param browser_version: Version of the browser used
        :param timeout: time after which browser should timeout
        :param name: name of the worker
        :param build: name of the build
        :param project: name of the project
        :param enable_video_recording: False or True
        :return: Id of the worker
        """
        if os not in MOBILE_OS_LIST and not (browser and browser_version):
            raise BStackException("For Mobile OS, browser and browser_version also required")
        if timeout < 60 or timeout > 300:
            raise BStackException("timeout should be between 60 and 300 seconds")
        self._validate_input(os, os_version, browser, browser_version)
        response = self.apihelper.post(
            url=URLS.WORKER_API,
            data={
                'url': url,
                'os': os,
                'os_version': os_version,
                'browser': browser,
                'browser_version': browser_version,
                'name': name,
                'build': build,
                'project': project,
                'browserstack.video': enable_video_recording,
            }
        )
        return response['id']

    def take_screenshot(self, worker_id, response_format='json'):
        response = self.apihelper.get(
            url=URLS.WORKER_SCREENSHOT.format(worker_id, response_format),
        )
        return response

    def delete_worker(self, worker_id):
        response = self.apihelper.delete(
            url="{}/{}".format(URLS.WORKER_API, worker_id)
        )
        success = False
        if 'time' in response:
            success = True
        return {
            'success': success,
            'message': response.get('message')
        }

    def get_workers(self):
        return self.apihelper.get(
            url=URLS.WORKER_API + 's'
        )

    def check_status(self):
        return self.apihelper.get(
            url=URLS.API_STATUS
        )