import platform
import pdfkit
from pathlib import Path

# Kita arahkan path-nya relatif terhadap root project
# .parent.parent karena file ini ada di /app/pdf_helper.py
BASE_DIR = Path(__file__).resolve().parent.parent

def get_pdf_config():
    """
    Fungsi global buat dapetin konfigurasi wkhtmltopdf 
    yang bisa jalan di Windows (lokal) dan Linux (server).
    """
    current_os = platform.system()
    
    if current_os == "Windows":
        # Pastiin lo udah naruh file .exe di folder bin/
        path_binary = str(BASE_DIR / "bin" / "wkhtmltopdf.exe")
    else:
        # Pastiin lo udah naruh file binary linux di folder bin/
        path_binary = str(BASE_DIR / "bin" / "wkhtmltopdf_linux")
            
    return pdfkit.configuration(wkhtmltopdf=path_binary)