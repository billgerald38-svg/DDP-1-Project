import streamlit as st
from PIL import Image
import numpy as np

# ── Konfigurasi halaman ─────────────────────────────────────────
st.set_page_config(
    page_title="Penyensor KTP",
    page_icon="🪪",
    layout="centered"
)

# ── Header ──────────────────────────────────────────────────────
st.title("🪪 Penyensor Kartu Identitas")
st.caption("Versi 0.1.0 — Hari 1: capture + display")

st.info(
    "Posisikan KTP di dalam frame kamera. "
    "Pastikan seluruh KTP terlihat dan pencahayaan cukup."
)

# ── Inisialisasi session_state ──────────────────────────────────
if "captured_image" not in st.session_state:
    st.session_state.captured_image = None

if "camera_key" not in st.session_state:
    st.session_state.camera_key = 0

# ── Kamera ──────────────────────────────────────────────────────
camera_image = st.camera_input(
    "Ambil foto KTP",
    key=f"camera_{st.session_state.camera_key}",
)

# ── Simpan hasil capture ────────────────────────────────────────
if camera_image is not None:
    img_pil = Image.open(camera_image)
    img_np = np.array(img_pil)
    st.session_state.captured_image = img_np

# ── Tampilkan hasil ─────────────────────────────────────────────
if st.session_state.captured_image is not None:
    st.subheader("Hasil Capture")

    st.image(
        st.session_state.captured_image,
        caption="KTP yang tersimpan di session",
        use_container_width=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Lebar", f"{st.session_state.captured_image.shape[1]} px")
    with col2:
        st.metric("Tinggi", f"{st.session_state.captured_image.shape[0]} px")

    if st.button("🔄 Hapus & ambil ulang"):
        st.session_state.captured_image = None
        st.session_state.camera_key += 1
        st.rerun()
else:
    st.caption("Belum ada gambar. Klik tombol kamera di atas untuk mulai.")