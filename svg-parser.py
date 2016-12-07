from xml.dom import minidom
from xml.dom.minidom import parse
import xml.dom.minidom
from collections import defaultdict
from xml.dom.minidom import Node
import xml.etree.ElementTree as ET

doc = minidom.parse('sign-in.svg')

# parents = {}
# for elem in doc.getElementsByTagName('svg'):
#     for x in elem.childNodes:
#         if x.nodeType == Node.ELEMENT_NODE:
#         	if x.firstChild:
#         		parents[x.tagName] =  x.attributes.items()
#         	else:
#         		parents[x.tagName] = []
# print parents

# parents = {}
# tree = ET.parse('sign-in.svg')
# root = tree.getroot()
# for child in root[3][0]:	
# 	tagName = child.tag.split('}')[1]
# 	parents[tagName] = child.attrib
# 	print tagName, child.attrib
# print len(root[3][0][3][0])

objects = []
elm = {}
def print_child(root, parent):
	for child in root:
		tag = child.tag.split('}')[1]
		attribute = child.attrib
		if tag == 'text' or tag == 'tspan' or tag == 'rect' or tag == 'g':
			print tag, attribute, parent
			elm = {tag: attribute}
			objects.append(elm)
		print_child(child, root)


tree = ET.parse('sign-in.svg')
root = tree.getroot()
print_child(root, '')
# print '\n\n\n'
# for i in objects:
# 	print i