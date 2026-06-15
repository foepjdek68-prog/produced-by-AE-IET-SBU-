with right:

    st.subheader("📊 Insight Panel")

    st.markdown("### 📍 Latest Overview")

    # ---------------- GLOBAL STATS ----------------
    cols_all = ["CO2", "CH4", "NO2", "PM25", "Temp", "Humidity"]

    for col in cols_all:

        if col not in df.columns:
            continue

        last = df[col].iloc[-1]
        avg = df[col].mean()
        mx = df[col].max()

        # mini status logic
        if col == "CO2":
            status = "🟢" if avg < 450 else "🟡" if avg < 500 else "🔴"
        elif col == "PM25":
            status = "🟢" if avg < 25 else "🟡" if avg < 50 else "🔴"
        elif col == "Temp":
            status = "🟢" if 20 <= avg <= 35 else "🟡"
        elif col == "Humidity":
            status = "🟢" if 40 <= avg <= 70 else "🟡"
        else:
            status = "🟢" if avg < mx * 0.8 else "🟡"

        st.markdown(
            f"""
            <div style="
                background:#0f172a;
                padding:10px;
                border-radius:10px;
                margin-bottom:8px;
                border:1px solid #1f2937;
            ">
                <b>{status} {col}</b><br>
                <small>Latest: {last:.2f}</small><br>
                <small>Avg: {avg:.2f} | Max: {mx:.2f}</small>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    # ---------------- CO2 SPECIAL STATUS ----------------
    st.subheader("🌍 CO₂ Status")

    avg_co2 = df["CO2"].mean()

    if avg_co2 < 450:
        st.success("Normal 🟢 Safe emission level")
    elif avg_co2 < 500:
        st.warning("Warning 🟡 Moderate emission level")
    else:
        st.error("Critical 🔴 High emission level")

    st.markdown("---")

    # ---------------- QUICK SUMMARY ----------------
    st.subheader("📌 Quick Summary")

    st.metric("Highest CO2", f"{df['CO2'].max():.2f}")
    st.metric("Lowest CO2", f"{df['CO2'].min():.2f}")

    st.metric("Highest Temp", f"{df['Temp'].max():.2f}")
    st.metric("Highest PM2.5", f"{df['PM25'].max():.2f}")
