import xml.etree.ElementTree as ET

tree = ET.parse('rect.svg')
root = tree.getroot()
translate = []
annotations = []
g_attributes = {}
defs = {}

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
				if len(translate) > 2:
					translation = [0] * 2
					for i in range(len(translate)):
						if i % 2 == 0:
							translation[0] += translate[i]
						else:
							translation[1] += translate[i]
				else:
					translation = translate[:]

				attribute['x'] = float(attribute['x']) + translation[0]
				attribute['y'] = float(attribute['y']) + translation[1]
			if tag == 'tspan':
				g_attributes.clear()
				attribute['text'] = subchild.text
			# print tag, attribute, '\n'
			attribute['type'] = tag
			if g_attributes:
				attribute.update(g_attributes)
			annotations.append(attribute)

		if tag == 'g':
			g_attributes.clear()
			for i in attribute.keys():
				if i == 'id' or i == 'transform':
					continue
				else:
					g_attributes[i] = attribute[i]

		if tag == 'use':
			for i in attribute.keys():
				if 'href' in i:
					id = attribute[i]
					del attribute[i]
					break
			id = id.replace('#', '')
			defs_list = defs.copy()
			defs_list[id]['id'] = attribute['id']
			if translate and 'x' in defs_list[id].keys():
				if len(translate) > 2:
					translation = [0] * 2
					for i in range(len(translate)):
						if i % 2 == 0:
							translation[0] += translate[i]
						else:
							translation[1] += translate[i]
				else:
					translation = translate[:]

				defs_list[id]['x'] = float(defs_list[id]['x']) + translation[0]
				defs_list[id]['y'] = float(defs_list[id]['y']) + translation[1]
			annotations.append(defs_list[id])

		getSubChild(subchild)
		if translate:
			translate.pop()
			translate.pop()
	return annotations

def getDefs(root):
	for child in root:
		tag = child.tag.split('}')[1]
		if tag == 'rect':
			attribute = child.attrib
			if 'id' in attribute.keys():
				id = attribute['id']
				del attribute['id']
				attribute['type'] = 'rect'
				defs[id] = attribute

# def getOuterChild(root):
	# for child in root:


def getChild(root):
	for child in root:
		tag = child.tag.split('}')[1]
		if len(child) > 0 and tag == 'defs':
			getDefs(child)

		elif len(child) > 0 and tag != 'title' and tag != 'desc' and tag != 'defs':
			getSubChild(child)

		# elif tag != 'title' and tag != 'desc' and tag != 'defs':
		# 	getOuterChild(child)

getChild(root)
for i in annotations:
	print i
