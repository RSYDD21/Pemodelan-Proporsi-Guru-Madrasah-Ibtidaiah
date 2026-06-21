import streamlit as st
import pandas as pd
import numpy as np

import plotly.express as px
import plotly.graph_objects as go

# ==================================================
# KONFIGURASI HALAMAN
# ==================================================

st.set_page_config(
    page_title="Pemodelan Proporsi Guru MI",
    page_icon="📊",
    layout="wide"
)

# ==================================================
# CUSTOM CSS (tema netral/profesional)
# ==================================================

st.markdown("""
<style>

.main {
    background-color: #f8fafc;
}

[data-testid="stMetric"] {
    background-color: #ffffff;
    padding: 20px;
    border-radius: 15px;
    border-left: 6px solid #2563eb;
    box-shadow: 0px 2px 10px rgba(0,0,0,0.08);
}

section[data-testid="stSidebar"] {
    background-color: #0f172a;
}

section[data-testid="stSidebar"] * {
    color: white;
}

h1, h2, h3 {
    color: #1e293b;
}

</style>
""", unsafe_allow_html=True)

# ==================================================
# KOEFISIEN MODEL REGRESI
# (disimpan terpusat agar tidak diketik ulang
#  di beberapa menu yang berbeda)
# ==================================================

INTERCEPT = 175.3598
KOEF_SISWA = 0.0222
KOEF_SEKOLAH = 4.7393
RASIO_IDEAL = 15  # PP No. 74 Tahun 2008 -> rasio ideal 1:15


def hitung_prediksi_guru(jumlah_siswa, jumlah_sekolah):
    """Menghitung prediksi jumlah guru berdasarkan model regresi."""
    return (
        INTERCEPT
        + (KOEF_SISWA * jumlah_siswa)
        + (KOEF_SEKOLAH * jumlah_sekolah)
    )


def hitung_guru_ideal(jumlah_siswa):
    """Menghitung jumlah guru ideal berdasarkan rasio 1:15."""
    return jumlah_siswa / RASIO_IDEAL


def klasifikasi_prioritas(gap):
    """Klasifikasi prioritas distribusi berdasarkan besaran gap."""
    if gap >= 2000:
        return "Sangat Tinggi"
    elif gap >= 1000:
        return "Tinggi"
    elif gap >= 500:
        return "Sedang"
    elif gap > 0:
        return "Rendah"
    else:
        return "Tidak Prioritas"


# ==================================================
# LOAD DATA
# ==================================================

@st.cache_data
def load_data():
    df = pd.read_excel("Hasil_Analisis_Guru_MI.xlsx")
    return df


df = load_data()

# ==================================================
# SIDEBAR — MENU (6 menu hasil penggabungan)
# ==================================================

st.sidebar.title("📚 Menu Analisis")

menu = st.sidebar.radio(
    "Pilih Menu",
    [
        "Dashboard",
        "Pemodelan Regresi",
        "Simulasi Prediksi",
        "Analisis Gap & Klasifikasi",
        "Rekomendasi Distribusi",
        "Laporan"
    ]
)

# ==================================================
# FILTER GLOBAL
# ==================================================

st.sidebar.markdown("---")

tahun_list = sorted(df["Tahun"].unique())
kota_list = sorted(df["Kota"].unique())

tahun_filter = st.sidebar.selectbox(
    "📅 Filter Tahun",
    ["Semua"] + list(tahun_list)
)

kota_filter = st.sidebar.selectbox(
    "🏙️ Filter Kota",
    ["Semua"] + list(kota_list)
)

# ==================================================
# DATA FILTER
# ==================================================

df_filter = df.copy()

if tahun_filter != "Semua":
    df_filter = df_filter[df_filter["Tahun"] == tahun_filter]

if kota_filter != "Semua":
    df_filter = df_filter[df_filter["Kota"] == kota_filter]

# ==================================================
# INFORMASI SIDEBAR
# ==================================================

st.sidebar.markdown("---")

st.sidebar.info(
    """
Pemodelan Proporsi Guru Madrasah Ibtidaiyah
Menggunakan Regresi Linear Berganda
dan Analisis Gap
Provinsi Jawa Barat
    """
)

# ==================================================
# 1. DASHBOARD
# (gabungan: Dashboard lama + Visualisasi Data)
# ==================================================

if menu == "Dashboard":

    st.title("📊 Dashboard Pemodelan Proporsi Guru Madrasah Ibtidaiyah")

    st.markdown(
        "Ringkasan dan eksplorasi data guru, siswa, dan sekolah "
        "Madrasah Ibtidaiyah di Provinsi Jawa Barat."
    )

    # ----------------------------------------
    # KPI Ringkasan
    # ----------------------------------------

    total_guru = int(df_filter["Jumlah_Guru"].sum())
    total_siswa = int(df_filter["Jumlah_Siswa"].sum())
    total_sekolah = int(df_filter["Jumlah_Sekolah"].sum())
    rata_rasio = round(df_filter["Rasio_Siswa_Guru"].mean(), 2)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("👨‍🏫 Total Guru", f"{total_guru:,}")

    with col2:
        st.metric("🎓 Total Siswa", f"{total_siswa:,}")

    with col3:
        st.metric("🏫 Total Sekolah", f"{total_sekolah:,}")

    with col4:
        st.metric("📈 Rasio Siswa-Guru", rata_rasio)

    st.markdown("---")

    # ----------------------------------------
    # Tren umum
    # ----------------------------------------

    tab_ringkasan, tab_eksplorasi = st.tabs(
        ["Ringkasan Tren", "Eksplorasi Hubungan Variabel"]
    )

    with tab_ringkasan:

        col1, col2 = st.columns(2)

        with col1:
            kondisi = df_filter["Kondisi"].value_counts().reset_index()
            kondisi.columns = ["Kondisi", "Jumlah"]

            fig_kondisi = px.pie(
                kondisi,
                values="Jumlah",
                names="Kondisi",
                hole=0.45,
                title="Distribusi Kondisi Guru"
            )
            fig_kondisi.update_layout(template="plotly_white")
            st.plotly_chart(fig_kondisi, use_container_width=True, key="dash_pie_kondisi")

        with col2:
            guru_tahun = df.groupby("Tahun")["Jumlah_Guru"].sum().reset_index()

            fig_guru = px.line(
                guru_tahun,
                x="Tahun",
                y="Jumlah_Guru",
                markers=True,
                title="Perkembangan Jumlah Guru"
            )
            fig_guru.update_layout(template="plotly_white")
            st.plotly_chart(fig_guru, use_container_width=True, key="dash_line_guru")

        col1, col2 = st.columns(2)

        with col1:
            siswa_tahun = df.groupby("Tahun")["Jumlah_Siswa"].sum().reset_index()

            fig_siswa = px.bar(
                siswa_tahun,
                x="Tahun",
                y="Jumlah_Siswa",
                title="Jumlah Siswa per Tahun"
            )
            fig_siswa.update_layout(template="plotly_white")
            st.plotly_chart(fig_siswa, use_container_width=True, key="dash_bar_siswa_tahun")

        with col2:
            sekolah_tahun = df.groupby("Tahun")["Jumlah_Sekolah"].sum().reset_index()

            fig_sekolah = px.bar(
                sekolah_tahun,
                x="Tahun",
                y="Jumlah_Sekolah",
                title="Jumlah Sekolah per Tahun"
            )
            fig_sekolah.update_layout(template="plotly_white")
            st.plotly_chart(fig_sekolah, use_container_width=True, key="dash_bar_sekolah_tahun")

        st.markdown("---")

        # Top 10 kekurangan & kelebihan guru (tahun terakhir di data)
        tahun_terbaru = int(df["Tahun"].max())

        st.subheader(f"🔴 Top 10 Kekurangan Guru Tahun {tahun_terbaru}")

        data_terbaru = df[df["Tahun"] == tahun_terbaru]

        top_kurang = (
            data_terbaru[data_terbaru["Gap"] > 0]
            .sort_values(by="Gap", ascending=False)
            .head(10)
        )
        top_kurang["Gap_Label"] = top_kurang["Gap"].round(0).astype(int)

        fig_kurang = px.bar(
            top_kurang,
            x="Gap",
            y="Kota",
            orientation="h",
            color="Gap",
            text="Gap_Label",
            title=f"Top 10 Kekurangan Guru Tahun {tahun_terbaru}"
        )
        fig_kurang.update_layout(template="plotly_white", height=500)
        st.plotly_chart(fig_kurang, use_container_width=True, key="dash_bar_top_kurang")

        st.dataframe(
            top_kurang[["Tahun", "Kota", "Jumlah_Guru", "Guru_Ideal", "Gap"]],
            use_container_width=True
        )

        st.subheader(f"🟢 Top 10 Kelebihan Guru Tahun {tahun_terbaru}")

        top_lebih = (
            data_terbaru[data_terbaru["Gap"] < 0]
            .sort_values(by="Gap")
            .head(10)
        )
        top_lebih["Gap_Label"] = top_lebih["Gap"].round(0).astype(int)

        fig_lebih = px.bar(
            top_lebih,
            x="Gap",
            y="Kota",
            orientation="h",
            color="Gap",
            text="Gap_Label",
            title=f"Top 10 Kelebihan Guru Tahun {tahun_terbaru}"
        )
        fig_lebih.update_layout(template="plotly_white", height=500)
        st.plotly_chart(fig_lebih, use_container_width=True, key="dash_bar_top_lebih")

        st.dataframe(
            top_lebih[["Kota", "Jumlah_Guru", "Guru_Ideal", "Gap"]],
            use_container_width=True
        )

    with tab_eksplorasi:

        st.markdown(
            "Eksplorasi hubungan jumlah siswa, jumlah sekolah, jumlah guru, "
            "dan proporsi guru."
        )

        st.subheader("Hubungan Jumlah Siswa dan Jumlah Guru")
        fig = px.scatter(
            df, x="Jumlah_Siswa", y="Jumlah_Guru",
            color="Tahun", size="Jumlah_Sekolah", hover_name="Kota",
            title="Jumlah Siswa vs Jumlah Guru"
        )
        st.plotly_chart(fig, use_container_width=True, key="eksplor_scatter_siswa_guru")

        st.subheader("Hubungan Jumlah Sekolah dan Jumlah Guru")
        fig = px.scatter(
            df, x="Jumlah_Sekolah", y="Jumlah_Guru",
            color="Tahun", hover_name="Kota",
            title="Jumlah Sekolah vs Jumlah Guru"
        )
        st.plotly_chart(fig, use_container_width=True, key="eksplor_scatter_sekolah_guru")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader(f"Top 10 Kota — Guru Terbanyak ({tahun_terbaru})")
            top_guru = (
                df[df["Tahun"] == tahun_terbaru]
                .sort_values(by="Jumlah_Guru", ascending=False)
                .head(10)
            )
            fig = px.bar(
                top_guru, x="Jumlah_Guru", y="Kota", orientation="h",
                color="Jumlah_Guru", title=f"Top 10 Guru Terbanyak {tahun_terbaru}"
            )
            st.plotly_chart(fig, use_container_width=True, key="eksplor_bar_top_guru")

        with col2:
            st.subheader(f"Top 10 Kota — Siswa Terbanyak ({tahun_terbaru})")
            top_siswa = (
                df[df["Tahun"] == tahun_terbaru]
                .sort_values(by="Jumlah_Siswa", ascending=False)
                .head(10)
            )
            fig = px.bar(
                top_siswa, x="Jumlah_Siswa", y="Kota", orientation="h",
                color="Jumlah_Siswa", title=f"Top 10 Siswa Terbanyak {tahun_terbaru}"
            )
            st.plotly_chart(fig, use_container_width=True, key="eksplor_bar_top_siswa")

        st.subheader("Distribusi Rasio Siswa-Guru")
        fig = px.histogram(
            df, x="Rasio_Siswa_Guru", nbins=20,
            title="Distribusi Rasio Siswa-Guru"
        )
        st.plotly_chart(fig, use_container_width=True, key="eksplor_hist_rasio")

        st.subheader(f"Top 10 Rasio Siswa-Guru Tertinggi ({tahun_terbaru})")
        top_rasio = (
            df[df["Tahun"] == tahun_terbaru]
            .sort_values(by="Rasio_Siswa_Guru", ascending=False)
            .head(10)
        )
        st.dataframe(
            top_rasio[["Kota", "Jumlah_Siswa", "Jumlah_Guru", "Rasio_Siswa_Guru"]],
            use_container_width=True
        )

        st.markdown("---")

        st.success(f"""
        Insight Data Tahun {tahun_terbaru}:

        • Kota dengan jumlah guru terbanyak: {top_guru.iloc[0]['Kota']}

        • Kota dengan jumlah siswa terbanyak: {top_siswa.iloc[0]['Kota']}

        • Rasio siswa-guru tertinggi: {top_rasio.iloc[0]['Kota']}
          ({top_rasio.iloc[0]['Rasio_Siswa_Guru']:.2f})
        """)

    st.markdown("---")
    st.subheader("📋 Ringkasan Dataset (sesuai filter)")
    st.dataframe(df_filter, use_container_width=True)


# ==================================================
# 2. PEMODELAN REGRESI
# (gabungan: Pemodelan Regresi lama + Evaluasi Model)
# ==================================================

elif menu == "Pemodelan Regresi":

    st.title("🧮 Pemodelan Regresi Linear Berganda")

    st.markdown("""
    Model regresi digunakan untuk memodelkan hubungan
    antara jumlah siswa dan jumlah sekolah terhadap
    jumlah guru Madrasah Ibtidaiyah, sekaligus menampilkan
    hasil evaluasi kelayakan model tersebut.
    """)

    tab_model, tab_evaluasi = st.tabs(
        ["Hasil Model", "Evaluasi & Uji Asumsi Klasik"]
    )

    # ----------------------------------------
    # TAB 1: HASIL MODEL
    # ----------------------------------------
    with tab_model:

        st.subheader("Persamaan Regresi")

        st.latex(
            r'''
            Y =
            175.3598
            +
            0.0222X_1
            +
            4.7393X_2
            '''
        )

        st.markdown("---")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("R²", "0.929")

        with col2:
            st.metric("Adj R²", "0.927")

        with col3:
            st.metric("Variabel Signifikan", "2")

        with col4:
            st.metric("Observasi", "108")

        st.markdown("---")

        st.subheader("Interpretasi Koefisien")

        interpretasi = pd.DataFrame({
            "Variabel": ["Jumlah Siswa", "Jumlah Sekolah"],
            "Koefisien": [0.0222, 4.7393],
            "Interpretasi": [
                "Setiap kenaikan 1 siswa meningkatkan jumlah guru sebesar 0.0222",
                "Setiap kenaikan 1 sekolah meningkatkan jumlah guru sebesar 4.7393"
            ]
        })

        st.dataframe(interpretasi, use_container_width=True)

        st.markdown("---")

        st.subheader("Aktual vs Prediksi")

        fig = px.scatter(
            df, x="Jumlah_Guru", y="Guru_Prediksi",
            color="Tahun", hover_name="Kota",
            title="Perbandingan Guru Aktual dan Prediksi"
        )
        st.plotly_chart(fig, use_container_width=True, key="model_scatter_aktual_prediksi")

        st.subheader("Distribusi Error Prediksi")

        df_error = df.copy()
        df_error["Error"] = df_error["Jumlah_Guru"] - df_error["Guru_Prediksi"]

        fig = px.histogram(
            df_error, x="Error", nbins=20,
            title="Distribusi Error Prediksi"
        )
        st.plotly_chart(fig, use_container_width=True, key="model_hist_error")

        st.markdown("---")

        st.subheader("Korelasi Variabel")

        corr = df[["Jumlah_Siswa", "Jumlah_Sekolah", "Jumlah_Guru"]].corr()

        fig = px.imshow(
            corr, text_auto=True, aspect="auto",
            title="Matriks Korelasi"
        )
        st.plotly_chart(fig, use_container_width=True, key="model_imshow_korelasi")

        st.markdown("---")

        st.success("""
        Kesimpulan Model:

        • Model mampu menjelaskan 92,9% variasi jumlah guru.

        • Jumlah siswa berpengaruh positif terhadap jumlah guru.

        • Jumlah sekolah berpengaruh positif terhadap jumlah guru.

        • Model layak digunakan untuk analisis kebutuhan guru MI.
        """)

    # ----------------------------------------
    # TAB 2: EVALUASI MODEL
    # ----------------------------------------
    with tab_evaluasi:

        st.markdown("""
        Evaluasi dilakukan untuk menilai kualitas model
        regresi linear berganda yang digunakan dalam
        penelitian, mencakup metrik akurasi dan uji asumsi klasik.
        """)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("R²", "0.929")

        with col2:
            st.metric("Adj R²", "0.927")

        with col3:
            # TODO: ganti dengan nilai MAE aktual hasil perhitungan
            st.metric("MAE", "Isi Hasil")

        with col4:
            # TODO: ganti dengan nilai RMSE aktual hasil perhitungan
            st.metric("RMSE", "Isi Hasil")

        st.markdown("---")

        st.subheader("Distribusi Error")

        df_eval = df.copy()
        df_eval["Error"] = df_eval["Jumlah_Guru"] - df_eval["Guru_Prediksi"]

        fig = px.histogram(
            df_eval, x="Error", nbins=20,
            title="Distribusi Error Prediksi"
        )
        st.plotly_chart(fig, use_container_width=True, key="eval_hist_error")

        st.markdown("---")

        st.subheader("Uji Normalitas")

        # TODO: ganti baris berikut dengan hasil uji Shapiro-Wilk aktual
        normalitas = pd.DataFrame({
            "Metode": ["Shapiro-Wilk"],
            "Statistik": ["Isi Hasil"],
            "P-Value": ["Isi Hasil"],
            "Kesimpulan": ["Isi Hasil"]
        })
        st.dataframe(normalitas, use_container_width=True)

        st.subheader("Uji Multikolinearitas")

        # TODO: ganti baris berikut dengan nilai VIF aktual per variabel
        vif_df = pd.DataFrame({
            "Variabel": ["Jumlah_Siswa", "Jumlah_Sekolah"],
            "VIF": ["Isi Hasil", "Isi Hasil"]
        })
        st.dataframe(vif_df, use_container_width=True)

        st.subheader("Uji Heteroskedastisitas")

        # TODO: ganti baris berikut dengan hasil uji Breusch-Pagan aktual
        bp_df = pd.DataFrame({
            "Metode": ["Breusch-Pagan"],
            "P-Value": ["Isi Hasil"],
            "Kesimpulan": ["Isi Hasil"]
        })
        st.dataframe(bp_df, use_container_width=True)

        st.subheader("Uji Autokorelasi")

        # TODO: ganti baris berikut dengan nilai Durbin-Watson aktual
        dw_df = pd.DataFrame({
            "Metode": ["Durbin-Watson"],
            "Nilai": ["Isi Hasil"],
            "Kesimpulan": ["Isi Hasil"]
        })
        st.dataframe(dw_df, use_container_width=True)

        st.markdown("---")

        st.success("""
        Ringkasan Evaluasi Model

        • Model memiliki kemampuan prediksi yang baik.

        • Variabel jumlah siswa dan jumlah sekolah
          berpengaruh signifikan terhadap jumlah guru.

        • Model dapat digunakan untuk mendukung
          analisis kebutuhan guru MI.

        • Hasil evaluasi menunjukkan model layak
          digunakan pada penelitian ini.
        """)


# ==================================================
# 3. SIMULASI PREDIKSI
# (gabungan: Simulasi Prediksi lama + What-If Analysis)
# ==================================================

elif menu == "Simulasi Prediksi":

    st.title("🔮 Simulasi Prediksi Jumlah Guru")

    st.markdown("""
    Masukkan nilai jumlah siswa dan jumlah sekolah secara manual,
    atau gunakan slider untuk menjelajahi berbagai skenario (what-if)
    dan melihat dampaknya terhadap kebutuhan guru secara langsung.
    """)

    mode_input = st.radio(
        "Mode Input",
        ["Input Manual (nilai presisi)", "Slider (eksplorasi skenario)"],
        horizontal=True
    )

    st.markdown("---")

    if mode_input == "Input Manual (nilai presisi)":

        col1, col2 = st.columns(2)

        with col1:
            jumlah_siswa = st.number_input(
                "Jumlah Siswa", min_value=0, value=10000, step=100
            )

        with col2:
            jumlah_sekolah = st.number_input(
                "Jumlah Sekolah", min_value=0, value=100, step=1
            )

        hitung = st.button("Hitung Prediksi Guru")

    else:

        col1, col2 = st.columns(2)

        with col1:
            jumlah_siswa = st.slider(
                "Jumlah Siswa", min_value=100, max_value=300000,
                value=50000, step=100
            )

        with col2:
            jumlah_sekolah = st.slider(
                "Jumlah Sekolah", min_value=1, max_value=2000,
                value=300, step=1
            )

        hitung = True  # slider langsung menampilkan hasil tanpa tombol

    if hitung:

        prediksi = hitung_prediksi_guru(jumlah_siswa, jumlah_sekolah)
        guru_ideal = hitung_guru_ideal(jumlah_siswa)
        gap = guru_ideal - prediksi
        kondisi = "Kekurangan Guru" if gap > 0 else "Kelebihan Guru"

        st.success(f"Prediksi Jumlah Guru: {round(prediksi)} Guru")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Jumlah Siswa", f"{jumlah_siswa:,}")

        with col2:
            st.metric("Jumlah Sekolah", f"{jumlah_sekolah:,}")

        with col3:
            st.metric("Prediksi Guru", round(prediksi))

        with col4:
            st.metric("Guru Ideal (Rasio 1:15)", round(guru_ideal))

        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=prediksi,
                title={'text': "Prediksi Guru"},
                gauge={'axis': {'range': [0, prediksi * 1.5]}}
            )
        )
        st.plotly_chart(fig, use_container_width=True, key="sim_gauge_prediksi")

        chart_df = pd.DataFrame({
            "Kategori": ["Prediksi Guru", "Guru Ideal"],
            "Jumlah": [prediksi, guru_ideal]
        })

        fig = px.bar(
            chart_df, x="Kategori", y="Jumlah", color="Kategori",
            title="Perbandingan Guru Prediksi dan Guru Ideal"
        )
        st.plotly_chart(fig, use_container_width=True, key="sim_bar_perbandingan")

        st.markdown("---")

        if gap > 0:
            st.warning(
                f"Berdasarkan simulasi, dengan {jumlah_siswa:,} siswa dan "
                f"{jumlah_sekolah:,} sekolah, masih terdapat kekurangan "
                f"sekitar {round(gap)} guru."
            )
        else:
            st.success(
                f"Berdasarkan simulasi, dengan {jumlah_siswa:,} siswa dan "
                f"{jumlah_sekolah:,} sekolah, kebutuhan guru telah terpenuhi."
            )

        hasil = pd.DataFrame({
            "Jumlah_Siswa": [jumlah_siswa],
            "Jumlah_Sekolah": [jumlah_sekolah],
            "Prediksi_Guru": [round(prediksi)],
            "Guru_Ideal": [round(guru_ideal)],
            "Gap": [round(gap)],
            "Status": [kondisi]
        })

        st.dataframe(hasil, use_container_width=True)


# ==================================================
# 4. ANALISIS GAP & KLASIFIKASI
# (gabungan: Analisis Gap + Monitoring Distribusi + Klasifikasi)
# ==================================================

elif menu == "Analisis Gap & Klasifikasi":

    st.title("📉 Analisis Gap & Klasifikasi Distribusi Guru")

    st.markdown("""
    Halaman ini menggabungkan analisis kesenjangan (gap) antara guru
    aktual dan guru ideal, penelusuran kondisi per kota/tahun, serta
    klasifikasi wilayah berdasarkan kategori kekurangan/kelebihan guru.
    """)

    tab_gap, tab_monitor, tab_klasifikasi = st.tabs(
        ["Analisis Gap (Seluruh Wilayah)", "Telusur per Kota & Tahun", "Klasifikasi Kondisi"]
    )

    # ----------------------------------------
    # TAB 1: ANALISIS GAP
    # ----------------------------------------
    with tab_gap:

        st.subheader("Statistik Gap")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Gap Minimum", round(df["Gap"].min()))

        with col2:
            st.metric("Gap Maksimum", round(df["Gap"].max()))

        with col3:
            st.metric("Rata-rata Gap", round(df["Gap"].mean()))

        with col4:
            st.metric("Median Gap", round(df["Gap"].median()))

        st.markdown("---")

        st.subheader("Distribusi Nilai Gap")

        fig_gap = px.histogram(
            df, x="Gap", nbins=25,
            color_discrete_sequence=["#ef4444"]
        )
        fig_gap.update_layout(title="Distribusi Gap Guru")
        st.plotly_chart(fig_gap, use_container_width=True, key="gap_hist_distribusi")

        st.subheader("Sebaran Gap")

        fig_box = px.box(df, y="Gap", points="outliers")
        st.plotly_chart(fig_box, use_container_width=True, key="gap_box_sebaran")

        st.markdown("---")

        tahun_terbaru = int(df["Tahun"].max())
        data_terbaru = df[df["Tahun"] == tahun_terbaru]

        st.subheader(f"🔴 Top 10 Kekurangan Guru Tahun {tahun_terbaru}")

        top_kurang = (
            data_terbaru[data_terbaru["Gap"] > 0]
            .sort_values(by="Gap", ascending=False)
            .head(10)
        )

        fig_kurang = px.bar(
            top_kurang, x="Gap", y="Kota", orientation="h",
            color="Gap", text="Gap", title="Top 10 Kekurangan Guru"
        )
        st.plotly_chart(fig_kurang, use_container_width=True, key="gap_bar_top_kurang")

        st.subheader(f"🟢 Top 10 Kelebihan Guru Tahun {tahun_terbaru}")

        top_lebih = (
            data_terbaru[data_terbaru["Gap"] < 0]
            .sort_values(by="Gap")
            .head(10)
        )

        fig_lebih = px.bar(
            top_lebih, x="Gap", y="Kota", orientation="h",
            color="Gap", text="Gap", title="Top 10 Kelebihan Guru"
        )
        st.plotly_chart(fig_lebih, use_container_width=True, key="gap_bar_top_lebih")

        st.markdown("---")

        st.subheader(f"Ranking Gap Seluruh Kota Tahun {tahun_terbaru}")

        ranking_gap = data_terbaru.sort_values(by="Gap", ascending=False)

        st.dataframe(
            ranking_gap[["Kota", "Jumlah_Guru", "Guru_Ideal", "Gap", "Kondisi"]],
            use_container_width=True
        )

        st.markdown("---")

        if len(top_kurang) > 0:
            kota_terburuk = top_kurang.iloc[0]["Kota"]
            gap_terbesar = round(top_kurang.iloc[0]["Gap"])

            st.warning(
                f"Kota dengan kekurangan guru terbesar pada tahun "
                f"{tahun_terbaru} adalah {kota_terburuk} dengan kekurangan "
                f"sekitar {gap_terbesar} guru."
            )

    # ----------------------------------------
    # TAB 2: TELUSUR PER KOTA & TAHUN (Monitoring)
    # ----------------------------------------
    with tab_monitor:

        st.markdown(
            "Pilih kota dan tahun tertentu untuk melihat kondisi "
            "distribusi guru secara spesifik."
        )

        col1, col2 = st.columns(2)

        with col1:
            kota_pilih = st.selectbox(
                "Pilih Kota", sorted(df["Kota"].unique()), key="kota_monitor"
            )

        with col2:
            tahun_pilih = st.selectbox(
                "Pilih Tahun", sorted(df["Tahun"].unique()), key="tahun_monitor"
            )

        data_monitor = df[
            (df["Kota"] == kota_pilih) & (df["Tahun"] == tahun_pilih)
        ]

        if len(data_monitor) > 0:

            data = data_monitor.iloc[0]

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("👨‍🏫 Guru Aktual", int(data["Jumlah_Guru"]))

            with col2:
                st.metric("🎯 Guru Ideal", round(data["Guru_Ideal"]))

            with col3:
                st.metric("⚖️ Gap", round(data["Gap"]))

            with col4:
                st.metric("📈 Rasio", round(data["Rasio_Siswa_Guru"], 2))

            st.markdown("---")

            kondisi = data["Kondisi"]

            if kondisi == "Kekurangan Guru":
                st.error(f"Status: {kondisi}")
            else:
                st.success(f"Status: {kondisi}")

            st.subheader("Perbandingan Guru Aktual dan Ideal")

            chart_df = pd.DataFrame({
                "Kategori": ["Guru Aktual", "Guru Ideal"],
                "Jumlah": [data["Jumlah_Guru"], data["Guru_Ideal"]]
            })

            fig = px.bar(
                chart_df, x="Kategori", y="Jumlah", color="Kategori",
                title="Perbandingan Guru Aktual dan Guru Ideal"
            )
            st.plotly_chart(fig, use_container_width=True, key="monitor_bar_perbandingan")

            st.subheader("Detail Data")
            st.dataframe(data_monitor, use_container_width=True)

            st.markdown("---")

            if data["Gap"] > 0:
                st.warning(
                    f"Kota {kota_pilih} masih mengalami kekurangan sekitar "
                    f"{round(data['Gap'])} guru."
                )
            else:
                st.success(
                    f"Kota {kota_pilih} telah memenuhi kebutuhan guru "
                    f"berdasarkan hasil analisis."
                )

        else:
            st.error("Data tidak ditemukan.")

    # ----------------------------------------
    # TAB 3: KLASIFIKASI KONDISI
    # ----------------------------------------
    with tab_klasifikasi:

        st.markdown("""
        Klasifikasi dilakukan berdasarkan hasil analisis gap
        untuk mengidentifikasi wilayah yang mengalami
        kekurangan atau kelebihan guru.
        """)

        kondisi_count = df["Kondisi"].value_counts().reset_index()
        kondisi_count.columns = ["Kondisi", "Jumlah"]

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Kekurangan Guru",
                int((df["Kondisi"] == "Kekurangan Guru").sum())
            )

        with col2:
            st.metric(
                "Kelebihan Guru",
                int((df["Kondisi"] == "Kelebihan Guru").sum())
            )

        st.markdown("---")

        fig = px.pie(
            kondisi_count, values="Jumlah", names="Kondisi",
            hole=0.4, title="Distribusi Kondisi Guru"
        )
        st.plotly_chart(fig, use_container_width=True, key="klasifikasi_pie_kondisi")

        fig_bar = px.bar(
            kondisi_count, x="Kondisi", y="Jumlah", color="Kondisi",
            title="Jumlah Data pada Setiap Kondisi"
        )
        st.plotly_chart(fig_bar, use_container_width=True, key="klasifikasi_bar_jumlah")

        st.subheader("Detail Klasifikasi")

        st.dataframe(
            df[["Tahun", "Kota", "Jumlah_Guru", "Guru_Ideal", "Gap", "Kondisi"]],
            use_container_width=True
        )

        st.markdown("---")

        gap_max = df.sort_values(by="Gap", ascending=False).iloc[0]

        st.warning(
            f"Wilayah dengan kekurangan guru terbesar adalah "
            f"{gap_max['Kota']} dengan gap sebesar "
            f"{round(gap_max['Gap'])} guru."
        )


# ==================================================
# 5. REKOMENDASI DISTRIBUSI
# ==================================================

elif menu == "Rekomendasi Distribusi":

    st.title("🎯 Rekomendasi Prioritas Distribusi Guru")

    st.markdown("""
    Rekomendasi disusun berdasarkan hasil analisis gap pada menu
    sebelumnya untuk menentukan wilayah yang perlu diprioritaskan
    dalam pemerataan guru.
    """)

    tahun_terbaru = int(df["Tahun"].max())
    data_terbaru = df[df["Tahun"] == tahun_terbaru].copy()

    data_terbaru["Prioritas"] = data_terbaru["Gap"].apply(klasifikasi_prioritas)

    ranking = data_terbaru.sort_values(by="Gap", ascending=False)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Prioritas Sangat Tinggi",
            len(ranking[ranking["Prioritas"] == "Sangat Tinggi"])
        )

    with col2:
        st.metric(
            "Prioritas Tinggi",
            len(ranking[ranking["Prioritas"] == "Tinggi"])
        )

    with col3:
        st.metric(
            "Prioritas Sedang",
            len(ranking[ranking["Prioritas"] == "Sedang"])
        )

    with col4:
        st.metric(
            "Tidak Prioritas",
            len(ranking[ranking["Prioritas"] == "Tidak Prioritas"])
        )

    st.markdown("---")

    prioritas_count = ranking["Prioritas"].value_counts().reset_index()
    prioritas_count.columns = ["Prioritas", "Jumlah"]

    fig = px.bar(
        prioritas_count, x="Prioritas", y="Jumlah", color="Prioritas",
        title="Distribusi Prioritas Distribusi Guru"
    )
    st.plotly_chart(fig, use_container_width=True, key="rekom_bar_distribusi_prioritas")

    st.subheader("Top 10 Prioritas Distribusi Guru")

    top10 = ranking[ranking["Gap"] > 0].head(10)

    fig = px.bar(
        top10, x="Gap", y="Kota", orientation="h",
        color="Prioritas", text="Gap",
        title="Top 10 Prioritas Distribusi Guru"
    )
    st.plotly_chart(fig, use_container_width=True, key="rekom_bar_top10")

    st.dataframe(
        top10[["Kota", "Jumlah_Guru", "Guru_Ideal", "Gap", "Prioritas"]],
        use_container_width=True
    )

    st.markdown("---")

    if len(top10) > 0:
        kota_prioritas = top10.iloc[0]["Kota"]
        gap_prioritas = round(top10.iloc[0]["Gap"])

        st.warning(
            f"Berdasarkan hasil analisis gap, wilayah yang menjadi "
            f"prioritas utama distribusi guru adalah {kota_prioritas} "
            f"dengan kekurangan sekitar {gap_prioritas} guru."
        )


# ==================================================
# 6. LAPORAN
# ==================================================

elif menu == "Laporan":

    st.title("📄 Laporan Hasil Analisis")

    st.markdown("""
    Halaman ini digunakan untuk melihat ringkasan hasil penelitian
    dan mengunduh dataset hasil analisis.
    """)

    st.subheader("Ringkasan Penelitian")

    st.success("""
    Judul:

    Pemodelan Proporsi Guru Madrasah Ibtidaiyah
    Menggunakan Regresi Linear Berganda
    dan Analisis Gap di Provinsi Jawa Barat

    Metode:
    - Regresi Linear Berganda
    - Analisis Gap

    Data:
    - 108 observasi
    - Periode 2022–2025

    Variabel:
    - Jumlah Siswa
    - Jumlah Sekolah
    - Jumlah Guru
    """)

    st.subheader("Ringkasan Model")

    model_df = pd.DataFrame({
        "Metrik": ["R²", "Adjusted R²"],
        "Nilai": [0.929, 0.927]
    })

    st.dataframe(model_df, use_container_width=True)

    st.subheader("Preview Dataset")
    st.dataframe(df.head(20), use_container_width=True)

    st.subheader("Download Dataset")

    with open("Hasil_Analisis_Guru_MI.xlsx", "rb") as file:
        st.download_button(
            label="📥 Download Hasil Analisis",
            data=file,
            file_name="Hasil_Analisis_Guru_MI.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
