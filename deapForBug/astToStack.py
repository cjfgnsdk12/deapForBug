import json

stack=[]

info_list=['_nodetype','coord','name'
,'type','value','bitsize','funcspec'
,'quals','storage','names']

def addStack(name,data):
   global stack
   if(str(type(data))=="<class 'str'>"):
       name+="' : '"+data+"'"
       name="'"+name
       stack.append([name,0])
       return
   else:
       keys=[x for x in data.keys()]
   node_info=[]
   for info_data in info_list:
       for key in keys:
           if info_data==key :
               node_info.append(key)
               keys.remove(key)
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
   for key in reversed(keys):
       addStack(key,data[key])

def getStack(data):
    addStack("main",data)
    return stack

