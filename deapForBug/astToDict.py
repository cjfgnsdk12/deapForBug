from __future__ import print_function

import json
import sys
import re
import copy

# This is not required if you've installed pycparser into
# your site-packages/ with setup.py
#
sys.path.extend(['.', '..'])

from pycparser import parse_file, c_ast,c_parser,c_generator
from pycparser.plyparser import Coord


RE_CHILD_ARRAY = re.compile(r'(.*)\[(.*)\]')
RE_INTERNAL_ATTR = re.compile('__.*__')


class CJsonError(Exception):
  pass


def memodict(fn):
  """ Fast memoization decorator for a function taking a single argument """
  class memodict(dict):
      def __missing__(self, key):
          ret = self[key] = fn(key)
          return ret
  return memodict().__getitem__


@memodict
def child_attrs_of(klass):
  """
  Given a Node class, get a set of child attrs.
  Memoized to avoid highly repetitive string manipulation
  """
  non_child_attrs = set(klass.attr_names)
  all_attrs = set([i for i in klass.__slots__ if not RE_INTERNAL_ATTR.match(i)])
  return all_attrs - non_child_attrs


def to_dict(node):
  """ Recursively convert an ast into dict representation. """
  klass = node.__class__

  result = {}

  # Metadata
  result['_nodetype'] = klass.__name__

  # Local node attributes
  for attr in klass.attr_names:
      result[attr] = getattr(node, attr)

  # Coord object
  if node.coord:
      result['coord'] = str(node.coord)
  else:
      result['coord'] = None
  # Child attributes
  for child_name, child in node.children():
      # Child strings are either simple (e.g. 'value') or arrays (e.g. 'block_items[1]')
      match = RE_CHILD_ARRAY.match(child_name)
      if match:
          array_name, array_index = match.groups()
          array_index = int(array_index)
          # arrays come in order, so we verify and append.
          result[array_name] = result.get(array_name, [])
          if array_index != len(result[array_name]):
              raise CJsonError('Internal ast error. Array {} out of order. '
                  'Expected index {}, got {}'.format(
                  array_name, len(result[array_name]), array_index))
          result[array_name].append(to_dict(child))
      else:
          result[child_name] = to_dict(child)

  # Any child attributes that were missing need "None" values in the json.
  for child_attr in child_attrs_of(klass):
      if child_attr not in result:
          result[child_attr] = None

  return result


def to_json(node, **kwargs):
  """ Convert ast node to json string """
  return json.dumps(to_dict(node), **kwargs)


def file_to_dict(filename):
  """ Load C file into dict representation of ast """
  ast = parse_file(filename, use_cpp=True,cpp_path='gcc',cpp_args=['-E', r'-Iutils/fake_libc_include'])
  return to_dict(ast)


def file_to_json(filename, **kwargs):
  """ Load C file into json string representation of ast """
  ast = parse_file(filename, use_cpp=True)
  return to_json(ast, **kwargs)


def _parse_coord(coord_str):
  """ Parse coord string (file:line[:column]) into Coord object. """
  if coord_str is None:
      return None

  vals = coord_str.split(':')
  vals.extend([None] * 3)
  filename, line, column = vals[:3]
  return Coord(filename, line, column)


def _convert_to_obj(value):
  """
  Convert an object in the dict representation into an object.
  Note: Mutually recursive with from_dict.
  """
  value_type = type(value)
  if value_type == dict:
      return from_dict(value)
  elif value_type == list:
      return [_convert_to_obj(item) for item in value]
  else:
      # String
      return value


def from_dict(node_dict):
  """ Recursively build an ast from dict representation """
  class_name = node_dict.pop('_nodetype')

  klass = getattr(c_ast, class_name)

  # Create a new dict containing the key-value pairs which we can pass
  # to node constructors.
  objs = {}
 
  for key, value in node_dict.items():
     
      if key == 'coord':
          objs[key] = _parse_coord(value)
      else:
          objs[key] = _convert_to_obj(value)
 
  # Use keyword parameters, which works thanks to beautifully consistent
  # ast Node initializers.
  return klass(**objs)


def from_json(ast_json):
  """ Build an ast from json string representation """
  return from_dict(json.loads(ast_json))





def find_line(ast_dict,line):
  '''
  이철훈\n
  2020-02-25\n
  현재까지 while, if 문으로 이루어진 구조에서만
  원하는 라인의 정보를 가져 올 수 있음
  ex) for문 안됨
  좀 더 복잡한 라인을 넣으려면 수정이 필요함
  '''
  if type(ast_dict['ext']) is list: # 2개 이상의 함수로 구성
    for idx, ext in enumerate(ast_dict['ext']):
      for idx2, block_items in enumerate(ext['body']['block_items']):
        tmp_block=recursive_find_line(block_items,line)
        if tmp_block is not None: #None이 return 되는것을 방지
          return "ast_dict['ext']["+str(idx)+"]['body']['block_items']["+str(idx2)+"]"+tmp_block
  else: # 1개의 함수로 구성
    for idx, block_items in enumerate(ext['body']['block_items']):
      tmp_block=recursive_find_line(block_items,line)
      if tmp_block is not None: #None이 return 되는것을 방지
        return "ast_dict['ext']['body']['block_items']["+str(idx)+"]"+recursive_find_line(block_items,line)




def recursive_find_line(block_items,line):
  '''
  이철훈\n
  2020-02-26\n
  재귀적으로 dict블럭을 들어가며 원하는 라인의 정보를 찾는 함수
  return 은 각 블럭의 위치를 저장하기 위한 것이고, result는 위치를 전역변수로 반환한다.
  '''
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
      #print(block_items['cond']) # while의 cond 가 맞으면 출력
      result=block_items['cond']
      return "['cond']"
    else: # 아니면
      for idx, new_block in enumerate(block_items['stmt']['block_items']): # stmt의 block을 각각 확인
        tmp_block=recursive_find_line(new_block,line)
        if tmp_block is not None: # None이 return 되는것을 방지
          return "['stmt']['block_items']["+str(idx)+"]"+tmp_block # 다음 블럭에 대해 재귀호출하여 찾음
  # 노드가 if면        
  elif(nodetype=="If"):
    coord=block_items['cond']['coord'].split(':')
    if(coord[1]==line):
      #print(block_items['cond'])  # if 의 cond가 맞으면 출력
      result=block_items['cond']
      return "['cond']"
    else: #  if 의 cond가 아니면
      if block_items['iffalse'] is not None:
        for idx, new_block in enumerate(block_items['iffalse']['block_items']):
          tmp_block=recursive_find_line(new_block,line)
          if tmp_block is not None: #None이 return 되는것을 방지
            return "['iffalse']['block_items']["+str(idx)+"]"+tmp_block
      for idx, new_block in enumerate(block_items['iftrue']['block_items']):
        tmp_block=recursive_find_line(new_block,line)
        if tmp_block is not None: #None이 return 되는것을 방지
          return "['iftrue']['block_items']["+str(idx)+"]"+tmp_block
  else:   # while if가 아닌 문장
    coord=block_items['coord'].split(':')
    if(coord[1]==line):
      #print(block_items)
      result=block_items
      return ""



def remove_parse(ast):
  '''
  일단 보류 coord가 c로 변환하는데 무리가 없음
  '''
  print()





stack=[]

info_list=['_nodetype','coord','name'
,'type','value','bitsize','funcspec'
,'quals','storage','names','subscript'
,'init']

def addStack(name,data):
  global stack
  if(str(type(data))=="<class 'str'>"):
     name+="' : '"+data+"'"
     name="'"+name
     stack.append([name,0])
     return
  elif(str(type(data))=="<class 'list'>"):
      tmp={}
      for i in data:
          tmp.update(i)
      data=tmp
  keys=[x for x in data.keys()]
  node_info=[]
  for info_data in info_list:
      for key in keys:
          if info_data==key :
              node_info.append(key)
              keys.remove(key)
  if(len(node_info)==0):
      name="'"+name+"' : {"+"}"
  else:
      for idx, key in enumerate(node_info):
          if(idx==0):
              name+="' : {'"+key+"':'"+str(data[key])+"'"
          else:
              name+=", '"+key+"':'"+str(data[key])+"'"
      name+="}"
      name= "'"+name            
  stack.append([name,len(keys)])
  if(len(keys)==0):
      return
  for key in keys:
      addStack(key,data[key])


def getStack(data):
  addStack("main",data)
  return stack





stack_to_ast={}  # 전역변수
def make_dict(result_list):
  '''
  2020-03-03\n
  이철훈\n
  Deap에서 GP연산 후 돌아온 스택을 DFS를 이용하여
  다시 dict 자료형으로 바꿔주는 함수
  나머지 케이스 확인 요망
  결과 : stack_to_ast
  '''
  global stack_to_ast
  dict_stack=[]  #dfs 알고리즘을 위해 사용하는 스택
  for stack_data in result_list:   # 결과물 리스트를 하나씩 받아온다
    tmp="{"+stack_data[0]+"}"  
    dict_line=eval(tmp)  # 리스트에서 받아온 한줄을 dict로 바꾼다.
    #print( str(dict_line)+"  "+ str(stack_data[1])  ) # 디버깅용
    tree_num=stack_data[1]  # 각 트리의 자식 수
    if 'main' in dict_line:  # 가장 상위의 트리로서 다르게 처리함
      for key, value in dict_line['main'].items():
        stack_to_ast[key]=value
        for _ in range(0,tree_num):  # 자식 수만큼 스택에 저장
          dict_stack.append(stack_to_ast)
    else:
      if tree_num is not 0:  # 말단이 아닌경우
        now_stack=dict_stack.pop()    # 현재 위치를 스택에서 받아옴
        #print(dict_line.keys())  # 디버깅
        #print(dict_line.values()) # 디버깅
        for key, value in dict_line.items():
          now_stack[key]=value
          for _ in range(0,tree_num):
            dict_stack.append(now_stack[key])   # 현재위치를 자식 수만큼 저장
      else:  # 말단인 경우
        now_stack=dict_stack.pop()  # 현재위치 받아옴
        for key, value in dict_line.items():
          now_stack[key]=value
  #print(stack_to_ast)  # 결과물 출력
     



def find_pos(pos,ast_dict,stack_to_ast):
  '''
  2020-03-03
  이철훈
  ast_dict에서 원래 위치로 다시 삽입하는 함수
  '''
  #match=re.search('[+]',pos)
  tmp=pos.split('[')
  match=[]
  for unit in tmp:
    unit=unit[:-1]
    unit=unit.replace("'",'')
    match.append(unit)
  #print(match)
  del match[0]
  tmp_dict=ast_dict
  for idx, p in enumerate(match):
    if p.isdecimal() is True:
      p=int(p)
    if(idx==len(match)-1):
      tmp_dict[p]=stack_to_ast
    else:
      tmp_dict=tmp_dict[p]


'''
# zune.c
int isLeapYear(int y)
{
return (y%4 == 0);
}

int main(int argc, char *argv[])
{
int year = 1980;
int days;
days = atoi(argv[1]);
while (days > 365)
{
  if (isLeapYear(year))
  {
    if (days > 366)
    {
      days -= 366;
      year += 1;
    }
  }
  else
  {
    days -= 365;
    year += 1;
  }
}
printf("current year is %d\n", year);
return 0;
}
'''
#------------------------------------------------------------------------------

# 사용되는 zune.c
text = r"""
int isLeapYear(int y)
{
return (y%4 == 0);
}

int main(int argc, char *argv[])
{
int year = 1980;
int days;
days = atoi(argv[1]);
while (days > 365)
{
  if (isLeapYear(year))
  {
    if (days > 366)
    {
      days -= 366;
      year += 1;
    }
  }
  else
  {
    days -= 365;
    year += 1;
  }
}
printf("current year is %d\n", year);
return 0;
}
"""


parser = c_parser.CParser()
#ast = parser.parse(text)
#ast.show()
#ast_dict=to_dict(ast)
#ast_json=to_json(ast,sort_keys=True, indent=4)
#print(ast_dict)

'''
# 제이슨 저장
write_file=open('zune.json','w')
write_file.write(ast_json)
write_file.close()
'''

def resultStack(text, line):
  global stack
  global result
  line=str(line)
  parser = c_parser.CParser()
  ast = parser.parse(text)
  ast_dict=to_dict(ast)
  find_line(ast_dict,line)
  return getStack(result)

def makeC(text, GP_result,line):
  global result
  global stack_to_ast
  line=str(line)
  parser = c_parser.CParser()
  ast = parser.parse(text)
  ast_dict=to_dict(ast)
  stack_to_ast={}
  make_dict(GP_result)
  pos=find_line(ast_dict,line)
  #print(pos)
  #position=find_pos(pos,ast_dict,stack_to_ast)
  #print(position)
  #print(stack_to_ast)
  #position=copy.deepcopy(stack_to_ast)
  find_pos(pos,ast_dict,stack_to_ast)
  generator = c_generator.CGenerator()
  #print(ast_dict)
  try:
    ast=from_dict(ast_dict)
  except:
    return False
  return generator.visit(ast)




# 변경할 라인 설정
#line="4"
result={}  # GP로 넘겨줄 dict
#print(find_line(ast_dict))
#print(result)

# 여기서 genprog 과정이 필요함
# result= genprog_result
#print(getStack(result))
#stack=[]

#read_file=open('zune_stack.txt','r')
#GP_list=read_file.read()
#GP_result=eval(GP_list)
#make_dict(GP_result)
#print(makeC(text,GP_result,4))
#make_dict(getStack(result))  

#pos=find_line(ast_dict)
#position=find_pos(pos)
#position=stack_to_ast   # 변경된 dict을 원래 자리에 넣어줌
#print(position)
#print(ast_dict)

#ast를 보고 C파일로 다시 바꿔주는 코드
# 나중에  dict 버전으로 변경해야 함
#generator = c_generator.CGenerator()
#read_file=open('zune.json','r')
#ast=json.load(read_file)
#ast=from_dict(ast_dict)
#print(ast)
#print(generator.visit(ast))
