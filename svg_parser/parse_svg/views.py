from django.shortcuts import render, redirect
from django.contrib.auth import logout as auth_logout
import xml.etree.ElementTree as ET
from svg_parser.settings import EMAIL_SUBJECT, EMAIL_MESSAGE, EMAIL_HOST_USER
from svg_parser import settings
import os
import json
from models import Project, ArtBoard
import uuid
import zipfile
from django.core.mail import EmailMessage
import jwt

translate = []
annotations = []
g_attributes = {}
defs = {}
trans_child = []

def getSubChild(child):
	global trans_child
	for subchild in child:
		elm = {}
		attribute = subchild.attrib
		tag = subchild.tag.split('}')[1]
		if tag == 'g' and 'transform' in attribute.keys():
			transform = attribute['transform']
			if transform.startswith('translate'):
				trans_child.append(subchild)
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
			# print tag, attribute, translate, '\n'
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

		if tag == 'path':
			path_data = {}
			path = attribute['d'].split(' ')
			paths = []
			for i in path:
				if i == 'z' or i == 'Z':
					continue
				point = i.split(',')
				if not point[0].replace('.', '').isdigit():
					point[0] = point[0][1:]
				point[0] = float(point[0])
				point[1] = float(point[1])
				paths.extend(point)
			x_array = []
			y_array = []
			for j in range(len(paths)):
				if j % 2 == 0:
					x_array.append(paths[j])
				else:
					y_array.append(paths[j])
			x_max = max(x_array)
			y_max = max(y_array)
			x_min = min(x_array)
			y_min = min(y_array)
			x = x_min
			y = y_min
			if translate:
				if len(translate) > 2:
					translation = [0] * 2
					for i in range(len(translate)):
						if i % 2 == 0:
							translation[0] += translate[i]
						else:
							translation[1] += translate[i]
				else:
					translation = translate[:]
				y = y_min + translation[1]
				x = x_min + translation[0]
			height = y_max - y_min
			width = x_max - x_min
			del attribute['d']
			path_data.update(attribute)
			path_data.update(g_attributes)
			path_data['height'] = height
			path_data['width'] = width
			path_data['x'] = x
			path_data['y'] = y
			annotations.append(path_data)

		getSubChild(subchild)
		if translate and subchild == trans_child[len(trans_child) - 1]:
			translate.pop()
			translate.pop()
			trans_child.pop()
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

def getChild(root):
	for child in root:
		tag = child.tag.split('}')[1]
		if len(child) > 0 and tag == 'defs':
			getDefs(child)
		if len(child) > 0 and tag != 'title' and tag != 'desc' and tag != 'defs':
			getSubChild(child)

def index(request):
	params = request.GET.get('url')
	print params
	global annotations
	annotations = []
	tree = ET.parse(os.path.join(settings.BASE_DIR, 'parse_svg', 'templates') + '/' + params)
	root = tree.getroot()
	getChild(root)
	return render(request, 'index.html', {'annotations': json.dumps(annotations), 'url': params})

def login(request):
	return render(request, 'login.html')

def artboards(request):
	project = request.GET.get('project')
	request.session['project'] = project
	project = Project.objects.filter(project=project)
	artboards = ArtBoard.objects.filter(project=project)
	return render(request, 'artboards.html', {'artboards': artboards})

def svg_images(request):
	project = request.session['project']
	redirection = '/artboards?project=' + project
	project = Project.objects.get(project=project)
	images_path = os.path.join('parse_svg', 'templates', 'uploads')
	if not os.path.exists(images_path):
           os.makedirs(images_path)
	for f in request.FILES.getlist('svgfile'):
		filename = f.name
		print 'filename: ', filename
		if filename.endswith('zip'):
			archive = zipfile.ZipFile(f)
			for file in archive.namelist():
				print 'file: ', file
				if file.endswith('svg'):
					img_data = archive.read(file)
					uuid_name = uuid.uuid4()
					img_name = "%s.%s" % (uuid_name, 'svg')
					image_path = 'uploads/' + img_name
					url = image_path
					with open(os.path.join(images_path, img_name), "wb") as image:
					   image.write(img_data)
					if '/' in file:
						file = file.split('/')[1]
					new_entry = ArtBoard(project=project, artboard=file, location=url)
					new_entry.save()

		else:
			img_data = f.read()
			uuid_name = uuid.uuid4()
			img_name = "%s.%s" % (uuid_name, 'svg')
			image_path = 'uploads/' + img_name
			url = image_path
			with open(os.path.join(images_path, img_name), "wb") as image:
			   image.write(img_data)
			new_entry = ArtBoard(project=project, artboard=filename, location=url)
			new_entry.save()
	return redirect(redirection)

def logout(request):
	auth_logout(request)
	return redirect('/')

def projects(request):
	if request.user:
		email = request.user.email
	print 'email: ', email
	all_projects = Project.objects.filter(email=email)
	return render(request, 'projects.html', {'projects': all_projects})

def create_project(request):
	email = request.user.email
	project_name = request.POST.get('project-name')
	project_description = request.POST.get('project-description')
	new_project = Project(email=email, project=project_name, description=project_description, share=True, edit=True)
	new_project.save()
	return redirect('/projects')

def share_project(request):
	project = request.session['project']
	redirection = '/artboards?project=' + project
	email = request.POST.get('email')
	share = request.POST.get('share')
	edit = request.POST.get('edit')
	encoded = jwt.encode({'code': 'verification_success', 'redirection': redirection, 'email': email}, 'svgparser', algorithm='HS256')
	url = '127.0.0.1:8000/verify_share?token=' + encoded
	mail = EmailMessage(EMAIL_SUBJECT, EMAIL_MESSAGE + url, EMAIL_HOST_USER, [email])
	mail.send(fail_silently=False)
	
	return redirect(redirection)

def verify_share(request):
	token = request.GET.get('token')
	decoded = jwt.decode(token, 'svgparser', algorithms=['HS256'])
	if decoded['code'] == 'verification_success':
		new_user = Project(email=decoded['email'])
		return redirect(decoded['redirection'])

