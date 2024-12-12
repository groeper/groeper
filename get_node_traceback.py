
import os
import sys
import shutil

testnode = """        <Node ToolID="41">
          <GuiSettings Plugin="AlteryxBasePluginsGui.Formula.Formula">
            <Position x="1110" y="438" />
          </GuiSettings>
          <Properties>
            <Configuration>
              <FormulaFields>
                <FormulaField expression="IF [Contract Signed Date] &gt;= [Window Start Date] and [Contract Signed Date] &lt;= [Window End Date]&#xA;	then &quot;Contract signed during date window&quot;&#xA;ELSEIF [Contract Effective Start Date] &gt;= [Window Start Date] and [Contract Effective Start Date] &lt;= [Window End Date] &#xA;	then &quot;Contract Effective Start Date within date window&quot;&#xA;ELSEIF [Project End Date] &gt;= [Window Start Date] and [Project End Date] &lt;= [Window End Date]&#xA;	then &quot;Project End Date within date window&quot;&#xA;ELSE &quot;Project End Date outside of date window&quot;&#xA;ENDIF&#xA;&#xA;" field="Justification" size="1073741823" type="V_WString" />
              </FormulaFields>
            </Configuration>
            <Annotation DisplayMode="0">
              <Name />
              <DefaultAnnotationText>Justification = IF [Contract Signed Date] &gt;= [Window Start Date] and [Contract S...</DefaultAnnotationText>
              <Left value="False" />
            </Annotation>
          </Properties>
          <EngineSettings EngineDll="AlteryxBasePluginsEngine.dll" EngineDllEntryPoint="AlteryxFormula" />
        </Node>
"""
#######################################################################################
def alias_nodes(inlist):
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
		outlist.append(inlist[foo])
		foo += 1
	return outlist

#######################################################################################
def alias_connections(inlist):
	outlist = []
	foo = 0
	endfoo = len(inlist)
	while foo < endfoo:
		if inlist[foo].find("<Connections>") > -1:
			#print(f"Before /Connections foo = {foo}")
			outlist.append(inlist[foo])
			outlist.append("__CONNECTIONS__\n")
			while inlist[foo].find("</Connections>") == -1:
				foo += 1
			#print(f"After /Connections foo = {foo}")
		outlist.append(inlist[foo])
		foo += 1
	return outlist

#######################################################################################
def get_tag_contents(intag):
	return  intag.split(">")[1].split("<")[0]

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
outconnections = []

with open (file, "r", encoding="utf-8") as f:
	contents = f.readlines()

# get list of all nodes and connections
for foo in range(len(contents)):
	line = contents[foo]
	if line.find('<Node ToolID') > -1:
		asp = line.split('"')
		nodelist.append(int(asp[1]))
	if line.find('<Connections') > -1:
		inputtool = 0
		destinationtool = 0
		foo += 1
		while line.find("</Connections") == -1:
			if line.find("<Origin ToolID") > -1:
				inputtool = int(line.split('"')[1])
			if line.find("<Destination ToolID") > -1:
				destinationtool = int(line.split('"')[1])
			if line.find("</Connection>") > -1:
				connections.append([inputtool,destinationtool])
			foo += 1
			line = contents[foo]

#for foo in connections:
#	print(foo)

# get nodes within connections
savelength = 0
while savelength != len(outnodelist):
	#print("Loop")
	savelength = len(outnodelist)
	for bar in outnodelist:
		for foo in connections:
			if foo[1] == bar:
				#print(bar, foo)
				if foo[0] not in outnodelist:
					outnodelist.append(foo[0])

#print(len(nodelist))
#print(len(outnodelist))
#print(outnodelist)
#print(len(connections))

# go back and get the nodes
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

# go back and get the connections
connections = ""
for foo in range(len(contents)):
	line = contents[foo]
	if line.find('<Connection>') > -1:
		destination = int(contents[foo+2].split('"')[1])
		if destination in outnodelist:
			connections += f"     <Connection>\n{contents[foo+1]}{contents[foo+2]}    </Connection>"

outlist = alias_nodes(contents)
outlist = alias_connections(outlist)

ot = "".join(s for s in outlist)
with open(f"path_to_{sys.argv[2]}.yxmd", "w") as f:
	f.writelines(ot.replace("__NODES__",nodes).replace("__CONNECTIONS__",connections))
print(f"Wrote file path_to_{sys.argv[2]}.yxmd")
