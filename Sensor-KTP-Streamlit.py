"""
Penyensor KTP — versi live capture (camera_input_live + overlay eksperimental)
Satu file, siap dijalankan: streamlit run app.py
Dependensi: streamlit, streamlit-camera-input-live, pillow
"""

from io import BytesIO

import streamlit as st
import streamlit.components.v1 as components
from camera_input_live import camera_input_live
from PIL import Image

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
# Dipakai bersama oleh: overlay JS (live) dan overlay Python (verifikasi)
# ═══════════════════════════════════════════════════════════════
KTP_FIELDS = [
    # (x1, y1, x2, y2, label) — sesuaikan angka ini setelah tes dengan KTP asli
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
    "captured_image": None,     # PIL.Image hasil capture
    "overlay_enabled": True,    # toggle overlay live (untuk debugging)
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ═══════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════
st.title("🪪 Penyensor Kartu Identitas")
st.caption("Versi live — preview kamera di dalam aplikasi + panduan posisi")

st.info(
    "Posisikan KTP di dalam frame kamera. "
    "Garis hijau = tepi KTP, box merah = field yang akan disensor. "
    "Tekan **Ambil Gambar** saat posisi sudah pas."
)

# ═══════════════════════════════════════════════════════════════
# OVERLAY LIVE (Day 2) — suntikkan SVG ke iframe camera_input_live
# ═══════════════════════════════════════════════════════════════
if st.session_state.overlay_enabled:
    # Serialisasi KTP_FIELDS ke JS array literal
    fields_js = ",\n".join(
        f"[{x1}, {y1}, {x2}, {y2}, {label!r}]"
        for x1, y1, x2, y2, label in KTP_FIELDS
    )

    OVERLAY_HTML = f"""
<script>
(function() {{
    const FIELDS = [
        {fields_js}
    ];
    const INSTALL_FLAG = '__ktpOverlayInstalled_v2';
    if (window.parent[INSTALL_FLAG]) return;
    window.parent[INSTALL_FLAG] = true;

    const NS = "http://www.w3.org/2000/svg";

    function findIframe() {{
        const iframes = window.parent.document.querySelectorAll('iframe');
        for (const f of iframes) {{
            const t = (f.title || '').toLowerCase();
            if (t.includes('camera_input_live') || t.includes('camera-input-live')) return f;
        }}
        return null;
    }}

    function drawOverlay(doc, video) {{
        const rect = video.getBoundingClientRect();
        if (rect.width < 40 || rect.height < 40) return;

        let svg = doc.getElementById('ktp-overlay-svg');
        if (svg) svg.remove();

        svg = doc.createElementNS(NS, 'svg');
        svg.id = 'ktp-overlay-svg';
        svg.setAttribute('width', rect.width);
        svg.setAttribute('height', rect.height);
        svg.setAttribute('viewBox', `0 0 ${{rect.width}} ${{rect.height}}`);
        svg.style.cssText = 'position:absolute;top:0;left:0;' +
            'pointer-events:none;z-index:9999;';

        // Frame luar KTP (hijau, putus-putus)
        const outer = doc.createElementNS(NS, 'rect');
        outer.setAttribute('x', 2);
        outer.setAttribute('y', 2);
        outer.setAttribute('width', rect.width - 4);
        outer.setAttribute('height', rect.height - 4);
        outer.setAttribute('fill', 'none');
        outer.setAttribute('stroke', '#00e676');
        outer.setAttribute('stroke-width', 3);
        outer.setAttribute('stroke-dasharray', '12,8');
        outer.setAttribute('rx', 10);
        svg.appendChild(outer);

        // Box per field (merah)
        FIELDS.forEach(function(f) {{
            const x1 = f[0]*rect.width,  y1 = f[1]*rect.height;
            const x2 = f[2]*rect.width,  y2 = f[3]*rect.height;

            const r = doc.createElementNS(NS, 'rect');
            r.setAttribute('x', x1);
            r.setAttribute('y', y1);
            r.setAttribute('width', x2 - x1);
            r.setAttribute('height', y2 - y1);
            r.setAttribute('fill', 'rgba(255,60,60,0.06)');
            r.setAttribute('stroke', '#ff3c3c');
            r.setAttribute('stroke-width', 1.5);
            svg.appendChild(r);

            const t = doc.createElementNS(NS, 'text');
            t.setAttribute('x', x1 + 3);
            t.setAttribute('y', y1 + 12);
            t.setAttribute('fill', '#ff3c3c');
            t.setAttribute('font-size', '11');
            t.setAttribute('font-weight', '700');
            t.setAttribute('paint-order', 'stroke');
            t.setAttribute('stroke', 'white');
            t.setAttribute('stroke-width', '3');
            t.textContent = f[4];
            svg.appendChild(t);
        }});

        if (video.parentElement) {{
            video.parentElement.style.position = 'relative';
            video.parentElement.appendChild(svg);
        }}
    }}

    function tick() {{
        const iframe = findIframe();
        if (!iframe) return;
        let doc;
        try {{ doc = iframe.contentDocument; }} catch (e) {{ return; }}
        if (!doc) return;
        const video = doc.querySelector('video');
        if (!video || video.readyState < 1 || !video.videoWidth) return;
        drawOverlay(doc, video);
    }}

    setInterval(tick, 400);
    window.parent.addEventListener('resize', tick);
    tick();
}})();
</script>
"""
    components.html(OVERLAY_HTML, height=0)

# ═══════════════════════════════════════════════════════════════
# LIVE CAMERA
# ═══════════════════════════════════════════════════════════════
st.subheader("📹 Preview Kamera")

live_frame = camera_input_live(debounce=200)

if live_frame is not None:
    current_img = Image.open(live_frame).convert("RGB")

    col_cap, col_toggle = st.columns([2, 1])
    with col_cap:
        if st.button("📸 Ambil Gambar", type="primary", use_container_width=True):
            st.session_state.captured_image = current_img.copy()
            st.success("Gambar tersimpan.")
    with col_toggle:
        st.checkbox(
            "Overlay live",
            value=st.session_state.overlay_enabled,
            key="overlay_toggle",
            help="Matikan jika overlay tidak muncul atau mengganggu.",
            on_change=lambda: st.session_state.update(
                overlay_enabled=st.session_state.overlay_toggle
            ),
        )
else:
    st.info(
        "Menunggu akses kamera. Izinkan browser untuk mengakses webcam. "
        "Jika tidak muncul, pastikan aplikasi berjalan di `localhost` atau HTTPS."
    )

# ═══════════════════════════════════════════════════════════════
# HASIL CAPTURE + OVERLAY VERIFIKASI (Day 2 fallback)
# ═══════════════════════════════════════════════════════════════
if st.session_state.captured_image is not None:
    st.subheader("🔍 Verifikasi Hasil")

    # Overlay Python di atas foto yang sudah di-capture
    from PIL import ImageDraw, ImageFont

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

    # Frame luar
    draw.rectangle([2, 2, W - 3, H - 3], outline=(0, 230, 118), width=3)

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
    st.caption("Belum ada gambar. Arahkan KTP ke kamera lalu tekan **Ambil Gambar**.")