from executors.clovastudio_executor import CLOVAStudioExecutor
from http import HTTPStatus
import requests
import time
 
class ChatCompletionExecutor(CLOVAStudioExecutor):
    def __init__(self, host, api_key, api_key_primary_val, request_id):
        super().__init__(host, api_key, api_key_primary_val, request_id)
 
    def execute(self, completion_request):
        headers = {
            'X-NCP-CLOVASTUDIO-API-KEY': self._api_key,
            'X-NCP-APIGW-API-KEY': self._api_key_primary_val,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': self._request_id,
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'application/json'
        }
        
        success = 0
 
        while success == 0:
            with requests.post(self._host + '/testapp/v1/chat-completions/HCX-003',
                            headers=headers, json=completion_request, stream=False) as r:
                if r.status_code == HTTPStatus.OK:
                    success = 1
                    return r.json()
                else:
                    print("Chat Completion Error")
                    print(r.text)
                    if r.text == "{\"status\":{\"code\":\"42901\",\"message\":\"Too many requests - rate exceeded\"},\"result\":null}":
                        print("Take a little break...")
                        time.sleep(60)