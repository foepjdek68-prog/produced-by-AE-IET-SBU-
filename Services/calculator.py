def emission_score(df):

    latest = df.iloc[-1]

    score = (
        latest["CO2"] * 0.5 +
        latest["CH4"] * 0.3 +
        latest["NO2"] * 0.2
    )

    return round(score,2)
