from flask import Flask
import os

this_dir = os.path.dirname(__file__)

files = {}
def get_app():
    app = Flask(__name__)

    @app.route('/')
    @app.route('/home')
    def index():
        fname = this_dir + os.sep + "display.html"
        with open(fname) as fp:
            # print(fp.read())
            return fp.read()
        # return 'Hello World'


    def add_all_local_files_as_routes():

        def make_route(path):

            # print("long file path:", path)
            with open(path) as fp:
                # print(fp.read())
                files[path] = fp.read()

            def f():
                # print(files[path])
                return files[path]

            url = path[len(this_dir):]
            # print("url:", url)
            app.add_url_rule(url, url, f)

        for root, dirs, _ in os.walk(this_dir):
            # print('root:', root)
            for file in os.listdir(root):
                if file.startswith("."):
                    continue
                path = root + os.sep + file
                if os.path.isfile(path):
                    # print("making route for [{}]".format(path))
                    make_route(path)
            if 'CVS' in dirs:
                dirs.remove('CVS')  # don't visit CVS directories

    add_all_local_files_as_routes()

    return app



if __name__ == '__main__':
    app = get_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
