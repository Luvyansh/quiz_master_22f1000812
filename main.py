from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from applications.config import Config
from applications.database import db
from applications.models import User, Role, UserRoles, Subject, Chapter, Quiz, Question, Score
from datetime import datetime

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    Migrate(app, db)
    
    with app.app_context():
        db.create_all()
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(name='admin')
            db.session.add(admin_role)
            db.session.commit()
        admin_user = User.query.filter_by(email='admin@qm.com').first()
        if not admin_user:
            admin_user = User(email='admin@qm.com', password='admin', name='Quiz Master', qualifications='Admin', dob=datetime.strptime('2000-01-01', '%Y-%m-%d').date())
            admin_user.roles.append(admin_role)
            db.session.add(admin_user)
            db.session.commit()
        student_role = Role.query.filter_by(name='user').first()
        if not student_role:
            student_role = Role(name='user')
            db.session.add(student_role)
            db.session.commit()
        subject = Subject.query.filter_by(name='Computer Science Engineering (CSE)').first()
        if not subject:
            subject = Subject(name='Computer Science Engineering (CSE)', description='The study of computers and computational systems, encompassing the theory, design, development, and application of software and hardware, with areas like algorithms, programming, and data structures being key components.')
            db.session.add(subject)
            db.session.commit()
    return app

app = create_app()

from applications.routes import *
from controllers.controllers import *

if __name__ == "__main__":
    app.run(debug=True)