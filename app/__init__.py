from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from celery import Celery
import celeryconfig
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')
    db.init_app(app)
   
    with app.app_context():
        db.create_all()
    return app
    
from app import models
app = create_app()
migrate = Migrate(app, db)

def make_celery(app):
    # create context tasks in celery
    celery = Celery(
        app.import_name,
        broker=app.config['BROKER_URL']
    )
    celery.config_from_object(celeryconfig)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask

    return celery

celery = make_celery(app)

@app.route('/', methods=['GET'])
def race():
    races_from_db = db.session.query(models.Race).all()
    return render_template('races.html', races_from_db=races_from_db)


app.run(host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8080)))
if __name__ == '__main__':
    app.run()
    app.debug(True)