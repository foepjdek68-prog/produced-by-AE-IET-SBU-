with col_map:
            st.markdown("##### 🗺️ แผนที่พยากรณ์โครงข่าย (Spatial 2D View)")
            all_data['lat'] = all_data['region'].map(lambda x: COORDS[x][0])
            all_data['lon'] = all_data['region'].map(lambda x: COORDS[x][1])
            
            # แก้ไขส่วนนี้: ใช้ Style พื้นฐานที่ไม่ต้องพึ่งพา Mapbox Token มากเกินไป
            st.pydeck_chart(pdk.Deck(
                map_style=None, # ลองเซตเป็น None เพื่อใช้ Default ของ Deck.gl
                initial_view_state=pdk.ViewState(
                    latitude=13.5, 
                    longitude=101.0, 
                    zoom=5.0, 
                    pitch=0
                ),
                layers=[
                    pdk.Layer(
                        "ScatterplotLayer", 
                        all_data, 
                        get_position="[lon, lat]", 
                        get_color="[255, 100, 100, 200]", # เปลี่ยนเป็นสีแดงชั่วคราวเพื่อเช็คบัค
                        get_radius=60000,
                        pickable=True
                    )
                ],
            ))
