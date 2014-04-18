#!/bin/python

import re
import sys

white = " |\n"
white = re.compile(white)

end = "(\)?(\.|,)?$)"
ismath = """((.+\(.*\).*)|(\\\\.+)|(.+(_|\^).+)|(.*\|.*)|([A-Za-z0-9]'+))""" + end 
isatex = re.compile(ismath)

isintermediate = """(\d+|[A-Z]|[a-z]|\+|-|=|:|,)""" + end

arrows = dict()
arrows[' -> '] = " \\\\rightarrow "
arrows[' => '] = " \\\\Rightarrow "
arrows[' <- '] = " \\\\leftarrow "
arrows[' <= '] = " \\\\Leftarrow "
arrows[' \\\\forall '] = " \\\\, \\\\forall \\\\, "
arrows[' \\\\exists '] = " \\\\, \\\\exists \\\\, "

for line in open(sys.argv[1]):
  
  # special treatment for arrows
  for arrow in arrows:
    line = re.sub(arrow, arrows[arrow], line)

  # split and fix braces
  splittedraw = re.split(white, line)
  splitted = []
  nopen = 0
  for i in range(len(splittedraw)):
    if nopen > 0:
      splitted[-1] = splitted[-1] + " " + splittedraw[i]
    else:
      splitted = splitted + [splittedraw[i]]
      
    nopen += splittedraw[i].count("{")
    nopen -= splittedraw[i].count("}")    

  # detect latex on the first level
  tokenismath = [re.match(ismath, token) for token in splitted]
      
  # merge if necessary
  tokenisintermediate = [None for token in tokenismath]
  for i in range(len(tokenisintermediate)):
    if (not tokenismath[i]) and ((i < len(tokenismath)-1 and tokenismath[i+1]) or (i > 0 and tokenismath[i-1])):
      tokenisintermediate[i] = re.match(isintermediate, splitted[i])
      
  # an ugly version of a componentwise or
  for i in range(len(tokenismath)):
    if tokenismath[i] or tokenisintermediate[i]:
      tokenismath[i] = 1
    
  # print with math signs
  splitted = [token + " " for token in splitted]
  
  if all(tokenismath):
    print("\\[".join(splitted).join("\\]")) # display
    
  else: # inline math
    
    if tokenismath[0]:
      splitted[0] = "$" + splitted[0]
    if tokenismath[-1]:
      splitted[-1] = "$" + splitted[-1]
      
    for i in range(1,len(splitted)):
      if not tokenismath[i-1] and tokenismath[i]:
        splitted[i] = "$" + splitted[i]
      if tokenismath[i-1] and not tokenismath[i]:
        splitted[i] = "$ " + splitted[i]

    print("".join(splitted))

    