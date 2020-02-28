def find_line(ast_dict):
 if type(ast_dict['ext']) is list: # 2개 이상의 함수로 구성
   for ext in ast_dict['ext']:
     for block_items in ext['body']['block_items']:
       recursive_find_line(block_items)
 else: # 1개의 함수로 구성
   for block_items in ext['body']['block_items']:
     recursive_find_line(block_items)
​
​
# 재귀적으로 dict블럭을 들어가며 원하는 라인의 정보를 찾는 함수
def recursive_find_line(block_items):
 global result # result를 전역 변수fh 사용하겠다고 설정
 # 노드 정보
 nodetype=block_items['_nodetype']
 # 노드가 ID 거나 Constant면 탐색 중지(종단점)
 if(nodetype=="ID" or nodetype=="Constant"):
   return
 # 노득가 while이면  
 if(nodetype=="While"):
   coord=block_items['cond']['coord'].split(':')
   if(coord[1]==line):
     print(block_items['cond']) # while의 cond 가 맞으면 출력
     result=block_items['cond']
   else: # 아니면
     for new_block in block_items['stmt']['block_items']: # stmt의 block을 각각 확인
       recursive_find_line(new_block) # 다음 블럭에 대해 재귀호출하여 찾음
 # 노드가 if면        
 elif(nodetype=="If"):
   coord=block_items['cond']['coord'].split(':')
   if(coord[1]==line):
     print(block_items['cond'])  # if 의 cond 가 맞으면 출력
     result=block_items['cond']
   else: # 아니면
     if block_items['iffalse'] is not None:
       for new_block in block_items['iffalse']['block_items']:
         recursive_find_line(new_block)
     for new_block in block_items['iftrue']['block_items']:
       recursive_find_line(new_block)
 # 노드가 if도 while도 아니라면
 else: # while if가 아닌 문장을 출력해주는 함수
   coord=block_items['coord'].split(':')
   if(coord[1]==line):
     print(block_items)
     result=block_items
​
​
​
line="4"
result={}
find_line(ast_dict)
print(result)​
