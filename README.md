
# LaporIN — Aplikasi Pelaporan Fasilitas Publik

LaporIN adalah aplikasi berbasis web yang digunakan untuk melaporkan kerusakan fasilitas publik secara cepat, terstruktur, dan transparan.  
Aplikasi ini dibuat untuk mempermudah masyarakat dalam menyampaikan laporan serta memudahkan petugas dalam memantau, memverifikasi, dan menindaklanjuti laporan.

---

## 👥 Tim Pengembang
**Team:** LaporIN  
**Kelompok:** 2

- Rizki Anas Mustakim — 2313010536  
- Bagas Putra Ardian — 2313010550  
- Afif Afandi — 2313010551  
- Fajar Hermawan — 2313010643  

---

## 📝 Deskripsi Aplikasi
Aplikasi LaporIN dirancang untuk:
- menerima laporan fasilitas publik yang rusak,
- mengelola kategori laporan,
- memudahkan admin dan petugas dalam menangani laporan,
- memberikan transparansi dan status update bagi pelapor.

Pengguna dapat mengirim laporan berupa lokasi, deskripsi, dan foto.  
Admin dapat mengelola laporan mulai dari verifikasi hingga penyelesaian.

---

## ✨ Fitur Utama
- **User Login & Register**  
- **Pengiriman Laporan Fasilitas Rusak**  
- **Upload Foto Kerusakan**  
- **Kategori Laporan (jalan, lampu, fasilitas umum, dsb.)**  
- **Dashboard Admin/Petugas**  
- **Status Tracking (Diajukan → Diproses → Selesai)**  
- **Riwayat Laporan User**  
- **Manajemen User & Laporan**

---

## 🧰 Teknologi yang Digunakan
- **Python** (Flask Framework)
- **Flask SQLAlchemy**
- **MySQL / MariaDB**
- **Flask-Login** (Autentikasi)
- **Flask-Bcrypt** (Hash Password)
- **HTML, CSS, Bootstrap**
- **JavaScript**

---

## ⚙️ Cara Menjalankan Project

### 1. Clone Repository
```
git clone https://github.com/kampusriset/23g_flask_laporan_publik.git
```
### 2. Open Folder
```
cd 23g_flask_laporan_publik
```
### 3. Persiapan Lingkungan env
```
python -m venv env :: (nama bebas)
```
### 4, Aktivasi env
### - windows
```
env\Scripts\activate
```
### - linux
```
source env/bin/activate
```
### 5. Install Dependensi
### - windows
```
pip install -r requirements.txt
```
### - linux
```
pip3 install -r requirements.txt
```
jika menggunakan pip3 di linux jika tidak maka sama seperti windows
### 6. copy env configuration dan generate secret
### - windows 
```
copy .env.example .env
python gen-secret.py
```
### - linux
```
cp .env.example
python3 gen-secret.py
```
### 7. Set flask app agar simple
### - windows 
```
set FLASK_APP=run.py
```
### - linux
```
export FLASK_APP=run.py
```
### 8. seeder admin ke db
```
flask seed-user
```
### 9. Jalankan Aplikasi
```
flask run
```