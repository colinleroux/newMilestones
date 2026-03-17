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
    milestones_enabled = db.Column(db.Boolean, default=False)

    completed = db.Column(db.Boolean, default=False)  # ✅ New field

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    steps = db.relationship("Step", backref="goal", cascade="all, delete-orphan")
    milestones = db.relationship('Milestone', backref='goal', cascade='all, delete-orphan')

    def __repr__(self):
        return f"Goal('{self.name}', color='{self.color}', completed={self.completed})"


class Milestone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    percentage = db.Column(db.Float, nullable=False, default=0.0)  # Contribution to goal
    color = db.Column(db.String(20), default="#60A5FA")
    achieved = db.Column(db.Boolean, default=False)
    deadline = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    steps = db.relationship('Step', backref='milestone', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Milestone {self.name} ({self.percentage}%) for Goal {self.goal_id}>"

class Step(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    value = db.Column(db.Float, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    reflection = db.Column(db.Text, nullable=True)
    order = db.Column(db.Integer, nullable=True)
    date_for = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.id'), nullable=False)
    milestone_id = db.Column(db.Integer, db.ForeignKey('milestone.id'), nullable=True)  # Nullable for catch-all or direct-to-goal steps
    percentage = db.Column(db.Float, nullable=True)  # % contribution toward milestone

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'value': self.value,
            'completed': self.completed,
            'reflection': self.reflection,
            'order': self.order,
            'date_for': self.date_for.isoformat() if self.date_for else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'goal_id': self.goal_id,
            'goal_name': self.goal.name if self.goal else None,
            'goal_color': self.goal.color if self.goal else "#ccc",
            'milestone_id': self.milestone_id,
            'milestone_name': self.milestone.name if self.milestone else None,
            'milestone_percentage': self.percentage,
        }

    def __repr__(self):
        return f"<Step {self.id}: {self.title} (Goal {self.goal_id})>"
