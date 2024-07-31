from executors.clovastudio_executor import CLOVAStudioExecutor
import time
 
class SlidingWindowExecutor(CLOVAStudioExecutor):
    def execute(self, completion_request):
        endpoint = '/v1/api-tools/sliding/chat-messages/HCX-003'
        success = 0 
        try:
            while success == 0:
                result, status = super().execute(completion_request, endpoint)
                if status == 200:
                    success = 1
                    return result['result']['messages']
                else:
                    error_message = result.get('status', {}).get('message', 'Unknown error')
                    print("Sliding Window Error")
                    print(error_message['message'])
                    if error_message['message'] == "Too many requests - rate exceeded":
                        print("Take a little break...")
                        time.sleep(60)
                
        except Exception as e:
            print(f"Error in SlidingWindowExecutor: {e}")
            return 'Error'
