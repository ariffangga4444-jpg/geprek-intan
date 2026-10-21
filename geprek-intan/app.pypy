from flask import Flask, request

app = Flask(__name__)

# Data Menu Makanan & Harga
MENU = {
    "Nasi Goreng": 15000,
    "Ayam Geprek": 15000,
    "Mie GenZ": 13000,
    "Soto Ayam": 15000,
    "Es Teh": 5000,
    "Jus Segar": 5000,
}


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        nama = request.form.get("nama")
        meja = request.form.get("meja")
        catatan = request.form.get("catatan", "")

        pesanan_items = []
        total_harga = 0

        for item, harga in MENU.items():
            qty = request.form.get(f"qty_{item}", 0)
            if qty and int(qty) > 0:
                jumlah = int(qty)
                subtotal = jumlah * harga
                total_harga += subtotal
                pesanan_items.append(
                    {"nama": item, "harga": harga, "qty": jumlah, "subtotal": subtotal}
                )

        if not pesanan_items:
            return """<script>alert('Pilih minimal 1 menu!'); window.history.back();</script>"""

        # Tampilan Struk / Konfirmasi Pesanan
        html_struk = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Struk Pesanan - GEPREK INTAN</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #eef2f5; padding: 20px; }}
                .card {{ max-width: 450px; margin: 0 auto; background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
                .success {{ color: #2ecc71; text-align: center; margin-bottom: 10px; }}
                h2 {{ text-align: center; color: #d63031; margin-top: 0; }}
                .info {{ background: #f8f9fa; padding: 12px; border-radius: 8px; margin-bottom: 20px; font-size: 14px; line-height: 1.6; }}
                table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #eee; }}
                th {{ background: #ff7675; color: white; border-radius: 4px; }}
                .total {{ font-size: 18px; font-weight: bold; color: #d63031; text-align: right; margin-top: 15px; }}
                .btn {{ display: block; width: 100%; text-align: center; background: #d63031; color: white; text-decoration: none; padding: 12px; border-radius: 8px; font-weight: bold; margin-top: 20px; box-sizing: border-box; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h3 class="success">✅ Pesanan Berhasil Dibuat!</h3>
                <h2>🍗 GEPREK INTAN</h2>
                
                <div class="info">
                    <b>Nama Pemesan:</b> {nama}<br>
                    <b>Nomor Meja / Alamat:</b> {meja}<br>
                    <b>Catatan:</b> {catatan if catatan else '-'}
                </div>

                <h3>Rincian Pesanan:</h3>
                <table>
                    <tr>
                        <th>Menu</th>
                        <th>Qty</th>
                        <th>Harga</th>
                        <th>Subtotal</th>
                    </tr>
        """
        for item in pesanan_items:
            html_struk += f"""
                    <tr>
                        <td>{item['nama']}</td>
                        <td>{item['qty']}x</td>
                        <td>Rp{item['harga']:,}</td>
                        <td>Rp{item['subtotal']:,}</td>
                    </tr>
            """

        html_struk += f"""
                </table>

                <div class="total">Total Bayar: Rp{total_harga:,}</div>

                <a href="/" class="btn">Pesanan Baru</a>
            </div>
        </body>
        </html>
        """
        return html_struk

    # Tampilan Halaman Utama (Pemesanan Menu)
    menu_html = ""
    for item, harga in MENU.items():
        menu_html += f"""
        <div class="menu-item">
            <div class="menu-info">
                <span class="menu-title">{item}</span>
                <span class="menu-price">Rp {harga:,}</span>
            </div>
            <div class="qty-control">
                <button type="button" onclick="changeQty('{item}', -1)">-</button>
                <input type="number" id="input_{item}" name="qty_{item}" value="0" min="0" readonly>
                <button type="button" onclick="changeQty('{item}', 1)">+</button>
            </div>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>GEPREK INTAN - Order Food</title>
        <style>
            * {{ box-sizing: border-box; }}
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8f9fa; margin: 0; padding: 15px; color: #333; }}
            .container {{ max-width: 480px; margin: 0 auto; background: white; padding: 20px; border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); }}
            .header {{ text-align: center; border-bottom: 2px dashed #ff7675; padding-bottom: 12px; margin-bottom: 20px; }}
            .header h1 {{ color: #d63031; margin: 0; font-size: 24px; }}
            .header p {{ color: #636e72; margin: 4px 0 0 0; font-size: 14px; }}
            
            .section-title {{ font-size: 16px; font-weight: bold; margin-bottom: 12px; color: #2d3436; display: flex; align-items: center; justify-content: space-between; }}
            
            .menu-item {{ display: flex; justify-content: space-between; align-items: center; padding: 12px; margin-bottom: 10px; background: #fff5f5; border-radius: 12px; border: 1px solid #ffeaa7; }}
            .menu-info {{ display: flex; flex-direction: column; }}
            .menu-title {{ font-weight: bold; font-size: 15px; color: #2d3436; }}
            .menu-price {{ color: #d63031; font-weight: bold; font-size: 14px; margin-top: 3px; }}
            
            .qty-control {{ display: flex; align-items: center; gap: 6px; }}
            .qty-control button {{ width: 32px; height: 32px; border-radius: 50%; border: none; background: #d63031; color: white; font-size: 18px; font-weight: bold; cursor: pointer; display: flex; align-items: center; justify-content: center; }}
            .qty-control input {{ width: 35px; text-align: center; border: none; background: transparent; font-weight: bold; font-size: 16px; }}

            .form-group {{ margin-top: 15px; }}
            .form-group label {{ font-size: 13px; font-weight: bold; color: #636e72; display: block; margin-bottom: 5px; }}
            .form-group input, .form-group textarea {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; outline: none; }}
            .form-group input:focus {{ border-color: #d63031; }}

            .footer-bar {{ margin-top: 20px; padding-top: 15px; border-top: 1px solid #eee; }}
            .total-display {{ display: flex; justify-content: space-between; font-size: 18px; font-weight: bold; margin-bottom: 15px; color: #2d3436; }}
            .total-amount {{ color: #d63031; }}

            .btn-order {{ width: 100%; background: #d63031; color: white; border: none; padding: 14px; border-radius: 10px; font-size: 16px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 10px rgba(214, 48, 49, 0.3); }}
            .btn-order:active {{ transform: scale(0.98); }}
        </style>
        <script>
            const menuHarga = { {
                "Nasi Goreng": 15000,
                "Ayam Geprek": 15000,
                "Mie GenZ": 13000,
                "Soto Ayam": 15000,
                "Es Teh": 5000,
                "Jus Segar": 5000
            } };

            function changeQty(item, delta) {{
                const input = document.getElementById('input_' + item);
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
                        const qty = parseInt(input.value) || 0;
                        total += qty * menuHarga[item];
                    }}
                }}
                document.getElementById('totalAmount').innerText = 'Rp ' + total.toLocaleString('id-ID');
            }}
        </script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🍗 GEPREK INTAN</h1>
                <p>Pesan Makanan Praktis & Cepat</p>
            </div>

            <form method="POST">
                <div class="section-title">
                    <span>Pilih Menu Makanan</span>
                </div>

                {menu_html}

                <div class="form-group">
                    <label>Nama Pemesan *</label>
                    <input type="text" name="nama" placeholder="Contoh: Intan" required>
                </div>

                <div class="form-group">
                    <label>Nomor Meja / Alamat Pengiriman *</label>
                    <input type="text" name="meja" placeholder="Contoh: Meja 05 / Jl. Mawar No 12" required>
                </div>

                <div class="form-group">
                    <label>Catatan Khusus (Opsional)</label>
                    <textarea name="catatan" rows="2" placeholder="Contoh: Ayam pedas sedang, es teh manis banget"></textarea>
                </div>

                <div class="footer-bar">
                    <div class="total-display">
                        <span>Total Bayar:</span>
                        <span class="total-amount" id="totalAmount">Rp 0</span>
                    </div>
                    <button type="submit" class="btn-order">🛒 Kirim Pesanan</button>
                </div>
            </form>
        </div>
    </body>
    </html>
    """


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=5000)
