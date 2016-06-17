import web # imports the web.py module
#web.config.debug = False # sessions don't work with debug

#tell web.py to look for templates in template directory
render = web.template.render('templates/')

# tell web.py the URL structure
# first part is regex 
# parentheses say to capture that piece of the matched data for use later on
# second part is the name of a class to send the request to
urls = (
	'/', 'index',
	"/count", "count",
    "/reset", "reset"
    #,
	#'/(.*)', 'redirect'
)
app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'count': 0})

# get - request text of web page
# post - whenever the act of submitting a request does something

class index:
	def GET(self):  
		i = web.input(name=None)
		return render.index(i.name)

class count:
    def GET(self):
        session.count += 1
        return str(session.count)

class reset:
    def GET(self):
        session.kill()
        return ""

class redirect:
	def GET(self, path):
		web.seeother('/')

# create application with above URLs,
# looking up the classes in the global namespace of this file.
# make sure that web.py serves the application we created above
if __name__ == "__main__":
	app.run()