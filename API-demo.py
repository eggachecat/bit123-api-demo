from hashlib import sha1

import hmac

import base64
import json
import time
import requests

RUN_MIDDLEWARE_CONFIGS = json.load(open("./run_middleware_configs.json", "r"))
API_SIGNATURE_FIELD = "bit123-access-signature"
API_TIMESTAMP_FIELD = "bit123-access-timestamp"
API_KEY_FIELD = "bit123-access-key"
API_TOKEN_FIELD = "user_token"


def get_signature(secret, request_body, timestamp):
    raw_str = str(timestamp)
    raw_str += "id=" + str(request_body["id"]) + "&"
    raw_str += "method=" + str(request_body["method"]) + "&"

    params_str = ""
    if request_body["params"]:
        for item in request_body["params"]:
            params_str += str(item)
    raw_str += "params=" + params_str
    return base64.b64encode(hmac.new(secret.encode(), base64.b64encode(raw_str.encode()), sha1).digest()).decode(
        "utf-8")


class BlockingHttpAPITest:
    def __init__(self, url, headers, secret=None):
        self.url = url
        self.headers = headers
        self.message_id = 0
        self.secret = secret

    def send_request(self, request_method, params, url=None):
        if url is None:
            url = self.url

        body = {
            "method": request_method,
            "params": params,
            "id": self.message_id,
        }

        if self.secret is not None:
            self.headers[API_SIGNATURE_FIELD] = get_signature(self.secret, body,
                                                              self.headers[API_TIMESTAMP_FIELD])

        bodyStr = json.dumps(body)
        print("[{}]Sending to {} with body {} and header {}".format(request_method, url, bodyStr, self.headers))
        r = requests.post(url, data=bodyStr, headers=self.headers)
        print("[{}]Result: {}".format(request_method, r.json()))


def run_with_configs(test_client, configs):
    for k, v in configs["cases"].items():
        test_client.send_request(k, v["params"])


def run_with_header(HttpAPI, headers, secret, configs):
    test_client = HttpAPI(configs["settings"]["url"], headers, secret)
    run_with_configs(test_client, configs)
    return test_client


def run_with_token(HttpAPI, configs):
    headers = {
        API_TOKEN_FIELD: "fake_token",
    }
   if secret == "fake_token":
        print("You need apply for the real token (And for the best you should call the API with `key` and `secret`.)")
        exit(1)
    run_with_header(HttpAPI, headers, None, configs)


def run_with_signature(HttpAPI, configs):
    """
    headers[`bit123-access-key`] 和 secret 向 bit123 申请
    """
    headers = {
        API_KEY_FIELD: "fake_key",
        API_TIMESTAMP_FIELD: str(int(time.time()))
    }
    secret = "fake_secret"
    if secret == "fake_secret":
        print("You need apply for the real value for `bit123-access-key` and ")
        exit(1)
    run_with_header(HttpAPI, headers, secret, configs)


if __name__ == '__main__':
    print("Demo with signature...")
    run_with_signature(BlockingHttpAPITest, RUN_MIDDLEWARE_CONFIGS)
    print("Demo with token...")
    run_with_token(BlockingHttpAPITest, RUN_MIDDLEWARE_CONFIGS)


