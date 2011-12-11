

import re
#from utils import *
from utils import num_or_str,isnumber,issequence,if_,find_if



class Expr:
    """A symbolic mathematical expression.  We use this class for logical
    expressions, and for terms within logical expressions. In general, an
    Expr has an op (operator) and a list of args.  The op can be:
      Null-ary (no args) op:
        A number, representing the number itself.  (e.g. Expr(42) => 42)
        A symbol, representing a variable or constant (e.g. Expr('F') => F)
      Unary (1 arg) op:
        '~', '-', representing NOT, negation (e.g. Expr('~', Expr('P')) => ~P)
      Binary (2 arg) op:
        '>>', '<<', representing forward and backward implication
        '+', '-', '*', '/', '**', representing arithmetic operators
        '<', '>', '>=', '<=', representing comparison operators
        '<=>', '^', representing logical equality and XOR
      N-ary (0 or more args) op:
        '&', '|', representing conjunction and disjunction
        A symbol, representing a function term or FOL proposition

    Exprs can be constructed with operator overloading: if x and y are Exprs,
    then so are x + y and x & y, etc.  Also, if F and x are Exprs, then so is
    F(x); it works by overloading the __call__ method of the Expr F.  Note
    that in the Expr that is created by F(x), the op is the str 'F', not the
    Expr F.   See http://www.python.org/doc/current/ref/specialnames.html
    to learn more about operator overloading in Python.

    WARNING: x == y and x != y are NOT Exprs.  The reason is that we want
    to write code that tests 'if x == y:' and if x == y were the same
    as Expr('==', x, y), then the result would always be true; not what a
    programmer would expect.  But we still need to form Exprs representing
    equalities and disequalities.  We concentrate on logical equality (or
    equivalence) and logical disequality (or XOR).  You have 3 choices:
        (1) Expr('<=>', x, y) and Expr('^', x, y)
            Note that ^ is bitwose XOR in Python (and Java and C++)
        (2) expr('x <=> y') and expr('x =/= y').
            See the doc string for the function expr.
        (3) (x % y) and (x ^ y).
            It is very ugly to have (x % y) mean (x <=> y), but we need
            SOME operator to make (2) work, and this seems the best choice.

    WARNING: if x is an Expr, then so is x + 1, because the int 1 gets
    coerced to an Expr by the constructor.  But 1 + x is an error, because
    1 doesn't know how to add an Expr.  (Adding an __radd__ method to Expr
    wouldn't help, because int.__add__ is still called first.) Therefore,
    you should use Expr(1) + x instead, or ONE + x, or expr('1 + x').
    """

    def __init__(self, op, *args):
        "Op is a string or number; args are Exprs (or are coerced to Exprs)."
        assert isinstance(op, str) or (isnumber(op) and not args)
        self.op = num_or_str(op)
        self.args = map(expr, args) ## Coerce args to Exprs

    def __call__(self, *args):
        """Self must be a symbol with no args, such as Expr('F').  Create a new
        Expr with 'F' as op and the args as arguments."""
        assert is_symbol(self.op) and not self.args
        return Expr(self.op, *args)

    def __repr__(self):
        "Show something like 'P' or 'P(x, y)', or '~P' or '(P | Q | R)'"
        if len(self.args) == 0: # Constant or proposition with arity 0
            return str(self.op)
        elif is_symbol(self.op): # Functional or Propositional operator
            return '%s(%s)' % (self.op, ', '.join(map(repr, self.args)))
        elif len(self.args) == 1: # Prefix operator
            return self.op + repr(self.args[0])
        else: # Infix operator
            return '(%s)' % (' '+self.op+' ').join(map(repr, self.args))

    def __eq__(self, other):
        """x and y are equal iff their ops and args are equal."""
        return (other is self) or (isinstance(other, Expr)
            and self.op == other.op and self.args == other.args)

    def __hash__(self):
        "Need a hash method so Exprs can live in dicts."
        return hash(self.op) ^ hash(tuple(self.args))

    # See http://www.python.org/doc/current/lib/module-operator.html
    # Not implemented: not, abs, pos, concat, contains, *item, *slice
#    def __lt__(self, other):     return Expr('<',  self, other)
#    def __le__(self, other):     return Expr('<=', self, other)
#    def __ge__(self, other):     return Expr('>=', self, other)
#    def __gt__(self, other):     return Expr('>',  self, other)
#    def __add__(self, other):    return Expr('+',  self, other)
#    def __sub__(self, other):    return Expr('-',  self, other)
    def __and__(self, other):    return Expr('&',  self, other)
#    def __div__(self, other):    return Expr('/',  self, other)
#    def __truediv__(self, other):return Expr('/',  self, other)
    def __invert__(self):        return Expr('~',  self)
    def __lshift__(self, other): return Expr('<<', self, other)
    def __rshift__(self, other): return Expr('>>', self, other)
#    def __mul__(self, other):    return Expr('*',  self, other)
    def __neg__(self):           return Expr('-',  self)
    def __or__(self, other):     return Expr('|',  self, other)
#    def __pow__(self, other):    return Expr('**', self, other)
#    def __xor__(self, other):    return Expr('^',  self, other)
    def __mod__(self, other):    return Expr('<=>',  self, other) ## (x % y)



def expr(s):
    """Create an Expr representing a logic expression by parsing the input
    string. Symbols and numbers are automatically converted to Exprs.
    In addition you can use alternative spellings of these operators:
      'x ==> y'   parses as   (x >> y)    # Implication
      'x <== y'   parses as   (x << y)    # Reverse implication
      'x <=> y'   parses as   (x % y)     # Logical equivalence
      'x =/= y'   parses as   (x ^ y)     # Logical disequality (xor)
    But BE CAREFUL; precedence of implication is wrong. expr('P & Q ==> R & S')
    is ((P & (Q >> R)) & S); so you must use expr('(P & Q) ==> (R & S)').
    >>> expr('P <=> Q(1)')
    (P <=> Q(1))
    >>> expr('P & Q | ~R(x, F(x))')
    ((P & Q) | ~R(x, F(x)))
    """
    if isinstance(s, Expr): return s
    if isnumber(s): return Expr(s)
    ## Replace the alternative spellings of operators with canonical spellings
    s = s.replace('==>', '>>').replace('<==', '<<')
    s = s.replace('<=>', '%').replace('=/=', '^')
    ## Replace a symbol or number, such as 'P' with 'Expr("P")'
    s = re.sub(r'([a-zA-Z0-9_.]+)', r'Expr("\1")', s)
    ## Now eval the string.  (A security hole; do not use with an adversary.)
    return eval(s, {'Expr':Expr})

def is_symbol(s):
    "A string s is a symbol if it starts with an alphabetic char."
    return isinstance(s, str) and s[0].isalpha()

def is_var_symbol(s):
    "A logic variable symbol is an initial-lowercase string."
    return is_symbol(s) and s[0].islower()

def is_prop_symbol(s):
    """A proposition logic symbol is an initial-uppercase string other than
    TRUE or FALSE."""
    return is_symbol(s) and s[0].isupper() and s != 'TRUE' and s != 'FALSE'


## Useful constant Exprs used in examples and code:
TRUE, FALSE, ZERO, ONE, TWO = map(Expr, ['TRUE', 'FALSE', 0, 1, 2])
A, B, C, F, G, P, Q, x, y, z  = map(Expr, 'ABCFGPQxyz')




def unify(x, y, s):
    """Unify expressions x,y with substitution s; return a substitution that
    would make x,y equal, or None if x,y can not unify. x and y can be
    variables (e.g. Expr('x')), constants, lists, or Exprs. [Fig. 9.1]
    >>> unify(x + y, y + C, {})
    {y: C, x: y}
    """
    #print 'Taher: ', x
    if s == None:
        return None
    elif x == y:
        return s
    elif is_variable(x):
        return unify_var(x, y, s)
    elif is_variable(y):
        return unify_var(y, x, s)
    elif isinstance(x, Expr) and isinstance(y, Expr):
        return unify(x.args, y.args, unify(x.op, y.op, s))
    elif isinstance(x, str) or isinstance(y, str) or not x or not y:
        return if_(x == y, s, None)
    elif issequence(x) and issequence(y) and len(x) == len(y):
        return unify(x[1:], y[1:], unify(x[0], y[0], s))
    else:
        return None

def is_variable(x):
    "A variable is an Expr with no args and a lowercase symbol as the op."
    return isinstance(x, Expr) and not x.args and is_var_symbol(x.op)


def unify_var(var, x, s):
    # h =  s[var]
    #print 'Hello', var
#    if(var in s):
#        h = s[var]
#        print 'hashas: ', h 
    if var in s:  #and not s[var]== var:
        return unify(s[var], x, s)
    elif occur_check(var, x) :
        return None
    else:
        return extend(s, var, x)


def occur_check(var, x):
    """
    Return true if var occurs anywhere in x.
    """    
    if var == x:
        return True
    elif isinstance(x, Expr):
        return var.op == x.op or occur_check(var, x.args)
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
    # substitute the variables in val with the values from s2
    t= subst(val,s2)
    # check if any substitution leads to a loop 
    for sub in s2:
        if occur_check(var, s2[sub]):
            if occur_check(sub, val):
                return None
    #insert t in s2
    s2[var] = t
    # fixing vlues of dict according to added sub
    s2=dict(map(lambda ex: (ex,subst(s2[ex],s2)),s2))
    return s2


def subst(sentence, dic):
    """Substitute the substitution s into the expression x.
    >>> subst(expr('P(x,f(x),y,z)'),{x:c,y:g(u)})
    'P(c,f(c),g(u),z)'
    """
    #print sentence.op, sentence.args, 'dict:',dic
    if not isinstance(sentence, Expr):
        return sentence
    elif is_var_symbol(sentence.op) :#or isinstance(sentence.op, str):
        if sentence in dic:
            #print 'in dict', sentence,dic[sentence] 
            return dic[sentence]
    return Expr(sentence.op, *[subst(a, dic) for a in sentence.args])



#def standardize_apart(sentence, dic):
#    """Replace all the variables in sentence with new variables."""
#    if not isinstance(sentence, Expr):
#        print 'here'
#        return sentence
#    elif is_var_symbol(sentence.op):
#        if sentence in dic:
#            return dic[sentence]
#        else:
#            standardize_apart.counter += 1
#            dic[sentence] = Expr('V_%d' % standardize_apart.counter)
#            return dic[sentence]
#    else:
#        return Expr(sentence.op, *[standardize_apart(a, dic) for a in sentence.args])
#
#standardize_apart.counter = 0

#x=expr('x')
#s3={}
#s3[x]=expr('c')
#print subst(expr('P(x,f(g(x)),f(v))'), s3)
#print expr('Q(x) ==> P(x)')
#y2= expr('x ==> y')
#h= expr('z ==> l')
#
#m=expr('P(x,g(x),g(f(a)))')
#n=expr('P(f(u),v,v)')
#
#f= unify(m, n, {})
#print m,n, f
#
#m=expr('P(a,y,f(y))')
#n=expr('P(z,z,u)')

#f= unify(m, n, {})
#print m,n,f


#m = expr('P(x,g(x),x)')
#n = expr('P(g(u),g(g(z)),z)')
#
#f= unify(m, n, {})
#print m,n,f
#
##print f[z]
#m = expr('P(x)')
#n = expr('P(f(x))')
#print m.args
#
#f= unify(m, n, {})
#print m,n,f

#m=expr('Q(y,g(A,B))')
#n=expr('Q(g(x,x),y)')
#
#f= unify(m, n, {})
#print m,n,f
#
#d= unify(y2, h, {})
#print d
#print d[y]
#print x
#




#-------------Clause Form---------------------------

def to_clause_form(s,trace= False):
    temp = to_cnf(s, trace)
    temp = disjuncts(temp)
    temp = conjuncts(temp)
    return temp
    
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
    if trace: print 'Original:\n',s
    
    s= eliminate_equivalence(s) # Step 1
    if trace: print 'Step 1:(Eliminate Equivalence)\n',s
    
    s = eliminate_implications(s) # Steps 2
    if trace: print 'Step 2:(Eliminate Implication)\n',s
    
    s = move_not_inwards(s) # Step 3
    if trace: print 'Step 3:(Move not inwards)\n',s
    
    s = standardize_apart(s) # Step 4
    if trace: print 'Step 4:(Standardize apart)\n',s
    
    s = skolemize(s) # Step 5
    if trace: print 'Step 5:(Skolemize)\n',s
    
    s = eliminate_for_All(s) # Step 6
    if trace: print 'Step 6:(Eliminate for all)\n',s
    
    s = distribute_and_over_or(s) # Step 7,8
    if trace: print 'Step 7,8:(Distribute And over Or and flatten)\n',s
    
    return s 



def eliminate_equivalence(s):
    """
    step 1: remove equivalence
    """
    #print 'just here', s.args
    if not s.args or (is_symbol(s.op) and s.op != 'All' and s.op != 'Exists') : return s     ## (Atoms are unchanged.)
    args = map(eliminate_equivalence, s.args)
    a, b = args[0], args[-1]
    #print s.op
    if s.op == '<=>':
        #print 'eq'
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
         step 3: push not inwards
    """
     
#    print '\n'
#    print 'Start!: ', s 
    if s.op == '~':
        NOT = lambda b: move_not_inwards(~b)
        a = s.args[0]
        
        if a.op =='All': 
            return NaryExpr('Exists', *[a.args[0], NOT(a.args[1])])
        
        if a.op =='Exists': 
            return NaryExpr('All', *[a.args[0], NOT(a.args[1])])

        if a.op == '~': 
#            print 'Hello from negation!'
            return move_not_inwards(a.args[0]) # ~~A ==> A
        if a.op =='&': 
#            print 'Hello from AND!'
            return NaryExpr('|', *map(NOT, a.args))
        if a.op =='|':
#            print 'Hello from OR!' 
            return NaryExpr('&', *map(NOT, a.args))
        return s
    elif (is_symbol(s.op) or not s.args):
#        print 'Hello from Base case!'
        return s
    else:
#        print 'Hello from unknown!'
        return Expr(s.op, *map(move_not_inwards, s.args))   


def standardize_apart(s,dic={}):
    """
    step 4: rename variables
    """
    if is_symbol(s.op) and (s.op == 'All' or s.op == 'Exists'):
        dictTemp=dic.copy()
        standardize_apart.counter += 1
        dictTemp[s.args[0]] = Expr('x_%d' % standardize_apart.counter)
        return Expr(s.op, *[standardize_apart(a, dictTemp) for a in s.args]) 
    elif is_variable(s.op):
        if s in dic:
            return dic[s]
        else:
            return s
    else:
        return Expr(s.op, *[standardize_apart(a, dic) for a in s.args])

standardize_apart.counter = 0
    


def skolemize(s,qun=[],dict={}):
    """
    step 5: to remove exist
    """
    #print s, qun , dict
#    if not isinstance(s, Expr):
#        return s
    if is_symbol(s.op) and s.op == 'All':#if it's for all save the var to add to function
        qun2=qun[:]
        qun2.append(s.args[0])
        return Expr(s.op,*[s.args[0],skolemize(s.args[1],qun2,dict)])
    if  is_symbol(s.op) and s.op == 'Exists':# if it's there exists add new substitution for this var to dict 
        if qun!=[]:
            skolemize.__functionsCount+=1
            f=  Expr('f_%d' % skolemize.__functionsCount)
        else:
            skolemize.__varscount+=1
            f=  Expr('v_%d' % skolemize.__varscount)
        dict2=dict.copy()
        dict2[s.args[0]]=Expr(f.op,*qun)
        return skolemize(s.args[1], qun,dict2)
    if is_variable(s):# if variable subsititute 
        if s in dict:
            return dict[s]
        else: 
            return s
    else:#otherwise continue with args 
        return Expr(s.op,*map(lambda x: skolemize(x,qun,dict),s.args))
# counters to make functions and vars unique          
skolemize.__varscount=0
skolemize.__functionsCount=0

#testing skolemize
e=expr('All(i,All(z,Exists(x ,R(i) & Exists(y,P(x,y,z)))) | Exists(y,Q(y) &E(i))) & Exists(x,Exists(y,M(x,y))) | Exists(y,M(x,y))')
#print e, e.op,e.args
#print e
#print standardize_apart(e) 
#print skolemize(e)



def eliminate_for_All (s):
    """
    step 6: elimenate For All 
    """
#    print 'All: ' , s.op
    
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
    step 7,8: distribute and over or and flaten
    
    Given a sentence s consisting of conjunctions and disjunctions
    of literals, return an equivalent sentence in CNF.
    >>> distribute_and_over_or((A & B) | C)
    ((A | C) & (B | C))
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



#Should be fixed to work like clause form
def disjuncts(s):
    """
    step 9: listify disjunctions
    Return a list of the disjuncts in the sentence s.
    >>> disjuncts(A | B)
    [A, B]
    >>> disjuncts(A & B)
    [(A & B)]
    """
    if isinstance(s, Expr) and s.op == '|':
        return s.args
    else:
        return [s]

def conjuncts(s):
    """
    step 10: listify conjunctions
    Return a list of the conjuncts in the sentence s.
    >>> conjuncts(A & B)
    [A, B]
    >>> conjuncts(A | B)
    [(A | B)]
    """
    if isinstance(s, Expr) and s.op == '&':
        return s.args
    else:
        return [s]


#print expr('Q(x) ==> P(x)')
#y2= expr('x ==> y')
#h= expr('z ==> l')
#
#m=expr('P(x,g(x),g(f(a)))')
#n=expr('P(f(u),v,v)')
#
#f= unify(m, n, {})
#print m,n, f
#
#m=expr('P(a,y,f(y))')
#n=expr('P(z,z,u)')
#
#f= unify(m, n, {})
#print m,n,f

#
#m = expr('P(x,g(x),x)')
#n = expr('P(g(u),g(g(z)),z)')
#print n.op, n.args
#f= unify(m, n, {})
#print m,n,f
#
##print f[z]
#m = expr('P(x)')
#n = expr('P(z)')
#print m.args
#
#f= unify(m, n, {})
#print m,n,f

#===============================================================================
#===============================================================================
#---------CNF Testing------------------------ 
#===============================================================================
#===============================================================================






#m = expr('x <=> y')
#
#n = to_cnf(m)
#
#print 'CNF: ', n 


      

m = expr ('All(x, B(x) <=> Q(x))')
#
#print m
#print to_clause_form(m, True)


#===============================================================================
# Taken from: Working right! 
# http://www.csupomona.edu/~jrfisher/www/prolog_tutorial/logic_topics/normal_forms/normal_form.html
#===============================================================================
n = expr ('All(x, P(x) | Q(x)) >> Exists(y, R(x, y))')

print to_clause_form(n, False)

#===============================================================================
# Taken from: Working wrong! > Bug in move not inwards 
# https://docs.google.com/viewer?url=http%3A%2F%2Fwww.cse.msstate.edu%2F~hansen%2Fclasses%2FAIspring04%2Fslides%2Fpredicatelogic.pdf
#===============================================================================
l = expr ('All(x, (Pass(x, History) & Win (x, Lottery)) >> Happy(x))')

# Take care: you should not write the previous expression as:
# l = expr ('All(x, Pass(x, History) & Win (x, Lottery) >> Happy(x))')

print to_clause_form(l, True)

#
#
#g = expr ('~(All (x, All(y, P(x) | ~M(x, y) )))')

#print '\nExpression to negate: ', g

#print 'Expr of elimination: ', eliminate_for_All(g)

#m = expr ('~(All (x, All(y, P(x) | M(x, y) )))')


#notm = test2(m)
#notm = move_not_inwards(m)


#print 'Negation in For all: ', notm


#m = expr ('~(Exists (x, Exists(y, P(x) | M(x, y) )))')
#print '\nExpression to negate: ', m
#notm = move_not_inwards(m)
#
#print 'Negation in There Exists: ', notm
#
#m = expr ('~(Exists (x, All(y, P(x) | M(x, y) )))')
#print '\nExpression to negate: ', m
#notm = move_not_inwards(m)
#
#print 'Negation in There Exists with For all: ', notm


#print 'Removing negation: ', test3_h(notm)

#h = eliminate_for_All(m)

#print to_cnf(h)



#print eliminate_for_All(m)


#print expr('ForAll x');

#m=expr('Q(y,g(A,B))')
#n=expr('Q(g(x,x),y)')
#
#f= unify(m, n, {})
#print m,n,f
#
#d= unify(y2, h, {})
#print d
#print d[y]
#print x
#
