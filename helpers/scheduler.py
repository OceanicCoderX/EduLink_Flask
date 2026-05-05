# ============================================================
# helpers/scheduler.py — Background Scheduled Notifications
# Jobs:
#   1. Daily 7:00 AM IST → Task notification (email + WhatsApp)
#   2. Every Sunday 7:00 AM IST → Weekly report email
#   3. 1st of every month 7:00 AM IST → Monthly report email
# ============================================================

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

IST = pytz.timezone('Asia/Kolkata')


# ── Email HTML Builders ──────────────────────────────────────

def build_task_email_html(user_name, today_tasks, overdue_tasks):
    today_rows = ''.join([
        f"""<tr>
              <td style="padding:10px 12px; border-bottom:1px solid #eee; color:#32325d; font-size:14px;">{t['title']}</td>
              <td style="padding:10px 12px; border-bottom:1px solid #eee; text-align:center;">
                <span style="background:#e8f5e9; color:#2dce89; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:600;">{t['priority'].upper()}</span>
              </td>
              <td style="padding:10px 12px; border-bottom:1px solid #eee; color:#8898aa; font-size:13px; text-align:center;">{t['due_date']}</td>
            </tr>"""
        for t in today_tasks
    ]) or '<tr><td colspan="3" style="padding:12px; color:#adb5bd; text-align:center;">No tasks due today 🎉</td></tr>'

    overdue_rows = ''.join([
        f"""<tr>
              <td style="padding:10px 12px; border-bottom:1px solid #eee; color:#32325d; font-size:14px;">{t['title']}</td>
              <td style="padding:10px 12px; border-bottom:1px solid #eee; text-align:center;">
                <span style="background:#fdecea; color:#f5365c; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:600;">{t['priority'].upper()}</span>
              </td>
              <td style="padding:10px 12px; border-bottom:1px solid #eee; color:#f5365c; font-size:13px; text-align:center;">{t['due_date']}</td>
            </tr>"""
        for t in overdue_tasks
    ]) or '<tr><td colspan="3" style="padding:12px; color:#adb5bd; text-align:center;">No overdue tasks 🎉</td></tr>'

    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0; padding:0; background:#f4f6fa; font-family:'Segoe UI', Arial, sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f6fa; padding:40px 0;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="background:white; border-radius:16px; overflow:hidden; box-shadow:0 4px 24px rgba(0,0,0,0.08);">
        
        <!-- Header -->
        <tr>
          <td style="background:linear-gradient(135deg, #5e72e4, #825ee4); padding:36px 40px; text-align:center;">
            <h1 style="color:white; margin:0; font-size:26px; font-weight:700; letter-spacing:-0.5px;">📚 EduLink</h1>
            <p style="color:rgba(255,255,255,0.85); margin:8px 0 0; font-size:15px;">Your Daily Task Reminder</p>
          </td>
        </tr>

        <!-- Greeting -->
        <tr>
          <td style="padding:32px 40px 20px;">
            <h2 style="color:#32325d; font-size:20px; margin:0 0 8px;">Good Morning, {user_name}! 👋</h2>
            <p style="color:#8898aa; font-size:15px; margin:0; line-height:1.6;">Here's your task summary for today. Stay focused and keep going! 💪</p>
          </td>
        </tr>

        <!-- Today's Tasks -->
        <tr>
          <td style="padding:0 40px 24px;">
            <h3 style="color:#5e72e4; font-size:15px; text-transform:uppercase; letter-spacing:1px; margin:0 0 12px; font-weight:700;">📅 Today's Tasks</h3>
            <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e9ecef; border-radius:10px; overflow:hidden;">
              <thead>
                <tr style="background:#f8f9fe;">
                  <th style="padding:10px 12px; text-align:left; color:#8898aa; font-size:12px; text-transform:uppercase; letter-spacing:0.5px;">Task</th>
                  <th style="padding:10px 12px; text-align:center; color:#8898aa; font-size:12px; text-transform:uppercase; letter-spacing:0.5px;">Priority</th>
                  <th style="padding:10px 12px; text-align:center; color:#8898aa; font-size:12px; text-transform:uppercase; letter-spacing:0.5px;">Due Date</th>
                </tr>
              </thead>
              <tbody>{today_rows}</tbody>
            </table>
          </td>
        </tr>

        <!-- Overdue Tasks -->
        <tr>
          <td style="padding:0 40px 32px;">
            <h3 style="color:#f5365c; font-size:15px; text-transform:uppercase; letter-spacing:1px; margin:0 0 12px; font-weight:700;">⚠️ Overdue Tasks</h3>
            <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #fde8ec; border-radius:10px; overflow:hidden;">
              <thead>
                <tr style="background:#fff5f7;">
                  <th style="padding:10px 12px; text-align:left; color:#8898aa; font-size:12px; text-transform:uppercase; letter-spacing:0.5px;">Task</th>
                  <th style="padding:10px 12px; text-align:center; color:#8898aa; font-size:12px; text-transform:uppercase; letter-spacing:0.5px;">Priority</th>
                  <th style="padding:10px 12px; text-align:center; color:#8898aa; font-size:12px; text-transform:uppercase; letter-spacing:0.5px;">Due Date</th>
                </tr>
              </thead>
              <tbody>{overdue_rows}</tbody>
            </table>
          </td>
        </tr>

        <!-- CTA Button -->
        <tr>
          <td style="padding:0 40px 40px; text-align:center;">
            <a href="http://127.0.0.1:5000/tasks" style="display:inline-block; background:linear-gradient(135deg, #5e72e4, #825ee4); color:white; text-decoration:none; padding:14px 36px; border-radius:50px; font-size:15px; font-weight:600; box-shadow:0 4px 15px rgba(94,114,228,0.4);">
              Open My Tasks →
            </a>
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="background:#f8f9fe; padding:20px 40px; text-align:center; border-top:1px solid #e9ecef;">
            <p style="color:#adb5bd; font-size:13px; margin:0;">You're receiving this because you're a member of EduLink 🎓</p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""


def build_report_email_html(user_name, timeframe, report):
    period = "This Week" if timeframe == 'weekly' else "This Month"
    tasks_rows = ''.join([f'<li style="padding:6px 0; border-bottom:1px solid #f0f0f0; color:#32325d; font-size:14px;">✅ {t["title"]} <span style="color:#adb5bd;font-size:12px;">({t["date"]})</span></li>' for t in report['tasks']]) or '<li style="color:#adb5bd; font-size:14px; padding:8px 0;">No tasks completed.</li>'
    notes_rows = ''.join([f'<li style="padding:6px 0; border-bottom:1px solid #f0f0f0; color:#32325d; font-size:14px;">📓 {n["title"]} <span style="color:#adb5bd;font-size:12px;">({n["date"]})</span></li>' for n in report['notes']]) or '<li style="color:#adb5bd; font-size:14px; padding:8px 0;">No notes created.</li>'
    class_rows = ''.join([f'<li style="padding:6px 0; border-bottom:1px solid #f0f0f0; color:#32325d; font-size:14px;">🏫 {c["name"]} <span style="color:#adb5bd;font-size:12px;">({c["date"]})</span></li>' for c in report['classrooms']]) or '<li style="color:#adb5bd; font-size:14px; padding:8px 0;">No classrooms joined.</li>'
    comm_rows = ''.join([f'<li style="padding:6px 0; border-bottom:1px solid #f0f0f0; color:#32325d; font-size:14px;">👥 {c["name"]} <span style="color:#adb5bd;font-size:12px;">({c["date"]})</span></li>' for c in report['communities']]) or '<li style="color:#adb5bd; font-size:14px; padding:8px 0;">No communities joined.</li>'

    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0; padding:0; background:#f4f6fa; font-family:'Segoe UI', Arial, sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f6fa; padding:40px 0;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="background:white; border-radius:16px; overflow:hidden; box-shadow:0 4px 24px rgba(0,0,0,0.08);">
        <tr>
          <td style="background:linear-gradient(135deg, #11cdef, #1171ef); padding:36px 40px; text-align:center;">
            <h1 style="color:white; margin:0; font-size:26px; font-weight:700;">📊 EduLink</h1>
            <p style="color:rgba(255,255,255,0.85); margin:8px 0 0; font-size:15px;">{timeframe.capitalize()} Progress Report — {period}</p>
          </td>
        </tr>
        <tr>
          <td style="padding:32px 40px 20px;">
            <h2 style="color:#32325d; font-size:20px; margin:0 0 8px;">Great work, {user_name}! 🌟</h2>
            <p style="color:#8898aa; font-size:15px; margin:0;">Here's a summary of your study activity {period.lower()}.</p>
          </td>
        </tr>
        <!-- Stats Row -->
        <tr>
          <td style="padding:0 40px 28px;">
            <table width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="text-align:center; background:#f0f2ff; border-radius:12px; padding:20px;">
                  <div style="font-size:32px; font-weight:700; color:#5e72e4;">{report['focus_minutes']}</div>
                  <div style="font-size:13px; color:#8898aa; margin-top:4px;">Focus Minutes</div>
                </td>
                <td width="12"></td>
                <td style="text-align:center; background:#f0fff8; border-radius:12px; padding:20px;">
                  <div style="font-size:32px; font-weight:700; color:#2dce89;">{len(report['tasks'])}</div>
                  <div style="font-size:13px; color:#8898aa; margin-top:4px;">Tasks Done</div>
                </td>
                <td width="12"></td>
                <td style="text-align:center; background:#fff8f0; border-radius:12px; padding:20px;">
                  <div style="font-size:32px; font-weight:700; color:#fb6340;">{len(report['notes'])}</div>
                  <div style="font-size:13px; color:#8898aa; margin-top:4px;">Notes Created</div>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <!-- Details -->
        <tr><td style="padding:0 40px;">
          <h3 style="color:#5e72e4; font-size:14px; text-transform:uppercase; letter-spacing:1px; margin:0 0 10px;">✅ Completed Tasks</h3>
          <ul style="list-style:none; margin:0 0 24px; padding:0 0 0 4px;">{tasks_rows}</ul>
          <h3 style="color:#fb6340; font-size:14px; text-transform:uppercase; letter-spacing:1px; margin:0 0 10px;">📓 Created Notes</h3>
          <ul style="list-style:none; margin:0 0 24px; padding:0 0 0 4px;">{notes_rows}</ul>
          <h3 style="color:#11cdef; font-size:14px; text-transform:uppercase; letter-spacing:1px; margin:0 0 10px;">🏫 Classrooms Joined</h3>
          <ul style="list-style:none; margin:0 0 24px; padding:0 0 0 4px;">{class_rows}</ul>
          <h3 style="color:#f5365c; font-size:14px; text-transform:uppercase; letter-spacing:1px; margin:0 0 10px;">👥 Communities Joined</h3>
          <ul style="list-style:none; margin:0 0 32px; padding:0 0 0 4px;">{comm_rows}</ul>
        </td></tr>
        <tr>
          <td style="padding:0 40px 40px; text-align:center;">
            <a href="http://127.0.0.1:5000/dashboard" style="display:inline-block; background:linear-gradient(135deg,#11cdef,#1171ef); color:white; text-decoration:none; padding:14px 36px; border-radius:50px; font-size:15px; font-weight:600;">
              View Dashboard →
            </a>
          </td>
        </tr>
        <tr>
          <td style="background:#f8f9fe; padding:20px 40px; text-align:center; border-top:1px solid #e9ecef;">
            <p style="color:#adb5bd; font-size:13px; margin:0;">EduLink — Smart Study Management 🎓</p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


# ── Data Fetch Functions ─────────────────────────────────────

def get_all_users():
    from db import get_db_connection
    mydb = get_db_connection()
    cursor = mydb.cursor()
    cursor.execute("SELECT user_id, profilename, email, whatsapp FROM users")
    users = [{'user_id': r[0], 'name': r[1], 'email': r[2], 'whatsapp': r[3]} for r in cursor.fetchall()]
    cursor.close()
    mydb.close()
    return users


def get_user_tasks(user_id):
    from db import get_db_connection
    from datetime import date
    mydb = get_db_connection()
    cursor = mydb.cursor()

    today = date.today()

    # Today's pending tasks
    cursor.execute("""
        SELECT task_title, priority, due_date FROM tasks
        WHERE user_id=%s AND status='pending' AND DATE(due_date)=%s
        ORDER BY priority DESC
    """, (user_id, today))
    today_tasks = [{'title': r[0], 'priority': r[1] or 'medium', 'due_date': str(r[2])} for r in cursor.fetchall()]

    # Overdue tasks (due before today, still pending)
    cursor.execute("""
        SELECT task_title, priority, due_date FROM tasks
        WHERE user_id=%s AND status='pending' AND DATE(due_date) < %s
        ORDER BY due_date ASC
    """, (user_id, today))
    overdue_tasks = [{'title': r[0], 'priority': r[1] or 'medium', 'due_date': str(r[2])} for r in cursor.fetchall()]

    cursor.close()
    mydb.close()
    return today_tasks, overdue_tasks


def get_user_report(user_id, timeframe='weekly'):
    from db import get_db_connection
    mydb = get_db_connection()
    cursor = mydb.cursor()

    interval = '1 MONTH' if timeframe == 'monthly' else '7 DAY'

    cursor.execute(f"SELECT COALESCE(SUM(duration_minutes), 0) FROM focus WHERE user_id=%s AND session_date >= DATE_SUB(CURDATE(), INTERVAL {interval})", (user_id,))
    focus_mins = int(cursor.fetchone()[0] or 0)

    cursor.execute(f"SELECT task_title, DATE(completed_date) FROM tasks WHERE user_id=%s AND status='completed' AND completed_date >= DATE_SUB(CURDATE(), INTERVAL {interval}) ORDER BY completed_date DESC", (user_id,))
    tasks = [{'title': r[0], 'date': str(r[1])} for r in cursor.fetchall()]

    cursor.execute(f"SELECT notes_title, created_date FROM notes WHERE user_id=%s AND created_date >= DATE_SUB(CURDATE(), INTERVAL {interval}) ORDER BY created_date DESC", (user_id,))
    notes = [{'title': r[0], 'date': str(r[1])} for r in cursor.fetchall()]

    cursor.execute(f"SELECT c.room_name, rm.join_date FROM room_members rm JOIN classroom c ON rm.room_id=c.room_id WHERE rm.member_id=%s AND rm.join_date >= DATE_SUB(CURDATE(), INTERVAL {interval}) ORDER BY rm.join_date DESC", (user_id,))
    classrooms = [{'name': r[0], 'date': str(r[1])} for r in cursor.fetchall()]

    cursor.execute(f"SELECT c.group_name, gm.join_date FROM group_members gm JOIN community c ON gm.group_id=c.group_id WHERE gm.member_id=%s AND gm.join_date >= DATE_SUB(CURDATE(), INTERVAL {interval}) ORDER BY gm.join_date DESC", (user_id,))
    communities = [{'name': r[0], 'date': str(r[1])} for r in cursor.fetchall()]

    cursor.close()
    mydb.close()
    return {'focus_minutes': focus_mins, 'tasks': tasks, 'notes': notes, 'classrooms': classrooms, 'communities': communities}


# ── Job Functions ────────────────────────────────────────────

def job_daily_task_notification(app):
    """Send daily task email + WhatsApp to all users at 7 AM IST."""
    from helpers.notifications import send_email, send_whatsapp
    print("[Scheduler] Running daily task notification job...")
    users = get_all_users()
    with app.app_context():
        for user in users:
            today_tasks, overdue_tasks = get_user_tasks(user['user_id'])
            # Only notify if there are any tasks
            if not today_tasks and not overdue_tasks:
                continue

            # Email
            if user['email']:
                html = build_task_email_html(user['name'], today_tasks, overdue_tasks)
                try:
                    from flask_mail import Mail, Message
                    from config import MAIL_DEFAULT_SENDER
                    mail = Mail(app)
                    msg = Message(
                        subject="📅 EduLink — Your Daily Task Reminder",
                        recipients=[user['email']],
                        html=html,
                        sender=MAIL_DEFAULT_SENDER
                    )
                    mail.send(msg)
                    print(f"[Scheduler] Task email sent to {user['email']}")
                except Exception as e:
                    print(f"[Scheduler] Email error for {user['email']}: {e}")

            # WhatsApp
            if user.get('whatsapp'):
                number = user['whatsapp']
                if not number.startswith('+'):
                    number = '+91' + number
                today_list = '\n'.join([f"• {t['title']} ({t['due_date']})" for t in today_tasks]) or 'No tasks today 🎉'
                overdue_list = '\n'.join([f"• {t['title']} ({t['due_date']})" for t in overdue_tasks]) or 'None 🎉'
                wa_msg = (
                    f"📚 *EduLink — Daily Reminder*\n\n"
                    f"Good Morning, {user['name']}! 👋\n\n"
                    f"📅 *Today's Tasks:*\n{today_list}\n\n"
                    f"⚠️ *Overdue Tasks:*\n{overdue_list}\n\n"
                    f"Stay focused and productive! 💪\n_EduLink Team_"
                )
                send_whatsapp(number, wa_msg)


def job_weekly_report(app):
    """Send weekly progress report on Sunday at 7 AM IST."""
    from helpers.notifications import send_whatsapp
    print("[Scheduler] Running weekly report job...")
    users = get_all_users()
    with app.app_context():
        for user in users:
            report = get_user_report(user['user_id'], 'weekly')

            if user['email']:
                try:
                    from flask_mail import Mail, Message
                    from config import MAIL_DEFAULT_SENDER
                    mail = Mail(app)
                    html = build_report_email_html(user['name'], 'weekly', report)
                    msg = Message(
                        subject="📊 EduLink — Your Weekly Progress Report",
                        recipients=[user['email']],
                        html=html,
                        sender=MAIL_DEFAULT_SENDER
                    )
                    mail.send(msg)
                    print(f"[Scheduler] Weekly report email sent to {user['email']}")
                except Exception as e:
                    print(f"[Scheduler] Email error: {e}")

            if user.get('whatsapp'):
                number = user['whatsapp']
                if not number.startswith('+'):
                    number = '+91' + number
                wa_msg = (
                    f"📊 *EduLink — Weekly Report*\n\n"
                    f"Hi {user['name']}! Here's your week in review:\n\n"
                    f"⏱ Focus Time: {report['focus_minutes']} mins\n"
                    f"✅ Tasks Done: {len(report['tasks'])}\n"
                    f"📓 Notes Created: {len(report['notes'])}\n"
                    f"🏫 Classrooms: {len(report['classrooms'])}\n"
                    f"👥 Communities: {len(report['communities'])}\n\n"
                    f"Keep up the great work! 🌟\n_EduLink Team_"
                )
                send_whatsapp(number, wa_msg)


def job_monthly_report(app):
    """Send monthly progress report on 1st of every month at 7 AM IST."""
    from helpers.notifications import send_whatsapp
    print("[Scheduler] Running monthly report job...")
    users = get_all_users()
    with app.app_context():
        for user in users:
            report = get_user_report(user['user_id'], 'monthly')

            if user['email']:
                try:
                    from flask_mail import Mail, Message
                    from config import MAIL_DEFAULT_SENDER
                    mail = Mail(app)
                    html = build_report_email_html(user['name'], 'monthly', report)
                    msg = Message(
                        subject="📊 EduLink — Your Monthly Progress Report",
                        recipients=[user['email']],
                        html=html,
                        sender=MAIL_DEFAULT_SENDER
                    )
                    mail.send(msg)
                    print(f"[Scheduler] Monthly report email sent to {user['email']}")
                except Exception as e:
                    print(f"[Scheduler] Email error: {e}")

            if user.get('whatsapp'):
                number = user['whatsapp']
                if not number.startswith('+'):
                    number = '+91' + number
                wa_msg = (
                    f"📊 *EduLink — Monthly Report*\n\n"
                    f"Hi {user['name']}! Your month in review:\n\n"
                    f"⏱ Focus Time: {report['focus_minutes']} mins\n"
                    f"✅ Tasks Completed: {len(report['tasks'])}\n"
                    f"📓 Notes Created: {len(report['notes'])}\n"
                    f"🏫 Classrooms: {len(report['classrooms'])}\n"
                    f"👥 Communities: {len(report['communities'])}\n\n"
                    f"Amazing progress! Keep going! 🚀\n_EduLink Team_"
                )
                send_whatsapp(number, wa_msg)


# ── Scheduler Initializer ────────────────────────────────────

def init_scheduler(app):
    """Start APScheduler with all notification jobs."""
    scheduler = BackgroundScheduler(timezone=IST)

    # Daily task reminder — 7:00 AM IST every day
    scheduler.add_job(
        func=job_daily_task_notification,
        args=[app],
        trigger=CronTrigger(hour=7, minute=0, timezone=IST),
        id='daily_task_notif',
        replace_existing=True
    )

    # Weekly report — Every Sunday 7:00 AM IST (day_of_week=6 = Sunday)
    scheduler.add_job(
        func=job_weekly_report,
        args=[app],
        trigger=CronTrigger(day_of_week=6, hour=7, minute=0, timezone=IST),
        id='weekly_report',
        replace_existing=True
    )

    # Monthly report — 1st of every month 7:00 AM IST
    scheduler.add_job(
        func=job_monthly_report,
        args=[app],
        trigger=CronTrigger(day=1, hour=7, minute=0, timezone=IST),
        id='monthly_report',
        replace_existing=True
    )

    scheduler.start()
    print("[Scheduler] All notification jobs scheduled successfully.")
    return scheduler
