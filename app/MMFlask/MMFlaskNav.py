from dominate import tags
from flask_nav import Nav, register_renderer
from flask_nav.elements import Navbar, View
from flask_nav.renderers import Renderer


class MMFlaskNav:
    def __init__(self, app):
        self.nav = Nav()
        self.nav.init_app(app)
        self.nav.register_element('top', self.mm_top_nav(app.sites))
        register_renderer(app, 'MMTopNavRenderer', MMTopNavRenderer)

    @staticmethod
    def mm_top_nav(sites):
        items = []

        for site in sites:
            if site['nav']['top']:
                items.append({'view': View(site['name'], site['url']),
                              'permission': site['permission']})

        return Navbar('', *items)


class MMTopNavRenderer(Renderer):
    def __init__(self, user_role):
        self.user_role = user_role

    def visit_Navbar(self, node):
        nav_html = tags.div(id="navbarNav", Class="collapse navbar-collapse")

        with nav_html.add(tags.ul(Class="navbar-nav")):
            for item in node.items:
                if item['permission'][self.user_role] is True:
                    self.visit(item['view'])

        return nav_html

    def visit_View(self, node):
        li_html = tags.li(Class="nav-item active" if node.active else "nav-item")
        li_html.add(tags.a(node.text, Class="nav-link", href=node.get_url(), title=node.text))

        return li_html

    def visit_Subgroup(self, node):
        # almost the same as visit_nav_bar, but written a bit more concise
        return tags.div(node.title,
                        *[self.visit(item) for item in node.items])
