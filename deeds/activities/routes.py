from datetime import date, datetime, time, timedelta

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from deeds.models import ActivityLog, ActivityType
from deeds import db
from deeds.activities.forms import ActivityLogForm, ActivityTypeForm
from deeds.activities.utils import (
    current_month_range,
    current_week_range,
    format_distance,
    format_duration,
    format_weight,
    summarize_logs,
)

activities = Blueprint("activities", __name__, url_prefix="/activities")


def _active_activity_types():
    return (
        ActivityType.query.filter_by(user_id=current_user.id, archived=False)
        .order_by(ActivityType.name.asc())
        .all()
    )


def _assign_log_form_defaults(form, activity_types):
    if request.method == "GET" and activity_types and not form.activity_type_id.data:
        form.activity_type_id.data = activity_types[0].id


def _populate_log_from_form(log, form):
    activity_type_id = form.activity_type_id.data
    if activity_type_id in ("", None):
        return None

    activity_type = ActivityType.query.filter_by(
        id=int(activity_type_id),
        user_id=current_user.id,
    ).first()
    if activity_type is None:
        return None

    log.activity_type_id = activity_type.id
    log.logged_at = datetime.combine(form.logged_on.data, time.min)
    log.duration_seconds = int(form.duration_minutes.data * 60) if form.duration_minutes.data is not None else None
    log.distance_m = float(form.distance_km.data * 1000) if form.distance_km.data is not None else None
    log.weight_kg = form.weight_kg.data
    log.sets = form.sets.data
    log.reps = form.reps.data
    log.notes = form.notes.data.strip() if form.notes.data else None
    return activity_type


@activities.route("/", methods=["GET", "POST"])
@login_required
def index():
    activity_types = _active_activity_types()
    quick_log_form = ActivityLogForm(prefix="quick")
    _assign_log_form_defaults(quick_log_form, activity_types)

    if quick_log_form.validate_on_submit():
        log = ActivityLog(user_id=current_user.id)
        activity_type = _populate_log_from_form(log, quick_log_form)
        if activity_type is None:
            flash("Please choose a valid activity type.", "danger")
            return redirect(url_for("activities.index"))

        db.session.add(log)
        db.session.commit()
        flash(f"Quick log saved for {activity_type.name}.", "success")
        return redirect(url_for("activities.index"))

    activity_type_count = len(activity_types)
    activity_log_count = ActivityLog.query.filter_by(user_id=current_user.id).count()
    latest_log = (
        ActivityLog.query.filter_by(user_id=current_user.id)
        .order_by(ActivityLog.logged_at.desc())
        .first()
    )
    recent_five_logs = (
        ActivityLog.query.filter_by(user_id=current_user.id)
        .order_by(ActivityLog.logged_at.desc())
        .limit(5)
        .all()
    )
    week_start, week_end = current_week_range()
    month_start, month_end = current_month_range()
    current_week_logs = ActivityLog.query.filter(
        ActivityLog.user_id == current_user.id,
        ActivityLog.logged_at >= datetime.combine(week_start, time.min),
        ActivityLog.logged_at < datetime.combine(week_end + timedelta(days=1), time.min),
    ).all()
    current_month_logs = ActivityLog.query.filter(
        ActivityLog.user_id == current_user.id,
        ActivityLog.logged_at >= datetime.combine(month_start, time.min),
        ActivityLog.logged_at < datetime.combine(month_end + timedelta(days=1), time.min),
    ).all()
    current_week_summary = summarize_logs(current_week_logs)
    current_month_summary = summarize_logs(current_month_logs)

    return render_template(
        "activities/index.html",
        title="Activities",
        activity_types=activity_types,
        quick_log_form=quick_log_form,
        activity_type_count=activity_type_count,
        activity_log_count=activity_log_count,
        recent_five_logs=recent_five_logs,
        latest_log=latest_log,
        current_week_summary=current_week_summary,
        current_month_summary=current_month_summary,
        format_duration=format_duration,
        format_distance=format_distance,
        format_weight=format_weight,
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
    activity_types = _active_activity_types()
    _assign_log_form_defaults(form, activity_types)

    if edit_log_id is not None:
        editing_log = ActivityLog.query.filter_by(id=edit_log_id, user_id=current_user.id).first()
        if editing_log and request.method == "GET":
            form.logged_on.data = editing_log.logged_at.date()
            form.activity_type_id.data = editing_log.activity_type_id
            form.duration_minutes.data = (editing_log.duration_seconds / 60) if editing_log.duration_seconds is not None else None
            form.distance_km.data = (editing_log.distance_m / 1000) if editing_log.distance_m is not None else None
            form.weight_kg.data = editing_log.weight_kg
            form.sets.data = editing_log.sets
            form.reps.data = editing_log.reps
            form.notes.data = editing_log.notes

    if form.validate_on_submit():
        if edit_log_id and editing_log:
            log = editing_log
            flash("Activity log updated.", "success")
        else:
            log = ActivityLog(user_id=current_user.id)
            flash("Activity log created.", "success")

        activity_type = _populate_log_from_form(log, form)
        if activity_type is None:
            flash("Please choose a valid activity type.", "danger")
            return redirect(url_for("activities.activity_logs"))

        if not edit_log_id or not editing_log:
            db.session.add(log)

        db.session.commit()
        return redirect(url_for("activities.activity_logs"))

    selected_type_id = request.args.get("type_id", type=int)
    start_date = request.args.get("start")
    end_date = request.args.get("end")
    period = request.args.get("period", "")

    if period == "week" and not start_date and not end_date:
        week_start, week_end = current_week_range()
        start_date = week_start.isoformat()
        end_date = week_end.isoformat()
    elif period == "month" and not start_date and not end_date:
        month_start, month_end = current_month_range()
        start_date = month_start.isoformat()
        end_date = month_end.isoformat()

    logs_query = ActivityLog.query.filter_by(user_id=current_user.id)
    if selected_type_id:
        logs_query = logs_query.filter(ActivityLog.activity_type_id == selected_type_id)
    if start_date:
        logs_query = logs_query.filter(ActivityLog.logged_at >= datetime.fromisoformat(start_date))
    if end_date:
        logs_query = logs_query.filter(ActivityLog.logged_at < datetime.fromisoformat(end_date) + timedelta(days=1))

    logs = logs_query.order_by(ActivityLog.logged_at.desc()).all()
    filtered_summary = summarize_logs(logs)

    return render_template(
        "activities/logs.html",
        title="Activity Logs",
        activity_logs=logs,
        activity_types=activity_types,
        form=form,
        editing_log=editing_log,
        selected_type_id=selected_type_id,
        start_date=start_date,
        end_date=end_date,
        period=period,
        filtered_summary=filtered_summary,
        format_duration=format_duration,
        format_distance=format_distance,
        format_weight=format_weight,
    )


@activities.route("/logs/<int:log_id>/delete", methods=["POST"])
@login_required
def delete_activity_log(log_id):
    activity_log = ActivityLog.query.filter_by(id=log_id, user_id=current_user.id).first_or_404()
    db.session.delete(activity_log)
    db.session.commit()
    flash("Activity log deleted.", "success")
    return redirect(url_for("activities.activity_logs"))


@activities.route("/logs/<int:log_id>/repeat", methods=["POST"])
@login_required
def repeat_activity_log(log_id):
    source_log = ActivityLog.query.filter_by(id=log_id, user_id=current_user.id).first_or_404()
    repeated_note_date = source_log.logged_at.strftime("%d %b %Y")
    repeated_log = ActivityLog(
        user_id=current_user.id,
        activity_type_id=source_log.activity_type_id,
        step_id=source_log.step_id,
        logged_at=datetime.combine(date.today(), time.min),
        duration_seconds=source_log.duration_seconds,
        distance_m=source_log.distance_m,
        weight_kg=source_log.weight_kg,
        sets=source_log.sets,
        reps=source_log.reps,
        notes=f"This is a repeated exercise completed on {repeated_note_date} - edit me",
    )
    db.session.add(repeated_log)
    db.session.commit()
    flash("Repeated the activity as a new log for today.", "success")
    return redirect(url_for("activities.activity_logs"))
