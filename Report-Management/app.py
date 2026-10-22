import os
import tempfile
import streamlit as st
import pandas as pd

# Import class dan parser dari skrip utama milikmu
# Pastikan nama file skrip utama kamu misal: jmeter_report_generator.py
from jmeter_report_generator import ReportParameters, JMeterReportGenerator

st.set_page_config(
    page_title="JMeter Report Generator",
    page_icon="📊",
    layout="wide"
)

st.title("📊 JMeter Performance Report Generator")
st.write("Unggah file hasil pengujian JMeter (`.jtl`/`.csv`) dan konfigurasi (`.md`) untuk menghasilkan laporan Word otomatis.")

# --------------------------------------------------------------------------- #
# Sidebar: Konfigurasi Parameter & LLM
# --------------------------------------------------------------------------- #
st.sidebar.header("⚙️ Konfigurasi Parameter & Metadata")

st.sidebar.subheader("📌 Metadata & Target SLA")
input_app_name = st.sidebar.text_input("Nama Aplikasi / Proyek", value="Sistem E-Commerce")
input_qa_name = st.sidebar.text_input("Nama QA / Disusun Oleh", value="Aditya Daffa Syahputra")
input_max_p95 = st.sidebar.number_input("Max Response Time P95 (ms)", value=1000, step=100)

st.sidebar.subheader("🤖 Mode AI / Rekomendasi")

llm_option = st.sidebar.radio(
    "2. Mode Generasi Rekomendasi",
    options=[
        "Groq API (Llama Cloud - Fast & Online)", 
        "Ollama (Llama Lokal - Req: Localhost)", 
        "Tanpa LLM (Gunakan Playbook Static)"
    ],
    index=0
)

output_filename = st.sidebar.text_input(
    "3. Nama File Output",
    value="Laporan_Lengkap_JMeter_Performance.docx"
)

# --------------------------------------------------------------------------- #
# Main Area: Upload File Result & Eksekusi
# --------------------------------------------------------------------------- #
st.subheader("📁 Unggah Berkas Pengujian")

col1, col2 = st.columns(2)

with col1:
    uploaded_md = st.file_uploader(
        "1. Upload File Parameter (.md) - Opsional", 
        type=["md"],
        help="Jika tidak diunggah, sistem akan menggunakan 'report_parameters.md' bawaan."
    )

with col2:
    uploaded_jtl = st.file_uploader(
        "2. Upload Hasil JMeter (.jtl / .csv) - Wajib", 
        type=["jtl", "csv"],
        help="File log mentah hasil pengujian dari JMeter."
    )

# --------------------------------------------------------------------------- #
# Eksekusi Pembuatan Laporan
# --------------------------------------------------------------------------- #

if uploaded_jtl and st.button("🚀 Proses & Buat Laporan", type="primary"):
    with st.spinner("Menganalisis data dan menghasilkan laporan Word..."):
        try:
            with tempfile.TemporaryDirectory() as tmpdirname:
                # 1. Simpan JTL & MD sementara
                jtl_path = os.path.join(tmpdirname, uploaded_jtl.name)
                with open(jtl_path, "wb") as f:
                    f.write(uploaded_jtl.getbuffer())

                if uploaded_md:
                    md_path = os.path.join(tmpdirname, uploaded_md.name)
                    with open(md_path, "wb") as f:
                        f.write(uploaded_md.getbuffer())
                else:
                    md_path = "report_parameters.md"

                # 2. Inisialisasi Params
                params = ReportParameters(md_path)
                
                # 3. OVERRIDE PARAMETER DARI INPUT STREAMLIT (Membuat Nilai Dinamis)
                if input_app_name:
                    params.meta["project_name"] = input_app_name
                if input_qa_name:
                    params.meta["prepared_by"] = input_qa_name
                if input_max_p95:
                    params.sla["max_p95_ms"] = int(input_max_p95)

                # 4. Inisialisasi Generator
                use_llm = True if "Playbook" not in llm_option else False
                generator = JMeterReportGenerator(jtl_path, params, llm_override=use_llm)
                
                generator.load_data()
                generator.compute()
                generator.detect_findings()

                docx_out_path = os.path.join(tmpdirname, output_filename)

                # 5. Logika Pemanggilan LLM vs Playbook
                if "Groq" in llm_option:
                    llm_text = generator.llm_recommendations(provider="groq")
                    if not llm_text:
                        st.warning("⚠️ Groq API tidak merespons. Menggunakan Playbook sebagai cadangan.")
                        blocks = generator.playbook_blocks()
                    else:
                        blocks = None
                elif "Ollama" in llm_option:
                    llm_text = generator.llm_recommendations(provider="ollama")
                    if not llm_text:
                        st.warning("⚠️ Ollama lokal tidak terhubung. Menggunakan Playbook sebagai cadangan.")
                        blocks = generator.playbook_blocks()
                    else:
                        blocks = None
                else:
                    llm_text = None
                    blocks = generator.playbook_blocks()

                # 6. Ekspor Laporan Word
                charts = generator._charts(tmpdirname)
                generator._build_doc(docx_out_path, charts, llm_text, blocks)

                # 7. Preview & Download Button
                st.divider()
                st.subheader("📈 Preview Metrik Utama")
                g = generator.g
                
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Total Requests", f"{g['total_req']:,}")
                c2.metric("P95 Latency", f"{g['p95']:.0f} ms", delta=f"Target: ≤{input_max_p95} ms", delta_color="inverse")
                c3.metric("Error Rate", f"{g['error_rate']:.2f}%")
                c4.metric("Active TPS", f"{g['tps']:.2f} req/s")

                if "endpoint" in charts:
                    st.image(charts["endpoint"], caption="P95 Response Time & Error Rate per Endpoint", use_container_width=True)

                with open(docx_out_path, "rb") as f:
                    file_data = f.read()

                st.divider()
                st.download_button(
                    label="📥 Download Laporan Word (.docx)",
                    data=file_data,
                    file_name=output_filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    type="primary"
                )
                st.balloons()

        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses laporan: {e}")