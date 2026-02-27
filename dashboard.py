import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'NanumGothic'
import os

# 페이지 설정
st.set_page_config(page_title="네모스토어 매물 대시보드", layout="wide")

# 데이터 로드 함수
def load_data():
    db_path = "/Users/jeonjiyeong/Documents/fcicb7/nemostore/data/nemo_store.db"
    conn = sqlite3.connect(db_path)
    query = "SELECT * FROM nemo_stores"
    df = pd.read_sql(query, conn)
    conn.close()
    
    # 금액 변환 (천 원 단위 -> 만 원 단위)
    # DB의 deposit, monthly_rent, premium, maintenance_fee 등은 천 원 단위임 (예: 45000 -> 4500만원)
    cols_to_convert = ['deposit', 'monthly_rent', 'premium', 'sale', 'maintenance_fee']
    for col in cols_to_convert:
        if col in df.columns:
            df[col] = df[col] * 0.1  # 만 원 단위로 변환
            
    return df

# 금액 포맷팅 함수
def format_currency(val):
    if val >= 10000:
        return f"{val/10000:.1f}억"
    return f"{val:,.0f}만"

# 데이터 로드
df = load_data()

# 사이드바 필터
st.sidebar.header("필터 설정")

# 업종 필터
business_types = st.sidebar.multiselect(
    "업종 선택",
    options=df['business_middle_code_name'].unique(),
    default=df['business_middle_code_name'].unique()
)

# 층수 필터
floors = st.sidebar.multiselect(
    "층수 선택",
    options=df['floor'].unique(),
    default=df['floor'].unique()
)

# 가격 범위 필터 (보증금 기준)
min_deposit = int(df['deposit'].min())
max_deposit = int(df['deposit'].max())
deposit_range = st.sidebar.slider(
    "보증금 범위 (만원)",
    min_value=min_deposit,
    max_value=max_deposit,
    value=(min_deposit, max_deposit)
)

# 데이터 필터링
filtered_df = df[
    (df['business_middle_code_name'].isin(business_types)) &
    (df['floor'].isin(floors)) &
    (df['deposit'] >= deposit_range[0]) &
    (df['deposit'] <= deposit_range[1])
]

# 메인 화면
st.title("🏬 네모스토어 매물 분석 대시보드")
st.markdown(f"현재 총 **{len(filtered_df)}** 개의 매물이 검색되었습니다.")

# 주요 지표 (KPI)
col1, col2, col3, col4 = st.columns(4)
with col1:
    avg_deposit = filtered_df['deposit'].mean()
    st.metric("평균 보증금", format_currency(avg_deposit))
with col2:
    avg_rent = filtered_df['monthly_rent'].mean()
    st.metric("평균 월세", format_currency(avg_rent))
with col3:
    avg_premium = filtered_df['premium'].mean()
    st.metric("평균 권리금", format_currency(avg_premium))
with col4:
    avg_size = filtered_df['size'].mean()
    st.metric("평균 전용면적", f"{avg_size:.1f}㎡")

st.divider()

# 시각화 영역
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("📊 업종별 매물 분포")
    if not filtered_df.empty:
        type_counts = filtered_df['business_middle_code_name'].value_counts()
        fig, ax = plt.subplots(figsize=(10, 6))
        type_counts.plot(kind='barh', ax=ax, color='skyblue')
        ax.set_xlabel("매물 수")
        ax.set_ylabel("업종")
        st.pyplot(fig)
    else:
        st.write("데이터가 없습니다.")

with col_chart2:
    st.subheader("💰 권리금 vs 보증금")
    if not filtered_df.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(filtered_df['deposit'], filtered_df['premium'], alpha=0.5, color='orange')
        ax.set_xlabel("보증금 (만원)")
        ax.set_ylabel("권리금 (만원)")
        st.pyplot(fig)
    else:
        st.write("데이터가 없습니다.")

# 상세 데이터 테이블
st.subheader("📋 매물 상세 목록")
display_df = filtered_df[[
    'title', 'business_middle_code_name', 'price_type_name', 
    'deposit', 'monthly_rent', 'premium', 'maintenance_fee', 
    'floor', 'size', 'near_subway_station'
]].copy()

# 컬럼명 변경 (가독성)
display_df.columns = [
    '제목', '업종', '거래형태', '보증금(만)', '월세(만)', 
    '권리금(만)', '관리비(만)', '층수', '면적(㎡)', '지하철역'
]

st.dataframe(display_df, use_container_width=True)

# 실행 방법 안내
st.sidebar.info("실행 방법: `streamlit run nemostore/dashboard.py` (이미 실행 중일 수 있습니다)")
