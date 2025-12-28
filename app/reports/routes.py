from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os

from app import db
from app.models import Laporan, Kategori
from . import bp

UPLOAD_FOLDER = 'uploads/laporan_foto'


@bp.route('/my-reports')
@login_required
def my_reports():
    if current_user.role == "admin":
        return redirect(url_for("admin.dashboard"))

    q = Laporan.query.filter_by(user_id=current_user.id)

    search = request.args.get('q', '').strip()
    if search:
        like = f"%{search}%"
        q = q.filter(
            db.or_(
                Laporan.kode_pelaporan.ilike(like),
                Laporan.judul.ilike(like),
                Laporan.lokasi.ilike(like),
                Laporan.status.ilike(like),
            )
        )

    laporan = q.order_by(Laporan.created_at.desc()).all()

    now = datetime.now()
    batas = timedelta(minutes=5)
    for lp in laporan:
        lp.bisa_edit = (now - lp.created_at) <= batas

    return render_template('reports/my_reports.html', laporan=laporan, search=search)


@bp.route('/track')
@login_required
def track():
    return render_template('reports/track.html')


@bp.route('/<int:laporan_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(laporan_id):
    laporan = Laporan.query.get_or_404(laporan_id)

    if laporan.user_id != current_user.id:
        abort(403)

    if datetime.now() - laporan.created_at > timedelta(minutes=5):
        flash('Batas waktu edit laporan sudah lewat (lebih dari 5 menit).', 'warning')
        return redirect(url_for('reports.my_reports'))

    if request.method == 'POST':
        laporan.judul = request.form['judul']
        laporan.kategori_id = request.form['kategori_id']
        laporan.lokasi = request.form['lokasi']
        laporan.wilayah = request.form.get('wilayah') or None
        laporan.deskripsi = request.form['deskripsi']
        lat = request.form.get('lat') or None
        lng = request.form.get('lng') or None
        laporan.latitude = float(lat) if lat else None
        laporan.longitude = float(lng) if lng else None
        laporan.prioritas = request.form.get('prioritas', 'normal')

        foto = request.files.get('foto')
        if foto and foto.filename:
            filename = secure_filename(foto.filename)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            full_path = os.path.join(UPLOAD_FOLDER, filename)
            foto.save(full_path)
            laporan.foto_path = full_path

        db.session.commit()
        flash('Laporan berhasil diperbarui.', 'success')
        return redirect(url_for('reports.my_reports'))

    kategoris = Kategori.query.all()
    return render_template(
        'reports/create.html',
        kategoris=kategoris,
        edit_mode=True,
        laporan=laporan,
        preview_kode=None,
    )


@bp.route('/<int:laporan_id>/delete', methods=['POST'])
@login_required
def delete(laporan_id):
    laporan = Laporan.query.get_or_404(laporan_id)

    if laporan.user_id != current_user.id:
        abort(403)

    now = datetime.now()
    if now - laporan.created_at > timedelta(minutes=5):
        flash('Batas waktu hapus laporan sudah lewat (lebih dari 5 menit).', 'warning')
        return redirect(url_for('reports.my_reports'))

    db.session.delete(laporan)
    db.session.commit()

    flash('Laporan berhasil dihapus.', 'success')
    return redirect(url_for('reports.my_reports'))


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        judul = request.form['judul']
        kategori_id = request.form['kategori_id']
        lokasi = request.form['lokasi']
        wilayah = request.form.get('wilayah') or None
        deskripsi = request.form['deskripsi']
        lat = request.form.get('lat') or None
        lng = request.form.get('lng') or None
        prioritas = request.form.get('prioritas', 'normal')

        foto = request.files.get('foto')
        foto_path = None
        if foto and foto.filename:
            filename = secure_filename(foto.filename)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            full_path = os.path.join(UPLOAD_FOLDER, filename)
            foto.save(full_path)
            foto_path = full_path

        laporan = Laporan(
            kode_pelaporan=Laporan.generate_kode(current_user.id),
            user_id=current_user.id,
            judul=judul,
            kategori_id=kategori_id,
            lokasi=lokasi,
            wilayah=wilayah,
            deskripsi=deskripsi,
            latitude=float(lat) if lat else None,
            longitude=float(lng) if lng else None,
            prioritas=prioritas,
            foto_path=foto_path,
        )

        db.session.add(laporan)
        db.session.commit()

        flash(
            f'Laporan berhasil dikirim. Kode pelaporan: {laporan.kode_pelaporan}',
            'success'
        )
        flash('popup_laporan', 'popup')
        return redirect(url_for('main.dashboard'))

    kategoris = Kategori.query.all()
    return render_template(
        'reports/create.html',
        kategoris=kategoris,
        laporan=None,
        edit_mode=False,
        preview_kode=None,
    )
