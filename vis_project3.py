# 필요한 라이브러리 불러오기
import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from folium.features import GeoJson, GeoJsonTooltip
from streamlit_folium import st_folium


# 제목 지어줌
st.title("대한민국 시군구 합계출산율 지도")

# 데이터 불러오고 이름 불일치하는 창원시 전처리 + 파일 병합하는 함수 만듦
# @을 써서 결과를 캐시에 저장 -> 속도 향상
# 가독성을 위해 함수로 만들어줌
@st.cache_data
def load_data():
    # GeoJSON 데이터 불러오고 컬럼명 변경해주기
    gdf_gu = gpd.read_file("N3A_G01.json")
    gdf_gu = gdf_gu.rename(columns={"NAME": "행정구"})
    
    # 합계출산율 데이터 불러오고 컬럼명 변경해주기
    df_birth = pd.read_csv("연령별_출산율_및_합계출산율_행정구역별__20241120131149.csv", header=1, encoding="EUC-KR")
    df_birth = df_birth[["행정구역별", "합계출산율 (가임여성 1명당 명)"]]
    df_birth.columns = ["행정구", "합계출산율"]
    
    # 창원시의 이름이 불일치하는 문제 -> 전처리
    df_birth["행정구"] = df_birth["행정구"].replace("통합창원시", "창원시")
    
    # GeoJSON과 출생률 데이터 병합
    gdf_gu = gdf_gu.merge(df_birth, on="행정구", how="left")
    
    return gdf_gu

# 데이터 불러오는 함수 
gdf_gu = load_data()

# folium 지도 생성
def create_map(gdf_gu):
    korea_map = folium.Map(
        location=[36.5, 127.5],  # 대한민국 중심 좌표라고 함 - 거기를 시각화의 시작으로 삼음
        zoom_start=7,
        tiles="cartodbpositron"
    )
    
    # Choropleth 지도 추가
    folium.Choropleth(
        geo_data=gdf_gu,
        data=gdf_gu,
        columns=("행정구", "합계출산율"),
        key_on="feature.properties.행정구",
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.5,
        legend_name="합계출산율 (TFR)"
    ).add_to(korea_map)
    
    # tooltip 추가 -> 마우스를 올리면 행정구와 합계출산율 정보가 나오도록 설정
    tooltip = GeoJson(
        gdf_gu,
        style_function=lambda x: {"fillColor": "transparent", "color": "transparent"},
        tooltip=GeoJsonTooltip(
            fields=["행정구", "합계출산율"],
            aliases=["행정구:", "합계출산율:"],
            localize=True
        )
    )
    tooltip.add_to(korea_map)
    
    return korea_map

# 지도 생성 및 표시
korea_map = create_map(gdf_gu)
st_folium(korea_map, width=700, height=500)

# 설명 + tooltip 이 있음을 설명해주기
st.write("시군구별 합계출산율입니다.")
st.write("마우스를 아무 지역 위에 올리면 행정구와 합계출산율 정보를 보실 수 있습니다.")
