
import urllib2
from xml.dom import minidom

def check_number_items(page, tag):
	p = urllib2.urlopen(page)
	
	xml = p.read()
	dom = minidom.parseString(xml)
	#To get the value of that tag you use item[0].firstChild.nodeValue
	items = dom.getElementsByTagName(tag)
	return len(items)

print check_number_items("http://www.nytimes.com/services/xml/rss/nyt/GlobalHome.xml", "item")