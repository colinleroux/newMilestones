from datetime import datetime, time

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from deeds.models import ActivityLog, ActivityType
from deeds import db
from deeds.activities.forms import ActivityLogForm, ActivityTypeForm

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


@activities.route("/types", methods=["GET", "POST"])
@login_required
def activity_types():
    form = ActivityTypeForm()
    edit_type_id = request.args.get("edit", type=int)
    editing_type = None

    if edit_type_id is not None:
        editing_type = ActivityType.query.filter_by(id=edit_type_id, user_id=current_user.id).first()
        if editing_type:
            form.name.data = editing_type.name

    if form.validate_on_submit():
        if edit_type_id and editing_type:
            editing_type.name = form.name.data.strip()
            flash("Activity type updated.", "success")
        else:
            new_type = ActivityType(name=form.name.data.strip(), user_id=current_user.id)
            db.session.add(new_type)
            flash("Activity type created.", "success")

        db.session.commit()
        return redirect(url_for("activities.activity_types"))

    types = ActivityType.query.filter_by(user_id=current_user.id).order_by(ActivityType.name.asc()).all()
    return render_template(
        "activities/types.html",
        title="Activity Types",
        activity_types=types,
        form=form,
        editing_type=editing_type,
    )


@activities.route("/types/<int:type_id>/archive", methods=["POST"])
@login_required
def archive_activity_type(type_id):
    activity_type = ActivityType.query.filter_by(id=type_id, user_id=current_user.id).first_or_404()
    activity_type.archived = not activity_type.archived
    db.session.commit()
    flash("Activity type updated.", "success")
    return redirect(url_for("activities.activity_types"))


@activities.route("/types/<int:type_id>/delete", methods=["POST"])
@login_required
def delete_activity_type(type_id):
    activity_type = ActivityType.query.filter_by(id=type_id, user_id=current_user.id).first_or_404()
    if activity_type.logs:
        flash("You cannot delete an activity type that already has logs. Archive it instead.", "warning")
        return redirect(url_for("activities.activity_types"))

    db.session.delete(activity_type)
    db.session.commit()
    flash("Activity type deleted.", "success")
    return redirect(url_for("activities.activity_types"))


@activities.route("/logs", methods=["GET", "POST"])
@login_required
def activity_logs():
    form = ActivityLogForm()
    edit_log_id = request.args.get("edit", type=int)
    editing_log = None
    activity_types = ActivityType.query.filter_by(user_id=current_user.id, archived=False).order_by(ActivityType.name.asc()).all()

    if edit_log_id is not None:
        editing_log = ActivityLog.query.filter_by(id=edit_log_id, user_id=current_user.id).first()
        if editing_log:
            form.logged_on.data = editing_log.logged_at.date()
            form.activity_type_id.data = editing_log.activity_type_id
            form.duration_seconds.data = editing_log.duration_seconds
            form.distance_m.data = editing_log.distance_m
            form.weight_kg.data = editing_log.weight_kg
            form.reps.data = editing_log.reps
            form.notes.data = editing_log.notes

    if request.method == "GET" and activity_types and not form.activity_type_id.data:
        form.activity_type_id.data = activity_types[0].id

    if form.validate_on_submit():
        activity_type = ActivityType.query.filter_by(id=form.activity_type_id.data, user_id=current_user.id).first()
        if activity_type is None:
            flash("Please choose a valid activity type.", "danger")
            return redirect(url_for("activities.activity_logs"))

        logged_at = datetime.combine(form.logged_on.data, time.min)

        if edit_log_id and editing_log:
            log = editing_log
            flash("Activity log updated.", "success")
        else:
            log = ActivityLog(user_id=current_user.id)
            db.session.add(log)
            flash("Activity log created.", "success")

        log.activity_type_id = activity_type.id
        log.logged_at = logged_at
        log.duration_seconds = form.duration_seconds.data
        log.distance_m = form.distance_m.data
        log.weight_kg = form.weight_kg.data
        log.reps = form.reps.data
        log.notes = form.notes.data.strip() if form.notes.data else None

        db.session.commit()
        return redirect(url_for("activities.activity_logs"))

    logs = (
        ActivityLog.query.filter_by(user_id=current_user.id)
        .order_by(ActivityLog.logged_at.desc())
        .all()
    )
    return render_template(
        "activities/logs.html",
        title="Activity Logs",
        activity_logs=logs,
        activity_types=activity_types,
        form=form,
        editing_log=editing_log,
    )


@activities.route("/logs/<int:log_id>/delete", methods=["POST"])
@login_required
def delete_activity_log(log_id):
    activity_log = ActivityLog.query.filter_by(id=log_id, user_id=current_user.id).first_or_404()
    db.session.delete(activity_log)
    db.session.commit()
    flash("Activity log deleted.", "success")
    return redirect(url_for("activities.activity_logs"))
