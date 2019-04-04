from flask import Flask, render_template
from flask_nav import Nav
from flask_nav.elements import Navbar, View

nav = Nav()

app = Flask(__name__)
nav.init_app(app)


def user_is_logged_in():
    return False


@nav.navigation()
def top_nav():
    items = [View('Home', 'index'), View('Shopping Area', 'index')]

    # only logged in users get to see the secret shop
    if user_is_logged_in():
        items.append(View('Secret Shop', 'secret'))

    return Navbar('', *items)


@app.route('/')
def index():
    return render_template('navtest.html')


@app.route('/_secret/')
def secret():
    return 'You found the secret shop!'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)