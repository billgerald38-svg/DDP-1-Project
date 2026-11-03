import streamlit as st

st.set_page_config(
    page_title="Penyensor KTP",
    page_icon="🪪",
    layout="centered",
)

st.title("🪪 Penyensor Kartu Identitas")
st.caption("Versi 0.0.1 — setup Hari 0")

st.info(
    "Aplikasi untuk memfoto KTP dengan panduan posisi, "
    "lalu menyensor field sensitif (NIK, Nama, Alamat, Foto, Tanda Tangan)."
)

if st.button("Cek environment"):
    import cv2
    import numpy as np
    import PIL
    import piexif

    st.success(f"Streamlit: {st.__version__}")
    st.success(f"OpenCV: {cv2.__version__}")
    st.success(f"NumPy: {np.__version__}")
    st.success(f"Pillow: {PIL.__version__}")
    st.success("piexif: ok")
