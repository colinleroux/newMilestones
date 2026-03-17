def compute_goal_progress(goal):
    if not goal.milestones:
        return 0.0

    progress = 0.0
    for milestone in goal.milestones:
        steps = milestone.steps
        if not steps:
            continue
        completed = sum(1 for s in steps if s.completed)
        step_progress = completed / len(steps)
        progress += (milestone.percentage / 100.0) * step_progress

    return round(progress * 100.0, 1)  # percent out of 100
