with left:

    st.subheader("📈 กราฟแสดงข้อมูล")

    graph_mode = st.radio(
        "โหมดการแสดงผล",
        ["Actual Values", "Comparison Mode"],
        horizontal=True
    )

    # ---------------- LABEL OPTIONS (เหมือนโค้ดเก่า แต่ clean) ----------------
    options = {
        "CO2": "CO2",
        "CH4": "CH4",
        "NO2": "NO2",
        "PM25": "PM25",
        "Temp": "Temp",
        "Humidity": "Humidity"
    }

    display_names = {
        "CO2": "CO₂ (Carbon Dioxide)",
        "CH4": "CH₄ (Methane)",
        "NO2": "NO₂ (Nitrogen Dioxide)",
        "PM25": "PM 2.5",
        "Temp": "Temperature",
        "Humidity": "Relative Humidity"
    }

    color_map = {
        "CO2": "#DC2626",
        "CH4": "#F97316",
        "NO2": "#7C3AED",
        "PM25": "#EAB308",
        "Temp": "#22C55E",
        "Humidity": "#2563EB"
    }

    plot_df = df_plot.copy()

    # ---------------- MULTI SELECT (แก้ให้เหมือน "โค้ดเก่า" ที่ใช้ได้จริง) ----------------
    selected = st.multiselect(
        "เลือกข้อมูล",
        list(options.keys()),
        default=["CO2"]
    )

    if not selected:
        st.warning("Please select at least one parameter.")
        st.stop()

    # ---------------- SCALE (เฉพาะ comparison mode) ----------------
    if graph_mode == "Comparison Mode":

        reference_scale = {
            "CO2": 1000,
            "CH4": 100,
            "NO2": 100,
            "PM25": 100,
            "Temp": 50,
            "Humidity": 100
        }

        for col in selected:
            plot_df[col] = pd.to_numeric(plot_df[col], errors="coerce").fillna(0)
            plot_df[col] = (plot_df[col] / reference_scale[col]) * 100

    # ---------------- TIME FIX ----------------
    plot_df["Date"] = pd.to_datetime(plot_df["Date"], errors="coerce")
    plot_df = plot_df.sort_values("Date")

    # ---------------- PLOT ----------------
    fig = px.line(
        plot_df,
        x="Date",
        y=selected,
        template="plotly_dark",
        markers=True
    )

    for trace in fig.data:
        col_key = trace.name

        trace.line.color = color_map.get(col_key, "#ffffff")
        trace.line.width = 3

        trace.name = display_names.get(col_key, col_key)

        trace.hovertemplate = "%{y:.2f}<br>%{x|%d/%m/%Y %H:%M}<extra></extra>"

    fig.update_layout(
        legend=dict(orientation="h"),
        hovermode="x unified",
        xaxis=dict(type="date")
    )

    if graph_mode == "Actual Values":
        fig.update_yaxes(title_text="Actual Value")
    else:
        fig.update_yaxes(title_text="Relative Scale (%)", range=[0, 100])

    st.plotly_chart(fig, use_container_width=True)
