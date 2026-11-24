"""
Penyensor KTP — Day 3
Field selection + saran default + preview area sensor
Dependensi: streamlit, pillow
"""

import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# ═══════════════════════════════════════════════════════════════
# KONFIGURASI
# ═══════════════════════════════════════════════════════════════
st.set_page_config(page_title="Penyensor KTP", page_icon="🪪", layout="centered")

# ═══════════════════════════════════════════════════════════════
# DEFINISI FIELD KTP
# ═══════════════════════════════════════════════════════════════
KTP_FIELDS = [
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

# Field yang disarankan disensor (tanda ⭐)
SUGGESTED_FIELDS = {"Foto", "NIK", "Nama", "Alamat", "TTD"}

# ═══════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════
if "captured_image" not in st.session_state:
    st.session_state.captured_image = None

# ═══════════════════════════════════════════════════════════════
# HELPER: FONT
# ═══════════════════════════════════════════════════════════════
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

# ═══════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════
st.title("🪪 Penyensor Kartu Identitas")
st.caption("Ambil foto KTP → verifikasi posisi → pilih field yang disensor")

st.info(
    "Posisikan KTP memenuhi frame kamera. Setelah foto diambil, "
    "Anda akan melihat box penanda field KTP, lalu bisa memilih mana yang disensor."
)

st.warning(
    "📱 **Pengguna ponsel:** kamera hanya aktif via **HTTPS** atau **localhost**. "
    "Akses via IP LAN (http://192.168.x.x) akan diblokir browser tanpa pesan error. "
    "Gunakan Streamlit Community Cloud atau tunnel HTTPS."
)

# ═══════════════════════════════════════════════════════════════
# 1️⃣ KAMERA
# ═══════════════════════════════════════════════════════════════
st.subheader("1️⃣ Ambil Foto KTP")

captured_file = st.camera_input(
    "Arahkan kamera ke KTP, pastikan seluruh bagian KTP masuk ke frame",
    key="ktp_cam",
)

if captured_file is not None:
    st.session_state.captured_image = Image.open(captured_file).convert("RGB")

if st.session_state.captured_image is None:
    st.caption("Belum ada gambar. Tekan tombol kamera di atas.")
    st.stop()

# ═══════════════════════════════════════════════════════════════
# 2️⃣ VERIFIKASI POSISI
# ═══════════════════════════════════════════════════════════════
st.subheader("2️⃣ Verifikasi Posisi")
st.caption("Pastikan seluruh KTP berada di dalam frame hijau dan box pas menutupi field.")

verified = st.session_state.captured_image.copy()
draw = ImageDraw.Draw(verified)
W, H = verified.size
font = get_font(max(12, W // 60))

draw.rectangle([2, 2, W - 3, H - 3], outline=(0, 230, 118), width=3)
for x1, y1, x2, y2, label in KTP_FIELDS:
    box = (int(x1 * W), int(y1 * H), int(x2 * W), int(y2 * H))
    color = (255, 60, 60) if label in SUGGESTED_FIELDS else (60, 140, 255)
    draw.rectangle(box, outline=color, width=2)
    draw.text((box[0] + 3, box[1] + 2), label, fill=color, font=font)

st.image(verified, use_container_width=True)

col1, col2 = st.columns([1, 2])
with col1:
    if st.button("🔄 Ambil Ulang", use_container_width=True):
        st.session_state.captured_image = None
        st.rerun()
with col2:
    st.caption("🔴 Merah = disarankan disensor · 🔵 Biru = opsional")

# ═══════════════════════════════════════════════════════════════
# 3️⃣ PEMILIHAN FIELD
# ═══════════════════════════════════════════════════════════════
st.subheader("3️⃣ Pilih Field yang Akan Disensor")
st.caption("Field bertanda ⭐ disarankan disensor. Anda bebas mengubah pilihan.")

selected_labels = []
cols = st.columns(2)
for i, (_, _, _, _, label) in enumerate(KTP_FIELDS):
    is_suggested = label in SUGGESTED_FIELDS
    display = f"{label} ⭐" if is_suggested else label
    with cols[i % 2]:
        if st.checkbox(display, value=is_suggested, key=f"field_{label}"):
            selected_labels.append(label)

st.session_state.selected_fields = selected_labels

# ═══════════════════════════════════════════════════════════════
# PREVIEW AREA SENSOR
# ═══════════════════════════════════════════════════════════════
st.subheader("4️⃣ Preview Area Sensor")

if selected_labels:
    st.success(
        f"**{len(selected_labels)} field** akan disensor: "
        f"{', '.join(selected_labels)}"
    )

    preview = st.session_state.captured_image.convert("RGBA")
    overlay = Image.new("RGBA", preview.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    W, H = preview.size
    for x1, y1, x2, y2, label in KTP_FIELDS:
        if label in selected_labels:
            box = (int(x1 * W), int(y1 * H), int(x2 * W), int(y2 * H))
            overlay_draw.rectangle(
                box,
                fill=(255, 0, 0, 70),
                outline=(255, 60, 60, 255),
                width=2,
            )
    preview = Image.alpha_composite(preview, overlay).convert("RGB")
    st.image(
        preview,
        caption="Area merah akan diblur/dihitamkan di Day 4.",
        use_container_width=True,
    )
else:
    st.warning(
        "⚠️ Tidak ada field dipilih — semua isi KTP akan terlihat di gambar akhir. "
        "Centang minimal NIK dan Nama untuk privasi."
    )

st.caption("Day 4: sensor aktual (blur/blackout) · Day 5: keterangan penggunaan · Day 6: unduh")

# ═══════════════════════════════════════════════════════════════
# DEBUG (opsional — hapus sebelum final)
# ═══════════════════════════════════════════════════════════════
with st.expander("🔧 Debug info"):
    st.write(f"Ukuran gambar: {W}×{H} px")
    st.write(f"Field dipilih: {selected_labels}")
    st.write(f"Total field KTP: {len(KTP_FIELDS)}")
    st.write(f"Field disarankan: {sorted(SUGGESTED_FIELDS)}")