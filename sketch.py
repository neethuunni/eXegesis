from xml.dom import minidom
from xml.dom.minidom import parse
import xml.dom.minidom
from collections import defaultdict
from xml.dom.minidom import Node
import xml.etree.ElementTree as ET

# doc = minidom.parse('svg.svg')  # parseString also exists

# for elem in doc.getElementsByTagName('svg'):
#     for x in elem.childNodes:
#         if x.nodeType == Node.ELEMENT_NODE:
#         	if x.firstChild:
#         		print '1'
#         		print x.tagName, x.attributes.items()
#         		print x.parentNode.tagName
#         	else:
#         		print '2'
#         		print x.tagName, x.firstChild

tree = ET.parse('svg.svg')
root = tree.getroot()
