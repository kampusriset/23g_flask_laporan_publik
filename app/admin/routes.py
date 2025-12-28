from functools import wraps

from flask import abort, render_template
from flask_login import current_user, login_required

from app.admin import bp
from app.models import User, Laporan


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if getattr(current_user, "role", None) != "admin":
            abort(403)
        return view(*args, **kwargs)
    return wrapped


@bp.route("/dashboard")
@admin_required
def dashboard():
    total_users = User.query.count()
    total_reports = Laporan.query.count()
    reports_in_progress = Laporan.query.filter_by(status="diproses").count()
    reports_done = Laporan.query.filter_by(status="selesai").count()
    latest_reports = (
        Laporan.query.order_by(Laporan.created_at.desc())
        .limit(10)
        .all()
    )
    return render_template(
        "admin/admin_dashboard.html",
        total_users=total_users,
        total_reports=total_reports,
        reports_in_progress=reports_in_progress,
        reports_done=reports_done,
        latest_reports=latest_reports,
    )
