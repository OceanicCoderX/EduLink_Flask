# ============================================================
# helpers/stacks.py — Centralized Stack Award System
# Rule 8: All stack awards go through this one function
# ============================================================

from db import get_db_connection
from datetime import date


def award_stack(user_id: int, reason: str, amount: int = 1) -> dict:
    """
    Award stacks to a user and log it in stack_history.

    Usage:
        award_stack(user_id, 'task_complete')
        award_stack(user_id, 'pomodoro_done')
        award_stack(user_id, 'room_created')
        award_stack(user_id, 'daily_login')
        award_stack(user_id, 'room_notes_saved')
        award_stack(user_id, 'focus_interval', amount=2)

    Returns: { success, new_total, awarded }
    """
    try:
        mydb   = get_db_connection()
        cursor = mydb.cursor()

        # Update user's total stacks
        cursor.execute(
            "UPDATE users SET stacks = stacks + %s WHERE user_id = %s",
            (amount, user_id)
        )

        # Log the stack event (safe — table may not exist before migration)
        try:
            cursor.execute(
                "INSERT INTO stack_history (user_id, reason, stacks_given) VALUES (%s, %s, %s)",
                (user_id, reason, amount)
            )
        except Exception:
            pass

        # Log activity
        reason_labels = {
            'task_complete':     'Completed a task',
            'pomodoro_done':     'Completed a Pomodoro session',
            'room_created':      'Created/hosted a study room',
            'daily_login':       'Daily login bonus',
            'room_notes_saved':  'Saved collaborative room notes',
            'focus_interval':    f'Active focus: 10-minute interval',
        }
        label = reason_labels.get(reason, reason.replace('_', ' ').title())

        try:
            cursor.execute(
                "INSERT INTO activity_log (user_id, action_type, action_desc) VALUES (%s, %s, %s)",
                (user_id, 'stack', f'+{amount} Stack — {label}')
            )
        except Exception:
            pass

        mydb.commit()

        # Get updated total
        cursor.execute("SELECT stacks, streak FROM users WHERE user_id = %s", (user_id,))
        row = cursor.fetchone()
        new_total = row[0] if row else 0
        streak    = row[1] if row else 0

        cursor.close()
        mydb.close()

        return {
            'success':   True,
            'new_total': new_total,
            'awarded':   amount,
            'streak':    streak
        }

    except Exception as e:
        print(f"[Stacks] Error awarding stack: {e}")
        return {'success': False, 'error': str(e), 'new_total': 0, 'awarded': 0}


def log_activity(user_id: int, action_type: str, desc: str) -> None:
    """Log an activity for the profile's Recent Activity section (safe — silent fail before migration)."""
    try:
        mydb   = get_db_connection()
        cursor = mydb.cursor()
        cursor.execute(
            "INSERT INTO activity_log (user_id, action_type, action_desc) VALUES (%s, %s, %s)",
            (user_id, action_type, desc)
        )
        mydb.commit()
        cursor.close()
        mydb.close()
    except Exception:
        pass  # Silently skip if table not yet created


def handle_daily_login(user_id: int) -> dict:
    """
    Check if user already got their daily stack today.
    If not → award +1 + update streak.
    Safe — does nothing if columns don't exist yet (pre-migration).
    """
    try:
        today  = date.today()
        mydb   = get_db_connection()
        cursor = mydb.cursor()

        cursor.execute(
            "SELECT last_login_date, streak FROM users WHERE user_id = %s",
            (user_id,)
        )
        row = cursor.fetchone()

        if not row:
            cursor.close()
            mydb.close()
            return {'awarded': False}

        last_login, streak = row[0], row[1]

        awarded = False
        if last_login != today:
            # Check streak continuity
            from datetime import timedelta
            yesterday  = today - timedelta(days=1)
            new_streak = (streak + 1) if last_login == yesterday else 1

            cursor.execute(
                "UPDATE users SET last_login_date=%s, streak=%s WHERE user_id=%s",
                (today, new_streak, user_id)
            )
            mydb.commit()
            cursor.close()
            mydb.close()

            result          = award_stack(user_id, 'daily_login', 1)
            result['streak']  = new_streak
            result['awarded'] = True
            return result

        cursor.close()
        mydb.close()
        return {'awarded': False, 'streak': streak}

    except Exception as e:
        # Columns may not exist before migration — silently skip
        return {'awarded': False}


def get_user_stacks(user_id: int) -> int:
    """Quick helper to get a user's current stack total."""
    try:
        mydb   = get_db_connection()
        cursor = mydb.cursor()
        cursor.execute("SELECT stacks FROM users WHERE user_id=%s", (user_id,))
        row = cursor.fetchone()
        cursor.close()
        mydb.close()
        return row[0] if row else 0
    except Exception:
        return 0
