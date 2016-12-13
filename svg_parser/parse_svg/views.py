from django.shortcuts import render, redirect
from django.contrib.auth import logout as auth_logout
import xml.etree.ElementTree as ET
from svg_parser import settings
import os
import json
from models import Image

translate = []
annotations = []
g_attributes = {}

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
			# print tag, attribute, translate
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
	params = request.GET.get('url')
	print params
	global annotations
	annotations = []
	tree = ET.parse(os.path.join(settings.BASE_DIR, 'parse_svg', 'templates', 'sign-in.svg'))
	root = tree.getroot()
	getChild(root)
	# args = {'annotations': annotations}
	return render(request, 'index.html', {'annotations': json.dumps(annotations)})

def login(request):
	return render(request, 'login.html')

def home(request):
	if request.user:
		user = request.user
		email = user.email

	# obj, created = Image.objects.get_or_create(email=email)
	# print 'obj: ', obj
	# print 'created: ', created
	images = Image.objects.filter(email=email)
	return render(request, 'home.html', {'images': images})

def logout(request):
    auth_logout(request)
    return redirect('/')
