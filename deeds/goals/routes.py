import datetime
from flask import (render_template, url_for, flash,
                   redirect, request, abort, jsonify, Blueprint, current_app)
from flask_login import current_user, login_required
from deeds import db
from deeds.models import ActivityLog, ActivityType, Goal, Idea, Step
from .utils import compute_goal_progress

goals = Blueprint('goals', __name__)

# -------------------- Dashboard & Views --------------------


def serialize_goal(goal):
    return {
        "id": goal.id,
        "name": goal.name,
        "motivation": goal.motivation,
        "color": goal.color,
        "progress": compute_goal_progress(goal),
        "completed": goal.completed,
    }


def _coerce_activity_type_id(raw_activity_type_id):
    if raw_activity_type_id in (None, "", 0, "0"):
        return None

    activity_type = ActivityType.query.filter_by(
        id=int(raw_activity_type_id),
        user_id=current_user.id,
    ).first()
    if activity_type:
        return activity_type.id

    return None


def _apply_step_activity_fields(step, data):
    if "log_activity" in data:
        step.log_activity = bool(data.get("log_activity"))

    if "activity_type_id" in data:
        step.activity_type_id = _coerce_activity_type_id(data.get("activity_type_id")) if step.log_activity else None

    if "duration_minutes" in data:
        step.duration_seconds = int(float(data["duration_minutes"]) * 60) if data.get("duration_minutes") not in (None, "") else None

    if "distance_km" in data:
        step.distance_m = float(data["distance_km"]) * 1000 if data.get("distance_km") not in (None, "") else None

    if "weight_kg" in data:
        step.weight_kg = float(data["weight_kg"]) if data.get("weight_kg") not in (None, "") else None

    if "sets" in data:
        step.sets = int(data["sets"]) if data.get("sets") not in (None, "") else None

    if "reps" in data:
        step.reps = int(data["reps"]) if data.get("reps") not in (None, "") else None

    if "activity_notes" in data:
        step.activity_notes = data.get("activity_notes")
    if isinstance(step.activity_notes, str):
        step.activity_notes = step.activity_notes.strip() or None
    if not step.log_activity:
        step.duration_seconds = None
        step.distance_m = None
        step.weight_kg = None
        step.sets = None
        step.reps = None
        step.activity_notes = None


@goals.route("/dashboard")
@login_required
def dashboard():
    current_goals = Goal.query.filter_by(user_id=current_user.id, completed=False).all()
    completed_goals = Goal.query.filter_by(user_id=current_user.id, completed=True).all()

    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())

    steps = Step.query.join(Goal).filter(
        Goal.user_id == current_user.id,
        Step.date_for >= monday,
        Step.date_for < monday + datetime.timedelta(days=7)
    ).order_by(Step.date_for).all()

    # Serialize goals for Alpine
    serialized_goals = [serialize_goal(g) for g in current_goals]
    serialized_completed_goals = [serialize_goal(g) for g in completed_goals]

    return render_template(
        "dashboard.html",
        goals=serialized_goals,
        completed_goals=serialized_completed_goals,
        steps=steps,
        week_start=monday,
    )


@goals.route("/weeklyplanner")
@login_required
def weeklyplanner():
    goals_list = Goal.query.filter_by(user_id=current_user.id).all()
    activity_types = ActivityType.query.filter_by(user_id=current_user.id, archived=False).order_by(ActivityType.name.asc()).all()
    selected_goal_id = request.args.get("goal_id", type=int)
    return render_template(
        "weeklyplanner.html",
        goals=goals_list,
        selected_goal_id=selected_goal_id,
        activity_types=[
            {"id": activity_type.id, "name": activity_type.name}
            for activity_type in activity_types
        ],
    )


@goals.route('/milestones')
@login_required
def milestone_view():
    return redirect(url_for('goals.goal_planner'))


@goals.route('/planner')
@login_required
def planner_home():
    return render_template('planner.html', title="Planner Hub")


@goals.route('/goalplanner')
@login_required
def goal_planner():
    return render_template('goalplanner.html')


# -------------------- Goal Routes --------------------
@goals.route("/api/goals", methods=["GET"])
@login_required
def api_get_goals():
    goals = Goal.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        "id": g.id,
        "name": g.name,
        "description": g.description,
        "motivation": g.motivation,
        "color": g.color,
        "progress": compute_goal_progress(g)
    } for g in goals])

@goals.route("/api/goals/<int:goal_id>/progress", methods=["GET"])
@login_required
def api_goal_progress(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    if goal.user_id != current_user.id:
        abort(403)

    from .utils import compute_goal_progress  # ensure this is defined
    return jsonify({ "progress": compute_goal_progress(goal) })



@goals.route("/api/goals", methods=["POST"])
@login_required
def create_goal():
    data = request.get_json()
    name = data.get("name")
    if not name:
        return jsonify({"error": "Name is required"}), 400

    goal = Goal(
        name=name,
        description=data.get("description", ""),
        color=data.get("color", "#0d9488"),
        motivation=data.get("motivation", ""),
        user_id=current_user.id
    )
    db.session.add(goal)
    db.session.commit()

    return jsonify({
        "id": goal.id,
        "name": goal.name,
        "description": goal.description,
        "motivation": goal.motivation,
        "color": goal.color,
        "progress": compute_goal_progress(goal),
        "completed": goal.completed
    }), 201


@goals.route("/api/goals/<int:goal_id>", methods=["PUT", "PATCH"])
@login_required
def update_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    if goal.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()

    # Update only if field present in data
    if "name" in data:
        goal.name = data["name"]
    if "description" in data:
        goal.description = data["description"]
    if "color" in data:
        goal.color = data["color"]
    if "motivation" in data:
        goal.motivation = data["motivation"]
    if "completed" in data:
        goal.completed = data["completed"]

    db.session.commit()

    return jsonify({
        "id": goal.id,
        "name": goal.name,
        "description": goal.description,
        "motivation": goal.motivation,
        "color": goal.color,
        "progress": compute_goal_progress(goal),
        "completed": goal.completed
    })

@goals.route("/api/goals/<int:goal_id>", methods=["DELETE"])
@login_required
def delete_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    if goal.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    step_ids = [step.id for step in goal.steps]
    if step_ids:
        ActivityLog.query.filter(ActivityLog.step_id.in_(step_ids)).update({"step_id": None}, synchronize_session=False)
    db.session.delete(goal)
    db.session.commit()
    return jsonify({"message": "Goal and related steps deleted"})


@goals.route("/api/goals/full", methods=["GET"])
@login_required
def api_get_goals_with_steps():
    user_goals = Goal.query.filter_by(user_id=current_user.id).all()
    logged_activity_map = {
        step_id: log_id
        for step_id, log_id in db.session.query(ActivityLog.step_id, ActivityLog.id)
        .filter(ActivityLog.step_id.isnot(None), ActivityLog.user_id == current_user.id)
        .all()
    }

    def serialize_goal(g):
        return {
            "id": g.id,
            "name": g.name,
            "description": g.description,
            "motivation": g.motivation,
            "color": g.color,
            "completed": g.completed,
            "progress": compute_goal_progress(g),
            "completed_steps": [
                {
                    "id": step.id,
                    "title": step.title,
                    "completed_at": step.completed_at.isoformat() if step.completed_at else None,
                    "date_for": step.date_for.isoformat() if step.date_for else None,
                    "reflection": step.reflection,
                    "logged_activity_id": logged_activity_map.get(step.id),
                }
                for step in sorted(
                    [step for step in g.steps if step.completed],
                    key=lambda step: step.completed_at or step.date_for or step.created_at or datetime.datetime.min,
                    reverse=True,
                )
            ],
        }

    current_goals = [serialize_goal(g) for g in user_goals if not g.completed]
    completed_goals = [serialize_goal(g) for g in user_goals if g.completed]

    return jsonify({
        "current_goals": current_goals,
        "completed_goals": completed_goals
    })

@goals.route("/api/goals/<int:goal_id>/steps", methods=["GET", "POST"])
@login_required
def get_steps_for_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    if goal.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    if request.method == "POST":
        data = request.get_json()
        date_for = data.get("date_for")
        if isinstance(date_for, str):
            date_for = datetime.datetime.strptime(date_for, "%Y-%m-%d").date()

        step = Step(
            goal_id=goal.id,
            title=data.get("title", ""),
            value=data.get("value"),
            completed=data.get("completed", False),
            description=data.get("description", ""),
            reflection=data.get("reflection", ""),
            date_for=date_for
        )
        _apply_step_activity_fields(step, data)
        db.session.add(step)
        db.session.commit()
        return jsonify(step.to_dict()), 201

    offset = request.args.get("week_offset", default=0, type=int)
    today = datetime.date.today()
    start = today - datetime.timedelta(days=today.weekday()) + datetime.timedelta(weeks=offset)
    end = start + datetime.timedelta(days=6)

    steps = Step.query.filter(
        Step.goal_id == goal_id,
        Step.date_for >= start,
        Step.date_for <= end
    ).all()

    unique_steps = {s.id: s for s in steps}.values()
    return jsonify({"steps": [s.to_dict() for s in unique_steps]})

@goals.route("/api/goals/<int:goal_id>/complete", methods=["PATCH"])
@login_required
def complete_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    if goal.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    goal.completed = data.get("completed", False)
    db.session.commit()
    return jsonify({"id": goal.id, "completed": goal.completed})

@goals.route("/api/steps/<int:step_id>", methods=["PATCH", "PUT"])
@login_required
def update_step(step_id):
    step = Step.query.get_or_404(step_id)
    if step.goal.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    step.title = data.get("title", step.title)
    step.description = data.get("description", step.description)
    previous_completed = step.completed
    step.completed = data.get("completed", step.completed)
    if step.completed and not previous_completed:
        step.completed_at = datetime.datetime.utcnow()
    elif not step.completed:
        step.completed_at = None
    step.reflection = data.get("reflection", step.reflection)
    if "date_for" in data:
        step.date_for = datetime.datetime.strptime(data["date_for"], "%Y-%m-%d").date()
    _apply_step_activity_fields(step, data)

    db.session.commit()
    return jsonify(step.to_dict())


@goals.route("/api/steps/<int:step_id>", methods=["DELETE"])
@login_required
def delete_step(step_id):
    step = Step.query.get_or_404(step_id)
    if step.goal.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    ActivityLog.query.filter_by(step_id=step.id).update({"step_id": None})
    db.session.delete(step)
    db.session.commit()
    return jsonify({"message": "Step deleted"})


@goals.route("/api/steps/range")
@login_required
def get_steps_in_range():
    start = request.args.get('start')
    end = request.args.get('end')
    goal_id = request.args.get('goal_id', type=int)
    if not start or not end:
        return jsonify({'error': 'Missing start or end date'}), 400

    query = Step.query.join(Goal).filter(
        Step.date_for >= start,
        Step.date_for <= end,
        Goal.user_id == current_user.id
    )
    if goal_id is not None:
        query = query.filter(Step.goal_id == goal_id)

    steps = query.all()
    return jsonify({'steps': [step.to_dict() for step in steps]})


@goals.route("/api/ideas", methods=["GET", "POST"])
@login_required
def ideas_collection():
    if request.method == "POST":
        data = request.get_json() or {}
        title = (data.get("title") or "").strip()
        if not title:
            return jsonify({"error": "Title is required"}), 400

        idea = Idea(
            title=title,
            notes=(data.get("notes") or "").strip() or None,
            user_id=current_user.id,
        )
        db.session.add(idea)
        db.session.commit()
        return jsonify(idea.to_dict()), 201

    ideas = (
        Idea.query.filter_by(user_id=current_user.id)
        .order_by(Idea.created_at.desc())
        .all()
    )
    return jsonify({"ideas": [idea.to_dict() for idea in ideas]})


@goals.route("/api/ideas/<int:idea_id>", methods=["PUT", "PATCH", "DELETE"])
@login_required
def idea_detail(idea_id):
    idea = Idea.query.get_or_404(idea_id)
    if idea.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    if request.method == "DELETE":
        db.session.delete(idea)
        db.session.commit()
        return jsonify({"message": "Idea deleted"})

    data = request.get_json() or {}
    title = data.get("title")
    if title is not None:
        title = title.strip()
        if not title:
            return jsonify({"error": "Title is required"}), 400
        idea.title = title

    if "notes" in data:
        idea.notes = (data.get("notes") or "").strip() or None

    db.session.commit()
    return jsonify(idea.to_dict())
