def compute_goal_progress(goal):
    if not goal.steps:
        return 0.0

    completed = sum(1 for step in goal.steps if step.completed)
    progress = completed / len(goal.steps)
    return round(progress * 100.0, 1)
