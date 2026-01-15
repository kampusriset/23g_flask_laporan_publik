# app/reports/routes.py
from datetime import datetime, timedelta
import os
import base64
import io
from pathlib import Path
from pydoc import html

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, abort, jsonify, make_response
)
import uuid
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from PIL import Image
import pdfkit

from app import db
from app.models import Laporan, Kategori
from app.reports import bp


import os
import uuid
from pathlib import Path
from werkzeug.utils import secure_filename

# 1. Pastikan BASE_DIR ini beneran nunjuk ke folder 'app' lo
# Kalau file ini ada di dalam folder 'app/', code ini udah bener.
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_FOLDER = BASE_DIR / "static"
UPLOAD_FOLDER = STATIC_FOLDER / "uploads" / "laporan_foto"

# Auto-create folder pas server start (biar aman)
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

def to_relative(path: Path) -> str:
    """Mengubah path absolut disk menjadi path relatif URL."""
    try:
        return str(path.relative_to(STATIC_FOLDER)).replace("\\", "/")
    except ValueError:
        return None

def save_uploaded_file(file_obj):
    """
    Simpan file dengan nama random (hashed/UUID) untuk mencegah duplikasi.
    """
    # Cek file kosong
    if not file_obj or not file_obj.filename:
        return None
    
    try:
        # 1. Generate Nama Unik
        original_filename = secure_filename(file_obj.filename)
        _, ext = os.path.splitext(original_filename)
        if not ext: ext = ".jpg" # Fallback extension
        
        unique_filename = f"{uuid.uuid4().hex}{ext.lower()}"
        full_path_obj = UPLOAD_FOLDER / unique_filename

        # 2. [CRITICAL FIX] Reset cursor jaga-jaga file udah dibaca sebelumnya
        file_obj.seek(0)
        
        # 3. [CRITICAL FIX] Convert Path Object jadi String biasa
        # Flask .save() kadang nolak kalau dikasih object Path mentah
        save_path_str = str(full_path_obj)
        
        print(f"DEBUG: Saving to -> {save_path_str}") # Cek console buat mastiin
        
        file_obj.save(save_path_str)
        
        return to_relative(full_path_obj)
        
    except Exception as e:
        print(f"❌ Gagal save file: {e}")
        return None


def save_camera_photo(data_url):
    """
    Terima data URL base64 dari kamera (image),
    simpan sebagai JPEG, kembalikan path relatif atau None.
    """
    if not data_url:
        return None

    try:
        header, encoded = data_url.split(",", 1)
    except ValueError:
        return None

    binary = base64.b64decode(encoded)
    img = Image.open(io.BytesIO(binary))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    filename = secure_filename(f"kamera_{int(datetime.now().timestamp())}.jpg")
    full_path = UPLOAD_FOLDER / filename
    with open(full_path, "wb") as f:
        f.write(buf.read())

    return to_relative(full_path)


def save_camera_video(data_url):
    """
    Terima data URL base64 video/webm dari kamera,
    simpan ke disk, kembalikan path relatif atau None.
    """
    if not data_url:
        return None

    try:
        header, encoded = data_url.split(",", 1)
    except ValueError:
        return None

    binary = base64.b64decode(encoded)
    filename = secure_filename(f"video_{int(datetime.utcnow().timestamp())}.webm")
    full_path = UPLOAD_FOLDER / filename
    with open(full_path, "wb") as f:
        f.write(binary)

    return to_relative(full_path)


@bp.route("/my-reports")
@login_required
def my_reports():
    if current_user.role == "admin":
        return redirect(url_for("admin.dashboard"))

    q = Laporan.query.filter_by(user_id=current_user.id)

    search = request.args.get("q", "").strip()
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

    return render_template("reports/my_reports.html", laporan=laporan, search=search)


@bp.route("/riwayat")
@login_required
def riwayat_laporan():
    laporan = (
        Laporan.query.filter_by(user_id=current_user.id)
        .order_by(Laporan.created_at.desc())
        .all()
    )
    return render_template("reports/riwayat_laporan.html", laporan=laporan)


@bp.route("/track")
@login_required
def track():
    kode = (request.args.get("kode") or "").strip()

    laporan = None
    if kode:
        laporan = (
            Laporan.query
            .filter_by(kode_pelaporan=kode, user_id=current_user.id)
            .first()
        )
        if not laporan:
            flash("Laporan dengan kode tersebut tidak ditemukan.", "warning")

    return render_template("reports/track.html", laporan=laporan, kode=kode)


@bp.route("/laporan/<int:laporan_id>")
@login_required
def detail(laporan_id):
    laporan = Laporan.query.get_or_404(laporan_id)
    if laporan.user_id != current_user.id and current_user.role != "admin":
        abort(403)
    return render_template("reports/detail.html", laporan=laporan)


@bp.route("/<int:laporan_id>/edit", methods=["GET", "POST"])
@login_required
def edit(laporan_id):
    laporan = Laporan.query.get_or_404(laporan_id)

    if laporan.user_id != current_user.id:
        abort(403)

    if datetime.now() - laporan.created_at > timedelta(minutes=5):
        flash(
            "Batas waktu edit laporan sudah lewat (lebih dari 5 menit).",
            "warning",
        )
        return redirect(url_for("reports.my_reports"))

    if request.method == "POST":
        laporan.judul = request.form["judul"]
        laporan.kategori_id = request.form["kategori_id"]
        laporan.lokasi = request.form["lokasi"]
        laporan.wilayah = request.form.get("wilayah") or None
        laporan.deskripsi = request.form["deskripsi"]
        lat = request.form.get("lat") or None
        lng = request.form.get("lng") or None
        laporan.latitude = float(lat) if lat else None
        laporan.longitude = float(lng) if lng else None
        laporan.prioritas = request.form.get("prioritas", "normal")

        paths = []

        # a) file dari galeri (boleh multiple)
        files = request.files.getlist("bukti_file")
        for f in files:
            rel = save_uploaded_file(f)
            if rel:
                paths.append(rel)

        # b) foto kamera yang sudah diupload via AJAX
        kamera_paths_str = request.form.get("bukti_camera_path", "").strip()
        if kamera_paths_str:
            for p in kamera_paths_str.split(","):
                p = p.strip()
                if p:
                    paths.append(p)

        # c) video kamera (base64 langsung dari form, opsional)
        video_data = request.form.get("bukti_video_data", "").strip()
        if video_data:
            rel = save_camera_video(video_data)
            if rel:
                paths.append(rel)

        if paths:
            laporan.foto_path = ",".join(paths)

        db.session.commit()
        flash("Laporan berhasil diperbarui.", "success")
        return redirect(url_for("reports.my_reports"))

    kategoris = Kategori.query.all()
    return render_template(
        "reports/create.html",
        kategoris=kategoris,
        edit_mode=True,
        laporan=laporan,
        preview_kode=None,
    )


@bp.route("/<int:laporan_id>/delete", methods=["POST"])
@login_required
def delete(laporan_id):
    laporan = Laporan.query.get_or_404(laporan_id)

    if laporan.user_id != current_user.id:
        abort(403)

    now = datetime.now()
    if now - laporan.created_at > timedelta(minutes=5):
        flash(
            "Batas waktu hapus laporan sudah lewat (lebih dari 5 menit).",
            "warning",
        )
        return redirect(url_for("reports.my_reports"))

    db.session.delete(laporan)
    db.session.commit()

    flash("Laporan berhasil dihapus.", "success")
    return redirect(url_for("reports.my_reports"))


@bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        judul = request.form["judul"]
        kategori_id = request.form["kategori_id"]
        lokasi = request.form["lokasi"]
        wilayah = request.form.get("wilayah") or None
        deskripsi = request.form["deskripsi"]
        lat = request.form.get("lat") or None
        lng = request.form.get("lng") or None
        prioritas = request.form.get("prioritas", "normal")

        paths = []

        # a) file dari galeri (multiple)
        files = request.files.getlist("bukti_file")
        for f in files:
            rel = save_uploaded_file(f)
            if rel:
                paths.append(rel)

        # b) foto kamera via AJAX
        kamera_paths_str = request.form.get("bukti_camera_path", "").strip()
        if kamera_paths_str:
            for p in kamera_paths_str.split(","):
                p = p.strip()
                if p:
                    paths.append(p)

        # c) video kamera dari form (base64)
        video_data = request.form.get("bukti_video_data", "").strip()
        if video_data:
            rel = save_camera_video(video_data)
            if rel:
                paths.append(rel)

        foto_path_str = ",".join(paths) if paths else None

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
            foto_path=foto_path_str,
        )

        db.session.add(laporan)
        db.session.commit()

        flash(
            f"Laporan berhasil dikirim. Kode pelaporan: {laporan.kode_pelaporan}",
            "success",
        )
        # arahkan ke halaman konfirmasi cetak
        return redirect(url_for("reports.confirm_cetak", laporan_id=laporan.id))

    kategoris = Kategori.query.all()
    return render_template(
        "reports/create.html",
        kategoris=kategoris,
        laporan=None,
        edit_mode=False,
        preview_kode=None,
    )


@bp.route("/laporan/<int:laporan_id>/konfirmasi-cetak")
@login_required
def confirm_cetak(laporan_id):
    laporan = Laporan.query.filter_by(
        id=laporan_id, user_id=current_user.id
    ).first_or_404()
    return render_template("reports/confirm_cetak.html", laporan=laporan)


@bp.route("/laporan/<int:laporan_id>/cetak-pdf")
@login_required
def cetak_pdf(laporan_id):
    laporan = Laporan.query.filter_by(
        id=laporan_id, user_id=current_user.id
    ).first_or_404()

    html = render_template("reports/laporan_pdf.html", laporan=laporan)

    # sesuaikan path wkhtmltopdf di Windows-mu
    config = pdfkit.configuration(
        wkhtmltopdf=r"D:\wkhtmltopdf\bin\wkhtmltopdf.exe"
    )
    pdf = pdfkit.from_string(html, False, configuration=config)

    response = make_response(pdf)
    filename = f"laporan_{laporan.kode_pelaporan or laporan.id}.pdf"
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"inline; filename={filename}"
    return response


@bp.route("/upload-camera-photo", methods=["POST"])
@login_required
def upload_camera_photo():
    data_url = request.form.get("bukti_camera_data")  # base64
    if not data_url:
        return jsonify(ok=False, error="Tidak ada data foto"), 400

    rel_path = save_camera_photo(data_url)
    if not rel_path:
        return jsonify(ok=False, error="Gagal menyimpan foto"), 500

    full_path = STATIC_FOLDER / rel_path
    filename = os.path.basename(rel_path)

    try:
        filesize = os.path.getsize(full_path)
    except OSError:
        filesize = None

    return jsonify(
        ok=True,
        filename=filename,
        path=rel_path,
        filesize_bytes=filesize,
    )
    # --- Tambahkan ini di bagian bawah app/reports/routes.py ---

@bp.route("/download-rekap-pdf")
@login_required
def download_rekap_pdf():
    # 1. Ambil filter status dari URL (contoh: /download-rekap-pdf?status=selesai)
    status_filter = request.args.get("status", "all")
    
    # 2. Query dasar (milik user yang login)
    query = Laporan.query.filter_by(user_id=current_user.id)
    
    # 3. Terapkan filter jika bukan 'all'
    title_suffix = "Semua Status"
    if status_filter != "all":
        # Validasi status agar sesuai Enum di database
        valid_statuses = ["diajukan", "diproses", "selesai", "ditolak"]
        if status_filter in valid_statuses:
            query = query.filter_by(status=status_filter)
            title_suffix = status_filter.capitalize()
    
    # Urutkan dari yang terbaru
    laporan_list = query.order_by(Laporan.created_at.desc()).all()
    
    # 4. Jika data kosong, beri notifikasi
    if not laporan_list:
        flash(f"Tidak ada laporan dengan status '{status_filter}' untuk dicetak.", "warning")
        return redirect(url_for("reports.my_reports"))

    # 5. Render template HTML khusus rekap
    html_content = render_template(
        "reports/rekap_pdf.html",
        laporan_list=laporan_list,
        filter_status=title_suffix,
        user=current_user,
        tanggal_cetak=datetime.now()
    )

    # 6. Konfigurasi PDFKit (Sesuaikan path jika dipindah ke server lain)
    # Pastikan path ini benar ada di komputer Anda
    path_wkhtmltopdf = r"D:\wkhtmltopdf\bin\wkhtmltopdf.exe"
    
    # Cek apakah file exe ada (untuk menghindari error server 500)
    if not os.path.exists(path_wkhtmltopdf):
        # Fallback untuk Linux/Production biasanya tidak butuh path spesifik
        config = None 
    else:
        config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

    # Opsi agar tabel rapi di PDF
    options = {
        'page-size': 'A4',
        'orientation': 'Landscape', # Landscape agar tabel lebar muat
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'no-outline': None
    }

    try:
        pdf = pdfkit.from_string(html_content, False, configuration=config, options=options)
    except OSError as e:
        # Error biasanya karena wkhtmltopdf tidak ditemukan atau path salah
        print(f"Error PDFKit: {e}")
        flash("Gagal memproses PDF. Pastikan wkhtmltopdf terinstall.", "danger")
        return redirect(url_for("reports.my_reports"))

    # 7. Return Response
    response = make_response(pdf)
    filename = f"Rekap_Laporan_{status_filter}_{datetime.now().strftime('%Y%m%d')}.pdf"
    response.headers["Content-Type"] = "application/pdf"
    # Gunakan 'attachment' agar otomatis download, atau 'inline' untuk preview browser
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    
    return response

@bp.route("/admin/laporan/<int:laporan_id>/update-status", methods=["POST"])
@login_required
def admin_update_status(laporan_id):
    if current_user.role != "admin":
        abort(403)

    laporan = Laporan.query.get_or_404(laporan_id)

    status_baru = request.form.get("status")
    ringkasan = request.form.get("ringkasan_hasil")
    alasan = request.form.get("alasan_ditolak")

    # === FOTO ADMIN ===
    file = request.files.get("admin_foto")
    if file and file.filename:
        rel_path = save_uploaded_file(file)
        if rel_path:
            laporan.foto_admin = rel_path

    # === STATUS LOGIC ===
    if status_baru == "diproses":
        laporan.status = "diproses"
        laporan.tgl_diproses = datetime.now()

    elif status_baru == "selesai":
        laporan.status = "selesai"
        laporan.ringkasan_hasil = ringkasan
        laporan.tgl_selesai = datetime.now()

    elif status_baru == "ditolak":
        laporan.status = "ditolak"
        laporan.alasan_ditolak = alasan
        laporan.tgl_ditolak = datetime.now()

    db.session.commit()
    flash("Status laporan berhasil diperbarui", "success")
    return redirect(url_for("admin.detail_laporan", laporan_id=laporan.id))
