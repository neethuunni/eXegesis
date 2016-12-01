from xml.dom import minidom

doc = minidom.parse('sign-up.svg')  # parseString also exists
path_strings = [path.getAttribute('d') for path in doc.getElementsByTagName('path')]
for item in path_strings:
	print item
doc.unlink()
