from flask import Blueprint, render_template
from flask_login import current_user, login_required

from deeds.models import ActivityLog, ActivityType

activities = Blueprint("activities", __name__, url_prefix="/activities")


@activities.route("/")
@login_required
def index():
    activity_type_count = ActivityType.query.filter_by(user_id=current_user.id, archived=False).count()
    activity_log_count = ActivityLog.query.filter_by(user_id=current_user.id).count()

    return render_template(
        "activities/index.html",
        title="Activities",
        activity_type_count=activity_type_count,
        activity_log_count=activity_log_count,
    )


@activities.route("/types")
@login_required
def activity_types():
    types = ActivityType.query.filter_by(user_id=current_user.id).order_by(ActivityType.name.asc()).all()
    return render_template("activities/types.html", title="Activity Types", activity_types=types)


@activities.route("/logs")
@login_required
def activity_logs():
    logs = (
        ActivityLog.query.filter_by(user_id=current_user.id)
        .order_by(ActivityLog.logged_at.desc())
        .all()
    )
    return render_template("activities/logs.html", title="Activity Logs", activity_logs=logs)
