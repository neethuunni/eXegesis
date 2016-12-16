# from xml.dom import minidom

# doc = minidom.parse('sign-in.svg')  # parseString also exists
# path_strings = [path.getAttribute('d') for path
#                 in doc.getElementsByTagName('path')]
# for i in path_strings:
# 	print i, '\n'
# doc.unlink()

import xml.etree.ElementTree as ET

tree = ET.parse('sign-in.svg')
root = tree.getroot()

paths = []
for elm in root.iter():
	attribute = elm.attrib
	tag = elm.tag.split('}')[1]
	if tag == 'path':
		path = attribute['d'].split(' ')
		each_path = []
		for i in path:
			if i == 'z' or i == 'Z':
				continue
			point = i.split(',')
			if not point[0].replace('.', '').isdigit():
				point[0] = point[0][1:]
			point[0] = float(point[0])
			point[1] = float(point[1])
			each_path.extend(point)
		paths.append(each_path)

for i in paths:
	# print i, len(i), '\n'
	x_array = []
	y_array = []
	for j in range(len(i)):
		if j % 2 == 0:
			x_array.append(i[j])
		else:
			y_array.append(i[j])
	x_max = max(x_array)
	y_max = max(y_array)
	x_min = min(x_array)
	y_min = min(y_array)
	print i, 'x_max', x_max, 'y_max', y_max, 'x_min', x_min, 'y_min', y_min, '\n'
