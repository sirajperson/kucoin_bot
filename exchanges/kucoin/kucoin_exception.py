class KucoinAPIException(Exception):
    """Exception class to handle general API Exceptions

        `code` values

        `msg` format: '[message] (err-code)'
    """

    def __init__(self, response):
        self.code = ''
        self.message = 'Unknown Error'
        try:
            json_res = response.json()
        except ValueError:
            self.message = response.content
        else:
            if 'error' in json_res:
                self.message = json_res['error']
            if 'msg' in json_res:
                self.message = json_res['msg']
            if 'code' in json_res:
                self.code = json_res['code']

        self.status_code = response.status_code
        self.response = response

    def __str__(self):
        return f'KucoinAPIException: {self.message} (code={self.code})'
