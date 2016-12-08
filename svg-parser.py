from xml.dom import minidom
from xml.dom.minidom import parse
import xml.dom.minidom
from collections import defaultdict
from xml.dom.minidom import Node
import xml.etree.ElementTree as ET

# doc = minidom.parse('sign-in.svg')

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
tree = ET.parse('sign-in.svg')
root = tree.getroot()
# for child in root[3][0]:	
# 	tagName = child.tag.split('}')[1]
# 	parents[tagName] = child.attrib
# 	print tagName, child.attrib
# print len(root[3][0][3][0])

# objects = []
# elm = {}
# def print_child(root, parent):
# 	for child in root:
# 		tag = child.tag.split('}')[1]
# 		attribute = child.attrib
# 		if tag == 'text' or tag == 'tspan' or tag == 'rect' or tag == 'g':
# 			print tag, attribute, parent
# 			elm = {tag: attribute}
# 			objects.append(elm)
# 		print_child(child, root)


# tree = ET.parse('sign-in.svg')
# root = tree.getroot()
# print_child(root, '')
translate = []
annotations = []

def getSubChild(child):
	elm = {}
	for subchild in child:
		attribute = subchild.attrib
		tag = subchild.tag.split('}')[1]
		if tag == 'g' and 'transform' in attribute.keys():
			transform = attribute['transform']
			if transform.startswith('translate'):
				# print 'transform: ', transform
				length = len(transform) - 1
				transform = transform[10:length]
				transform = transform.split(',')
				translate.append(float(transform[0]))
				translate.append(float(transform[1]))
		if tag == 'rect' or tag == 'text' or tag == 'tspan':
			if translate and 'x' in attribute.keys():
				attribute['x'] = float(attribute['x']) + translate[0]
				attribute['y'] = float(attribute['y']) + translate[1]
			print tag, attribute, translate
			elm[tag] = attribute
			annotations.append(elm)
		getSubChild(subchild)
		if translate:
			translate.pop()
			translate.pop()
	return annotations

def getChild(root):
	for child in root:
		tag = child.tag.split('}')[1]
		if len(child) > 0 and tag != 'title' and tag != 'desc' and tag != 'defs':
			getSubChild(child)

getChild(root)
# print annotations

