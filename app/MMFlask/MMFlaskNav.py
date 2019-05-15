from dominate import tags
from flask_nav import Nav, register_renderer
from flask_nav.elements import Navbar, View
from flask_nav.renderers import Renderer


class MMFlaskNav:
    def __init__(self, app):
        self.nav = Nav()
        self.nav.init_app(app)
        self.nav.register_element('mmTopNavLoggedIn', self.mm_top_nav(True))
        self.nav.register_element('mmTopNavLoggedOut', self.mm_top_nav(False))
        register_renderer(app, 'MMTopNavRenderer', MMTopNavRenderer)

    def mm_top_nav(self, logged_in):
        items = [View('Recipes', 'recipe'),
                 View('Ingredients', 'ingredient'),
                 View('Tubes', 'tube'),
                 View('Users', 'user')]

        if logged_in:
            # items.append(View('Scale', 'scale'))
            # items.append(View('LED', 'led'))
            items.append(View('Log out', 'logout'))
        else:
            items.append(View('Log in', 'login'))
            items.append(View('Sign up', 'signup'))

        items.append(View('Status', 'status'))

        return Navbar('', *items)


class MMTopNavRenderer(Renderer):
    def visit_Navbar(self, node):
        # sub = []
        # for item in node.items:
        # sub.append(self.visit(item))

        nav_html = tags.div(id="navbarNav", Class="collapse navbar-collapse")

        with nav_html.add(tags.ul(Class="navbar-nav")):
            for item in node.items:
                self.visit(item)

        return nav_html

    def visit_View(self, node):
        li_html = tags.li(Class="nav-item active" if node.active else "nav-item")
        li_html.add(tags.a(node.text, Class="nav-link", href=node.get_url(), title=node.text))

        return li_html

    def visit_Subgroup(self, node):
        # almost the same as visit_nav_bar, but written a bit more concise
        return tags.div(node.title,
                        *[self.visit(item) for item in node.items])
