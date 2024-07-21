from clovastudio_executor import CLOVAStudioExecutor
import json
 
class SlidingWindowExecutor(CLOVAStudioExecutor):
    def execute(self, completion_request):
        endpoint = '/v1/api-tools/sliding/chat-messages/HCX-003'
        try:
            result, status = super().execute(completion_request, endpoint)
            if status == 200:
                # 슬라이딩 윈도우 적용 후 메시지를 반환
                return result['result']['messages']
            else:
                error_message = result.get('status', {}).get('message', 'Unknown error')
                raise ValueError(f"오류 발생: HTTP {status}, 메시지: {error_message}")
        except Exception as e:
            print(f"Error in SlidingWindowExecutor: {e}")
            return 'Error'
