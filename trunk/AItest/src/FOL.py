
import sys
from Expr import *
from utils import issequence, find_if


# allowing tracing steps
trace= True

"""
-------------------------------------------------------------
Clause Form
------------------------------------------------------------
"""

def unify(x, y, s={}):
    """Unify expressions x,y with substitution s; return a substitution that
    would make x,y equal, or None if x,y can not unify. x and y can be
    variables (e.g. Expr('x')), constants, lists, or Exprs. [Fig. 9.1]
    >>> unify(P(x,y), P(a,b), {})
    {y: b, x: a}
    """
    if trace: print 'exp1:',x,' exp2:',y,' mu = ',s,'\n'
    if s == None:
        return None
    elif x == y:
        return s
    # if any of therm is variable unify it with it's correspondent
    elif is_variable(x):
        return unify_var(x, y, s)
    elif is_variable(y):
        return unify_var(y, x, s)
    #if they are expression
    elif isinstance(x, Expr) and isinstance(y, Expr):
        return unify(x.args, y.args, unify(x.op, y.op, s))
    # if atom
    elif isinstance(x, str) or isinstance(y, str) or not x or not y:
        return s if x == y else None
    # continue unification
    elif issequence(x) and issequence(y) and len(x) == len(y):
        return unify(x[1:], y[1:], unify(x[0], y[0], s))
    else:
        return None

def unify_var(var, x, s): 
    # if the variable in our mu
    if var in s:  
        return unify(s[var], x, s)
    else:
        # if not just substitute it 
        t= subst(x,s)
        if occur_check(var, t) :
            return None
        else:
            # if every thing ok add it to mu
            return extend(s, var, t)


def occur_check(var, x):
    """
    Return true if var occurs anywhere in x.
    """    
    # if both are equal
    if var == x:
        return True
    #if they are not and one the operands are equal or it's in occures in its variables 
    elif isinstance(x, Expr):
        return var.op == x.op or occur_check(var, x.args)
    # if it's list of arguments check every one
    elif not isinstance(x, str) and issequence(x):
        for xi in x:
            if occur_check(var, xi): return True
    return False


def extend(s, var, val):
    """Copy the substitution s and extend it by setting var to val; return copy.
    >>> extend({x: 1}, y, 2)
    {y: 2, x: 1}
    """
    s2 = s.copy()
    s2[var] = val
    # fix previous substitution 
    s2=dict(map(lambda ex: (ex,subst(s2[ex],s2)),s2))
    return s2


def subst(sentence, dic):
    """Substitute the substitution s into the expression x.
    >>> subst(expr('P(x,f(x),y,z)'),{x:c,y:g(u)})
    'P(c,f(c),g(u),z)'
    """
    # if not expr return it
    if not isinstance(sentence, Expr):
        return sentence
    # if variable check if it has substitution
    elif is_var_symbol(sentence.op) :
        if sentence in dic:
            return dic[sentence]
    #otherwise try to substitute in arguments
    return Expr(sentence.op, *[subst(a, dic) for a in sentence.args])



"""
-------------------------------------------------------------
Clause Form
------------------------------------------------------------
"""


def to_clause_form(s,trace= False):
    # convert to cnf first
    s = to_cnf(s, trace)
    
    s = cnf_to_clauses(s)
    if trace: print '\nStep 9:(to Clause form)\n',s
    
    s= clause_form_standardize_apart(s)
    if trace: print '\nStep 10:(Clause form renaming)\n',s,'\n\nFinal Result:'
    return s
    
#-------------CNF---------------------------

def to_cnf(s, trace = False):
    """Convert a propositional logical sentence s to conjunctive normal form.
    That is, of the form ((A | ~B | ...) & (B | C | ...) & ...) [p. 215]
    >>> to_cnf("~(B|C)")
    (~B & ~C)
    >>> to_cnf("B <=> (P1|P2)")
    ((~P1 | B) & (~P2 | B) & (P1 | P2 | ~B))
    >>> to_cnf("a | (b & c) | d")
    ((b | a | d) & (c | a | d))
    >>> to_cnf("A & (B | (D & E))")
    (A & (D | B) & (E | B))
    """
    if isinstance(s, str): s = expr(s)
    if trace: print '\nOriginal:\n',s
    
    s= eliminate_equivalence(s) # Step 1
    if trace: print '\nStep 1:(Eliminate Equivalence)\n',s
    
    s = eliminate_implications(s) # Steps 2
    if trace: print '\nStep 2:(Eliminate Implication)\n',s
    
    s = move_not_inwards(s) # Step 3
    if trace: print '\nStep 3:(Move not inwards)\n',s
    
    s = standardize_apart(s) # Step 4
    if trace: print '\nStep 4:(Standardize apart)\n',s
    
    s = skolemize(s) # Step 5
    if trace: print '\nStep 5:(Skolemize)\n',s
    
    s = eliminate_for_All(s) # Step 6
    if trace: print '\nStep 6:(Eliminate for all)\n',s
    
    s = distribute_and_over_or(s) # Step 7,8
    if trace: print '\nStep 7,8:(Distribute And over Or and flatten)\n',s
     
    return s 

    
def eliminate_equivalence(s):
    """
    step 1: remove equivalence
    """
    # in case of for all and exist go inside it
    if not s.args or (is_symbol(s.op) and s.op != 'All' and s.op != 'Exists') : return s     ## (Atoms are unchanged.)
    args = map(eliminate_equivalence, s.args)
    a, b = args[0], args[-1]
    # if equal separate it
    if s.op == '<=>':
        return (a >> b) & (b >> a)
    else:
        return Expr(s.op, *args)


def eliminate_implications(s):
    """
    step 2: remove implication
    
    Change >>, <<into &, |, and ~. That is, return an Expr
    that is equivalent to s, but has only &, |, and ~ as logical operators.
    >>> eliminate_implications(A >> (~B << C))
    ((~B | ~C) | ~A)
    """
    
    if not s.args or (is_symbol(s.op) and s.op != 'All' and s.op != 'Exists') : return s     ## (Atoms are unchanged.)
    args = map(eliminate_implications, s.args)
    a, b = args[0], args[-1]
    if s.op == '>>':
        return (b | ~a)
    elif s.op == '<<':
        return (a | ~b)
    else:
        return Expr(s.op, *args)

    
def move_not_inwards(s):
    """
         Step 3: Push not inwards for a given expression s
    """
    """   
    If I had a not operator, I make a function NOT to move the not into all the 
    expression (called b). 
    We take the first argument of the expression.
    We check on its operator as follows:
    
    if operator = 'All'
        then we return a Nary expression by distributing the Exists on the first argument 
        of the All and the not of the second argument. We do that, since the first argument
        of the All is the quantifying variable, while the 2nd argument is the expression
        quantified. We distribute the Exists since the inverse of All is Exists.
    if operator = 'Exists'
        then we return a Nary expression by distributing the All on the first argument 
        of the Exists and the not of the second argument. We do that, since the first argument
        of the Exists is the quantifying variable, while the 2nd argument is the expression
        quantified. We distribute the All since the inverse of Exists is All.
    if operator = '~'
        then we return the argument itself since ~~A = A
    if operator = '&'
        then we return a Nary expression by distributing the | on the list of arguments of a
    if operator = '|'
        then we return a Nary expression by distributing the & on the list of arguments of a
        
    if the operator is a symbol or s.args is false
        then we check if the the one of our reserved operators (All or Exists), then
        we return an Expression with the operator and mapping the NOT on the rest of 
        the expression. This is done to push a not inwards for an expression that has 
        already a not inside All. On the other hand, if is a normal operator, we return the 
        expression s, reaching a base case.
    
    if the operator is not a symbol
        We again return an Expression with the operator and mapping the NOT function
        on the arguments of this given expression.
     
   """
    if s.op == '~':
        NOT = lambda b: move_not_inwards(~b)
        a = s.args[0]
     
        if a.op =='All': 
            return NaryExpr('Exists', *[a.args[0], NOT(a.args[1])])
        
        if a.op =='Exists': 
            return NaryExpr('All', *[a.args[0], NOT(a.args[1])])

        if a.op == '~': 
            return move_not_inwards(a.args[0]) # ~~A ==> A
        if a.op =='&': 
            return NaryExpr('|', *map(NOT, a.args))
        if a.op =='|':
            return NaryExpr('&', *map(NOT, a.args))
        return s
    elif (is_symbol(s.op) or not s.args):
        if s.op == 'All' or s.op == 'Exists':
            return Expr(s.op, *map(move_not_inwards, s.args))
        else:
            return s
    else:
        return Expr(s.op, *map(move_not_inwards, s.args))   


def standardize_apart(s,dic={}):
    """
    step 4: Rename variables
    """
    #when hitting exist or all rename its variable and add it to dictionary 
    if is_symbol(s.op) and (s.op == 'All' or s.op == 'Exists'):        
        if s.args[0] in dic:
            standardize_apart.counter += 1
            dic[s.args[0]] = Expr('s%d' % standardize_apart.counter)
        else:
            dic[s.args[0]]= s.args[0]
        return Expr(s.op, *[standardize_apart(a, dic) for a in s.args]) 
    #if it hits variable it subst it from dictionary if it's exists
    if is_variable(s):
        if s in dic:
            return dic[s]
        else:
            return s
    else:
        # otherwise continue recursion
        return Expr(s.op, *[standardize_apart(a, dic) for a in s.args])

standardize_apart.counter = 0
    


def skolemize(s,qun=[],dic={}):
    """
    step 5: Removing Exists operator
    """
    if is_symbol(s.op) and s.op == 'All':#if it's for all save the var to add to function argument
        qun2=qun[:]
        qun2.append(s.args[0])
        return Expr(s.op,*[s.args[0],skolemize(s.args[1],qun2,dic)])
    if  is_symbol(s.op) and s.op == 'Exists':# if it's there exists add new substitution for this var to dic 
        if qun!=[]:# if it was in expression of 1 or more for all
            skolemize.__functionsCount+=1
            f=  Expr('f%d' % skolemize.__functionsCount)
        else:# if it is not in for all 
            skolemize.__varscount+=1
            f=  Expr('z%d' % skolemize.__varscount)
        dict2=dic.copy()
        dict2[s.args[0]]=Expr(f.op,*qun)
        return skolemize(s.args[1], qun,dict2)
    if is_variable(s):# if variable substitute 
        if s in dic:
            return dic[s]
        else: 
            return s
    else:#otherwise continue with args 
        return Expr(s.op,*map(lambda x: skolemize(x,qun,dic),s.args))
# counters to make functions and vars unique          
skolemize.__varscount=0
skolemize.__functionsCount=0


def eliminate_for_All (s):
    """
    step 6: Eliminates All operator for a given expression s 
    """
    """
        First we check if the operator is a symbol or the s.args = false, and finally
        the operator is not the All reserved operator, then we return s.
        
        Then we map our method on all the arguments of s and store it in the args variable.
        If we find that the operator is All we return b which is the args[n-1], where n 
        is the size of the list. Hence, leaving all except the All operator.
        Else
            We return an expression with the current operator and the args produced
            from mapping our function on the current arguments of the given expression.
        
    """
    
    if (not s.args or is_symbol(s.op)) and not s.op == 'All': 
        return s     ## (Atoms are unchanged.)
    
    args = map(eliminate_for_All, s.args)
    b = args[-1]
    
    if s.op == 'All':
        return b
    else:
        return Expr(s.op, *args)


def distribute_and_over_or(s):
    """
    step 7,8: distribute and over or and flatten
    
    Given a sentence s consisting of conjunctions and disjunctions
    of literals, return an equivalent sentence in CNF.
    >>> distribute_and_over_or((A & B) | C)
    ((A | C) & (B | C))
    """
    
    """
    This methods checks on the operators of the given expression.
    
    If the operator is |:
        It get an expression by distributing the | on the arguments of s.
        Then it check if the args of s are zero then it return false, but if one it 
        returns the result of the distribution on that argument.
        Then it checks if any of the arguments of s has & as an operator. If not, then 
        it returns just the | operator distributed on the given expression. Otherwise,
        it makes another list of arguments that are not in the conjuncts list. 
        Then, it checks if the length of this other list is 0, it returns the argument 
        it has. However, if it has more arguments, it distributes the | on the othersList.
        Afterwards, it return a nary expression of distributing the & on the list
        of applying this method on the | between the conjuncts and the rest without
        conjuncts and has all |.
        
     If the operator is &:
         Simply, it returns the nary expression of distributing the & on the list
         produced from applying our method on the rest of the args of the given expression
         s
      If the operator is neither & nor |:
          Therefore, we hit a base case and we return the given expression in a
          sum of products fashion.
    """   
    if s.op == '|':
        s = NaryExpr('|', *s.args)
        if len(s.args) == 0:
            return FALSE
        if len(s.args) == 1:
            return distribute_and_over_or(s.args[0])
        conj = find_if((lambda d: d.op == '&'), s.args)
        if not conj:
            return NaryExpr(s.op, *s.args)
        others = [a for a in s.args if a is not conj]
        if len(others) == 1:
            rest = others[0]
        else:
            rest = NaryExpr('|', *others)
        return NaryExpr('&', *map(distribute_and_over_or,
                                  [(c|rest) for c in conj.args]))
    elif s.op == '&':
        return NaryExpr('&', *map(distribute_and_over_or, s.args))
    else:
        return s


def NaryExpr(op, *args):
    """Create an Expr, but with an nary, associative op, so we can promote
    nested instances of the same op up to the top level.
    >>> NaryExpr('&', (A&B),(B|C),(B&C))
    (A & B & (B | C) & B & C)
    
    We loop on the given arguments, then we check if the operator passed is equal
    to the current operator, but the argument operator is neither Exists or All, 
    we add to the argList the arguments of the current argument. We check that it
    is neither All nor Exist since we don't want to lose the quantifier variables.
    
    Otherwise, we append the argument onto the argList.
    
    Then after finishing the loop, we check if the argument is just one, then we return it.
    If the length of arguments if zero, we return one of our reserved logic values 
    either True of False in our project (+ & * are not used).
    
    If neither of both cases, we return an expression with the operator and list of arguments
    collected from the loop and this class 
    returns an expression with N-ary (0 or more args) expression. 
    
    It is explained there how it is done that. 
    
    """
    arglist = []
    for arg in args:
        if arg.op == op and not arg.op == 'Exists' and not arg.op == 'All': 
            arglist.extend(arg.args)
        else:            
            arglist.append(arg)
    if len(args) == 1:
        return args[0]
    elif len(args) == 0:
        return _NaryExprTable[op]
    else:
        return Expr(op, *arglist)    

_NaryExprTable = {'&':TRUE, '|':FALSE, '+':ZERO, '*':ONE}



def cnf_to_clauses(s):
    """
    step 9: listify disjunctions
    Return a list of the disjuncts in the sentence s.
    >>> disjuncts(A | B)
    [A, B]
    >>> disjuncts(A & B)
    [(A & B)]
    """
    # if and go to next depth
    if isinstance(s, Expr) and s.op == '&':
        return map(lambda x:disjuncts_to_clauses(x),s.args)
    else:
        return [disjuncts_to_clauses(s)]
       
    
    
def disjuncts_to_clauses(s):
    """
    step 10: listify conjunctions
    Return a list of the conjuncts in the sentence s.
    >>> conjuncts(A & B)
    [A, B]
    >>> conjuncts(A | B)
    [(A | B)]
    """
    if isinstance(s, Expr) and s.op == '|':
        return s.args
    else:
        return [s]

def clause_form_standardize_apart(cf):   
    """
    Step 11: rename the variable in each clause such the same name does not appear in to clauses
    """ 
    #output list
    out_clause=[]
    #collect variable used in previous clauses to rename the repeated only 
    global_dic=[]
    #loop on conjunctions clauses
    for dis in cf:
        # initialize local dictionary for each disjunction clause
        local_dic={}  
        # call rename on each expr in disjunction clauses
        out_clause.append( map(lambda exp: rename(exp,local_dic,global_dic),dis))
    return out_clause

def rename(exp,local_dic,global_dic):
    """
    renaming helper for each expr
    """
    # if it is variable 
    if is_variable(exp):
        # if it's not in the local dict define it to be used
        if not exp in local_dic:
            # if it's in the local dict define ne variable name
            if exp in global_dic:
                rename.count+=1
                local_dic[exp]=Expr('x%d' % rename.count)
            else:
            # not in global so we can use the original variable name
                global_dic.append(exp)
                local_dic[exp]=exp
        return local_dic[exp] 
    else:
        # if it's not a var but symbol predicate or function apply rename on functions
        return Expr(exp.op,*[rename(a, local_dic,global_dic) for a in exp.args])
    
    
            
rename.count=0

"""
Main Method to run from Terminal
"""
if __name__== '__main__':
    if len(sys.argv)>2:
        if sys.argv[1] == 'unify':
            exp1=expr(sys.argv[2])
            exp2=expr(sys.argv[3])
            trace = True if int(sys.argv[4])==1 else False
            print '\n',unify(exp1,exp2,{})
        elif sys.argv[1] == 'toClause':
            exp1=expr(sys.argv[2])
            trace = True if int(sys.argv[3])==1 else False
            print '\nmu=',to_clause_form(exp1, trace)
    else:
        print '\nTo run from terminal input should be'
        print '[\'unify\'] \'exp1\' \'exp2\' [0 or 1 for trace] '
        print '[\'toClause\'] \'exp1\' [0 or 1 for trace] \n\n'
        
 
#------------------------------------------------------------------------------------------------------   

'''
TESTING Codes
'''

"""
to set the trace mode
"""
trace=True 

#===============================================================================
#===============================================================================
#--------- Unify Testing------------------------ 
#===============================================================================
#===============================================================================

m=expr('P(x,g(x),g(f(a)))')
n=expr('P(f(u),v,v)')
f= unify(m, n, {})
print m,n, f,'\n'

m=expr('P(a,y,f(y))')
n=expr('P(z,z,u)')
f= unify(m, n, {})
print m,n,f,'\n'

m = expr('P(x,g(x),x)')
n = expr('P(g(u),g(g(z)),z)')
f= unify(m, n, {})
print  m,n,f,'\n'


#testing skolemize
#e=expr('All(i,All(z,Exists(x ,R(i) & Exists(y,P(x,y,z)))) | Exists(y,Q(y) &E(i))) & Exists(x,Exists(y,M(x,y))) | Exists(x,All(y,M(x,y))&All(y,P(x,y)))')
#e=expr('All(x,R(x)&Exists(h,G(h,x)))|Exists(h,T(h,x))')
#
#print standardize_apart(e,{}) 
#print skolemize(e)
#
#le=expr('All(x,P(x)<=>(Q(x)|Exists(y,Q(y)&R(y,x))))')
#print to_clause_form(le,True)
#
##print expr('Q(x) ==> P(x)')
##y2= expr('x ==> y')
##h= expr('z ==> l')


#
#f= unify(m, n, {})
#print m,n,f
#
#m=expr('P(x,g(x),g(f(a)))')
#n=expr('P(f(u),v,v)')
#
#f= unify(m, n, {})
#print m,n, f
##
##m=expr('P(a,y,f(y))')
##n=expr('P(z,z,u)')
#
##f= unify(m, n, {})
##print m,n,f
#
#
#m = expr('P(x,g(x),x)')
#n = expr('P(g(u),g(g(z)),z)')
##
#f= unify(m, n)
#print m,n,f
##
###print f[z]
#m = expr('P(x)')
#n = expr('P(f(x))')
##print m.args
##
#f= unify(m, n, {})
#print m,n,f
#
#m=expr('Q(y,g(A,B))')
#n=expr('Q(g(x,x),y)')
##
#f= unify(m, n, {})
#print m,n,f
##
##d= unify(y2, h, {})
##print d
##print d[y]
##print x
##
#
##===============================================================================
##===============================================================================
##---------CNF Testing------------------------ 
##===============================================================================
##===============================================================================

le=expr('Exists(x,P(x) & All(x,Q(x)>>~P(x)))')
print to_clause_form(le,trace),'\n'

m = expr('All(x,P(x)<=>(Q(x) & Exists(y,Q(y) & R(y,x))))')
print to_clause_form(m, trace),'\n'

##m = expr('x <=> y')
##
##n = to_cnf(m)
##
##print 'CNF: ', n 
#
##m = expr ('All(x, B(x) <=> Q(x))')
##
##print m
##print to_clause_form(m, True)
#
##===============================================================================
## Taken from: Working right! 
## http://www.csupomona.edu/~jrfisher/www/prolog_tutorial/logic_topics/normal_forms/normal_form.html
##===============================================================================
##n = expr ('All(x, P(x) | Q(x)) >> Exists(y, R(x, y))')
##
##print to_clause_form(n)
#
##===============================================================================
## Taken from: Working wrong! > Bug in move not inwards 
## https://docs.google.com/viewer?url=http%3A%2F%2Fwww.cse.msstate.edu%2F~hansen%2Fclasses%2FAIspring04%2Fslides%2Fpredicatelogic.pdf
##===============================================================================
##l = expr ('All(x, (Pass(x, History) & Win (x, Lottery)) >> Happy(x))')
#
## Take care: you should not write the previous expression as:
##l = expr ('All(x, Pass(x, History) & Win (x, Lottery) >> Happy(x))')
#
##print to_clause_form(l, True)
#
##h  = expr (' ( P(x, A) & Q(x, B)) >> R(x)')
##
##n = to_cnf(h)
##
##print n 
#
##print to_clause_form(h, True)
##
##h  = expr (' All(x, ( P(x, A) & Q(x, B))  >> R(x))')
#
##print to_clause_form(h, True)
## BUG > Fixed
##print to_cnf(h)
#
## Expressions from the Project description
#
##m = expr ('Exists (x, (P(x) & All (x, Q(x) >> ~P(x) ) ) )')
##
##print to_cnf(m, True) #need to check the renaming?
##
##n = expr ('All (x, P(x) <=> (Q(x) & Exists (y, (Q(y) & R(y, x)))))')
##
##print to_clause_form(n, True)
#
##print to_cnf(n, True)
##
##
##g = expr ('~(All (x, All(y, P(x) | ~M(x, y) )))')
#
##print '\nExpression to negate: ', g
#
##print 'Expr of elimination: ', eliminate_for_All(g)
#
##m = expr ('~(All (x, All(y, P(x) | M(x, y) )))')
#
#
##notm = test2(m)
##notm = move_not_inwards(m)
#
#
##print 'Negation in For all: ', notm
#
#
##m = expr ('~(Exists (x, Exists(y, P(x) | M(x, y) )))')
##print '\nExpression to negate: ', m
##notm = move_not_inwards(m)
##
##print 'Negation in There Exists: ', notm
##
##m = expr ('~(Exists (x, All(y, P(x) | M(x, y) )))')
##print '\nExpression to negate: ', m
##notm = move_not_inwards(m)
##
##print 'Negation in There Exists with For all: ', notm
#
##m = expr ('Exists(x,(P(x)&Q(y))>>R(x))')
#
##print 'Removing negation: ', test3_h(notm)
#
##h = eliminate_for_All(m)
#
##print to_clause_form(m,True)
#
##print eliminate_for_All(m)
#
#
##print expr('ForAll x');
#
##m=expr('Q(y,g(A,B))')
##n=expr('Q(g(x,x),y)')
##
##f= unify(m, n, {})
##print m,n,f
##
##d= unify(y2, h, {})
##print d
##print d[y]
##print x
##
