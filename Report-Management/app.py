import os
import tempfile

import streamlit as st

from jmeter_report_generator import JMeterReportGenerator, ReportParameters

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PARAMS = os.path.join(BASE_DIR, "report_parameters.md")

st.set_page_config(page_title="JMeter Report Generator", page_icon="📊", layout="centered")

# --------------------------------------------------------------------------- #
# Tema minimalis (CSS ringan di atas theme pada .streamlit/config.toml)
# --------------------------------------------------------------------------- #
st.markdown(
    """
    <style>
      #MainMenu, footer, .stAppDeployButton, [data-testid="stToolbar"] {display: none !important;}
      [data-testid="stHeader"] {background: transparent;}
      .block-container {padding-top: 3rem; padding-bottom: 4rem; max-width: 720px;}

      .eyebrow {font-size: .75rem; letter-spacing: .12em; text-transform: uppercase; color: #6B7280; margin-bottom: .25rem;}
      h1 {font-size: 1.9rem !important; font-weight: 650 !important; letter-spacing: -.02em; padding: 0 0 .25rem 0 !important;}
      .lead {color: #6B7280; font-size: .98rem; margin-bottom: 2rem;}
      .section {font-size: .72rem; font-weight: 600; letter-spacing: .1em; text-transform: uppercase;
                color: #6B7280; margin: 1.8rem 0 .5rem 0;}

      [data-testid="stFileUploaderDropzone"] {border: 1px dashed #CBD2D9; border-radius: 12px; background: #FAFBFC;}
      [data-testid="stExpander"] {border: 1px solid #E5E7EB; border-radius: 12px; box-shadow: none;}
      [data-baseweb="input"], [data-baseweb="select"] > div {border-radius: 10px;}

      [data-testid="stElementContainer"]:has([data-testid="stButton"]),
      [data-testid="stElementContainer"]:has([data-testid="stDownloadButton"]) {width: 100% !important;}
      [data-testid="stButton"], [data-testid="stDownloadButton"] {width: 100%;}
      [data-testid="stButton"] button, [data-testid="stDownloadButton"] button {width: 100%; border-radius: 10px; padding: .6rem 1rem; font-weight: 600;}
      [data-testid="stRadio"] {margin-bottom: -.4rem;}
      .muted {margin-bottom: .9rem;}

      [data-testid="stMetric"] {background: #F6F7F9; border: 1px solid #E5E7EB; border-radius: 12px; padding: 14px 16px;}
      [data-testid="stMetricLabel"] p {font-size: .7rem; letter-spacing: .08em; text-transform: uppercase; color: #6B7280;}
      [data-testid="stMetricValue"] {font-size: 1.45rem; font-weight: 650;}

      .pill {display: inline-block; padding: .2rem .7rem; border-radius: 999px; font-size: .78rem; font-weight: 600;}
      .pill.ok {background: #E6F4EA; color: #1E6B3A;}  .pill.bad {background: #FDECEA; color: #B42318;}
      .row {display: flex; gap: .75rem; align-items: baseline; padding: .55rem 0; border-bottom: 1px solid #EEF0F3; font-size: .92rem;}
      .row:last-child {border-bottom: none; margin-bottom: .8rem;}
      .sev {flex: 0 0 4.6rem; font-size: .7rem; font-weight: 700; letter-spacing: .06em; text-transform: uppercase;}
      .sev.Critical {color: #B42318;} .sev.High {color: #C2410C;} .sev.Medium {color: #A16207;} .sev.Low {color: #6B7280;}
      .muted {color: #6B7280; font-size: .82rem;}
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
    '<div class="muted">'
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