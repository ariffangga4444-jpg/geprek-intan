import base64
import json
import os
import sqlite3
from datetime import datetime
from flask import Flask, Response, g, redirect, request, send_from_directory, session, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "geprek_intan_secret_key_sejahtera"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "geprek_intan.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
MENU_FOLDER = os.path.join(BASE_DIR, "static", "menu")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MENU_FOLDER, exist_ok=True)

def encode_menu_key(nama_menu):
    raw = nama_menu.encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")

def decode_menu_key(key):
    padded = key + ("=" * ((4 - len(key) % 4) % 4))
    return base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8")

def get_brand_image_url():
    if os.path.exists(os.path.join(BASE_DIR, "geprek-intan.png")):
        return "/geprek-intan.png"
    if os.path.exists(os.path.join(BASE_DIR, "static", "geprek-intan.png")):
        return url_for("static", filename="geprek-intan.png")
    return "/geprek-intan.png"

@app.route("/geprek-intan.png")
def serve_root_brand_image():
    if os.path.exists(os.path.join(BASE_DIR, "geprek-intan.png")):
        return send_from_directory(BASE_DIR, "geprek-intan.png", mimetype="image/png")
    static_dir = os.path.join(BASE_DIR, "static")
    if os.path.exists(os.path.join(static_dir, "geprek-intan.png")):
        return send_from_directory(static_dir, "geprek-intan.png", mimetype="image/png")
    return "", 404

@app.route("/manifest.json")
def pwa_manifest():
    icon_url = get_brand_image_url()
    manifest_data = {
        "name": "Resto & Cafe Geprek Intan",
        "short_name": "Geprek Intan",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#120e0e",
        "theme_color": "#c0392b",
        "icons": [
            {"src": icon_url, "sizes": "192x192", "type": "image/png", "purpose": "any"},
            {"src": icon_url, "sizes": "512x512", "type": "image/png", "purpose": "any"},
        ],
    }
    return Response(json.dumps(manifest_data), mimetype="application/manifest+json")

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute("""
            CREATE TABLE IF NOT EXISTS pesanan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama TEXT NOT NULL,
                meja TEXT NOT NULL,
                catatan TEXT,
                rincian TEXT NOT NULL,
                total INTEGER NOT NULL,
                metode_pembayaran TEXT NOT NULL,
                bukti_transfer TEXT,
                status TEXT NOT NULL,
                waktu TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cols = [row["name"] for row in db.execute("PRAGMA table_info(pesanan)").fetchall()]
        if "waktu" not in cols:
            db.execute("ALTER TABLE pesanan ADD COLUMN waktu TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        db.execute("""
            CREATE TABLE IF NOT EXISTS menu_status (
                nama_menu TEXT PRIMARY KEY,
                tersedia INTEGER NOT NULL
            )
        """)
        db.commit()

init_db()

MENU_MASTER = {
    "Nasi Putih / Mangkok": {
        "harga": 5000,
        "gambar": "/static/menu/nasi-putih.jpg",
        "deskripsi": "Nasi putih hangat pulen per mangkok",
        "kategori": "Menu Tambahan"
    },
    "Nasi Goreng Spesial + Jus": {
        "harga": 15000,
        "gambar": "/static/menu/nasi-goreng.jpg",
        "deskripsi": "Nasi goreng bumbu rempah spesial + segarnya minuman jus",
        "kategori": "Makanan Utama"
    },
    "Nasi Ayam Lalapan + Jus": {
        "harga": 15000,
        "gambar": "/static/menu/Nasi%20Ayam%20Lalapan%20%2B%20Jus.jpg",
        "deskripsi": "Nasi + ayam lalapan sambal segar + minuman jus",
        "kategori": "Makanan Utama"
    },
    "Nasi Ayam Geprek + Jus": {
        "harga": 15000,
        "gambar": "/static/menu/Nasi%20Ayam%20Geprek%20%2B%20Jus.jpg",
        "deskripsi": "Nasi + ayam krispi geprek pedas + minuman jus",
        "kategori": "Makanan Utama"
    },
    "Mie Bakso Biasa": {
        "harga": 15000,
        "gambar": "/static/menu/Mie%20Bakso%20Biasa.jpg",
        "deskripsi": "Mie kuah hangat dengan sajian bakso sapi gurih",
        "kategori": "Mie & Soto"
    },
    "Mie GenZ Pedas (LV 1)": {
        "harga": 10000,
        "gambar": "/static/menu/Mie%20GenZ%20Pedas%20%28LV%201%29.jpg",
        "deskripsi": "Mie pedas kekinian Level 1",
        "kategori": "Mie & Soto"
    },
    "Mie GenZ Pedas (LV 2)": {
        "harga": 12000,
        "gambar": "/static/menu/Mie%20GenZ%20Pedas%20%28LV%202%29.jpg",
        "deskripsi": "Mie pedas kekinian Level 2",
        "kategori": "Mie & Soto"
    },
    "Mie GenZ Pedas (LV 3)": {
        "harga": 13000,
        "gambar": "/static/menu/Mie%20GenZ%20Pedas%20%28LV%203%29.jpg",
        "deskripsi": "Mie pedas kekinian Level 3 mantap",
        "kategori": "Mie & Soto"
    },
    "Soto Ayam + Jus": {
        "harga": 15000,
        "gambar": "/static/menu/soto-ayam.jpg",
        "deskripsi": "Kuah soto kuning segar + suwiran ayam & soun + jus",
        "kategori": "Mie & Soto"
    },
    "Milu Siram / Bindebiluhuta": {
        "harga": 7000,
        "gambar": "/static/menu/milu-siram.jpg",
        "deskripsi": "Kuliner khas jagung siram kuah lezat",
        "kategori": "Spesial Khas"
    },
    "Ayam Lalapan Tanpa Nasi": {
        "harga": 13000,
        "gambar": "/static/menu/Ayam%20Lalapan%20Tanpa%20Nasi.jpg",
        "deskripsi": "Ayam krispi + lalapan sambal (tanpa nasi)",
        "kategori": "Menu Ala Carte"
    },
    "Ayam Geprek Tanpa Nasi": {
        "harga": 13000,
        "gambar": "/static/menu/Ayam%20Geprek%20Tanpa%20Nasi.jpg",
        "deskripsi": "Ayam krispi digeprek sambal pedas (tanpa nasi)",
        "kategori": "Menu Ala Carte"
    },
    "Teh Hangat": {
        "harga": 5000,
        "gambar": "/static/menu/teh-hangat.jpg",
        "deskripsi": "Teh hangat manis pas di badan",
        "kategori": "Minuman & Snack"
    },
    "Fanta Susu": {
        "harga": 10000,
        "gambar": "/static/menu/fanta-susu.jpg",
        "deskripsi": "Minuman bersoda Fanta dicampur susu kental manis",
        "kategori": "Minuman & Snack"
    },
    "Kopi": {
        "harga": 6000,
        "gambar": "/static/menu/kopi.jpg",
        "deskripsi": "Kopi hitam racikan nikmat",
        "kategori": "Minuman & Snack"
    },
    "Pisang Stik Goroho": {
        "harga": 12000,
        "gambar": "/static/menu/pisang-goroho.jpg",
        "deskripsi": "Stik pisang goroho renyah gurih",
        "kategori": "Minuman & Snack"
    }
}

def get_menu_status():
    db = get_db()
    cursor = db.execute("SELECT nama_menu, tersedia FROM menu_status")
    status_dict = {row["nama_menu"]: row["tersedia"] for row in cursor.fetchall()}
    for m in MENU_MASTER:
        if m not in status_dict:
            status_dict[m] = 1
    return status_dict

def parse_order_timestamp_ms(waktu_val):
    if not waktu_val:
        return None
    s = str(waktu_val).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f", "%Y/%m/%d %H:%M:%S"):
        try:
            dt = datetime.strptime(s, fmt)
            return int(dt.timestamp() * 1000)
        except ValueError:
            continue
    try:
        dt = datetime.fromisoformat(s)
        return int(dt.timestamp() * 1000)
    except Exception:
        return None

def get_customer_order_ids():
    raw_ids = session.get("my_order_ids", [])
    clean_ids = []
    for x in raw_ids:
        try:
            val = int(x)
            if val not in clean_ids:
                clean_ids.append(val)
        except Exception:
            continue
    return clean_ids

def remember_customer_order_id(order_id):
    ids = get_customer_order_ids()
    try:
        oid = int(order_id)
        if oid not in ids:
            ids.insert(0, oid)
        session["my_order_ids"] = ids[:50]
    except Exception:
        pass

def get_customer_orders():
    ids = get_customer_order_ids()
    if not ids:
        return []
    placeholders = ",".join("?" for _ in ids)
    db = get_db()
    return db.execute(f"SELECT * FROM pesanan WHERE id IN ({placeholders}) ORDER BY id DESC", ids).fetchall()

def get_status_badge_style(st):
    if st == "Menunggu Verifikasi":
        return ("#fef3c7", "#b45309", "#fde68a")
    if st == "Diproses":
        return ("#ffedd5", "#c2410c", "#fed7aa")
    if st == "Dibatalkan Pelanggan":
        return ("#fee2e2", "#b91c1c", "#fecaca")
    return ("#dcfce7", "#15803d", "#bbf7d0")

@app.route("/", methods=["GET", "POST"])
def index():
    menu_status = get_menu_status()
    brand_img = get_brand_image_url()
    my_orders = get_customer_orders()
    active_orders_count = sum(1 for o in my_orders if o["status"] in ("Menunggu Verifikasi", "Diproses"))

    if request.method == "POST":
        nama = request.form.get("nama", "").strip()
        meja = request.form.get("meja", "").strip()
        catatan = request.form.get("catatan", "").strip()
        metode_pembayaran = request.form.get("pembayaran", "").strip()
        pesanan_items = []
        total_harga = 0
        for item, detail in MENU_MASTER.items():
            if menu_status.get(item, 1) == 0:
                continue
            qty = request.form.get(f"qty_{item}", 0)
            if qty and int(qty) > 0:
                jumlah = int(qty)
                subtotal = jumlah * detail["harga"]
                total_harga += subtotal
                pesanan_items.append(f"{item} ({jumlah}x) - Rp{subtotal:,}")
        if not pesanan_items:
            return "<script>alert('Pilih minimal 1 menu yang tersedia!'); window.history.back();</script>"

        bukti_filename = None
        if "Transfer Bank" in metode_pembayaran:
            file_bukti = request.files.get("bukti_transfer")
            if not file_bukti or file_bukti.filename == "" or not allowed_file(file_bukti.filename):
                return "<script>alert('Harap unggah foto bukti transfer terlebih dahulu!'); window.history.back();</script>"
            filename = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file_bukti.filename}")
            file_bukti.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            bukti_filename = filename
            status_awal = "Menunggu Verifikasi"
        else:
            status_awal = "Diproses"

        waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rincian_str = ", ".join(pesanan_items)
        db = get_db()
        cur = db.execute(
            "INSERT INTO pesanan (nama, meja, catatan, rincian, total, metode_pembayaran, bukti_transfer, status, waktu) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (nama, meja, catatan, rincian_str, total_harga, metode_pembayaran, bukti_filename, status_awal, waktu_sekarang),
        )
        db.commit()
        new_order_id = cur.lastrowid
        remember_customer_order_id(new_order_id)
        status_badge_color = "#f39c12" if status_awal == "Menunggu Verifikasi" else "#27ae60"

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <meta name="theme-color" content="#c0392b">
            <link rel="icon" type="image/png" href="{brand_img}">
            <link rel="apple-touch-icon" href="{brand_img}">
            <link rel="manifest" href="/manifest.json">
            <title>Struk Pesanan #{new_order_id} - GEPREK INTAN</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #120c0c; background-image: linear-gradient(rgba(18, 12, 12, 0.78), rgba(18, 12, 12, 0.88)), url('{brand_img}'); background-position: center; background-size: contain; background-repeat: no-repeat; background-attachment: fixed; padding: 20px; color: #333; min-height: 100vh; }}
                .card {{
                    max-width: 480px;
                    margin: 0 auto;
                    background: rgba(255, 255, 255, 0.96);
                    padding: 25px;
                    border-radius: 20px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.22);
                }}
                h2 {{
                    text-align: center;
                    color: #c0392b;
                    margin-top: 0;
                }}
                .info {{
                    background: #fdfefe;
                    border: 1px solid #eaeded;
                    padding: 15px;
                    border-radius: 12px;
                    margin-bottom: 20px;
                    font-size: 14px;
                    line-height: 1.6;
                }}
                .total {{
                    font-size: 18px;
                    font-weight: bold;
                    color: #c0392b;
                    text-align: right;
                    margin-top: 15px;
                }}
                .btn-primary {{
                    display: block;
                    text-align: center;
                    background: linear-gradient(135deg, #2563eb, #1d4ed8);
                    color: white;
                    text-decoration: none;
                    padding: 13px;
                    border-radius: 12px;
                    font-weight: bold;
                    margin-top: 14px;
                    box-shadow: 0 4px 14px rgba(37,99,235,0.28);
                }}
                .btn-secondary {{
                    display: block;
                    text-align: center;
                    background: linear-gradient(135deg, #e74c3c, #c0392b);
                    color: white;
                    text-decoration: none;
                    padding: 13px;
                    border-radius: 12px;
                    font-weight: bold;
                    margin-top: 10px;
                    box-shadow: 0 4px 15px rgba(231,76,60,0.28);
                }}
            </style>
        </head>
        <body>
            <div class="card">
                <h3 style="color:#27ae60; text-align:center;">Pesanan Berhasil Dikirim!</h3>
                <h2>GEPREK INTAN</h2>
                <div class="info">
                    <b>No. Pesanan:</b> #{new_order_id}<br>
                    <b>Nama Pemesan:</b> {nama}<br>
                    <b>Meja / Alamat:</b> {meja}<br>
                    <b>Waktu Pesan:</b> {waktu_sekarang}<br>
                    <b>Metode Pembayaran:</b> {metode_pembayaran}<br>
                    <b>Status Pesanan:</b> <span style="background:{status_badge_color}; color:white; padding:3px 10px; border-radius:6px; font-weight:bold; font-size:12px;">{status_awal}</span><br>
                    <b>Catatan:</b> {catatan if catatan else '-'}<br><br>
                    <b>Rincian Menu:</b><br>{rincian_str}
                </div>
                <div class="total">Total Bayar: Rp{total_harga:,}</div>
                <a href="/pesanan-saya" class="btn-primary">Pantau Status & Cancel Pesanan Saya</a>
                <a href="/" class="btn-secondary">Buat Pesanan Baru</a>
            </div>
        </body>
        </html>
        """

    menu_html = ""
    menu_js_prices = {}
    for item, detail in MENU_MASTER.items():
        harga = detail["harga"]
        gambar = detail["gambar"]
        deskripsi = detail["deskripsi"]
        tersedia = menu_status.get(item, 1)
        menu_js_prices[item] = harga
        if tersedia == 1:
            menu_html += f"""
            <div class="menu-card">
                <img src="{gambar}" alt="{item}" class="menu-thumb" onclick="openLightbox(this.src, '{item}', 'Rp {harga:,}')" onerror="this.onerror=null;this.src='{brand_img}';">
                <div class="menu-info">
                    <div class="menu-title">{item}</div>
                    <div class="menu-desc">{deskripsi}</div>
                    <div class="menu-price">Rp {harga:,}</div>
                </div>
                <div class="qty-control">
                    <button type="button" class="qty-btn" onclick="changeQty('{item}', -1)">-</button>
                    <input type="number" id="input_{item}" name="qty_{item}" value="0" min="0" readonly class="qty-input">
                    <button type="button" class="qty-btn" onclick="changeQty('{item}', 1)">+</button>
                </div>
            </div>
            """
        else:
            menu_html += f"""
            <div class="menu-card sold-out">
                <img src="{gambar}" alt="{item}" class="menu-thumb" onclick="openLightbox(this.src, '{item}', 'Habis Terjual')" onerror="this.onerror=null;this.src='{brand_img}';">
                <div class="menu-info">
                    <div class="menu-title" style="text-decoration:line-through; color:#95a5a6;">{item}</div>
                    <div class="menu-desc">{deskripsi}</div>
                    <div style="color:#e74c3c; font-weight:bold; font-size:12px; margin-top:4px;">HABIS TERJUAL</div>
                </div>
                <div><span class="badge-habis">Habis</span></div>
            </div>
            """

    order_badge_text = f"{active_orders_count} Aktif" if active_orders_count > 0 else f"{len(my_orders)} Riwayat"

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="theme-color" content="#c0392b">
        <link rel="icon" type="image/png" href="{brand_img}">
        <link rel="apple-touch-icon" href="{brand_img}">
        <link rel="manifest" href="/manifest.json">
        <title>GEPREK INTAN - Resto & Cafe</title>
        <style>
            * {{ box-sizing: border-box; }}
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #140e0e; background-image: linear-gradient(rgba(18, 12, 12, 0.62), rgba(18, 12, 12, 0.78)), url('{brand_img}'); background-position: center 42%; background-size: 92% auto; background-repeat: no-repeat; background-attachment: fixed; margin: 0; padding: 0; color: #2c3e50; padding-bottom: 90px; min-height: 100vh; }}
            @media (min-width: 640px) {{ body {{ background-size: 460px auto; background-position: center; }} }}
            .hero-banner {{
                background: linear-gradient(135deg, rgba(30, 39, 46, 0.86), rgba(47, 54, 64, 0.86)), url('https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=1000&q=80');
                background-blend-mode: overlay;
                background-size: cover;
                background-position: center;
                color: white;
                text-align: center;
                padding: 30px 20px 32px 20px;
                border-bottom-left-radius: 25px;
                border-bottom-right-radius: 25px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.22);
            }}
            .hero-banner h1 {{
                margin: 0;
                font-size: 25px;
                font-weight: 800;
                letter-spacing: 1px;
                color: #f5cd79;
            }}
            .hero-banner p {{
                margin: 8px 0 0 0;
                font-size: 13px;
                color: #dcdde1;
            }}
            .hero-meta-bar {{
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 8px;
                flex-wrap: wrap;
                margin-top: 12px;
            }}
            .live-clock-pill {{
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 6px 13px;
                border-radius: 999px;
                background: rgba(15, 23, 42, 0.78);
                border: 1px solid rgba(245, 205, 121, 0.45);
                color: #f5cd79;
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 0.4px;
            }}
            .customer-dash-pill {{
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 6px 14px;
                border-radius: 999px;
                background: linear-gradient(135deg, #2563eb, #1d4ed8);
                color: #ffffff;
                text-decoration: none;
                font-size: 12px;
                font-weight: 700;
                box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35);
            }}
            .pill-count {{
                background: rgba(255, 255, 255, 0.22);
                padding: 2px 7px;
                border-radius: 999px;
                font-size: 11px;
                font-weight: 800;
            }}
            .container {{
                max-width: 500px;
                margin: 0 auto;
                padding: 15px;
            }}
            .menu-card {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                background: rgba(255, 255, 255, 0.95);
                padding: 12px;
                margin-bottom: 12px;
                border-radius: 16px;
                box-shadow: 0 6px 18px rgba(0,0,0,0.16);
                border: 1px solid rgba(255,255,255,0.7);
            }}
            .menu-card img.menu-thumb {{
                width: 75px;
                height: 75px;
                object-fit: cover;
                border-radius: 12px;
                border: 1px solid #eee;
                cursor: pointer;
                transition: transform 0.15s ease;
            }}
            .menu-card img.menu-thumb:active {{ transform: scale(0.95); }}
            .menu-info {{
                flex: 1;
                padding: 0 12px;
            }}
            .menu-title {{
                font-size: 15px;
                font-weight: 700;
                color: #2f3640;
            }}
            .menu-desc {{
                font-size: 11px;
                color: #718093;
                margin-top: 3px;
                line-height: 1.3;
            }}
            .menu-price {{
                font-size: 14px;
                font-weight: bold;
                color: #e74c3c;
                margin-top: 6px;
            }}
            .qty-control {{
                display: flex;
                align-items: center;
                background: #f8f9fa;
                padding: 4px;
                border-radius: 25px;
                border: 1px solid #dfe4ea;
            }}
            .qty-btn {{
                width: 30px;
                height: 30px;
                border-radius: 50%;
                border: none;
                background: #e74c3c;
                color: white;
                font-weight: bold;
                font-size: 16px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .qty-input {{
                width: 28px;
                text-align: center;
                border: none;
                background: transparent;
                font-weight: bold;
                font-size: 14px;
                color: #2f3640;
            }}
            .sold-out {{
                background: rgba(241, 242, 246, 0.9);
                opacity: 0.82;
            }}
            .badge-habis {{
                background: #c0392b;
                color: white;
                padding: 5px 10px;
                border-radius: 8px;
                font-size: 11px;
                font-weight: bold;
            }}
            .section-title {{
                font-size: 16px;
                font-weight: 700;
                color: #f5cd79;
                margin: 25px 0 12px 5px;
                border-left: 4px solid #e74c3c;
                padding-left: 8px;
                text-shadow: 0 1px 4px rgba(0,0,0,0.6);
            }}
            .form-box {{
                background: rgba(255, 255, 255, 0.96);
                padding: 20px;
                border-radius: 16px;
                box-shadow: 0 6px 18px rgba(0,0,0,0.16);
                margin-bottom: 20px;
                border: 1px solid rgba(255,255,255,0.7);
            }}
            .form-group {{ margin-bottom: 15px; }}
            .form-group label {{
                font-size: 12px;
                font-weight: bold;
                color: #718093;
                display: block;
                margin-bottom: 6px;
            }}
            .form-group input, .form-group select, .form-group textarea {{
                width: 100%;
                padding: 12px;
                border: 1px solid #dfe4ea;
                border-radius: 10px;
                box-sizing: border-box;
                font-size: 14px;
                background: #fdfefe;
            }}
            .bank-info {{
                background:#e8f4fd;
                border:1px solid #bbeeff;
                padding:15px;
                border-radius:12px;
                font-size:12px;
                margin-top:10px;
                display:none;
                color: #004080;
                line-height: 1.5;
            }}
            .floating-bar {{
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: rgba(255, 255, 255, 0.97);
                padding: 15px 20px;
                box-shadow: 0 -5px 25px rgba(0,0,0,0.18);
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-top-left-radius: 20px;
                border-top-right-radius: 20px;
                z-index: 1000;
            }}
            .total-text {{
                font-size: 13px;
                color: #718093;
            }}
            .total-price {{
                font-size: 18px;
                font-weight: 800;
                color: #e74c3c;
            }}
            .btn-order {{
                background: linear-gradient(135deg, #e74c3c, #c0392b);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 12px;
                font-size: 15px;
                font-weight: bold;
                cursor: pointer;
            }}
            .customer-link-box {{
                display: block;
                text-align: center;
                margin: 18px 0 10px 0;
                padding: 12px 16px;
                border-radius: 12px;
                background: rgba(15, 23, 42, 0.84);
                border: 1px solid rgba(96, 165, 250, 0.45);
                color: #93c5fd;
                font-size: 13px;
                font-weight: 700;
                text-decoration: none;
            }}
            .admin-link {{
                display: block;
                text-align: center;
                margin: 14px 0 40px 0;
                color: #f5cd79;
                font-size: 13px;
                text-decoration: none;
                font-weight: 600;
                text-shadow: 0 1px 4px rgba(0,0,0,0.6);
            }}
            .lightbox-overlay {{
                display: none;
                position: fixed;
                inset: 0;
                background: rgba(10, 10, 12, 0.9);
                z-index: 2000;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }}
            .lightbox-overlay.active {{ display: flex; }}
            .lightbox-box {{
                position: relative;
                max-width: 460px;
                width: 100%;
                background: #1e272e;
                border-radius: 18px;
                padding: 14px;
                box-shadow: 0 16px 40px rgba(0,0,0,0.5);
                text-align: center;
                color: #fff;
            }}
            .lightbox-box img {{
                width: 100%;
                max-height: 70vh;
                object-fit: contain;
                border-radius: 12px;
                background: #121212;
            }}
            .lightbox-caption {{ margin-top: 10px; }}
            .lightbox-title {{
                font-size: 16px;
                font-weight: 700;
                color: #f5cd79;
            }}
            .lightbox-sub {{
                font-size: 13px;
                color: #dcdde1;
                margin-top: 2px;
            }}
            .lightbox-close {{
                position: absolute;
                top: 10px;
                right: 10px;
                width: 34px;
                height: 34px;
                border-radius: 50%;
                border: none;
                background: rgba(0,0,0,0.65);
                color: #fff;
                font-size: 18px;
                font-weight: bold;
                cursor: pointer;
                line-height: 1;
            }}
        </style>
        <script>
            const menuHarga = {menu_js_prices};
            function changeQty(item, delta) {{
                const input = document.getElementById('input_' + item);
                if(!input) return;
                let currentVal = parseInt(input.value) || 0;
                currentVal += delta;
                if (currentVal < 0) currentVal = 0;
                input.value = currentVal;
                calculateTotal();
            }}
            function calculateTotal() {{
                let total = 0;
                for (let item in menuHarga) {{
                    const input = document.getElementById('input_' + item);
                    if (input) total += (parseInt(input.value) || 0) * menuHarga[item];
                }}
                document.getElementById('totalAmount').innerText = 'Rp ' + total.toLocaleString('id-ID');
            }}
            function checkPayment() {{
                const p = document.getElementById('pembayaran').value;
                const bankDiv = document.getElementById('bankInfo');
                const uploadDiv = document.getElementById('uploadArea');
                const fileInput = document.getElementById('buktiFile');
                if (p.includes('Transfer Bank')) {{
                    bankDiv.style.display = 'block'; uploadDiv.style.display = 'block'; fileInput.required = true;
                }} else {{
                    bankDiv.style.display = 'none'; uploadDiv.style.display = 'none'; fileInput.required = false;
                }}
            }}
            function updateLiveClock() {{
                const el = document.getElementById('liveClock');
                if (!el) return;
                const now = new Date();
                el.innerText = '🕒 ' + String(now.getHours()).padStart(2, '0') + ':' + String(now.getMinutes()).padStart(2, '0') + ':' + String(now.getSeconds()).padStart(2, '0');
            }}
            function openLightbox(src, title, sub) {{
                document.getElementById('lightboxImg').src = src;
                document.getElementById('lightboxTitle').innerText = title;
                document.getElementById('lightboxSub').innerText = sub;
                document.getElementById('lightboxOverlay').classList.add('active');
            }}
            function closeLightbox(event) {{
                if (!event || event.target.id === 'lightboxOverlay' || event.target.id === 'lightboxCloseBtn') {{
                    document.getElementById('lightboxOverlay').classList.remove('active');
                }}
            }}
            document.addEventListener('DOMContentLoaded', function() {{ updateLiveClock(); setInterval(updateLiveClock, 1000); }});
            document.addEventListener('keydown', function(e) {{ if (e.key === 'Escape') closeLightbox(); }});
        </script>
    </head>
    <body>
        <div class="hero-banner">
            <h1>RESTO & CAFE GEPREK INTAN</h1>
            <p>Nikmati Kuliner Lezat, Cita Rasa Bintang Lima</p>
            <div class="hero-meta-bar">
                <div id="liveClock" class="live-clock-pill">🕒 --:--:--</div>
                <a href="/pesanan-saya" class="customer-dash-pill">Pesanan Saya <span class="pill-count">{order_badge_text}</span></a>
            </div>
        </div>
        <div class="container">
            <form method="POST" enctype="multipart/form-data">
                <div class="section-title">Daftar Menu Pilihan</div>
                {menu_html}
                <div class="section-title">Informasi Pemesan</div>
                <div class="form-box">
                    <div class="form-group"><label>Nama Lengkap Pemesan *</label><input type="text" name="nama" placeholder="Masukkan nama Anda" required></div>
                    <div class="form-group"><label>Nomor Meja / Alamat Pengiriman *</label><input type="text" name="meja" placeholder="Contoh: Meja 05 / VIP Room" required></div>
                    <div class="form-group">
                        <label>Metode Pembayaran *</label>
                        <select name="pembayaran" id="pembayaran" onchange="checkPayment()" required>
                            <option value="">-- Pilih Pembayaran --</option>
                            <option value="Tunai di Kasir">Tunai di Kasir</option>
                            <option value="Transfer Bank SeaBank">Transfer Bank (SeaBank)</option>
                        </select>
                    </div>
                    <div id="bankInfo" class="bank-info"><b>Info Rekening SeaBank:</b><br><b>No Rek:</b> 901398695544 (a/n Nurdin Abas)<br><i>Transfer sesuai total harga & simpan bukti foto/screenshot transfer.</i></div>
                    <div class="form-group" id="uploadArea" style="display:none; margin-top:15px;"><label>Unggah Foto Bukti Transfer *</label><input type="file" name="bukti_transfer" id="buktiFile" accept="image/*"></div>
                    <div class="form-group" style="margin-bottom:0;"><label>Catatan Khusus (Opsional)</label><textarea name="catatan" rows="2" placeholder="Contoh: Sambal dipisah, tingkat kepedasan, es sedikit"></textarea></div>
                </div>
                <div class="floating-bar">
                    <div><div class="total-text">Total Pembayaran</div><div class="total-price" id="totalAmount">Rp 0</div></div>
                    <button type="submit" class="btn-order">Pesan Sekarang</button>
                </div>
            </form>
            <a href="/pesanan-saya" class="customer-link-box">Buka Dasbor Pesanan Saya (Cek Proses / Selesai & Cancel)</a>
            <a href="/admin-login" class="admin-link">Masuk ke Panel Admin & Pengaturan Menu</a>
        </div>
        <div id="lightboxOverlay" class="lightbox-overlay" onclick="closeLightbox(event)">
            <div class="lightbox-box" onclick="event.stopPropagation()">
                <button type="button" id="lightboxCloseBtn" class="lightbox-close" onclick="closeLightbox()">✕</button>
                <img id="lightboxImg" src="" alt="Preview Menu">
                <div class="lightbox-caption"><div id="lightboxTitle" class="lightbox-title"></div><div id="lightboxSub" class="lightbox-sub"></div></div>
            </div>
        </div>
    </body>
    </html>
    """

@app.route("/pesanan-saya", methods=["GET", "POST"])
def pesanan_saya():
    brand_img = get_brand_image_url()
    info_msg = ""
    if request.method == "POST":
        order_id_raw = request.form.get("order_id", "").replace("#", "").strip()
        if order_id_raw.isdigit():
            oid = int(order_id_raw)
            db = get_db()
            found = db.execute("SELECT id FROM pesanan WHERE id = ?", (oid,)).fetchone()
            if found:
                remember_customer_order_id(oid)
                info_msg = f"Pesanan #{oid} berhasil ditambahkan ke dasbor pesanan Anda."
            else:
                info_msg = f"Pesanan #{oid} tidak ditemukan."
        else:
            info_msg = "Masukkan nomor ID pesanan yang valid (contoh: 6)."

    orders = get_customer_orders()
    cards_html = ""
    for order in orders:
        oid = order["id"]
        st = order["status"]
        status_bg, status_fg, status_border = get_status_badge_style(st)
        catatan_text = order["catatan"] if order["catatan"] else "-"
        order_keys = order.keys()
        raw_waktu = order["waktu"] if "waktu" in order_keys else None
        ts_ms = parse_order_timestamp_ms(raw_waktu)
        waktu_label = str(raw_waktu) if raw_waktu else "Waktu tidak tercatat"
        if ts_ms is not None:
            elapsed_html = f'<span class="order-elapsed" data-ts="{ts_ms}" data-status="{st}">Menghitung...</span>'
        else:
            elapsed_html = '<span class="order-elapsed-na">Durasi belum tercatat</span>'

        if st in ("Menunggu Verifikasi", "Diproses"):
            status_desc = "Pesanan sedang ditangani. Anda bisa membatalkan pesanan jika belum direspons atau ingin membatalkannya."
            cancel_btn = f'<a href="/pesanan-saya/cancel/{oid}" onclick="return confirm(\'Yakin ingin membatalkan Pesanan #{oid}?\')" class="btn-cancel-order">Cancel Pesanan</a>'
        elif st == "Dibatalkan Pelanggan":
            status_desc = "Anda telah membatalkan pesanan ini. Riwayat tetap tersimpan dan hanya admin yang dapat menghapus riwayat."
            cancel_btn = '<span class="muted-status-note">Pesanan telah dibatalkan</span>'
        else:
            status_desc = "Pesanan sudah selesai. Riwayat pesanan hanya dapat dihapus oleh admin."
            cancel_btn = '<span class="muted-status-note">Pesanan selesai</span>'

        if order["bukti_transfer"]:
            bukti_note = f'<div class="bukti-info">Bukti Transfer: {order["bukti_transfer"]}</div>'
        else:
            bukti_note = f'<div class="bukti-info">Metode: {order["metode_pembayaran"]}</div>'

        cards_html += f"""
        <div class="order-card">
            <div class="order-card-head">
                <div>
                    <span class="order-id">Pesanan #{oid}</span>
                    <span class="order-customer-name"> • {order['nama']}</span>
                    <div class="order-table-sub">{order['meja']}</div>
                </div>
                <span class="status-pill" style="background:{status_bg}; color:{status_fg}; border:1px solid {status_border};">{st}</span>
            </div>
            <div class="order-time-strip"><span class="order-time-exact">{waktu_label}</span>{elapsed_html}</div>
            <div class="order-detail-box">
                <div class="order-detail-label">Rincian Paket / Menu</div>
                <div class="order-detail-text">{order['rincian']}</div>
                <div class="order-note-text"><b>Catatan:</b> {catatan_text}</div>
            </div>
            <div class="order-meta-row"><div><div class="order-total-val">Rp {order['total']:,}</div>{bukti_note}</div></div>
            <div class="order-status-note">{status_desc}</div>
            <div class="order-card-actions">{cancel_btn}</div>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="theme-color" content="#c0392b">
        <link rel="icon" type="image/png" href="{brand_img}">
        <link rel="apple-touch-icon" href="{brand_img}">
        <link rel="manifest" href="/manifest.json">
        <title>Dasbor Pesanan Saya - GEPREK INTAN</title>
        <style>
            * {{ box-sizing: border-box; }}
            html, body {{
                width: 100%;
                max-width: 100vw;
                overflow-x: hidden;
                margin: 0;
                padding: 0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #f1f5f9;
                color: #1e293b;
                min-height: 100vh;
            }}
            .dashboard-shell {{
                width: 100%;
                min-height: 100vh;
                background: #ffffff;
                padding: 16px 14px 36px 14px;
            }}
            @media (min-width: 768px) {{ body {{ padding: 16px; }} .dashboard-shell {{ border-radius: 18px; padding: 24px 28px 40px 28px; box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06); border: 1px solid #e2e8f0; }} }}
            .top-bar {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 8px;
                flex-wrap: wrap;
                padding-bottom: 12px;
                border-bottom: 1px solid #e2e8f0;
            }}
            .back-btn {{
                color: #dc2626;
                text-decoration: none;
                font-weight: 700;
                font-size: 13px;
                padding: 8px 12px;
                border-radius: 8px;
                background: #fef2f2;
                border: 1px solid #fecaca;
            }}
            .refresh-btn {{
                background: #0f172a;
                color: #ffffff;
                text-decoration: none;
                font-weight: 700;
                font-size: 12px;
                padding: 8px 12px;
                border-radius: 8px;
            }}
            .header-row {{
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                gap: 12px;
                flex-wrap: wrap;
                margin: 14px 0 16px 0;
            }}
            h2 {{
                color: #0f172a;
                margin: 0 0 4px 0;
                font-size: 20px;
                font-weight: 800;
                line-height: 1.25;
            }}
            .subtitle {{
                color: #64748b;
                font-size: 13px;
                margin: 0;
                line-height: 1.4;
            }}
            .lookup-box {{
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 12px;
                margin-bottom: 16px;
            }}
            .lookup-form {{
                display: flex;
                gap: 8px;
                flex-wrap: wrap;
            }}
            .lookup-input {{
                flex: 1;
                min-width: 160px;
                padding: 9px 12px;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                font-size: 13px;
                background: #ffffff;
            }}
            .lookup-btn {{
                background: #2563eb;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 9px 14px;
                font-size: 12.5px;
                font-weight: 700;
                cursor: pointer;
            }}
            .info-banner {{
                background: #eff6ff;
                border: 1px solid #bfdbfe;
                color: #1e40af;
                padding: 10px 12px;
                border-radius: 8px;
                font-size: 12.5px;
                font-weight: 600;
                margin-bottom: 14px;
            }}
            .orders-list {{
                display: grid;
                grid-template-columns: 1fr;
                gap: 12px;
            }}
            @media (min-width: 900px) {{ .orders-list {{ grid-template-columns: repeat(2, 1fr); gap: 16px; }} }}
            .order-card {{
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 14px;
                padding: 14px;
                box-shadow: 0 3px 10px rgba(15, 23, 42, 0.04);
                display: flex;
                flex-direction: column;
                gap: 10px;
            }}
            .order-card-head {{
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                gap: 8px;
            }}
            .order-id {{
                font-weight: 800;
                color: #dc2626;
                font-size: 13px;
            }}
            .order-customer-name {{
                font-weight: 800;
                color: #0f172a;
                font-size: 14px;
            }}
            .order-table-sub {{
                font-size: 12px;
                color: #64748b;
                margin-top: 2px;
            }}
            .status-pill {{
                padding: 4px 10px;
                border-radius: 999px;
                font-size: 11px;
                font-weight: 700;
                white-space: nowrap;
                flex-shrink: 0;
            }}
            .order-time-strip {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 8px;
                flex-wrap: wrap;
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 7px 10px;
                font-size: 12px;
            }}
            .order-time-exact {{
                font-weight: 700;
                color: #334155;
            }}
            .order-elapsed {{
                display: inline-block;
                background: #fff7ed;
                color: #c2410c;
                border: 1px solid #fed7aa;
                padding: 2px 8px;
                border-radius: 999px;
                font-size: 11px;
                font-weight: 700;
                white-space: nowrap;
            }}
            .order-elapsed.done-status {{
                background: #f0fdf4;
                color: #15803d;
                border-color: #bbf7d0;
            }}
            .order-elapsed-na {{
                font-size: 11px;
                color: #94a3b8;
            }}
            .order-detail-box {{
                background: #fafbfd;
                border-left: 3px solid #cbd5e1;
                padding: 8px 10px;
                border-radius: 0 8px 8px 0;
            }}
            .order-detail-label {{
                font-size: 10.5px;
                font-weight: 700;
                text-transform: uppercase;
                color: #64748b;
                letter-spacing: 0.3px;
                margin-bottom: 3px;
            }}
            .order-detail-text {{
                font-size: 13px;
                font-weight: 600;
                color: #0f172a;
                line-height: 1.45;
                word-wrap: break-word;
            }}
            .order-note-text {{
                font-size: 12px;
                color: #475569;
                margin-top: 5px;
                line-height: 1.35;
                word-wrap: break-word;
            }}
            .order-meta-row {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 10px;
                flex-wrap: wrap;
                padding-top: 4px;
                border-top: 1px dashed #e2e8f0;
            }}
            .order-total-val {{
                font-size: 15px;
                font-weight: 800;
                color: #0f172a;
            }}
            .bukti-info {{
                font-size: 12px;
                color: #64748b;
                margin-top: 2px;
                word-break: break-word;
            }}
            .order-status-note {{
                font-size: 12px;
                color: #475569;
                background: #f8fafc;
                padding: 8px 10px;
                border-radius: 8px;
                line-height: 1.35;
            }}
            .order-card-actions {{
                display: flex;
                gap: 8px;
                flex-wrap: wrap;
                align-items: center;
            }}
            .btn-cancel-order {{
                display: inline-block;
                background: #dc2626;
                color: #ffffff;
                text-decoration: none;
                padding: 7px 14px;
                border-radius: 8px;
                font-size: 12px;
                font-weight: 700;
            }}
            .muted-status-note {{
                font-size: 11.5px;
                color: #64748b;
                font-style: italic;
            }}
            .empty-orders-box {{
                text-align: center;
                padding: 28px 16px;
                color: #64748b;
                background: #f8fafc;
                border: 1px dashed #cbd5e1;
                border-radius: 12px;
                font-size: 13px;
                line-height: 1.5;
            }}
        </style>
        <script>
            function formatElapsed(sec) {{
                if (sec < 0) sec = 0;
                const jam = Math.floor(sec / 3600), menit = Math.floor((sec % 3600) / 60), detik = sec % 60;
                if (jam > 0) return jam + 'j ' + menit + 'm ' + detik + 'd lalu';
                if (menit > 0) return menit + 'm ' + detik + 'd lalu';
                return detik + 'd lalu';
            }}
            function updateCustomerElapsed() {{
                const nowMs = Date.now();
                document.querySelectorAll('.order-elapsed').forEach(function(el) {{
                    const ts = parseInt(el.getAttribute('data-ts'), 10);
                    const status = el.getAttribute('data-status') || '';
                    if (!isNaN(ts)) {{
                        const durText = formatElapsed(Math.floor((nowMs - ts) / 1000));
                        if (status === 'Selesai') {{ el.classList.add('done-status'); el.innerText = 'Selesai (' + durText + ')'; }}
                        else {{ el.classList.remove('done-status'); el.innerText = durText; }}
                    }}
                }});
            }}
            document.addEventListener('DOMContentLoaded', function() {{ updateCustomerElapsed(); setInterval(updateCustomerElapsed, 1000); }});
        </script>
    </head>
    <body>
        <div class="dashboard-shell">
            <div class="top-bar"><a href="/" class="back-btn">← Kembali ke Menu</a><a href="/pesanan-saya" class="refresh-btn">Refresh Status</a></div>
            <div class="header-row"><div><h2>Dasbor Pesanan Saya</h2><p class="subtitle">Cek apakah pesanan sedang diproses atau sudah selesai, serta batalkan jika belum direspons. Penghapusan riwayat hanya oleh admin.</p></div></div>
            <div class="lookup-box">
                <form method="POST" class="lookup-form">
                    <input type="text" name="order_id" class="lookup-input" placeholder="Masukkan No. ID Pesanan (contoh: 6)">
                    <button type="submit" class="lookup-btn">+ Tampilkan Pesanan</button>
                </form>
            </div>
            {f'<div class="info-banner">{info_msg}</div>' if info_msg else ''}
            <div class="orders-list">{cards_html if cards_html else '<div class="empty-orders-box">Belum ada pesanan yang tercatat di perangkat ini.<br>Silakan pesan menu terlebih dahulu atau masukkan No. ID Pesanan di atas.</div>'}</div>
        </div>
    </body>
    </html>
    """

@app.route("/pesanan-saya/cancel/<int:id>")
def cancel_pesanan_pelanggan(id):
    allowed_ids = get_customer_order_ids()
    if id not in allowed_ids:
        return redirect(url_for("pesanan_saya"))
    db = get_db()
    row = db.execute("SELECT status FROM pesanan WHERE id = ?", (id,)).fetchone()
    if row and row["status"] in ("Menunggu Verifikasi", "Diproses"):
        db.execute("UPDATE pesanan SET status = ? WHERE id = ?", ("Dibatalkan Pelanggan", id))
        db.commit()
    return redirect(url_for("pesanan_saya"))

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    error = ""
    brand_img = get_brand_image_url()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "admin" and password == "geprekintan123":
            session["logged_in"] = True
            return redirect(url_for("admin"))
        else:
            error = "Username atau Password salah!"

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="theme-color" content="#c0392b">
        <link rel="icon" type="image/png" href="{brand_img}">
        <link rel="apple-touch-icon" href="{brand_img}">
        <link rel="manifest" href="/manifest.json">
        <title>Login Admin - GEPREK INTAN</title>
        <style>
            * {{ box-sizing: border-box; }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #eef2f6;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                padding: 16px;
            }}
            .login-card {{
                background: white;
                padding: 28px 24px;
                border-radius: 18px;
                box-shadow: 0 12px 30px rgba(15,23,42,0.08);
                width: 100%;
                max-width: 420px;
                border: 1px solid #e2e8f0;
            }}
            h2 {{
                color: #1e293b;
                text-align: center;
                margin-top: 0;
                font-size: 22px;
            }}
            .form-group {{ margin-bottom: 15px; }}
            .form-group label {{
                font-size: 12px;
                font-weight: 700;
                color: #475569;
                display: block;
                margin-bottom: 6px;
            }}
            .form-group input {{
                width: 100%;
                padding: 12px 14px;
                border: 1px solid #cbd5e1;
                border-radius: 10px;
                box-sizing: border-box;
                font-size: 14px;
                color: #0f172a;
            }}
            .btn-login {{
                width: 100%;
                background: linear-gradient(135deg, #1e293b, #0f172a);
                color: white;
                border: none;
                padding: 13px;
                border-radius: 10px;
                font-size: 15px;
                font-weight: 700;
                cursor: pointer;
                margin-top: 8px;
            }}
            .error {{
                color: #dc2626;
                font-size: 13px;
                text-align: center;
                margin-bottom: 15px;
                font-weight: 700;
                background: #fef2f2;
                padding: 10px;
                border-radius: 8px;
                border: 1px solid #fecaca;
            }}
            .back-link {{
                display: block;
                text-align: center;
                margin-top: 16px;
                color: #475569;
                font-size: 13px;
                text-decoration: none;
                font-weight: 600;
            }}
        </style>
    </head>
    <body>
        <div class="login-card">
            <h2>Login Admin</h2>
            <p style="text-align:center; font-size:13px; color:#64748b; margin-bottom:20px;">Resto & Cafe Geprek Intan</p>
            {f'<div class="error">{error}</div>' if error else ''}
            <form method="POST">
                <div class="form-group"><label>Username</label><input type="text" name="username" placeholder="Masukkan username" required></div>
                <div class="form-group"><label>Password</label><input type="password" name="password" placeholder="Masukkan password" required></div>
                <button type="submit" class="btn-login">Masuk Panel Admin</button>
            </form>
            <a href="/" class="back-link">← Kembali ke Menu Utama</a>
        </div>
    </body>
    </html>
    """

@app.route("/admin")
def admin():
    if not session.get("logged_in"):
        return redirect(url_for("admin_login"))
    brand_img = get_brand_image_url()
    db = get_db()
    all_orders = db.execute("SELECT * FROM pesanan ORDER BY id DESC").fetchall()
    total_omset = sum(order["total"] for order in all_orders if order["status"] != "Dibatalkan Pelanggan")
    total_transaksi = len(all_orders)
    total_selesai = sum(1 for order in all_orders if order["status"] == "Selesai")
    total_proses = sum(1 for order in all_orders if order["status"] in ("Diproses", "Menunggu Verifikasi"))
    menu_status = get_menu_status()
    menu_rows = ""
    for item in MENU_MASTER:
        st = menu_status.get(item, 1)
        encoded_item = encode_menu_key(item)
        status_badge = '<span class="badge-ready">● Tersedia</span>' if st == 1 else '<span class="badge-empty">● Habis</span>'
        action_btn = f'<a href="/admin/menu-toggle/{encoded_item}/0" class="btn-action btn-close-menu">Tutup Stok</a>' if st == 1 else f'<a href="/admin/menu-toggle/{encoded_item}/1" class="btn-action btn-open-menu">Buka Stok</a>'
        menu_rows += f"""
        <tr>
            <td class="col-menu"><div class="menu-name-cell">{item}</div><div class="menu-cat-cell">{MENU_MASTER[item]['kategori']}</div></td>
            <td class="col-price">Rp {MENU_MASTER[item]['harga']:,}</td>
            <td class="col-status">{status_badge}</td>
            <td class="col-action">{action_btn}</td>
        </tr>
        """
    order_cards = ""
    for order in all_orders:
        oid = order["id"]
        st = order["status"]
        status_bg, status_fg, status_border = get_status_badge_style(st)
        if order["bukti_transfer"]:
            bukti_html = f'<a href="/static/uploads/{order["bukti_transfer"]}" target="_blank" class="btn-mini btn-bukti">Lihat Bukti Transfer</a>'
        else:
            bukti_html = '<span class="muted-note">Pembayaran Tunai (Tanpa Bukti)</span>'
        catatan_text = order["catatan"] if order["catatan"] else "-"
        order_keys = order.keys()
        raw_waktu = order["waktu"] if "waktu" in order_keys else None
        ts_ms = parse_order_timestamp_ms(raw_waktu)
        waktu_label = str(raw_waktu) if raw_waktu else "Waktu tidak tercatat"
        if ts_ms is not None:
            elapsed_html = f'<span class="order-elapsed" data-ts="{ts_ms}" data-status="{st}">Menghitung...</span>'
        else:
            elapsed_html = '<span class="order-elapsed-na">Durasi belum tercatat</span>'
        order_cards += f"""
        <div class="order-card">
            <div class="order-card-head">
                <div><span class="order-id">Pesanan #{oid}</span><span class="order-customer-name"> • {order['nama']}</span><div class="order-table-sub">{order['meja']}</div></div>
                <span class="status-pill" style="background:{status_bg}; color:{status_fg}; border:1px solid {status_border};">{st}</span>
            </div>
            <div class="order-time-strip"><span class="order-time-exact">{waktu_label}</span>{elapsed_html}</div>
            <div class="order-detail-box"><div class="order-detail-label">Rincian Menu</div><div class="order-detail-text">{order['rincian']}</div><div class="order-note-text"><b>Catatan:</b> {catatan_text}</div></div>
            <div class="order-meta-row"><div><div class="order-total-val">Rp {order['total']:,}</div><div class="order-pay-method">{order['metode_pembayaran']}</div></div><div>{bukti_html}</div></div>
            <div class="order-card-actions">
                <a href="/admin/status/{oid}/Diproses" class="btn-mini btn-proses">Proses</a>
                <a href="/admin/status/{oid}/Selesai" class="btn-mini btn-selesai">Selesai</a>
                <a href="/admin/hapus/{oid}" onclick="return confirm(\'Yakin ingin menghapus riwayat pesanan #{oid}?\')" class="btn-mini btn-hapus">Hapus Riwayat</a>
            </div>
        </div>
        """
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="theme-color" content="#c0392b">
        <link rel="icon" type="image/png" href="{brand_img}">
        <link rel="apple-touch-icon" href="{brand_img}">
        <link rel="manifest" href="/manifest.json">
        <title>Dashboard Admin - GEPREK INTAN</title>
        <style>
            * {{ box-sizing: border-box; }}
            html, body {{
                width: 100%;
                max-width: 100vw;
                overflow-x: hidden;
                margin: 0;
                padding: 0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #f1f5f9;
                color: #1e293b;
                min-height: 100vh;
            }}
            .dashboard-shell {{
                width: 100%;
                min-height: 100vh;
                background: #ffffff;
                padding: 16px 14px 36px 14px;
            }}
            @media (min-width: 768px) {{ body {{ padding: 16px; }} .dashboard-shell {{ border-radius: 18px; padding: 24px 28px 40px 28px; box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06); border: 1px solid #e2e8f0; }} }}
            .top-bar {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 8px;
                flex-wrap: wrap;
                padding-bottom: 12px;
                border-bottom: 1px solid #e2e8f0;
            }}
            .back-btn {{
                color: #dc2626;
                text-decoration: none;
                font-weight: 700;
                font-size: 13px;
                padding: 8px 12px;
                border-radius: 8px;
                background: #fef2f2;
                border: 1px solid #fecaca;
            }}
            .logout-btn {{
                background: #0f172a;
                color: white;
                padding: 8px 14px;
                border-radius: 8px;
                text-decoration: none;
                font-size: 12px;
                font-weight: 700;
            }}
            .header-row {{
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                gap: 12px;
                flex-wrap: wrap;
                margin: 14px 0 18px 0;
            }}
            h2 {{
                color: #0f172a;
                margin: 0 0 4px 0;
                font-size: 21px;
                font-weight: 800;
                line-height: 1.25;
            }}
            .subtitle {{
                color: #64748b;
                font-size: 13px;
                margin: 0;
            }}
            .admin-live-clock {{
                background: #0f172a;
                color: #f8fafc;
                padding: 8px 14px;
                border-radius: 10px;
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 0.3px;
                white-space: nowrap;
            }}
            h3 {{
                color: #0f172a;
                font-size: 15px;
                font-weight: 700;
                margin: 22px 0 10px 0;
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: 1fr;
                gap: 10px;
                margin: 14px 0 20px 0;
            }}
            @media (min-width: 640px) {{ .stats-grid {{ grid-template-columns: repeat(3, 1fr); gap: 14px; }} }}
            .stat-card {{
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 14px 16px;
                border-left: 5px solid #16a34a;
            }}
            .stat-card.primary {{
                border-left-color: #16a34a;
                background: #f0fdf4;
                border-color: #bbf7d0;
            }}
            .stat-card.blue {{
                border-left-color: #2563eb;
                background: #eff6ff;
                border-color: #bfdbfe;
            }}
            .stat-card.orange {{
                border-left-color: #ea580c;
                background: #fff7ed;
                border-color: #fed7aa;
            }}
            .stat-title {{
                font-size: 11px;
                font-weight: 700;
                color: #64748b;
                text-transform: uppercase;
                letter-spacing: 0.3px;
            }}
            .stat-value {{
                font-size: 19px;
                font-weight: 800;
                color: #0f172a;
                margin-top: 4px;
            }}
            .table-wrap {{
                width: 100%;
                overflow-x: hidden;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                margin-bottom: 22px;
            }}
            .menu-table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 13px;
                table-layout: fixed;
            }}
            .menu-table th, .menu-table td {{
                padding: 10px 8px;
                text-align: left;
                border-bottom: 1px solid #e2e8f0;
                vertical-align: middle;
                overflow-wrap: break-word;
                word-break: break-word;
            }}
            .menu-table th {{
                background: #1e293b;
                color: #f8fafc;
                font-size: 12px;
                font-weight: 700;
            }}
            .menu-table tr:last-child td {{ border-bottom: none; }}
            .menu-table tr:nth-child(even) td {{ background: #fafbfd; }}
            .menu-name-cell {{
                font-weight: 700;
                color: #0f172a;
                font-size: 12.5px;
                line-height: 1.3;
            }}
            .menu-cat-cell {{
                font-size: 10.5px;
                color: #64748b;
                margin-top: 2px;
            }}
            .badge-ready {{
                background: #dcfce7;
                color: #15803d;
                padding: 5px 7px;
                border-radius: 999px;
                font-size: 10.5px;
                font-weight: 700;
                display: inline-block;
                line-height: 1.25;
            }}
            .badge-empty {{
                background: #fee2e2;
                color: #b91c1c;
                padding: 5px 7px;
                border-radius: 999px;
                font-size: 10.5px;
                font-weight: 700;
                display: inline-block;
                line-height: 1.25;
            }}
            .btn-action {{
                display: inline-block;
                padding: 7px 8px;
                border-radius: 8px;
                text-decoration: none;
                font-size: 11px;
                font-weight: 700;
                color: #ffffff;
                text-align: center;
                line-height: 1.25;
            }}
            .btn-close-menu {{ background: #dc2626; }}
            .btn-open-menu {{ background: #16a34a; }}
            .orders-list {{
                display: grid;
                grid-template-columns: 1fr;
                gap: 12px;
            }}
            @media (min-width: 900px) {{ .orders-list {{ grid-template-columns: repeat(2, 1fr); gap: 16px; }} }}
            .order-card {{
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 14px;
                padding: 14px;
                box-shadow: 0 3px 10px rgba(15, 23, 42, 0.04);
                display: flex;
                flex-direction: column;
                gap: 10px;
            }}
            .order-card-head {{
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                gap: 8px;
            }}
            .order-id {{
                font-weight: 800;
                color: #dc2626;
                font-size: 13px;
            }}
            .order-customer-name {{
                font-weight: 800;
                color: #0f172a;
                font-size: 14px;
            }}
            .order-table-sub {{
                font-size: 12px;
                color: #64748b;
                margin-top: 2px;
            }}
            .status-pill {{
                padding: 4px 10px;
                border-radius: 999px;
                font-size: 11px;
                font-weight: 700;
                white-space: nowrap;
                flex-shrink: 0;
            }}
            .order-time-strip {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 8px;
                flex-wrap: wrap;
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 7px 10px;
                font-size: 12px;
            }}
            .order-time-exact {{
                font-weight: 700;
                color: #334155;
            }}
            .order-elapsed {{
                display: inline-block;
                background: #fff7ed;
                color: #c2410c;
                border: 1px solid #fed7aa;
                padding: 2px 8px;
                border-radius: 999px;
                font-size: 11px;
                font-weight: 700;
                white-space: nowrap;
            }}
            .order-elapsed.done-status {{
                background: #f0fdf4;
                color: #15803d;
                border-color: #bbf7d0;
            }}
            .order-elapsed-na {{
                font-size: 11px;
                color: #94a3b8;
            }}
            .order-detail-box {{
                background: #fafbfd;
                border-left: 3px solid #cbd5e1;
                padding: 8px 10px;
                border-radius: 0 8px 8px 0;
            }}
            .order-detail-label {{
                font-size: 10.5px;
                font-weight: 700;
                text-transform: uppercase;
                color: #64748b;
                letter-spacing: 0.3px;
                margin-bottom: 3px;
            }}
            .order-detail-text {{
                font-size: 13px;
                font-weight: 600;
                color: #0f172a;
                line-height: 1.45;
                word-wrap: break-word;
            }}
            .order-note-text {{
                font-size: 12px;
                color: #475569;
                margin-top: 5px;
                line-height: 1.35;
                word-wrap: break-word;
            }}
            .order-meta-row {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 10px;
                flex-wrap: wrap;
                padding-top: 4px;
                border-top: 1px dashed #e2e8f0;
            }}
            .order-total-val {{
                font-size: 15px;
                font-weight: 800;
                color: #0f172a;
            }}
            .order-pay-method {{
                font-size: 12px;
                color: #64748b;
                margin-top: 1px;
            }}
            .muted-note {{
                font-size: 11.5px;
                color: #94a3b8;
                font-style: italic;
            }}
            .order-card-actions {{
                display: flex;
                gap: 6px;
                flex-wrap: wrap;
                padding-top: 4px;
            }}
            .btn-mini {{
                display: inline-block;
                padding: 6px 12px;
                border-radius: 7px;
                text-decoration: none;
                font-size: 11.5px;
                font-weight: 700;
                color: #ffffff;
                white-space: nowrap;
            }}
            .btn-bukti {{ background: #2563eb; }}
            .btn-proses {{ background: #ea580c; }}
            .btn-selesai {{ background: #16a34a; }}
            .btn-hapus {{ background: #dc2626; }}
            .empty-orders-box {{
                text-align: center;
                padding: 28px 16px;
                color: #64748b;
                background: #f8fafc;
                border: 1px dashed #cbd5e1;
                border-radius: 12px;
                font-size: 13px;
            }}
        </style>
        <script>
            function formatElapsed(sec) {{
                if (sec < 0) sec = 0;
                const jam = Math.floor(sec / 3600), menit = Math.floor((sec % 3600) / 60), detik = sec % 60;
                if (jam > 0) return jam + 'j ' + menit + 'm ' + detik + 'd lalu';
                if (menit > 0) return menit + 'm ' + detik + 'd lalu';
                return detik + 'd lalu';
            }}
            function updateAdminTime() {{
                const now = new Date();
                const clockEl = document.getElementById('adminLiveClock');
                if (clockEl) clockEl.innerText = '🕒 Waktu Sekarang: ' + String(now.getHours()).padStart(2, '0') + ':' + String(now.getMinutes()).padStart(2, '0') + ':' + String(now.getSeconds()).padStart(2, '0');
                const nowMs = Date.now();
                document.querySelectorAll('.order-elapsed').forEach(function(el) {{
                    const ts = parseInt(el.getAttribute('data-ts'), 10);
                    const status = el.getAttribute('data-status') || '';
                    if (!isNaN(ts)) {{
                        const durText = formatElapsed(Math.floor((nowMs - ts) / 1000));
                        if (status === 'Selesai') {{ el.classList.add('done-status'); el.innerText = 'Selesai (' + durText + ')'; }}
                        else {{ el.classList.remove('done-status'); el.innerText = durText; }}
                    }}
                }});
            }}
            document.addEventListener('DOMContentLoaded', function() {{ updateAdminTime(); setInterval(updateAdminTime, 1000); }});
        </script>
    </head>
    <body>
        <div class="dashboard-shell">
            <div class="top-bar"><a href="/" class="back-btn">← Menu Pelanggan</a><a href="/admin-logout" class="logout-btn">Keluar</a></div>
            <div class="header-row">
                <div><h2>Dashboard Admin - GEPREK INTAN</h2><p class="subtitle">Kelola stok menu harian, pantau waktu pesanan, dan rekap omzet.</p></div>
                <div id="adminLiveClock" class="admin-live-clock">🕒 Waktu Sekarang: --:--:--</div>
            </div>
            <div class="stats-grid">
                <div class="stat-card primary"><div class="stat-title">Total Pendapatan / Omzet</div><div class="stat-value" style="color:#15803d;">Rp {total_omset:,}</div></div>
                <div class="stat-card blue"><div class="stat-title">Total Pesanan Masuk</div><div class="stat-value">{total_transaksi} Pesanan</div></div>
                <div class="stat-card orange"><div class="stat-title">Pesanan Diproses / Selesai</div><div class="stat-value">{total_proses} Proses / {total_selesai} Selesai</div></div>
            </div>
            <h3>Pengaturan Ketersediaan Menu (Buka / Tutup Stok)</h3>
            <div class="table-wrap">
                <table class="menu-table">
                    <thead><tr><th style="width:37%;">Menu</th><th style="width:20%;">Harga</th><th style="width:22%;">Status</th><th style="width:21%;">Aksi</th></tr></thead>
                    <tbody>{menu_rows}</tbody>
                </table>
            </div>
            <h3>Daftar Pesanan Pelanggan Masuk</h3>
            <div class="orders-list">{order_cards if order_cards else '<div class="empty-orders-box">Belum ada pesanan masuk.</div>'}</div>
        </div>
    </body>
    </html>
    """

@app.route("/admin/menu-toggle/<string:menu_key>/<int:status_baru>")
def menu_toggle(menu_key, status_baru):
    if not session.get("logged_in"):
        return redirect(url_for("admin_login"))
    try:
        nama_menu = decode_menu_key(menu_key)
    except Exception:
        nama_menu = menu_key
    if nama_menu not in MENU_MASTER:
        return redirect(url_for("admin"))
    db = get_db()
    db.execute("INSERT INTO menu_status (nama_menu, tersedia) VALUES (?, ?) ON CONFLICT(nama_menu) DO UPDATE SET tersedia = ?", (nama_menu, status_baru, status_baru))
    db.commit()
    return redirect(url_for("admin"))

@app.route("/admin/status/<int:id>/<string:status_baru>")
def ubah_status(id, status_baru):
    if not session.get("logged_in"):
        return redirect(url_for("admin_login"))
    db = get_db()
    db.execute("UPDATE pesanan SET status = ? WHERE id = ?", (status_baru, id))
    db.commit()
    return redirect(url_for("admin"))

@app.route("/admin/hapus/<int:id>")
def hapus_pesanan(id):
    if not session.get("logged_in"):
        return redirect(url_for("admin_login"))
    db = get_db()
    db.execute("DELETE FROM pesanan WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("admin"))

@app.route("/admin-logout")
def admin_logout():
    session.pop("logged_in", None)
    return redirect(url_for("admin_login"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
