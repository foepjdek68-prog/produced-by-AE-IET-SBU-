with right:

    st.subheader("📊 Detail Panel")

    # ---------------- SELECT SINGLE FOR DETAIL ----------------
    detail_col = st.selectbox(
        "เลือกดูรายละเอียด",
        ["CO2", "CH4", "NO2", "PM25", "Temp", "Humidity"]
    )

    series = pd.to_numeric(df[detail_col], errors="coerce").dropna()

    if len(series) > 0:

        last = series.iloc[-1]
        avg = series.mean()
        mx = series.max()
        mn = series.min()

        # trend (last vs 5 steps back)
        if len(series) >= 5:
            trend = series.iloc[-1] - series.iloc[-5]
        else:
            trend = series.iloc[-1] - series.iloc[0]

        # ---------------- HEADER ----------------
        st.markdown(f"### 🔎 {detail_col}")

        # ---------------- METRICS ----------------
        st.metric("Latest", f"{last:.2f}")
        st.metric("Average", f"{avg:.2f}")
        st.metric("Max", f"{mx:.2f}")
        st.metric("Min", f"{mn:.2f}")
        st.metric("Trend", f"{trend:.2f}")

        st.markdown("---")

        # ---------------- SIMPLE STATUS ----------------
        if detail_col == "CO2":
            if avg < 450:
                st.success("🟢 Normal")
            elif avg < 500:
                st.warning("🟡 Warning")
            else:
                st.error("🔴 Critical")

        elif detail_col == "PM25":
            if avg < 25:
                st.success("🟢 Good Air Quality")
            elif avg < 50:
                st.warning("🟡 Moderate")
            else:
                st.error("🔴 Unhealthy")

        elif detail_col == "Temp":
            if 20 <= avg <= 35:
                st.success("🟢 Normal Temperature")
            else:
                st.warning("🟡 Outside comfort range")

        elif detail_col == "Humidity":
            if 40 <= avg <= 70:
                st.success("🟢 Normal Humidity")
            else:
                st.warning("🟡 Abnormal")

        else:
            st.info("🟢 Normal monitoring range")
