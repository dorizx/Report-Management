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
st.sidebar.header("⚙️ Konfigurasi Pengujian")

uploaded_md = st.sidebar.file_uploader(
    "1. Upload Parameters (.md)", 
    type=["md"],
    help="Jika tidak diunggah, aplikasi akan mencari file 'report_parameters.md' bawaan."
)

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
uploaded_jtl = st.file_uploader(
    "Upload Hasil JMeter (.jtl / .csv)", 
    type=["jtl", "csv"],
    help="File log mentah hasil pengujian dari JMeter CLI/Non-GUI mode."
)

if uploaded_jtl and st.button("🚀 Proses & Buat Laporan", type="primary"):
        with st.spinner("Menganalisis data, membuat grafik, dan menghasilkan laporan Word..."):
            try:
                with tempfile.TemporaryDirectory() as tmpdirname:
                    # Simpan JTL & MD
                    jtl_path = os.path.join(tmpdirname, uploaded_jtl.name)
                    with open(jtl_path, "wb") as f:
                        f.write(uploaded_jtl.getbuffer())

                    if uploaded_md:
                        md_path = os.path.join(tmpdirname, uploaded_md.name)
                        with open(md_path, "wb") as f:
                            f.write(uploaded_md.getbuffer())
                    else:
                        md_path = "report_parameters.md"

                    params = ReportParameters(md_path)
                    
                    # Cek mode yang dipilih pengguna
                    use_llm = True if "Playbook" not in llm_option else False
                    generator = JMeterReportGenerator(jtl_path, params, llm_override=use_llm)
                    
                    generator.load_data()
                    generator.compute()
                    generator.detect_findings()

                    docx_out_path = os.path.join(tmpdirname, output_filename)

                    # Logika Pemanggilan berdasarkan Opsi Sidebar
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

                    # Ekspor Laporan
                    charts = generator._charts(tmpdirname)
                    generator._build_doc(docx_out_path, charts, llm_text, blocks)
                    
                    # 4. Tampilkan Preview di Web
                    st.divider()
                    st.subheader("📈 Preview Metrik Utama")
                    
                    g = generator.g
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Total Requests", f"{g['total_req']:,}")
                    c2.metric("P95 Latency", f"{g['p95']:.0f} ms")
                    c3.metric("Error Rate", f"{g['error_rate']:.2f}%")
                    c4.metric("Active TPS", f"{g['tps']:.2f} req/s")
                    
                    # Preview Grafik
                    if "endpoint" in charts:
                        st.image(charts["endpoint"], caption="P95 Response Time & Error Rate per Endpoint", use_container_width=True)
                    if "concurrency" in charts:
                        st.image(charts["concurrency"], caption="Response Time vs Virtual Users", use_container_width=True)

                    # 5. Siapkan Tombol Download File Word
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