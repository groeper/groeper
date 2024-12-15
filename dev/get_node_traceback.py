
import os
import sys
import shutil

#######################################################################################
def aliasfile(inlist):
	outlist = []
	foo = 0
	endfoo = len(inlist)
	while foo < endfoo:
		if inlist[foo].find("<Nodes>") > -1:
			#print(f"Before /Nodes foo = {foo}")
			outlist.append(inlist[foo])
			outlist.append("__NODES__\n")
			while inlist[foo].find("</Nodes>") == -1:
				foo += 1
			#print(f"After /Nodes foo = {foo}")
		if inlist[foo].find("<Connections>") > -1:
			#print(f"Before /Connections foo = {foo}")
			outlist.append(inlist[foo])
			outlist.append("__CONNECTIONS__\n")
			while inlist[foo].find("</Connections>") == -1:
				foo += 1
			#print(f"After /Connections foo = {foo}")
		outlist.append(inlist[foo])
		foo += 1
	return "".join(s for s in outlist)

#######################################################################################
#######################################################################################
if len(sys.argv) != 3:
	print(f"Usage: {os.path.basename(sys.argv[0])}: <alteryx workflow name>  <toolid>")
	exit()

file = sys.argv[1]
endnode = int(sys.argv[2])

if not os.path.isfile(file):
	print(f" File {file} does not exist")
	exit(1)

(filename, ext) = os.path.splitext(sys.argv[1])

outfile = ""
nodelist = []
outnodelist = [endnode]
connections = []


with open (file, "r", encoding="utf-8") as f:
	contents = f.readlines()

# get list of all nodes and connections

for foo in range(len(contents)):
	line = contents[foo]
	#if line.find('<Node ToolID') > -1:
	#	asp = line.split('"')
	#	nodelist.append(int(asp[1]))
	if line.find('<Connections') > -1:
		inputtool = 0
		destinationtool = 0
		foo += 1
		while line.find("</Connections") == -1:
			if line.find("<Connection") > -1:
				inputtool = int(contents[foo+1].split('"')[1])
				outputtool = int(contents[foo+2].split('"')[1])
				connections.append({'input':inputtool, 'output':outputtool, 'text':f"{contents[foo]}{contents[foo+1]}{contents[foo+2]}{contents[foo+3]}"})
			foo += 1
			line = contents[foo]

# get connected nodes.  loop until no more are found
savelength = 0
counter = 0
while savelength != len(outnodelist):
	savelength = len(outnodelist)
	for bar in outnodelist:
		counter += 1
		for foo in connections:
			if foo['output'] == bar:
				if foo['input'] not in outnodelist:
					outnodelist.append(foo['input'] )

# go back and get the related nodes
nodes = ""
for foo in range(len(contents)):
	line = contents[foo]
	if line.find('<Node ToolID') > -1:
		asp = line.split('"')
		thisnode = int(asp[1])
		if thisnode in outnodelist:
			while line.find("</Node") == -1:
				nodes += line
				foo += 1
				line = contents[foo]
			nodes += line

# write the connections
connection_string = ""
for foo in outnodelist:
	for bar in connections:
		if bar['output'] == foo:
			connection_string += bar['text']

ot = aliasfile(contents)

with open(f"path_to_{sys.argv[2]}.yxmd", "w") as f:
	f.writelines(ot.replace("__NODES__",nodes).replace("__CONNECTIONS__",connection_string))
print(f"Wrote file path_to_{sys.argv[2]}.yxmd")
