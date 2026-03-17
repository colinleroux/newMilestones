import datetime
from flask import (render_template, url_for, flash,
                   redirect, request, abort, jsonify, Blueprint, current_app)
from flask_login import current_user, login_required
from deeds import db
from deeds.models import Goal, Step, Milestone
from .utils import compute_goal_progress

goals = Blueprint('goals', __name__)

# -------------------- Dashboard & Views --------------------


def serialize_goal(goal):
    return {
        "id": goal.id,
        "name": goal.name,
        "motivation": goal.motivation,
        "color": goal.color,
        "progress": compute_goal_progress(goal)
    }


@goals.route("/dashboard")
@login_required
def dashboard():
    goals_list = Goal.query.filter_by(user_id=current_user.id, completed=False).all()

    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())

    steps = Step.query.join(Goal).filter(
        Goal.user_id == current_user.id,
        Step.date_for >= monday,
        Step.date_for < monday + datetime.timedelta(days=7)
    ).order_by(Step.date_for).all()

    # Serialize goals for Alpine
    serialized_goals = [serialize_goal(g) for g in goals_list]

    return render_template("dashboard.html", goals=serialized_goals, steps=steps, week_start=monday)


@goals.route("/weeklyplanner")
@login_required
def weeklyplanner():
    goals_list = Goal.query.filter_by(user_id=current_user.id).all()
    return render_template("weeklyplanner.html", goals=goals_list)


@goals.route('/milestones')
@login_required
def milestone_view():
    goals_with_milestones = Goal.query.filter_by(user_id=current_user.id).all()
    goal_data = []

    for goal in goals_with_milestones:
        milestones = [{
            'id': m.id,
            'name': m.name,
            'deadline': m.deadline.strftime('%Y-%m-%d') if m.deadline else None,
            'achieved': m.achieved,
            'percentage': m.percentage,
            'color': m.color,
            'created_at': m.created_at.strftime('%Y-%m-%d %H:%M:%S') if m.created_at else None,
            'description': m.description
        } for m in goal.milestones]

        goal_data.append({
            'id': goal.id,
            'name': goal.name,
            'color': goal.color,
            'milestones': milestones
        })

    return render_template('milestones.html', goal_data=goal_data)


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
        "milestones_enabled": g.milestones_enabled,
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
        milestones_enabled=data.get("milestones_enabled", False),
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
        "milestones_enabled": goal.milestones_enabled
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
    if "milestones_enabled" in data:
        goal.milestones_enabled = data["milestones_enabled"]
    if "completed" in data:
        goal.completed = data["completed"]

    db.session.commit()

    return jsonify({
        "id": goal.id,
        "name": goal.name,
        "description": goal.description,
        "motivation": goal.motivation,
        "color": goal.color,
        "milestones_enabled": goal.milestones_enabled,
        "completed": goal.completed
    })

@goals.route("/api/goals/<int:goal_id>", methods=["DELETE"])
@login_required
def delete_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    if goal.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    db.session.delete(goal)
    db.session.commit()
    return jsonify({"message": "Goal and related steps deleted"})


@goals.route("/api/goals/full", methods=["GET"])
@login_required
def api_get_goals_with_milestones():
    user_goals = Goal.query.filter_by(user_id=current_user.id).all()

    def serialize_goal(g):
        return {
            "id": g.id,
            "name": g.name,
            "description": g.description,
            "motivation": g.motivation,
            "color": g.color,
            "milestones_enabled": g.milestones_enabled,
            "completed": g.completed,
            "milestones": [{
                "id": m.id,
                "name": m.name,
                "description": m.description,
                "percentage": m.percentage,
                "deadline": m.deadline.isoformat() if m.deadline else None
            } for m in g.milestones]
        }

    current_goals = [serialize_goal(g) for g in user_goals if not g.completed]
    completed_goals = [serialize_goal(g) for g in user_goals if g.completed]

    return jsonify({
        "current_goals": current_goals,
        "completed_goals": completed_goals
    })

@goals.route("/api/goals/<int:goal_id>/steps", methods=["GET"])
@login_required
def get_steps_for_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    if goal.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

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


# -------------------- Milestone Routes --------------------
@goals.route('/milestones', methods=['POST'])
@login_required
def add_milestone():
    data = request.get_json()
    goal = Goal.query.get_or_404(data.get('goal_id'))
    if goal.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    milestone = Milestone(
        name=data.get('name'),
        color=data.get('color'),
        percentage=float(data.get('percentage', 0)),
        achieved=False,
        goal_id=goal.id
    )

    # Handle deadline if provided
    if 'deadline' in data and data['deadline']:
        try:
            milestone.deadline = datetime.datetime.strptime(data['deadline'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid deadline format'}), 400

    db.session.add(milestone)
    db.session.commit()

    return jsonify({
        'id': milestone.id,
        'name': milestone.name,
        'color': milestone.color,
        'percentage': milestone.percentage,
        'achieved': milestone.achieved,
        'deadline': milestone.deadline.isoformat() if milestone.deadline else None
    }), 201

@goals.route('/milestones/<int:milestone_id>', methods=['PUT'])
@login_required
def update_milestone(milestone_id):
    milestone = Milestone.query.get_or_404(milestone_id)
    if milestone.goal.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    milestone.name = data.get('name', milestone.name)
    milestone.percentage = data.get('percentage', milestone.percentage)
    milestone.color = data.get('color', milestone.color)
    if 'deadline' in data and data['deadline']:
        milestone.deadline = datetime.datetime.strptime(data['deadline'], '%Y-%m-%d').date()
    else:
        milestone.deadline = None
    db.session.commit()

    return jsonify({
        'id': milestone.id,
        'name': milestone.name,
        'percentage': milestone.percentage,
        'deadline': milestone.deadline.isoformat() if milestone.deadline else None,
        'color': milestone.color
    })


@goals.route('/milestones/<int:milestone_id>', methods=['DELETE'])
@login_required
def delete_milestone(milestone_id):
    milestone = Milestone.query.get_or_404(milestone_id)
    if milestone.goal.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    db.session.delete(milestone)
    db.session.commit()
    return jsonify({'success': True})


@goals.route('/milestones/<int:milestone_id>/percentage', methods=['PATCH'])
@login_required
def update_milestone_percentage(milestone_id):
    data = request.get_json()
    new_percentage = data.get('percentage')

    if new_percentage is None:
        return jsonify({'error': 'Missing percentage'}), 400

    milestone = Milestone.query.get_or_404(milestone_id)

    # Optional: check if the current user owns this milestone through the goal
    # if milestone.goal.user_id != current_user.id:
    #     return jsonify({'error': 'Unauthorized'}), 403

    milestone.percentage = new_percentage
    db.session.commit()
    return jsonify({'success': True, 'percentage': milestone.percentage}), 200
# -------------------- Step Routes --------------------
@goals.route('/api/milestones/<int:milestone_id>/steps', methods=['POST'])
@login_required
def add_step_to_milestone(milestone_id):
    milestone = Milestone.query.get_or_404(milestone_id)
    if milestone.goal.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    date_for = data.get('date_for')
    if isinstance(date_for, str):
        date_for = datetime.datetime.strptime(date_for, "%Y-%m-%d").date()

    step = Step(
        milestone_id=milestone.id,
        goal_id=milestone.goal_id,
        title=data.get('title', ''),
        value=data.get('value'),
        completed=data.get('completed', False),
        description=data.get('description', ''),
        reflection=data.get('reflection', ''),
        date_for=date_for
    )
    db.session.add(step)
    db.session.commit()

    return jsonify(step.to_dict()), 201


@goals.route("/api/milestones/<int:milestone_id>/steps", methods=["GET"])
@login_required
def get_steps_for_milestone(milestone_id):
    milestone = Milestone.query.get_or_404(milestone_id)
    if milestone.goal.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    offset = request.args.get("week_offset", default=0, type=int)
    today = datetime.date.today()
    start = today - datetime.timedelta(days=today.weekday()) + datetime.timedelta(weeks=offset)
    end = start + datetime.timedelta(days=6)

    steps = Step.query.filter(
        Step.milestone_id == milestone.id,
        Step.date_for >= start,
        Step.date_for <= end

    ).all()
    unique_steps = {s.id: s for s in steps}.values()
    return jsonify({"steps": [s.to_dict() for s in unique_steps]})


@goals.route("/api/steps/<int:step_id>", methods=["PATCH", "PUT"])
@login_required
def update_step(step_id):
    step = Step.query.get_or_404(step_id)
    if step.goal.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    step.title = data.get("title", step.title)
    step.description = data.get("description", step.description)
    step.completed = data.get("completed", step.completed)
    step.reflection = data.get("reflection", step.reflection)
    if "date_for" in data:
        step.date_for = datetime.datetime.strptime(data["date_for"], "%Y-%m-%d").date()

    db.session.commit()
    return jsonify(step.to_dict())


@goals.route("/api/steps/<int:step_id>", methods=["DELETE"])
@login_required
def delete_step(step_id):
    step = Step.query.get_or_404(step_id)
    if step.goal.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    db.session.delete(step)
    db.session.commit()
    return jsonify({"message": "Step deleted"})


@goals.route("/api/steps/range")
@login_required
def get_steps_in_range():
    start = request.args.get('start')
    end = request.args.get('end')
    if not start or not end:
        return jsonify({'error': 'Missing start or end date'}), 400

    steps = Step.query.join(Goal).filter(
        Step.date_for >= start,
        Step.date_for <= end,
        Goal.user_id == current_user.id
    ).all()
    return jsonify({'steps': [step.to_dict() for step in steps]})
