import xml.etree.ElementTree as ET

tree = ET.parse('sign-in.svg')
root = tree.getroot()
translate = []
annotations = []

def getSubChild(child):
	for subchild in child:
		elm = {}
		attribute = subchild.attrib
		tag = subchild.tag.split('}')[1]
		if tag == 'g' and 'transform' in attribute.keys():
			transform = attribute['transform']
			if transform.startswith('translate'):
				length = len(transform) - 1
				transform = transform[10:length]
				transform = transform.split(',')
				translate.append(float(transform[0]))
				translate.append(float(transform[1]))
		if tag == 'rect' or tag == 'text' or tag == 'tspan':
			if translate and 'x' in attribute.keys():
				attribute['x'] = float(attribute['x']) + translate[0]
				attribute['y'] = float(attribute['y']) + translate[1]
			if tag == 'tspan':
				attribute['text'] = subchild.text
			# print tag, attribute, translate
			attribute['type'] = tag
			annotations.append(attribute)
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
for i in annotations:
	print i
