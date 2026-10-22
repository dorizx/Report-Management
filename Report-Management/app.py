import os
import tempfile

import streamlit as st

from jmeter_report_generator import JMeterReportGenerator, ReportParameters

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PARAMS = os.path.join(BASE_DIR, "report_parameters.md")

st.set_page_config(page_title="JMeter Report Generator", page_icon="📊", layout="centered")

# --------------------------------------------------------------------------- #
# Tema Neo Brutalism (Didominasi Biru, Border Hitam, Hard Shadow, Space Grotesk)
# --------------------------------------------------------------------------- #
st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');

      /* Global Typography */
      html, body, [class*="css"], .stMarkdown {
          font-family: 'Space Grotesk', sans-serif !important;
          color: #000000;
      }

      /* Sembunyikan elemen bawaan Streamlit yang tidak perlu */
      #MainMenu, footer, .stAppDeployButton, [data-testid="stToolbar"] {display: none !important;}
      [data-testid="stHeader"] {background: transparent;}
      .block-container {padding-top: 3rem; padding-bottom: 4rem; max-width: 740px;}

      /* Header & Teks */
      .eyebrow {font-size: 1rem; font-weight: 700; letter-spacing: 0.15em; text-transform: uppercase; color: #0055FF; margin-bottom: 0px;}
      h1 {font-family: 'Space Grotesk', sans-serif !important; font-size: 2.8rem !important; font-weight: 800 !important; color: #000 !important; text-transform: uppercase; border-bottom: 5px solid #000; padding-bottom: 0.5rem; margin-bottom: 1.5rem; letter-spacing: -1px;}
      .lead {font-size: 1.05rem; font-weight: 600; background: #E0E7FF; padding: 1rem 1.2rem; border: 3px solid #000; box-shadow: 4px 4px 0px #000; border-radius: 6px; margin-bottom: 2rem;}
      
      /* Section Badge */
      .section {font-size: 0.9rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #FFF; background-color: #0055FF; display: inline-block; padding: 0.4rem 1rem; border: 3px solid #000; box-shadow: 3px 3px 0px #000; border-radius: 6px; margin: 2rem 0 1rem 0;}

      /* Input, Expander, File Uploader */
      [data-testid="stFileUploaderDropzone"],
      [data-testid="stExpander"],
      [data-baseweb="input"], [data-baseweb="select"] > div,
      [data-baseweb="number-input"] > div {
          border: 3px solid #000 !important;
          border-radius: 6px !important;
          box-shadow: 4px 4px 0px #000 !important;
          background-color: #FFFFFF !important;
          transition: all 0.2s ease;
      }
      [data-testid="stFileUploaderDropzone"] { border-style: dashed !important; background-color: #F0F4FF !important;}
      [data-testid="stExpander"] { background-color: #FAFAFA !important; }
      
      /* Reset hover state for inputs so shadow doesn't disappear weirdly */
      [data-baseweb="input"]:focus-within, [data-baseweb="select"] > div:focus-within { box-shadow: 4px 4px 0px #0055FF !important; }

      /* Buttons */
      [data-testid="stElementContainer"]:has([data-testid="stButton"]),
      [data-testid="stElementContainer"]:has([data-testid="stDownloadButton"]) {width: 100% !important;}
      [data-testid="stButton"], [data-testid="stDownloadButton"] {width: 100%;}
      [data-testid="stButton"] button, [data-testid="stDownloadButton"] button {
          width: 100%; 
          border: 3px solid #000 !important; 
          border-radius: 6px !important; 
          box-shadow: 5px 5px 0px #000 !important; 
          background-color: #0055FF !important; 
          color: #FFF !important; 
          font-family: 'Space Grotesk', sans-serif !important;
          font-weight: 700 !important; 
          font-size: 1.1rem;
          text-transform: uppercase;
          padding: 0.8rem 1rem;
          transition: all 0.1s ease-in-out !important;
      }
      [data-testid="stButton"] button:hover, [data-testid="stDownloadButton"] button:hover {
          transform: translate(3px, 3px) !important;
          box-shadow: 2px 2px 0px #000 !important;
          color: #FFF !important;
      }
      [data-testid="stButton"] button:disabled {
          background-color: #E5E7EB !important;
          color: #9CA3AF !important;
          box-shadow: none !important;
          transform: none !important;
          border-color: #9CA3AF !important;
      }

      /* Radio Buttons */
      [data-testid="stRadio"] {margin-bottom: -0.4rem; font-weight: 600;}

      /* Metrics */
      [data-testid="stMetric"] {
          background: #E0E7FF; 
          border: 3px solid #000; 
          border-radius: 6px; 
          box-shadow: 4px 4px 0px #000; 
          padding: 16px;
      }
      [data-testid="stMetricLabel"] p {font-size: 0.85rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #000;}
      [data-testid="stMetricValue"] {font-size: 1.8rem; font-weight: 800; color: #0055FF;}

      /* Pills & Rows */
      .pill { display: inline-block; padding: 0.4rem 1rem; border-radius: 4px; font-size: 0.85rem; font-weight: 700; text-transform: uppercase; border: 3px solid #000; box-shadow: 3px 3px 0px #000;}
      .pill.ok { background: #4ADE80; color: #000; }  
      .pill.bad { background: #FF4D4D; color: #000; }
      
      .row { display: flex; gap: 1rem; align-items: center; padding: 0.8rem; border: 3px solid #000; background: #FFF; box-shadow: 3px 3px 0px #000; margin-bottom: 0.75rem; border-radius: 6px; font-weight: 600; font-size: 0.95rem;}
      
      .sev { flex: 0 0 5rem; text-align: center; padding: 0.2rem 0; border: 2px solid #000; border-radius: 4px; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; box-shadow: 2px 2px 0px #000;}
      .sev.Critical { background: #FF4D4D; color: #000; } 
      .sev.High { background: #FFA500; color: #000; } 
      .sev.Medium { background: #FCD34D; color: #000; } 
      .sev.Low { background: #E2E8F0; color: #000; }
      
      .muted {color: #4B5563; font-size: 0.85rem; font-weight: 600;}
    </style>
    """,
    unsafe_allow_html=True,
)


def section(title: str) -> None:
    st.markdown(f'<div class="section">{title}</div>', unsafe_allow_html=True)


# --------------------------------------------------------------------------- #
# Header
# --------------------------------------------------------------------------- #
st.markdown('<div class="eyebrow">JMeter</div>', unsafe_allow_html=True)
st.title("Laporan Performa")
st.markdown('<div class="lead">Unggah hasil pengujian, dapatkan laporan Word lengkap dengan temuan dan rekomendasi tindakan.</div>',
            unsafe_allow_html=True)

# --------------------------------------------------------------------------- #
# Input
# --------------------------------------------------------------------------- #
section("Berkas pengujian")
uploaded_jtl = st.file_uploader("Hasil JMeter (.jtl atau .csv)", type=["jtl", "csv"], label_visibility="collapsed")

section("Detail laporan")
c1, c2, c3 = st.columns([1.4, 1.4, 1])
input_app_name = c1.text_input("Nama proyek", value="Sistem E-Commerce")
input_qa_name = c2.text_input("Disusun oleh", value="Aditya Daffa Syahputra")
input_max_p95 = c3.number_input("Target P95 (ms)", value=1000, step=100, min_value=1)

section("Rekomendasi")
mode = st.radio("Sumber rekomendasi", ["Groq", "Ollama", "Tanpa LLM"], horizontal=True, label_visibility="collapsed")
st.markdown(
    '<div class="muted" style="margin-bottom: 1rem;">'
    + {"Groq": "Dihasilkan model di Groq Cloud. Butuh GROQ_API_KEY di secrets atau environment.",
       "Ollama": "Dihasilkan model lokal. Butuh Ollama aktif di localhost.",
       "Tanpa LLM": "Memakai playbook dari file parameter. Cepat dan tanpa koneksi eksternal."}[mode]
    + "</div>",
    unsafe_allow_html=True,
)

with st.expander("Opsi lanjutan"):
    uploaded_md = st.file_uploader("File parameter (.md), opsional", type=["md"],
                                   help="Jika kosong, dipakai report_parameters.md bawaan.")
    output_filename = st.text_input("Nama file output", value="Laporan_Lengkap_JMeter_Performance.docx")

st.write("")
go = st.button("Buat laporan", type="primary", disabled=uploaded_jtl is None)


# --------------------------------------------------------------------------- #
# Proses
# --------------------------------------------------------------------------- #
def run_pipeline():
    result = {}
    with tempfile.TemporaryDirectory() as tmp:
        jtl_path = os.path.join(tmp, uploaded_jtl.name)
        with open(jtl_path, "wb") as f:
            f.write(uploaded_jtl.getbuffer())

        md_path = DEFAULT_PARAMS
        if uploaded_md:
            md_path = os.path.join(tmp, uploaded_md.name)
            with open(md_path, "wb") as f:
                f.write(uploaded_md.getbuffer())

        params = ReportParameters(md_path)
        if input_app_name:
            params.meta["project_name"] = input_app_name
        if input_qa_name:
            params.meta["prepared_by"] = input_qa_name
        if "SLA" not in params.sections:
            params.sections["SLA"] = {"kv": {}, "items": [], "text": ""}
        params.sections["SLA"]["kv"]["max_p95_ms"] = int(input_max_p95)

        provider = {"Groq": "groq", "Ollama": "ollama"}.get(mode)
        gen = JMeterReportGenerator(jtl_path, params, llm_override=provider is not None)

        with st.status("Memproses data", expanded=False) as status:
            status.update(label="Membaca dan menganalisis hasil pengujian")
            gen.load_data()
            gen.compute()
            gen.detect_findings()
            blocks = gen.playbook_blocks()

            llm_text, note = None, ("Rekomendasi dari playbook.", None)
            if provider:
                if not hasattr(gen, "llm_error"):
                    st.error("jmeter_report_generator.py yang terpasang masih versi lama. Ganti dengan versi terbaru lalu restart aplikasi.")
                    st.stop()
                status.update(label=f"Menyusun rekomendasi dengan {provider.capitalize()}")
                llm_text = gen.llm_recommendations(provider=provider)
                if llm_text and not str(llm_text).startswith("ERROR_"):
                    note = (f"Rekomendasi dihasilkan oleh {getattr(gen, 'llm_used', provider)}.", None)
                else:
                    reason = getattr(gen, "llm_error", None) or llm_text
                    llm_text = None
                    note = (None, f"{provider.capitalize()} gagal: {reason}. Laporan memakai playbook sebagai cadangan.")

            status.update(label="Membuat dokumen Word")
            charts = gen._charts(tmp)
            out_path = os.path.join(tmp, output_filename)
            gen._build_doc(out_path, charts, llm_text, blocks)

            with open(out_path, "rb") as f:
                result["docx"] = f.read()
            with open(charts["endpoint"], "rb") as f:
                result["chart"] = f.read()
            status.update(label="Selesai", state="complete")

        g, sla = gen.g, gen.sla
        result.update(
            name=output_filename, note=note, g=g, max_p95=int(input_max_p95),
            passed=(g["p95"] <= sla["max_p95_ms"] and g["error_rate"] <= sla["max_error_rate_pct"]
                    and g["tps"] >= sla["min_tps"]),
            findings=[(f["severity"], f["title"], f["evidence"]) for f in gen.findings[:5]],
        )
    return result


if go:
    try:
        st.session_state["result"] = run_pipeline()
    except Exception as exc:  # noqa: BLE001
        st.session_state.pop("result", None)
        st.error(f"Terjadi kesalahan saat memproses laporan: {exc}")

# --------------------------------------------------------------------------- #
# Hasil (disimpan di session_state agar tidak hilang saat tombol unduh ditekan)
# --------------------------------------------------------------------------- #
res = st.session_state.get("result")
if res:
    g = res["g"]
    st.divider()
    ok_note, warn_note = res["note"]
    if warn_note:
        st.warning(warn_note)

    pill = ('<span class="pill ok">Memenuhi SLA</span>' if res["passed"]
            else '<span class="pill bad">Melanggar SLA</span>')
    st.markdown(f"{pill}&nbsp;&nbsp;<span class='muted'>{ok_note or ''}</span>", unsafe_allow_html=True)
    st.write("")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Request", f"{g['total_req']:,}")
    m2.metric("P95", f"{g['p95']:.0f} ms", help=f"Target ≤ {res['max_p95']} ms")
    m3.metric("Error", f"{g['error_rate']:.2f}%")
    m4.metric("TPS aktif", f"{g['tps']:.2f}")

    if res["findings"]:
        section("Temuan utama")
        rows = "".join(
            f'<div class="row"><span class="sev {sev}">{sev}</span><span>{title}</span></div>'
            for sev, title, _ in res["findings"]
        )
        st.markdown(rows, unsafe_allow_html=True)

    with st.expander("Grafik per endpoint"):
        st.image(res["chart"])

    st.write("")
    st.download_button(
        "Unduh laporan (.docx)", data=res["docx"], file_name=res["name"],
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", type="primary",
    )