from django.shortcuts import render
import xml.etree.ElementTree as ET
from svg_parser import settings
import os
import json


# Create your views here.

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

def index(request):
	global annotations
	annotations = []
	tree = ET.parse(os.path.join(settings.BASE_DIR, 'parse_svg', 'templates', 'sign-in.svg'))
	root = tree.getroot()
	getChild(root)
	# args = {'annotations': annotations}
	return render(request, 'index.html', {'annotations': json.dumps(annotations)})





