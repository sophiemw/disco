#!/usr/bin/env python

## From http://www.dreamsyssoft.com/python-scripting-tutorial/create-simple-rest-web-service-with-python.php
# http://192.168.33.10:8080/users
import web
import xml.etree.ElementTree as ET

tree = ET.parse('user_data.xml')
root = tree.getroot()

urls = (
    '/users', 'list_users',
    '/users/(.*)', 'get_user',
	'/test/(.*)', 'test_paras'
)

app = web.application(urls, globals())

class list_users:        
    def GET(self):
	output = 'uusers:[';
	for child in root:
                print 'child', child.tag, child.attrib
                output += str(child.attrib) + ','
	output += ']';
        return output

class get_user:
    def GET(self, user):
	for child in root:
		if child.attrib['id'] == user:
		    return str(child.attrib)
			
class test_paras:
	def GET(self, paras):
		i = web.input(name=None, code=None)
		n = i.name
		if n == None:
			n = '<not given>'
		return 'Name is: ' + n + ', ' + 'Code is: ' + i.code


if __name__ == "__main__":
    app.run()