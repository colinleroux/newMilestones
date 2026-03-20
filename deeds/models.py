from datetime import datetime
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from flask import current_app
from deeds import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id}, salt="reset_password")

    @staticmethod
    def verify_reset_token(token, max_age=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, salt="reset_password", max_age=max_age)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True))

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image = db.Column(db.String(20), nullable=True, default='default.jpg')
    tags = db.relationship('Tag', secondary=post_tags, lazy='subquery',
                           backref=db.backref('posts', lazy=True))

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"Tag('{self.name}')"

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(20), default="#0d9488")
    motivation = db.Column(db.Text, nullable=True)

    completed = db.Column(db.Boolean, default=False)  # ✅ New field

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    steps = db.relationship("Step", backref="goal", cascade="all, delete-orphan")

    def __repr__(self):
        return f"Goal('{self.name}', color='{self.color}', completed={self.completed})"


class Idea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"Idea('{self.title}')"


class Step(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    value = db.Column(db.Float, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    reflection = db.Column(db.Text, nullable=True)
    order = db.Column(db.Integer, nullable=True)
    date_for = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.id'), nullable=False)
    percentage = db.Column(db.Float, nullable=True)
    log_activity = db.Column(db.Boolean, default=False)
    activity_type_id = db.Column(db.Integer, db.ForeignKey('activity_type.id'), nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=True)
    distance_m = db.Column(db.Float, nullable=True)
    weight_kg = db.Column(db.Float, nullable=True)
    sets = db.Column(db.Integer, nullable=True)
    reps = db.Column(db.Integer, nullable=True)
    activity_notes = db.Column(db.Text, nullable=True)

    def to_dict(self):
        linked_log = ActivityLog.query.filter_by(step_id=self.id).order_by(ActivityLog.logged_at.desc()).first()
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'value': self.value,
            'completed': self.completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'reflection': self.reflection,
            'order': self.order,
            'date_for': self.date_for.isoformat() if self.date_for else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'goal_id': self.goal_id,
            'goal_name': self.goal.name if self.goal else None,
            'goal_color': self.goal.color if self.goal else "#ccc",
            'log_activity': self.log_activity,
            'activity_type_id': self.activity_type_id,
            'duration_seconds': self.duration_seconds,
            'distance_m': self.distance_m,
            'weight_kg': self.weight_kg,
            'sets': self.sets,
            'reps': self.reps,
            'activity_notes': self.activity_notes,
            'logged_activity_id': linked_log.id if linked_log else None,
        }

    def __repr__(self):
        return f"<Step {self.id}: {self.title} (Goal {self.goal_id})>"


class ActivityType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(20), nullable=False, default="#0f766e")
    archived = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    logs = db.relationship("ActivityLog", backref="activity_type", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ActivityType {self.id}: {self.name}>"


class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_type_id = db.Column(db.Integer, db.ForeignKey('activity_type.id'), nullable=False)
    step_id = db.Column(db.Integer, db.ForeignKey('step.id'), nullable=True)
    logged_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    duration_seconds = db.Column(db.Integer, nullable=True)
    distance_m = db.Column(db.Float, nullable=True)
    weight_kg = db.Column(db.Float, nullable=True)
    sets = db.Column(db.Integer, nullable=True)
    reps = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<ActivityLog {self.id}: type={self.activity_type_id} user={self.user_id}>"
