from flask import Flask, render_template
from app.extensions import db, migrate
from app.views import *
from app.api.list_of_apis import *
from app.lib.log import *
from app.lib.import_csv_from_aws import import_csv_from_aws
import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")

def create_app():
    app = Flask(__name__, static_folder="./static", template_folder="./static")
    app.config.from_pyfile('./app/config.py', silent=True)

    register_blueprint(app)
    register_extension(app)

    with app.app_context():
        db.create_all()
        db.session.commit()
    return app


def register_blueprint(app):
    app.register_blueprint(view_blueprint)
    app.register_blueprint(race_blueprint)
    app.register_blueprint(results_blueprint)
    app.register_blueprint(qualifying_blueprint)
    app.register_blueprint(laptimes_blueprint)
    app.register_blueprint(pitstops_blueprint)

def register_extension(app):
    db.init_app(app)
    migrate.init_app(app)


app = create_app()

@app.cli.command()
def get_results():
    get_results_archive()

@app.cli.command()
def get_qual():
    get_qual_archive()

@app.cli.command()
def get_laptimes():
    get_laptimes_archive()    

@app.cli.command()
def get_pitstops():
    get_pitstops_archive()    

@app.cli.command()
def get_aws():
    import_csv_from_aws()  

@app.cli.command()
def recreate_db():
    db.drop_all()
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)