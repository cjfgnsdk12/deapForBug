import json

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

