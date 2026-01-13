from datetime import datetime
import pytz

wib = pytz.timezone("Asia/Jakarta")

def to_wib(dt):
    if dt is None:
        return None
    # jika datetime sudah naive (tanpa tz), anggap sudah WIB
    if dt.tzinfo is None:
        return dt
    # kalau ternyata disimpan sebagai UTC aware, baru digeser
    return dt.astimezone(wib)

def format_wib(dt):
    dt_wib = to_wib(dt)
    if dt_wib is None:
        return ""
    return dt_wib.strftime("%d %b %Y, %H:%M")
