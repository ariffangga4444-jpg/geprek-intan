import json
import os
import sqlite3
from datetime import datetime
from flask import (
    Flask,
    Response,
    g,
    redirect,
    request,
    send_from_directory,
    session,
    url_for,
)
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "geprek_intan_secret_key_sejahtera"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "geprek_intan.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


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
            {
                "src": icon_url,
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": icon_url,
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any",
            },
        ],
    }
    return Response(json.dumps(manifest_data), mimetype="application/manifest+json")


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


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
        db.execute(
            """
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
        """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS menu_status (
                nama_menu TEXT PRIMARY KEY,
                tersedia INTEGER NOT NULL
            )
        """
        )
        db.commit()


init_db()

MENU_MASTER = {
    "Nasi Putih / Mangkok": {
        "harga": 5000,
        "gambar": "https://images.unsplash.com/photo-1516684732162-7984084b22af?w=400&q=80",
        "deskripsi": "Nasi putih hangat pulen per mangkok",
        "kategori": "Menu Tambahan",
    },
    "Nasi Goreng Spesial + Jus": {
        "harga": 15000,
        "gambar": "https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=400&q=80",
        "deskripsi": "Nasi goreng bumbu rempah spesial + segarnya minuman jus",
        "kategori": "Makanan Utama",
    },
    "Nasi Ayam Lalapan + Jus": {
        "harga": 15000,
        "gambar": "https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?w=400&q=80",
        "deskripsi": "Nasi + ayam lalapan sambal segar + minuman jus",
        "kategori": "Makanan Utama",
    },
    "Nasi Ayam Geprek + Jus": {
        "harga": 15000,
        "gambar": "https://images.unsplash.com/photo-1562967914-608f82629710?w=400&q=80",
        "deskripsi": "Nasi + ayam krispi geprek pedas + minuman jus",
        "kategori": "Makanan Utama",
    },
    "Mie Bakso Biasa": {
        "harga": 15000,
        "gambar": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400&q=80",
        "deskripsi": "Mie kuah hangat dengan sajian bakso sapi gurih",
        "kategori": "Mie & Soto",
    },
    "Mie GenZ Pedas (LV 1)": {
        "harga": 10000,
        "gambar": "https://images.unsplash.com/photo-1612927601601-6638404737ce?w=400&q=80",
        "deskripsi": "Mie pedas kekinian Level 1",
        "kategori": "Mie & Soto",
    },
    "Mie GenZ Pedas (LV 2)": {
        "harga": 12000,
        "gambar": "https://images.unsplash.com/photo-1612927601601-6638404737ce?w=400&q=80",
        "deskripsi": "Mie pedas kekinian Level 2",
        "kategori": "Mie & Soto",
    },
    "Mie GenZ Pedas (LV 3)": {
        "harga": 13000,
        "gambar": "https://images.unsplash.com/photo-1612927601601-6638404737ce?w=400&q=80",
        "deskripsi": "Mie pedas kekinian Level 3 mantap",
        "kategori": "Mie & Soto",
    },
    "Soto Ayam + Jus": {
        "harga": 15000,
        "gambar": "https://images.unsplash.com/photo-1547592166-23ac45744acd?w=400&q=80",
        "deskripsi": "Kuah soto kuning segar + suwiran ayam & soun + jus",
        "kategori": "Mie & Soto",
    },
    "Milu Siram / Bindebiluhuta": {
        "harga": 7000,
        "gambar": "https://images.unsplash.com/photo-1541544741938-0af808871cc0?w=400&q=80",
        "deskripsi": "Kuliner khas jagung siram kuah lezat",
        "kategori": "Spesial Khas",
    },
    "Ayam Lalapan Tanpa Nasi": {
        "harga": 13000,
        "gambar": "https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?w=400&q=80",
        "deskripsi": "Ayam krispi + lalapan sambal (tanpa nasi)",
        "kategori": "Menu Ala Carte",
    },
    "Ayam Geprek Tanpa Nasi": {
        "harga": 13000,
        "gambar": "https://images.unsplash.com/photo-1562967914-608f82629710?w=400&q=80",
        "deskripsi": "Ayam krispi digeprek sambal pedas (tanpa nasi)",
        "kategori": "Menu Ala Carte",
    },
    "Teh Hangat": {
        "harga": 5000,
        "gambar": "https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=400&q=80",
        "deskripsi": "Teh hangat manis pas di badan",
        "kategori": "Minuman & Snack",
    },
    "Fanta Susu": {
        "harga": 10000,
        "gambar": "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=400&q=80",
        "deskripsi": "Minuman bersoda Fanta dicampur susu kental manis",
        "kategori": "Minuman & Snack",
    },
    "Kopi": {
        "harga": 6000,
        "gambar": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=400&q=80",
        "deskripsi": "Kopi hitam racikan nikmat",
        "kategori": "Minuman & Snack",
    },
    "Pisang Stik Goroho": {
        "harga": 12000,
        "gambar": "https://images.unsplash.com/photo-1599328821758-00a39d892d11?w=400&q=80",
        "deskripsi": "Stik pisang goroho renyah gurih",
        "kategori": "Minuman & Snack",
    },
}


def get_menu_status():
    db = get_db()
    cursor = db.execute("SELECT nama_menu, tersedia FROM menu_status")
    status_dict = {
        row["nama_menu"]: row["tersedia"] for row in cursor.fetchall()
    }
    for m in MENU_MASTER:
        if m not in status_dict:
            status_dict[m] = 1
    return status_dict


@app.route("/", methods=["GET", "POST"])
def index():
    menu_status = get_menu_status()
    brand_img = get_brand_image_url()

    if request.method == "POST":
        nama = request.form.get("nama")
        meja = request.form.get("meja")
        catatan = request.form.get("catatan", "")
        metode_pembayaran = request.form.get("pembayaran")
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
        if "Transfer Bank" in metode_pembayaran or "QRIS" in metode_pembayaran:
            file_bukti = request.files.get("bukti_transfer")
            if (
                not file_bukti
                or file_bukti.filename == ""
                or not allowed_file(file_bukti.filename)
            ):
                return "<script>alert('❌ Harap unggah foto bukti transfer terlebih dahulu!'); window.history.back();</script>"
            filename = secure_filename(
                f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file_bukti.filename}"
            )
            file_bukti.save(
                os.path.join(app.config["UPLOAD_FOLDER"], filename)
            )
            bukti_filename = filename
            status_awal = "Menunggu Verifikasi"
        else:
            status_awal = "Diproses"

        rincian_str = ", ".join(pesanan_items)
        db = get_db()
        db.execute(
            "INSERT INTO pesanan (nama, meja, catatan, rincian, total, metode_pembayaran, bukti_transfer, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                nama,
                meja,
                catatan,
                rincian_str,
                total_harga,
                metode_pembayaran,
                bukti_filename,
                status_awal,
            ),
        )
        db.commit()
        status_badge_color = (
            "#f39c12" if status_awal == "Menunggu Verifikasi" else "#27ae60"
        )

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <meta name="theme-color" content="#c0392b">
            <link rel="icon" type="image/png" href="{brand_img}">
            <link rel="apple-touch-icon" href="{brand_img}">
            <link rel="manifest" href="/manifest.json">
            <title>Struk Pesanan - GEPREK INTAN</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(rgba(18, 12, 12, 0.72), rgba(18, 12, 12, 0.86)),
                                url('{brand_img}') center / cover fixed no-repeat;
                    padding: 20px;
                    color: #333;
                    min-height: 100vh;
                }}
                .card {{ max-width: 480px; margin: 0 auto; background: rgba(255, 255, 255, 0.96); padding: 25px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.22); }}
                h2 {{ text-align: center; color: #c0392b; margin-top: 0; }}
                .info {{ background: #fdfefe; border: 1px solid #eaeded; padding: 15px; border-radius: 12px; margin-bottom: 20px; font-size: 14px; line-height: 1.6; }}
                .total {{ font-size: 18px; font-weight: bold; color: #c0392b; text-align: right; margin-top: 15px; }}
                .btn {{ display: block; text-align: center; background: linear-gradient(135deg, #e74c3c, #c0392b); color: white; text-decoration: none; padding: 14px; border-radius: 12px; font-weight: bold; margin-top: 20px; box-shadow: 0 4px 15px rgba(231,76,60,0.3); }}
            </style>
        </head>
        <body>
            <div class="card">
                <h3 style="color:#27ae60; text-align:center;">✨ Pesanan Berhasil Dikirim!</h3>
                <h2>🍗 GEPREK INTAN</h2>
                <div class="info">
                    <b>Nama Pemesan:</b> {nama}<br>
                    <b>Meja / Alamat:</b> {meja}<br>
                    <b>Metode Pembayaran:</b> {metode_pembayaran}<br>
                    <b>Status Pembayaran:</b> <span style="background:{status_badge_color}; color:white; padding:3px 10px; border-radius:6px; font-weight:bold; font-size:12px;">{status_awal}</span><br>
                    <b>Catatan:</b> {catatan if catatan else '-'}<br><br>
                    <b>Rincian Menu:</b><br>{rincian_str}
                </div>
                <div class="total">Total Bayar: Rp{total_harga:,}</div>
                <a href="/" class="btn">Buat Pesanan Baru</a>
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
                <img src="{gambar}" alt="{item}">
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
                <img src="{gambar}" alt="{item}">
                <div class="menu-info">
                    <div class="menu-title" style="text-decoration:line-through; color:#95a5a6;">{item}</div>
                    <div class="menu-desc">{deskripsi}</div>
                    <div style="color:#e74c3c; font-weight:bold; font-size:12px; margin-top:4px;">HABIS TERJUAL</div>
                </div>
                <div><span class="badge-habis">Habis</span></div>
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
        <title>GEPREK INTAN - Resto & Cafe</title>
        <style>
            * {{ box-sizing: border-box; }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(rgba(18, 12, 12, 0.68), rgba(18, 12, 12, 0.84)),
                            url('{brand_img}') center / cover fixed no-repeat;
                margin: 0;
                padding: 0;
                color: #2c3e50;
                padding-bottom: 90px;
                min-height: 100vh;
            }}
            .hero-banner {{
                background: linear-gradient(135deg, rgba(30, 39, 46, 0.86), rgba(47, 54, 64, 0.86)), url('https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=1000&q=80');
                background-blend-mode: overlay; background-size: cover; background-position: center;
                color: white; text-align: center; padding: 35px 20px;
                border-bottom-left-radius: 25px; border-bottom-right-radius: 25px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.22);
            }}
            .hero-banner h1 {{ margin: 0; font-size: 26px; font-weight: 800; letter-spacing: 1px; color: #f5cd79; }}
            .hero-banner p {{ margin: 8px 0 0 0; font-size: 13px; color: #dcdde1; }}
            .container {{ max-width: 500px; margin: 0 auto; padding: 15px; }}
            .menu-card {{
                display: flex; justify-content: space-between; align-items: center;
                background: rgba(255, 255, 255, 0.95); padding: 12px; margin-bottom: 12px; border-radius: 16px;
                box-shadow: 0 6px 18px rgba(0,0,0,0.16); border: 1px solid rgba(255,255,255,0.7);
            }}
            .menu-card img {{ width: 75px; height: 75px; object-fit: cover; border-radius: 12px; border: 1px solid #eee; }}
            .menu-info {{ flex: 1; padding: 0 12px; }}
            .menu-title {{ font-size: 15px; font-weight: 700; color: #2f3640; }}
            .menu-desc {{ font-size: 11px; color: #718093; margin-top: 3px; line-height: 1.3; }}
            .menu-price {{ font-size: 14px; font-weight: bold; color: #e74c3c; margin-top: 6px; }}
            .qty-control {{ display: flex; align-items: center; background: #f8f9fa; padding: 4px; border-radius: 25px; border: 1px solid #dfe4ea; }}
            .qty-btn {{ width: 30px; height: 30px; border-radius: 50%; border: none; background: #e74c3c; color: white; font-weight: bold; font-size: 16px; cursor: pointer; display: flex; align-items: center; justify-content: center; }}
            .qty-input {{ width: 28px; text-align: center; border: none; background: transparent; font-weight: bold; font-size: 14px; color: #2f3640; }}
            .sold-out {{ background: rgba(241, 242, 246, 0.9); opacity: 0.82; }}
            .badge-habis {{ background: #c0392b; color: white; padding: 5px 10px; border-radius: 8px; font-size: 11px; font-weight: bold; }}
            .section-title {{ font-size: 16px; font-weight: 700; color: #f5cd79; margin: 25px 0 12px 5px; border-left: 4px solid #e74c3c; padding-left: 8px; text-shadow: 0 1px 4px rgba(0,0,0,0.6); }}
            .form-box {{ background: rgba(255, 255, 255, 0.96); padding: 20px; border-radius: 16px; box-shadow: 0 6px 18px rgba(0,0,0,0.16); margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.7); }}
            .form-group {{ margin-bottom: 15px; }}
            .form-group label {{ font-size: 12px; font-weight: bold; color: #718093; display: block; margin-bottom: 6px; }}
            .form-group input, .form-group select, .form-group textarea {{ width: 100%; padding: 12px; border: 1px solid #dfe4ea; border-radius: 10px; box-sizing: border-box; font-size: 14px; background: #fdfefe; }}
            .bank-info {{ background:#e8f4fd; border:1px solid #bbeeff; padding:15px; border-radius:12px; font-size:12px; margin-top:10px; display:none; color: #004080; line-height: 1.5; }}
            .floating-bar {{
                position: fixed; bottom: 0; left: 0; right: 0; background: rgba(255, 255, 255, 0.97); padding: 15px 20px;
                box-shadow: 0 -5px 25px rgba(0,0,0,0.18); display: flex; justify-content: space-between; align-items: center;
                border-top-left-radius: 20px; border-top-right-radius: 20px; z-index: 1000;
            }}
            .total-text {{ font-size: 13px; color: #718093; }}
            .total-price {{ font-size: 18px; font-weight: 800; color: #e74c3c; }}
            .btn-order {{ background: linear-gradient(135deg, #e74c3c, #c0392b); color: white; border: none; padding: 12px 24px; border-radius: 12px; font-size: 15px; font-weight: bold; cursor: pointer; }}
            .admin-link {{ display: block; text-align: center; margin: 20px 0 40px 0; color: #f5cd79; font-size: 13px; text-decoration: none; font-weight: 600; text-shadow: 0 1px 4px rgba(0,0,0,0.6); }}
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
                    if (input) {{
                        total += (parseInt(input.value) || 0) * menuHarga[item];
                    }}
                }}
                document.getElementById('totalAmount').innerText = 'Rp ' + total.toLocaleString('id-ID');
            }}
            function checkPayment() {{
                const p = document.getElementById('pembayaran').value;
                const bankDiv = document.getElementById('bankInfo');
                const uploadDiv = document.getElementById('uploadArea');
                const fileInput = document.getElementById('buktiFile');
                if (p.includes('Transfer Bank') || p.includes('QRIS')) {{
                    bankDiv.style.display = 'block';
                    uploadDiv.style.display = 'block';
                    fileInput.required = true;
                }} else {{
                    bankDiv.style.display = 'none';
                    uploadDiv.style.display = 'none';
                    fileInput.required = false;
                }}
            }}
        </script>
    </head>
    <body>
        <div class="hero-banner">
            <h1>🍗 RESTO & CAFE GEPREK INTAN</h1>
            <p>Nikmati Kuliner Lezat, Cita Rasa Bintang Lima</p>
        </div>
        <div class="container">
            <form method="POST" enctype="multipart/form-data">
                <div class="section-title">Daftar Menu Pilihan</div>
                {menu_html}
                <div class="section-title">Informasi Pemesan</div>
                <div class="form-box">
                    <div class="form-group">
                        <label>Nama Lengkap Pemesan *</label>
                        <input type="text" name="nama" placeholder="Masukkan nama Anda" required>
                    </div>
                    <div class="form-group">
                        <label>Nomor Meja / Alamat Pengiriman *</label>
                        <input type="text" name="meja" placeholder="Contoh: Meja 05 / VIP Room" required>
                    </div>
                    <div class="form-group">
                        <label>Metode Pembayaran *</label>
                        <select name="pembayaran" id="pembayaran" onchange="checkPayment()" required>
                            <option value="">-- Pilih Pembayaran --</option>
                            <option value="Tunai di Kasir">💵 Tunai di Kasir</option>
                            <option value="Transfer Bank SeaBank">🏦 Transfer Bank (SeaBank)</option>
                            <option value="QRIS (Digital)">📱 Pembayaran Digital QRIS</option>
                        </select>
                    </div>
                    <div id="bankInfo" class="bank-info">
                        <b>🏦 Info Rekening SeaBank:</b><br>
                        <b>No Rek:</b> 901398695544 (a/n Nurdin Abas)<br>
                        <i>Transfer sesuai total harga & simpan bukti foto/screenshot transfer.</i>
                    </div>
                    <div class="form-group" id="uploadArea" style="display:none; margin-top:15px;">
                        <label>📸 Unggah Foto Bukti Transfer *</label>
                        <input type="file" name="bukti_transfer" id="buktiFile" accept="image/*">
                    </div>
                    <div class="form-group" style="margin-bottom:0;">
                        <label>Catatan Khusus (Opsional)</label>
                        <textarea name="catatan" rows="2" placeholder="Contoh: Sambal dipisah, tingkat kepedasan, es sedikit"></textarea>
                    </div>
                </div>
                <div class="floating-bar">
                    <div>
                        <div class="total-text">Total Pembayaran</div>
                        <div class="total-price" id="totalAmount">Rp 0</div>
                    </div>
                    <button type="submit" class="btn-order">Pesan Sekarang 🚀</button>
                </div>
            </form>
            <a href="/admin-login" class="admin-link">🔒 Masuk ke Panel Admin & Pengaturan Menu</a>
        </div>
    </body>
    </html>
    """


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
            error = "❌ Username atau Password salah!"

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
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f6f9; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
            .login-card {{ background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); width: 100%; max-width: 380px; }}
            h2 {{ color: #2c3e50; text-align: center; margin-top: 0; }}
            .form-group {{ margin-bottom: 15px; }}
            .form-group label {{ font-size: 12px; font-weight: bold; color: #718093; display: block; margin-bottom: 6px; }}
            .form-group input {{ width: 100%; padding: 12px; border: 1px solid #dfe4ea; border-radius: 10px; box-sizing: border-box; font-size: 14px; }}
            .btn-login {{ width: 100%; background: linear-gradient(135deg, #2c3e50, #1e272e); color: white; border: none; padding: 12px; border-radius: 10px; font-size: 15px; font-weight: bold; cursor: pointer; margin-top: 10px; }}
            .error {{ color: #e74c3c; font-size: 13px; text-align: center; margin-bottom: 15px; font-weight: bold; }}
            .back-link {{ display: block; text-align: center; margin-top: 15px; color: #718093; font-size: 13px; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="login-card">
            <h2>🔐 Login Admin</h2>
            <p style="text-align:center; font-size:12px; color:#718093; margin-bottom:20px;">Resto & Cafe Geprek Intan</p>
            {f'<div class="error">{error}</div>' if error else ''}
            <form method="POST">
                <div class="form-group">
                    <label>Username</label>
                    <input type="text" name="username" placeholder="Masukkan username" required>
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="password" placeholder="Masukkan password" required>
                </div>
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
    cursor = db.execute("SELECT * FROM pesanan ORDER BY id DESC")
    all_orders = cursor.fetchall()

    total_omset = sum(order["total"] for order in all_orders)
    total_transaksi = len(all_orders)
    total_selesai = sum(
        1 for order in all_orders if order["status"] == "Selesai"
    )
    total_proses = sum(
        1 for order in all_orders if order["status"] == "Diproses"
    )

    menu_status = get_menu_status()
    menu_rows = ""
    for item in MENU_MASTER:
        st = menu_status.get(item, 1)
        if st == 1:
            status_label = '<span style="color:#27ae60; font-weight:bold;">🟢 Tersedia (Ready)</span>'
            action_btn = f'<a href="/admin/menu-toggle/{item}/0" style="background:#e74c3c; color:white; padding:5px 10px; text-decoration:none; border-radius:6px; font-size:11px; font-weight:bold;">Tutup Menu (Habis)</a>'
        else:
            status_label = '<span style="color:#c0392b; font-weight:bold;">🔴 Habis (Kosong)</span>'
            action_btn = f'<a href="/admin/menu-toggle/{item}/1" style="background:#27ae60; color:white; padding:5px 10px; text-decoration:none; border-radius:6px; font-size:11px; font-weight:bold;">Buka Menu (Tersedia)</a>'
        menu_rows += f"""
        <tr>
            <td><b>{item}</b></td>
            <td>Rp {MENU_MASTER[item]['harga']:,}</td>
            <td>{status_label}</td>
            <td>{action_btn}</td>
        </tr>
        """

    order_rows = ""
    for order in all_orders:
        st = order["status"]
        status_color = (
            "#f39c12"
            if st == "Menunggu Verifikasi"
            else ("#d35400" if st == "Diproses" else "#27ae60")
        )
        bukti_btn = (
            f'<a href="/static/uploads/{order["bukti_transfer"]}" target="_blank" style="background:#2980b9; color:white; padding:4px 8px; border-radius:4px; text-decoration:none; font-size:11px;">📸 Lihat Bukti</a>'
            if order["bukti_transfer"]
            else "-"
        )
        order_rows += f"""
        <tr>
            <td>#{order['id']}</td>
            <td><b>{order['nama']}</b><br><small>{order['meja']}</small></td>
            <td>{order['rincian']}<br><small style="color:#7f8c8d;">Catatan: {order['catatan']}</small></td>
            <td><b>Rp{order['total']:,}</b><br><small>{order['metode_pembayaran']}</small></td>
            <td>{bukti_btn}</td>
            <td><span style="background: {status_color}; color: white; padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight:bold;">{st}</span></td>
            <td>
                <div style="display:flex; gap:4px; flex-wrap:wrap;">
                    <a href="/admin/status/{order['id']}/Diproses" style="background:#d35400; color:white; padding:4px 8px; text-decoration:none; border-radius:4px; font-size:11px; font-weight:bold;">Proses</a>
                    <a href="/admin/status/{order['id']}/Selesai" style="background:#27ae60; color:white; padding:4px 8px; text-decoration:none; border-radius:4px; font-size:11px; font-weight:bold;">Selesai</a>
                    <a href="/admin/hapus/{order['id']}" onclick="return confirm('Yakin ingin menghapus pesanan #{order['id']} ini?')" style="background:#c0392b; color:white; padding:4px 8px; text-decoration:none; border-radius:4px; font-size:11px; font-weight:bold;">🗑️ Hapus</a>
                </div>
            </td>
        </tr>
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
        <title>Admin Resto - GEPREK INTAN</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f6f9; padding: 20px; color: #333; }}
            .container {{ max-width: 950px; margin: 0 auto; background: white; padding: 25px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); }}
            h2, h3 {{ color: #2c3e50; }}
            .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0 30px 0; }}
            .stat-card {{ background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 12px; padding: 15px; border-left: 5px solid #27ae60; box-shadow: 0 2px 8px rgba(0,0,0,0.02); }}
            .stat-card.primary {{ border-left-color: #27ae60; background: #e8f8f5; }}
            .stat-card.blue {{ border-left-color: #2980b9; background: #ebf5fb; }}
            .stat-card.orange {{ border-left-color: #e67e22; background: #fef5e7; }}
            .stat-title {{ font-size: 12px; font-weight: bold; color: #7f8c8d; text-transform: uppercase; }}
            .stat-value {{ font-size: 22px; font-weight: 800; color: #2c3e50; margin-top: 5px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; margin-bottom: 25px; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #e9ecef; }}
            th {{ background: #2c3e50; color: white; }}
            .top-bar {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }}
            .back-btn {{ color: #e74c3c; text-decoration: none; font-weight: bold; }}
            .logout-btn {{ background: #c0392b; color: white; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-size: 12px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="top-bar">
                <a href="/" class="back-btn">← Kembali ke Menu Pelanggan</a>
                <a href="/admin-logout" class="logout-btn">🚪 Keluar (Logout)</a>
            </div>
            <h2>🛠️ Panel Manajemen Resto GEPREK INTAN</h2>

            <div class="stats-grid">
                <div class="stat-card primary">
                    <div class="stat-title">💰 Total Pendapatan / Omzet</div>
                    <div class="stat-value" style="color:#27ae60;">Rp {total_omset:,}</div>
                </div>
                <div class="stat-card blue">
                    <div class="stat-title">📦 Total Pesanan Masuk</div>
                    <div class="stat-value">{total_transaksi} Pesanan</div>
                </div>
                <div class="stat-card orange">
                    <div class="stat-title">⏳ Pesanan Diproses / Selesai</div>
                    <div class="stat-value">{total_proses} Proses / {total_selesai} Selesai</div>
                </div>
            </div>

            <h3>⚙️ Pengaturan Ketersediaan Menu (Buka / Tutup Stok)</h3>
            <div style="overflow-x:auto;">
                <table>
                    <tr><th>Nama Menu</th><th>Harga</th><th>Status</th><th>Aksi</th></tr>
                    {menu_rows}
                </table>
            </div>

            <h3>📦 Daftar Pesanan Pelanggan Masuk</h3>
            <div style="overflow-x:auto;">
                <table>
                    <tr><th>ID</th><th>Pemesan</th><th>Rincian</th><th>Total & Bayar</th><th>Bukti</th><th>Status</th><th>Aksi</th></tr>
                    {order_rows if order_rows else '<tr><td colspan="7" style="text-align:center; padding:20px; color:#7f8c8d;">Belum ada pesanan masuk.</td></tr>'}
                </table>
            </div>
        </div>
    </body>
    </html>
    """


@app.route("/admin/menu-toggle/<string:nama_menu>/<int:status_baru>")
def menu_toggle(nama_menu, status_baru):
    if not session.get("logged_in"):
        return redirect(url_for("admin_login"))
    db = get_db()
    db.execute(
        "INSERT INTO menu_status (nama_menu, tersedia) VALUES (?, ?) ON CONFLICT(nama_menu) DO UPDATE SET tersedia = ?",
        (nama_menu, status_baru, status_baru),
    )
    db.commit()
    return redirect(url_for("admin"))


@app.route("/admin/status/<int:id>/<string:status_baru>")
def ubah_status(id, status_baru):
    if not session.get("logged_in"):
        return redirect(url_for("admin_login"))
    db = get_db()
    db.execute(
        "UPDATE pesanan SET status = ? WHERE id = ?", (status_baru, id)
    )
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
