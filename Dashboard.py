with left:

    st.subheader("📈 กราฟแสดงข้อมูล")

    graph_mode = st.radio(
        "โหมดการแสดงผล",
        ["Actual Values", "Comparison Mode"],
        horizontal=True
    )

    options = {
        "CO₂ (Carbon Dioxide)": "CO2",
        "CH₄ (Methane)": "CH4",
        "NO₂ (Nitrogen Dioxide)": "NO2",
        "PM 2.5 (Particulate Matter)": "PM25",
        "Temp (Temperature)": "Temp",
        "Humidity (Relative Humidity)": "Humidity"
    }

    display_names = {v: k for k, v in options.items()}

    color_map = {
        "CO2": "#DC2626",
        "CH4": "#F97316",
        "NO2": "#7C3AED",
        "PM25": "#EAB308",
        "Temp": "#22C55E",
        "Humidity": "#2563EB"
    }

    # ---------------- SELECT MODE ----------------
    if graph_mode == "Actual Values":

        selected_actual = st.selectbox(
            "เลือกข้อมูล",
            list(options.keys())
        )

        selected = [options[selected_actual]]

    else:

        selected_labels = st.multiselect(
            "เลือกข้อมูล",
            list(options.keys()),
            default=["CO₂ (Carbon Dioxide)"]
        )

        selected = [options[x] for x in selected_labels]

        if not selected:
            st.warning("Please select at least one parameter.")
            st.stop()

    plot_df = df_plot.copy()

    # ---------------- SCALE (only for comparison mode) ----------------
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

    # ---------------- DATE FIX ----------------
    plot_df["Date"] = pd.to_datetime(plot_df["Date"], utc=True)
    plot_df["Date"] = plot_df["Date"].dt.tz_convert("Asia/Bangkok")
    plot_df["Date"] = plot_df["Date"].dt.tz_localize(None)
    plot_df["Date"] = plot_df["Date"].dt.floor("H")
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

        trace.hovertemplate = (
            "%{y:.2f}<br>"
            "%{x|%d/%m/%Y %H:%M}<extra></extra>"
        )

    fig.for_each_trace(lambda t: t.update(connectgaps=True))

    fig.update_layout(
        legend=dict(
            orientation="h",
            y=-0.25,
            x=0
        ),
        hovermode="x unified",
        xaxis=dict(automargin=True, type="date")
    )

    if graph_mode == "Actual Values":
        fig.update_yaxes(title_text="Actual Value")
    else:
        fig.update_yaxes(title_text="Relative Scale (%)", range=[0, 100])

    st.plotly_chart(fig, use_container_width=True)
