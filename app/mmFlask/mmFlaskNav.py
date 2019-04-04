from dominate import tags
from flask_nav import Nav, register_renderer
from flask_nav.elements import Navbar, View
from flask_nav.renderers import Renderer


class mmFlaskNav():
    def __init__(self, app):
        self.nav = Nav()
        self.nav.init_app(app)
        self.nav.register_element('mmTopNavLoggedIn', self.mmTopNav(True))
        self.nav.register_element('mmTopNavLoggedOut', self.mmTopNav(False))
        register_renderer(app, 'mmTopNavRenderer', mmTopNavRenderer)
    
    def mmTopNav(self, loggedIn):
        items = []
        
        if loggedIn:
            items.append(View('Scale', 'flaskScale'))
            items.append(View('LED', 'flaskLed'))
            items.append(View('Log out', 'flaskLogOut'))
        else:
            items.append(View('Log in', 'flaskLogIn'))
            items.append(View('Sign up', 'flaskSignUp'))
        
        return Navbar('', *items)

class mmTopNavRenderer(Renderer):
    def visit_Navbar(self, node):
        #sub = []
        #for item in node.items:
        #sub.append(self.visit(item))

        navHtml = tags.div(id="navbarNav", Class="collapse navbar-collapse")
        
        with navHtml.add(tags.ul(Class="navbar-nav")):
            for item in node.items:
                self.visit(item)
        
        return navHtml

    def visit_View(self, node):
        liHtml = tags.li(Class = "nav-item active" if node.active else "nav-item")
        liHtml.add(tags.a(node.text, Class="nav-link", href=node.get_url(), title=node.text))
            
        return liHtml

    def visit_Subgroup(self, node):
        # almost the same as visit_Navbar, but written a bit more concise
        return tags.div(node.title,
                        *[self.visit(item) for item in node.items])