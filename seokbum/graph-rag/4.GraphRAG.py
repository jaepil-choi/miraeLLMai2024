from neo4j import GraphDatabase
from executors.completion_executor import ChatCompletionExecutor

#----------4-1. user query에서 기업 이름과 시간 추출.----------#
# 1. user query: 특정 기업의 특정 시간대의 주가 변동에 대해 질문하는 내용. 
# 2. 객체 & 관계 추출했을 때와 동일하게 Completion Executor를 활용하여 기업 이름과 시간을 추출.

completion_executor = ChatCompletionExecutor(
    host='https://clovastudio.stream.ntruss.com',
    api_key='NTA0MjU2MWZlZTcxNDJiY+Uy9rYumYZsV6izDa9AFvO56MDOrkyLi3eCmugWbNRu',              
    api_key_primary_val='1yiWJOyxczG1Ichq95JEUty5cZKr3F5iBynZfQWL',  
    request_id='c157480f-7a49-4fff-bc49-65227afaaffb'            
)

instruction = {"role":"user","content":"다음의 과제를 수행해줘.\n\n-목표-\n한 문장이 입력되었을 때, 그 문장에 포함된 기업, 시간을 추출하기.\n답변의 양식은 (<기업>[구분]<시간>)으로 출력.\n답변 외의 어떠한 단어나 문장도 절대로 출력하지 않기.\n\n-예시 1- \n입력된 문장 : 현대차의 주가가 2024-07-12에 감소한 이유를 알려줘.\n답변 : (현대차[구분]2024-07-12)\n\n-예시 2- \n입력된 문장 : 2022-05-12에 쿠팡의 주식 가격이 증가한 이유를 알려줘.\r\n답변 : (쿠팡[구분]2022-05-12)\n"}
user_query = {"role":"user","content":"2021-01-08에 삼성전자의 주가가 상승했는데, 그 원인을 알려줄 수 있을까?"}

print("############################## <user query에서 기업 이름과 시간 추출> ##############################\n")
print("- user query: " + user_query["content"] + "\n")

message = [instruction, user_query]

completion_request_data = {
    "messages": message,
    "maxTokens": 1000, 
    "temperature": 0.5,
    "topK": 0,
    "topP": 0.8,
    "repeatPenalty": 1.2,
    "stopBefore": [],
    "includeAiFilters": True,
    "seed": 0
}

try:
    response = completion_executor.execute(completion_request_data)
    extract_result = response.get('result', {}).get('message', {}).get('content', '').strip()
         
except Exception as e:
    print(f"Error: {e}")
    
extract_result = extract_result[1:-1].split("[구분]")
company = extract_result[0]
time = extract_result[1]

print("- HyperCLOVA X가 user query에서 추출한 기업 이름 및 시간: 기업= " + company + ", 시간= " + time + "\n")
print("####################################################################################################\n")

#----------4-2. 추출한 기업 이름과 시간을 활용하여 neo4j Graph DB에서 관련 정보를 검색.----------#
# 1. cypher query를 활용하여 neo4j DB에서 해당 시간에 해당 기업이 어떠한 관계를 가지고 있는지를 검색.
# 2. 검색 결과를 references에 저장.

print("############### <추출한 기업 이름과 시간을 활용하여 neo4j Graph DB에서 관련 정보 검색> #############\n")

URL = "bolt://107.21.40.126:7687"                   
AUTH = ("neo4j", "rust-interface-refunds")

driver = GraphDatabase.driver(URL, auth=AUTH) 
session = driver.session()
cypher = "MATCH (dest:기업 {이름:\"" + company + "\"})<-[r:관계 {시간:\"" + time + "\"}]-(source) RETURN source.이름, source.설명, dest.이름, dest.설명, r.설명, r.URL"
cypher_results = session.run(cypher)
references = []
for result in cypher_results:
    result = result.items()
    reference_text = ""
    company_name = result[2][1]
    company_description = result[3][1]
    reference_text += "1. 관심 기업: " + company_name + ", " + company_description + "\n"
    source_name = result[0][1]
    source_description = result[1][1]
    reference_text += "2. 연관 객체: " + source_name + ", " + source_description + "\n"
    relation_description = result[4][1]
    reference_text += "3. 관심 기업과 연관 객체 간의 관계: " + relation_description + "\n"
    relation_url = result[5][1]
    reference_text += "4. 출처: " + relation_url + "\n"
    references.append(reference_text)

print("GraphDB Retrieval 결과: \n")
for ref in references:
    print(ref)
print("####################################################################################################\n")
    
session.close()

#----------4-3. GraphRAG.----------#
# 1. 4-2에서 검색한 정보를 Hyperclova X에게 제공.
# 2. Completion Executor를 활용하여 user query에 대한 답변을 생성.

instruction = {"role":"system","content": "- 너의 역할은 사용자의 질문에 reference들을 바탕으로 답변하는거야. \n- 각 reference는 user query에 포함된 날짜에 user의 관심 기업과 형성된 관계에 대한 설명으로 다음의 형식으로 구성되어있어.\n\n1. 관심 기업: <관심 기업 이름>, <관심 기업 설명>\n2. 연관 객체: <연관 객체 이름>, <연관 객체 설명>\n3. 관심 기업과 연관 객체 간의 관계: <관심 기업과 연관 객체 간의 관계 설명>\n4. 출처: <URL>\n\n- 각 reference마다 다음의 형식으로 답변을 작성해줘.\n\n1. reference가 호재인 경우:\n\n(+) <호재인 이유> (출처: <URL>)\n\n2. reference가 악재인 경우:\n\n(-) <악재인 이유> (출처: <URL>)\n\n-모든 referece에 대한 답변을 완성했으면 마지막에 모든 reference들을 기반으로 user query에 대한 너의 종합 의견을 제시해줘.\n- reference와 연관된 답변만을 작성하고 reference에 존재하지 않는 내용은 절대로 작성하지마.\n"}
example = {"role":"system","content":"reference들의 예시와 그에 대응되는 답변의 예시는 다음과 같아. 예시의 답변과 동일하게 형식으로 이후에 답변을 작성해줘.\n\nreference 예시:\n\nreference 1:\n1. 관심 기업: 현대차, 현대차는 대한민국의 자동차 제조 기업으로, 다양한 차종과 기술을 개발하고 있다.\n2. 관련 객체: 미국 환경보호청, 미국 환경보호청(EPA)은 미국의 환경 보호를 담당하는 기관으로, 자동차 배출가스 규제 등 다양한 정책을 시행하고 있다.\n3. 관심 기업과 관련 객체간의 관계: 미국 환경보호청(EPA)이 자동차 배출가스 규제를 대폭 강화하면서 현대차 등 내연기관차를 주로 판매하는 자동차 업체들이 비상에 걸렸다.\n4. 출처: https://n.news.naver.com/mnews/article/001/0014052905?sid=104\n\nreference 2:\n1. 관심기업: 현대차, 현대차는 대한민국의 자동차 제조 기업으로, 다양한 차종과 기술을 개발하고 있다.\n2. 관련 객체: 파나소닉, 파나소닉은 일본의 종합 가전제품 제조 회사로, 음향 및 영상기기, 반도체, 자동차 부품 등 다양한 분야에서 사업을 영위하고 있다.\n3. 관심 기업과 관련 객체간의 관계: 파나소닉은 현대차에 차량용 프리미엄 오디오·스피커 시스템 적용을 검토하고 있으며, 언제든 협업이 가능하다고 밝혔다.\n4. 출처: https://n.news.naver.com/mnews/article/011/0004285165?sid=101\n\n답변 예시:\n\n2024-01-01에 현대차 주가의 변동 원인은 다음과 같습니다.\n\n(-) 해당 시점에 미국 환경보호청이 자동차 배출가스 규제를 대폭 강화하여 현대차를 비롯한 내연기관차를 판매하는 기업들이 위기에 처했었습니다. (출처: https://n.news.naver.com/mnews/article/001/0014052905?sid=104)\n\n(+) 당시 파나소닉이 현대차에 차량용 프리미엄 오디어 및 스피커 시스템을 제공할 것을 검토했고, 현대차와의 협업에 긍정적인 태도를 보였습니다. (출처: URL: https://n.news.naver.com/mnews/article/011/0004285165?sid=101)\n\n종합 의견: 파나소닉과의 협업은 현대차에게 긍정적인 부분이나, 미국 환경보호청의 규제가 더욱 큰 영향을 주었을 것으로 판단되어 주가가 하락했다고 생각합니다.\n"}
print("########################################## <GraphRAG prompt> #######################################" + "\n\n" + instruction["content"] + "\n" + example["content"])
print("######################################################################################################\n")

print("##################### <GraphRAG를 활용한 HyperCLOVA X의 user query에 대한 답변> ######################")
message = [instruction]
cnt = 1
for ref in references:
    message.append(
        {
            "role": "system",
            "content": f"reference {cnt}:\n{ref}"
        }
    )
    cnt += 1
message.append(user_query)
    
completion_request_data = {
    "messages": message,
    "maxTokens": 1000, 
    "temperature": 0.5,
    "topK": 0,
    "topP": 0.8,
    "repeatPenalty": 1.2,
    "stopBefore": [],
    "includeAiFilters": True,
    "seed": 0
}

try:
    response = completion_executor.execute(completion_request_data)
    extract_result = response.get('result', {}).get('message', {}).get('content', '').strip()
    print("\n{}\n".format(extract_result))
         
except Exception as e:
    print(f"Error: {e}")
    
print("######################################################################################################\n")