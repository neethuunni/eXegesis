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
from random import randint
from datetime import datetime
import cairosvg
from django.http import HttpResponse

ET.register_namespace('', "http://www.w3.org/2000/svg")
ET.register_namespace('xlink', "http://www.w3.org/1999/xlink")

translate = []
annotations = []
g_attributes = {}
defs = {}
trans_child = []

def check_for_id():
	new_id = str(uuid.uuid4())[0:8]
	return new_id

def getTranslations(transform):
	trans = []
	transx = transy = 0
	p = transform.split(')')
	for i in p:
		if i.lstrip().startswith('translate'):
			q = i.split('(')[1]
			r = q.split(',')
			trans.append(float(r[0]))
			trans.append(float(r[1]))
	for i in range(len(trans)):
		if i % 2 == 0:
			transx += trans[i]
		else:
			transy += trans[i]
	translate.append(transx)
	translate.append(transy)

def getSubChild(child):
	global trans_child
	for subchild in child:
		elm = {}
		attribute = subchild.attrib
		tag = subchild.tag.split('}')[1]
		if tag == 'g' and 'transform' in attribute.keys():
			transform = attribute['transform']
			getTranslations(transform)
			if 'translate' in transform:
				trans_child.append(subchild)

		if tag == 'rect' or tag == 'text' or tag == 'tspan' or tag == 'ellipse':
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
			print 'defs_list: ', defs_list
			if 'id' in attribute.keys():
				if id in defs_list.keys():
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
			if 'd' in attribute.keys():
				path_data = {}
				path = attribute['d'].split(' ')
				paths = []
				if ',' in path[0]:
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
	count = 0
	for child in root:
		tag = child.tag.split('}')[1]
		if tag == 'rect' or tag == 'circle' or tag == 'ellipse' or tag == 'text':
			attribute = child.attrib
			if 'id' in attribute.keys():
				id = attribute['id']
				del attribute['id']
				attribute['type'] = tag
				defs[id] = attribute
			if tag == 'text':
				for subchild in child:
					sub_tag = subchild.tag.split('}')[1]
					if sub_tag == 'tspan':
						count += 1
						sub_attrib = subchild.attrib
						sub_text = subchild.text
						defs[id][sub_text] = sub_attrib
	annotations.append(count)

def getChild(root):
	for child in root:
		tag = child.tag.split('}')[1]
		if len(child) > 0 and tag == 'defs':
			getDefs(child)
		else:
			annotations.append(0)
		if len(child) > 0 and tag != 'title' and tag != 'desc' and tag != 'defs':
			getSubChild(child)

def login(request):
	return render(request, 'login.html')

def projects(request):
	if request.user:
		email = request.user.email
	user = request.user.first_name + ' ' + request.user.last_name
	request.session['username'] = user
	request.session.modified = True
	all_projects = Project.objects.filter(email=email)
	print 'Username projects: ', user
	proj = Project.objects.filter(email=email).values('project', 'density', 'screen', 'description')
	proj = json.dumps(list(proj))
	return render(request, 'projects.html', {'projects': all_projects, 'user': user, 'proj': proj})

def create_project(request):
	email = request.user.email
	project_name = request.POST.get('project-name')
	project_description = request.POST.get('project-description')
	user = request.user.first_name + ' ' + request.user.last_name
	thumbnail = 'static/project.jpg'
	screen = request.POST.get('screen')
	density = request.POST.get('density')
	created = datetime.now()
	uuid_name = uuid.uuid4()
	new_project = Project(email=email, project=project_name, description=project_description, share=True, edit=True, owner=user, thumbnail=thumbnail, screen=screen, density=density, created=created, last_updated=created, uuid=uuid_name)
	new_project.save()
	return redirect('/projects')

def artboards(request):
	user = request.session['username']
	print 'email: ', request.user.email
	project_name = request.GET.get('project')
	p = Project.objects.get(project=project_name, email=request.user.email)
	description = p.description
	thumbnail = p.thumbnail
	edit = p.edit
	share = p.share
	owner = p.owner
	screen = p.screen
	density = p.density
	created = p.created
	last_updated = p.last_updated
	shared_members = Project.objects.filter(project=project_name, share=True)
	print 'shared_members: ', shared_members
	request.session['project'] = project_name
	request.session['description'] = description
	request.session['thumbnail'] = thumbnail
	request.session['owner'] = owner
	request.session.modified = True
	print 'session values in artboard: ', request.session.keys(), request.session['project'], request.session['description']
	project = Project.objects.filter(project=project_name, email=request.user.email)
	artboards = ArtBoard.objects.filter(project__project__contains=project_name)
	print 'project_name', project_name
	print 'Username artboards: ', user
	print 'project: ', project
	print 'artboards: ', artboards
	return render(request, 'artboards.html', {'artboards': artboards, 'user': user, 'project': project_name, 'description': description, 'share': share, 'edit': edit, 'screen': screen, 'density': density, 'created': created, 'last_updated': last_updated, 'owner': owner, 'shared_members': shared_members})

def svg_images(request):
	defs_elms = []
	project_uuid = request.POST.get('project-uuid')
	project = Project.objects.get(uuid=project_uuid)
	project_name = project.project
	# project_name = request.session['project']
	# redirection = '/artboards?project=' + project_name
	redirection = '/projects'
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

					tree = ET.parse(os.path.join(settings.BASE_DIR, 'parse_svg', 'templates') + '/' + url)
					root = tree.getroot()
					for child in root.iter():
						if child.tag.split('}')[1] == 'defs':
							for subchild in child.iter():
								defs_elms.append(subchild)
					for child in root.iter():
						if child not in defs_elms:
							attribute = child.attrib
							if 'id' in attribute:
								elem_id = check_for_id()
								child.set('id', elem_id)
							if child.tag.split('}')[1] == 'use' and 'id' not in attribute.keys() or child.tag.split('}')[1] == 'text' and 'id' not in attribute.keys():
								elem_id = check_for_id()
								child.set('id', elem_id)
					tree.write(os.path.join(settings.BASE_DIR, 'parse_svg', 'templates') + '/' + url)

					Project.objects.filter(project=project_name, email=request.user.email).update(thumbnail=url)
					print 'project: ', project_name
					print 'email: ', request.user.email
					project = Project.objects.get(project=project_name, email=request.user.email)
					file = file.split('.')[0]
					new_entry = ArtBoard(project=project, artboard=file, location=url, uuid=uuid_name)
					new_entry.save()
		else:
			img_data = f.read()
			uuid_name = uuid.uuid4()
			img_name = "%s.%s" % (uuid_name, 'svg')
			image_path = 'uploads/' + img_name
			url = image_path
			with open(os.path.join(images_path, img_name), "wb") as image:
			   image.write(img_data)
			tree = ET.parse(os.path.join(settings.BASE_DIR, 'parse_svg', 'templates') + '/' + url)
			root = tree.getroot()
			for child in root.iter():
				if child.tag.split('}')[1] == 'defs':
					for subchild in child.iter():
						defs_elms.append(subchild)
			for child in root.iter():
				if child not in defs_elms:
					attribute = child.attrib
					if 'id' in child.attrib:
						elem_id = check_for_id()
						child.set('id', elem_id)
					if child.tag.split('}')[1] == 'use' and 'id' not in attribute.keys() or child.tag.split('}')[1] == 'text' and 'id' not in attribute.keys():
						elem_id = check_for_id()
						child.set('id', elem_id)
			tree.write(os.path.join(settings.BASE_DIR, 'parse_svg', 'templates') + '/' + url)
			Project.objects.filter(project=project_name, email=request.user.email).update(thumbnail=url)
			project = Project.objects.get(project=project_name, email=request.user.email)
			filename = filename.split('.')[0]
			new_entry = ArtBoard(project=project, artboard=filename, location=url, uuid=uuid_name)
			new_entry.save()
	return redirect(redirection)

def share_project(request):
	try:
		project = request.session['project']
		redirection = '/artboards?project=' + project
		email = request.POST.get('email')
		share = request.POST.get('share')
		edit = request.POST.get('edit')
		share = True if share else False
		edit = True if edit else False
		encoded = jwt.encode({'code': 'verification_success', 'email': email, 'project': project, 'share': share, 'edit': edit}, 'svgparser', algorithm='HS256')
		url = '10.7.30.2.xip.io:8000/verify_share?token=' + encoded
		mail = EmailMessage(EMAIL_SUBJECT, EMAIL_MESSAGE + url, EMAIL_HOST_USER, [email])
		mail.send(fail_silently=False)
		return redirect(redirection)
	except:
		email = request.POST.get('email')
		share = request.POST.get('share')
		edit = request.POST.get('edit')
		share = True if share else False
		edit = True if edit else False
		project = request.POST.get('project-name')
		encoded = jwt.encode({'code': 'verification_success', 'email': email, 'project': project, 'share': share, 'edit': edit}, 'svgparser', algorithm='HS256')
		url = '10.7.30.2.xip.io:8000/verify_share?token=' + encoded
		mail = EmailMessage(EMAIL_SUBJECT, EMAIL_MESSAGE + url, EMAIL_HOST_USER, [email])
		mail.send(fail_silently=False)
		return redirect('/projects')

def verify_share(request):
	print 'session values in verify: ', request.session.keys()
	token = request.GET.get('token')
	decoded = jwt.decode(token, 'svgparser', algorithms=['HS256'])
	if decoded['code'] == 'verification_success':
		project = decoded['project']
		p = Project.objects.filter(project=project)[0]
		description = p.description
		thumbnail = p.thumbnail
		owner = p.owner
		created = p.created
		last_updated = p.last_updated
		screen = p.screen
		density = p.density
		new_user = Project(email=decoded['email'], project=project, description=description, share=decoded['share'], edit=decoded['edit'], thumbnail=thumbnail, owner=owner, created=created, last_updated=last_updated, density=density, screen=screen)
		new_user.save()
		return render(request, 'verified.html')

def index(request):
	params = request.GET.get('url')
	print params
	global annotations
	annotations = []
	tree = ET.parse(os.path.join(settings.BASE_DIR, 'parse_svg', 'templates') + '/' + params)
	root = tree.getroot()
	getChild(root)
	for i in annotations:
		print i
	artboard = ArtBoard.objects.get(location=params)
	artboard = artboard.artboard
	return render(request, 'index.html', {'annotations': json.dumps(annotations), 'url': params, 'artboard': artboard})

def logout(request):
	auth_logout(request)
	print 'session keys: ', request.session.keys()
	return redirect('/')

def delete_artboard(request):
	url = request.GET.get('artboard')
	project = request.session['project']
	email = request.user.email
	ArtBoard.objects.filter(location=url).delete()
	redirection = '/artboards?project=' + project
	os.remove(os.path.join(settings.BASE_DIR, 'parse_svg', 'templates') + '/' + url)
	return redirect(redirection)

def rename_artboard(request):
	url = request.POST.get('artboard')
	new_name = request.POST.get('new-name')
	print 'url', url
	print 'new_name', new_name
	project = request.session['project']
	email = request.user.email
	ArtBoard.objects.filter(location=url).update(artboard=new_name)
	redirection = '/artboards?project=' + project
	return redirect(redirection)

def delete_project(request):
	project = request.GET.get('project')
	email = request.user.email
	Project.objects.get(project=project, email=email).delete()
	redirection = '/projects'
	return redirect(redirection)

def download_artboard(request):
	print 'download_artboard'
	url = request.GET.get('artboard')
	name = url.replace('svg', 'png')
	print 'name:', name
	cairosvg.svg2png(url=os.path.join(settings.BASE_DIR, 'parse_svg', 'templates') + '/' + url, write_to=os.path.join(settings.BASE_DIR, 'parse_svg', 'templates') + '/' + name)
	
	with open(os.path.join(settings.BASE_DIR, 'parse_svg', 'templates') + '/' + name, 'rb') as png:
		response = HttpResponse(png.read())
		response['content_type'] = 'image/png'
		response['Content-Disposition'] = 'attachment;filename=file.png'
		return response

def update_project(request):
	for f in request.FILES.getlist('svgfile'):
		filename = f.name
		print 'filename: ', filename
	print 'uuid: ', request.POST.get('project-uuid')