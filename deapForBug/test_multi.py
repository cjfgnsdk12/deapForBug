import copy
import math
import random
import re
import sys
import os
import warnings

from collections import defaultdict, deque
from functools import partial, wraps
from inspect import isclass
from operator import eq, lt

import random
import operator

import numpy

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from deapRevised import algorithms
from deapRevised import base
from deapRevised import creator
from deapRevised import tools
from deapRevised import gp

import astToStack

import json

with open('/home/hyun/Desktop/Lab/deap/deapForBug/samples/sample1.json','r') as json_file:
    json_data=json.load(json_file)


class psetCl:
    info=""
    def __init__(self,psetInfo,psetPar):
        self.info=psetInfo
        self.parNum=psetPar
    def ter(self):
        info=self.info
        parNum=self.parNum
    def pri(self):
        info=self.info
        parNum=self.parNum

def makePset(psetStack):
    global tree_arr
    obList=[]
    num=-1
    for psetList in psetStack:
        num+=1
        obList.append(psetCl(psetList[0],psetList[1]))
        #print(obList[num].info)
        if(psetList[1]==0):
            tree_arr.append('t')
            pset.addTerminal(obList[num].ter,info=obList[num].info,name=obList[num].ter)
        else:
            tree_arr.append('p')
            pset.addPrimitive(obList[num].pri,psetList[1],info=obList[num].info,name=obList[num].pri)
            

def generate(pset, min_, max_,condition, type_=None):
    """Generate a Tree as a list of list. The tree is build
    from the root to the leaves, and it stop growing when the
    condition is fulfilled.

    :param pset: Primitive set from which primitives are selected.
    :param min_: Minimum height of the produced trees.
    :param max_: Maximum Height of the produced trees.
    :param condition: The condition is a function that takes two arguments,
                      the height of the tree to build and the current
                      depth in the tree.
    :param type_: The type that should return the tree when called, when
                  :obj:`None` (default) the type of :pset: (pset.ret)
                  is assumed.
    :returns: A grown tree with leaves at possibly different depths
              depending on the condition function.
    """
    if type_ is None:
        type_ = pset.ret
    expr = []
    #height = random.randint(min_, max_)
    stack = [(0, type_)]
    idx_tree=0
    idx_pri=0
    idx_ter=0
    while len(stack) != 0:
        depth, type_ = stack.pop()
        # make terminal node
        if (tree_arr[idx_tree]=='t')|(condition(max_,depth)):
            idx_tree+=1
            try:
                if(idx_ter<pset.terms_count):
                    term = pset.terminals[type_][idx_ter]
                    idx_ter+=1
                else:
                    continue
            except IndexError:
                _, _, traceback = sys.exc_info()
            if isclass(term):
                term = term()
            expr.append(term)
        # make primitive node
        else:
            idx_tree+=1
            try:
                if(idx_pri<pset.prims_count):
                    prim = pset.primitives[type_][idx_pri]
                    idx_pri+=1
                else:
                    continue
            except IndexError:
                _, _, traceback = sys.exc_info()
            expr.append(prim)
            for arg in reversed(prim.args):
                stack.append((depth + 1, arg))
    return expr

def genFull(pset, min_, max_, type_=None):
    """Generate an expression where each leaf has the same depth
    between *min* and *max*.

    :param pset: Primitive set from which primitives are selected.
    :param min_: Minimum height of the produced trees.
    :param max_: Maximum Height of the produced trees.
    :param type_: The type that should return the tree when called, when
                  :obj:`None` (default) the type of :pset: (pset.ret)
                  is assumed.
    :returns: A full tree with all leaves at the same depth.
    """

    def condition(height, depth):
        """Expression generation stops when the depth is equal to height."""
        return depth == height

    return generate(pset, min_, max_, condition, type_)

def compile(expr, pset):
    """Compile the expression *expr*.

    :param expr: Expression to compile. It can either be a PrimitiveTree,
                 a string of Python code or any object that when
                 converted into string produced a valid Python code
                 expression.
    :param pset: Primitive set against which the expression is compile.
    :returns: a function if the primitive set has 1 or more arguments,
              or return the results produced by evaluating the tree.
    """
    code = str(expr)
    print("code\n",code)
    if len(pset.arguments) > 0:
        # This section is a stripped version of the lambdify
        # function of SymPy 0.6.6.
        args = ",".join(arg for arg in pset.arguments)
        print("args\n",args)
        code = "lambda {args}: {code}".format(args=args, code=code)
        print("code\n",code)

    print("eval(code, pset.context, )\n",eval(code, pset.context, {}))
    return eval(code, pset.context, {})
    
pset = gp.PrimitiveSet("MAIN", 0)

tree_arr=[]

psetStack=astToStack.getStack(json_data)
makePset(psetStack)

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("expr", genFull, pset=pset, min_=2, max_=4)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("compile", compile, pset=pset)

def evalFunc(individual):
    indivStack=[]
    for i in range(individual.__len__()):
        tmpList=[]
        tmpList.append(individual[i].info)
        tmpList.append(individual[i].arity)
        indivStack.append(tmpList)
    print(indivStack)
    print("break")
    return 0,

toolbox.register("evaluate", evalFunc)
toolbox.register("select", tools.selTournament, tournsize=7)
toolbox.register("mate", gp.cxOnePoint)
toolbox.register("expr_mut", gp.genGrow, min_=0, max_=2)
toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)

def main():
#    random.seed(10)
    pop = toolbox.population(n=1)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)
    
    algorithms.eaSimple(pop, toolbox, 0.8, 0.1, 4, stats, halloffame=hof)
    
    return pop, stats, hof

if __name__ == "__main__":
    main()