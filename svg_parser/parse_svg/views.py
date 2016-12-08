from django.shortcuts import render
import xml.etree.ElementTree as ET
from xml.dom.minidom import parse
from svg_parser import settings
import os


# Create your views here.

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

def index(request):
	tree = ET.parse(os.path.join(settings.BASE_DIR, 'parse_svg', 'templates', 'sign-in.svg'))
	root = tree.getroot()
	getChild(root)
	args = {'annotations': annotations}
	print annotations
	return render(request, 'index.html', context=args)





