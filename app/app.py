from flask import Flask

def get_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
        return 'Hello World'

    @app.route('/stats')
    def stats():
        return 'here are some stats'

    @app.route('/ex')
    def ex():
        return """<p>The RFM69HCW is an inexpensive and versatile radio module. You can use it to send text or binary data between two or hundreds of modules. It’s perfect for building inexpensive short-range wireless networks for home automation, citizen science, and more. The RFM69HCW comes in two frequency flavors; a <a href="https://www.sparkfun.com/products/12775">915 MHz version</a> and a <a href="https://www.sparkfun.com/products/12823">434 MHz version</a>. See the <a href="https://learn.sparkfun.com/tutorials/rfm69hcw-hookup-guide#hardware-overview">Hardware Overview</a> below for tips on which one to choose.</p>"""

    return app



if __name__ == '__main__':
    app = get_app()
    app.run(host='127.0.0.1', port=5000, debug=True)
