"""
Penyensor KTP — versi stabil Day 2
Satu file, siap dijalankan: streamlit run app.py
Dependensi: streamlit, pillow
"""

from io import BytesIO

import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# ═══════════════════════════════════════════════════════════════
# KONFIGURASI HALAMAN
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Penyensor KTP",
    page_icon="🪪",
    layout="centered",
)

# ═══════════════════════════════════════════════════════════════
# DEFINISI FIELD KTP (koordinat ternormalisasi 0..1)
# ═══════════════════════════════════════════════════════════════
KTP_FIELDS = [
    # (x1, y1, x2, y2, label)
    (0.03, 0.28, 0.35, 0.72, "Foto"),
    (0.38, 0.17, 0.97, 0.25, "NIK"),
    (0.38, 0.25, 0.97, 0.33, "Nama"),
    (0.38, 0.33, 0.97, 0.41, "TTL"),
    (0.38, 0.41, 0.58, 0.47, "JK"),
    (0.38, 0.47, 0.97, 0.55, "Alamat"),
    (0.38, 0.55, 0.58, 0.61, "RT/RW"),
    (0.58, 0.55, 0.97, 0.61, "Kel/Desa"),
    (0.38, 0.61, 0.97, 0.67, "Kec"),
    (0.38, 0.67, 0.58, 0.73, "Agama"),
    (0.38, 0.73, 0.97, 0.79, "Pekerjaan"),
    (0.60, 0.86, 0.97, 0.98, "TTD"),
]

# ═══════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════
for key, default in {
    "captured_image": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ═══════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════
st.title("🪪 Penyensor Kartu Identitas")
st.caption("Versi stabil — ambil foto KTP, lalu verifikasi posisi field")

st.info(
    "Posisikan KTP memenuhi frame kamera. "
    "Setelah foto diambil, Anda akan melihat box merah penanda field KTP. "
    "Tekan tombol kamera untuk mengambil gambar."
)

st.warning(
    "📱 **Pengguna ponsel:** kamera hanya dapat diakses melalui alamat "
    "**HTTPS** atau **localhost**. Jika aplikasi dibuka lewat IP LAN biasa "
    "(http://192.168.x.x), browser akan memblokir akses kamera tanpa pesan error. "
    "Gunakan Streamlit Community Cloud, ngrok, atau tunnel HTTPS lainnya."
)

# ═══════════════════════════════════════════════════════════════
# KAMERA
# ═══════════════════════════════════════════════════════════════
st.subheader("📹 Ambil Foto KTP")

captured_file = st.camera_input(
    "Arahkan kamera ke KTP, pastikan seluruh bagian KTP masuk ke frame",
    key="ktp_cam",
)

if captured_file is not None:
    current_img = Image.open(captured_file).convert("RGB")
    st.session_state.captured_image = current_img.copy()
    st.success("Gambar tersimpan.")
else:
    st.caption(
        "Belum ada gambar. Jika tombol kamera tidak muncul atau kamera tidak terbuka, "
        "periksa kembali apakah alamat akses sudah HTTPS."
    )

# ═══════════════════════════════════════════════════════════════
# HASIL CAPTURE + OVERLAY VERIFIKASI
# ═══════════════════════════════════════════════════════════════
if st.session_state.captured_image is not None:
    st.subheader("🔍 Verifikasi Hasil")

    def get_font(size=14):
        for path in (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
        return ImageFont.load_default()

    verified = st.session_state.captured_image.copy()
    draw = ImageDraw.Draw(verified)
    W, H = verified.size
    font = get_font(max(12, W // 60))

    # Frame luar KTP (hijau)
    draw.rectangle([2, 2, W - 3, H - 3], outline=(0, 230, 118), width=3)

    # Box per field (merah)
    for x1, y1, x2, y2, label in KTP_FIELDS:
        box = (int(x1 * W), int(y1 * H), int(x2 * W), int(y2 * H))
        draw.rectangle(box, outline=(255, 60, 60), width=2)
        draw.text((box[0] + 3, box[1] + 2), label, fill=(255, 60, 60), font=font)

    st.image(
        verified,
        caption="Pastikan seluruh KTP berada di dalam frame hijau dan box merah pas.",
        use_container_width=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Hapus & Ambil Ulang", use_container_width=True):
            st.session_state.captured_image = None
            st.rerun()
    with col2:
        st.caption("Lanjut ke pemilihan field sensor (Day 3) di iterasi berikutnya.")
else:
    st.caption("Belum ada gambar. Arahkan KTP ke kamera lalu ambil foto.")