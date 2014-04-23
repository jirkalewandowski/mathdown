#!/bin/python

import re
import sys

# TOKENTYPES:
UNKNOWN = -1
SPLIT = 0
PRESERVEMATH = 1
DETECTEDMATH = 2
DELETE = 3
INTERMEDIATE = 4

# REGEXPS:
splitat = "(\s+|\n|\.)"
splitat = re.compile(splitat)

dollar = re.compile("(?:(?:[^\\\\]|^)(\\$+))")

beginpreservemath = "(?:\\\\begin\\{((align)|(equation))\\*?\\})|(```.*)|(?:\\\\\\[)|(?:\\\\begin\\{(display)?math\\})|(?:\\\\begin\\{displaymath\\})"
endpreservemath = "(?:\\\\end\\{((align)|(equation))\\*?\\})|(```)|(?:\\\\\\])|(?:\\\\end\\{(display)math\\})|(?:\\\\end\\{displaymath\\})"
beginpreservemath = re.compile(beginpreservemath)
endpreservemath = re.compile(endpreservemath)

end = "(\)?(\.|,)?$)"
ismath = """((.+\(.*\).*)|(\\(?(\\\\[^\\$].*))|(.+(_|\^).+)|(.*\|.*)|([A-Za-z0-9]'+))""" + end 
isatex = re.compile(ismath)
isintermediate = """(\d+|[A-Z]|[a-z]|\+|-|=|:|,)""" + end
isintermediate = re.compile(isintermediate)

# DICTIONARY REPLACINGS:
repls = []
repls += [('~~>', "\\\\rightsquigarrow")]
repls += [('~>', "\\\\rightsquigarrow")]
repls += [('-->', "\\\\longrightarrow")]
repls += [('->', "\\\\rightarrow")]
repls += [('<--', "\\\\longleftarrow")]
repls += [('<-', "\\\\leftarrow")]
repls += [('<=', "\\\\Leftarrow")]
repls += [('=>', "\\\\Rightarrow")]
repls += [('\\\\forall', "\\\\, \\\\forall \\\\,")]
repls += [('\\\\exists', "\\\\, \\\\exists \\\\,")]

# read file
with open(sys.argv[1], 'r') as content_file:
  content = content_file.read()
  
# split
tokens = re.split(splitat, content)
tokentype = [SPLIT if re.match(splitat,token) else UNKNOWN for token in tokens]

# fix braces: merge some splits
nopen = 0
nhist = 0
for i in range(len(tokens)):
  if nopen > 0:
    nhist = nhist + 1
    tokentype[i] = DELETE
    tokens[i - nhist] = tokens[i - nhist] + tokens[i]
  else:
    nhist = 0
  nopen += tokens[i].count("{")
  nopen -= tokens[i].count("}")
tokens = [tokens[i] for i in range(len(tokens)) if not tokentype[i] == DELETE]
tokentype = [tokent for tokent in tokentype if not tokent == DELETE]

# preserve already marked math
nopen = 0
dollarisopen = 0
doubledollarisopen = 0
for i in range(len(tokens)):
  
  if nopen > 0 or dollarisopen or doubledollarisopen:
    tokentype[i] = PRESERVEMATH
  
  dollarlens = [len(x) for x in re.findall(dollar, tokens[i])]
  dollarisopen = (dollarisopen + len([x for x in dollarlens if x==1]))%2
  doubledollarisopen = (doubledollarisopen + len([x for x in dollarlens if x==2]))%2
  
  nopen += len(re.findall(beginpreservemath, tokens[i]))
  nopen -= len(re.findall(endpreservemath, tokens[i]))
  
  if nopen > 0 or dollarisopen or doubledollarisopen or len(dollarlens) > 0:
    tokentype[i] = PRESERVEMATH

# substitutions in non-preserved tokens
for i in range(len(tokens)):
  if tokentype[i] != PRESERVEMATH and tokentype[i] != SPLIT:
    for (a,b) in repls:
      tokens[i] = re.sub(a, b, tokens[i])

# detect math
for i in range(len(tokens)):
  if tokentype[i] != PRESERVEMATH and tokentype[i] != SPLIT:
    if re.match(ismath, tokens[i]):
      tokentype[i] = DETECTEDMATH
    elif re.match(isintermediate, tokens[i]):
      tokentype[i] = INTERMEDIATE
      
# classify intermediates according to context
for i in range(len(tokens)):
  if tokentype[i] == INTERMEDIATE:
    jl = i-1
    jr = i+1
    while jl >= 0 and tokentype[jl] == SPLIT:
      jl = jl - 1
    while jr < len(tokens) and tokentype[jr] == SPLIT:
      jr = jr + 1
    if tokentype[jl] == DETECTEDMATH or tokentype[jr] == DETECTEDMATH:
      tokentype[i] = DETECTEDMATH

# output and mark detected math
mathon = 0
for i in range(len(tokens)):
  if tokentype[i] == DETECTEDMATH:
    if mathon:
      print(tokens[i], end='')
    else:
      print('$' + tokens[i], end='')
      mathon = 1
    jr = i+1
    while jr < len(tokens) and tokentype[jr] == SPLIT:
      jr = jr + 1
    if tokentype[jr] != DETECTEDMATH:
      print("$", end='')
      mathon = 0
  else:
    print(tokens[i], end='')

    