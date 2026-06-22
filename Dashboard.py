st.markdown("""
<style>

/* พื้นหลังหลัก */
.stApp{
    background:#030712;
}

.block-container{
    padding-top:1rem;
}

/* Sidebar */
[data-testid="stSidebar"]{
    background:#1e293b !important;
}

/* ตัวหนังสือ Sidebar */
[data-testid="stSidebar"] *{
    color:#f8fafc !important;
}

/* KPI */
[data-testid="stMetric"]{
    background:#081226 !important;
    border:1px solid #334155 !important;
    border-radius:12px !important;
    padding:15px !important;
}

/* ชื่อ KPI */
[data-testid="stMetricLabel"]{
    color:#cbd5e1 !important;
}

/* ตัวเลข KPI */
[data-testid="stMetricValue"]{
    color:#ffffff !important;
    font-weight:700 !important;
}

/* ค่าเพิ่ม/ลด */
[data-testid="stMetricDelta"]{
    color:#22c55e !important;
}

</style>
""", unsafe_allow_html=True)
