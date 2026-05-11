import streamlit as st
import pandas as pd
import yfinance as yf # 금융 데이터 호출을 위해 추가
import numpy as np
from datetime import datetime, timedelta

# 1. 페이지 설정 (웹 브라우저 탭 이름 및 아이콘)
st.set_page_config(
    page_title="Streamlit 배포 템플릿",
    page_icon="📊",
    layout="wide"
)

# 2. 사이드바 구성
with st.sidebar:
    st.title("Settings")
    st.info("메뉴를 선택하고 설정을 변경하세요.")
    
    # 메뉴 선택 (라디오 버튼)
    menu = st.radio(
        "이동할 페이지",
        ["Home", "Main_Dashboard", "Settings"]
    )
    
    st.divider()
    
    # 사용자 입력 예시
    user_name = st.text_input("사용자 이름", value="Guest")
    check_val = st.checkbox("데이터 상세 보기")

# 3. 메인 페이지 로직
if menu == "Home":
    st.title(f"👋 {user_name}님, 시장 현황입니다.")
    
    # 1. 데이터 가져오기 (최대 범위인 10년치 미리 로드)
    @st.cache_data(ttl=3600)
    def get_market_data_10y():
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365 * 10)
        
        tickers = {"NASDAQ": "^IXIC", "S&P 500": "^GSPC"}
        data = pd.DataFrame()
        
        for name, ticker in tickers.items():
            df = yf.download(ticker, start=start_date, end=end_date)
            if isinstance(df.columns, pd.MultiIndex):
                data[name] = df[('Close', ticker)]
            else:
                data[name] = df['Close']
        return data

    try:
        with st.spinner('데이터를 불러오는 중...'):
            df_all = get_market_data_10y()

        # 2. 기간 선택 버튼 (10Y -> 1W 순서)
        st.write("### 📅 기간 선택")
        # 버튼들을 한 줄에 배치하기 위해 컬럼 생성
        time_tabs = ["10Year", "5Year", "1Year", "1Month", "1Week"]
        
        # 세션 상태를 이용해 초기 선택값 설정
        if 'selected_period' not in st.session_state:
            st.session_state.selected_period = "1Month"

        cols = st.columns(len(time_tabs))
        for i, tab in enumerate(time_tabs):
            if cols[i].button(tab, use_container_width=True):
                st.session_state.selected_period = tab

        # 선택된 기간에 따른 데이터 필터링 로직
        period_map = {
            "10Year": 365 * 10,
            "5Year": 365 * 5,
            "1Year": 365,
            "1Month": 30,
            "1Week": 7
        }
        
        days_to_cut = period_map[st.session_state.selected_period]
        cutoff_date = df_all.index[-1] - timedelta(days=days_to_cut)
        df_filtered = df_all[df_all.index >= cutoff_date]

        # 3. 메트릭스 표시
        m_col1, m_col2 = st.columns(2)
        for i, col in enumerate([m_col1, m_col2]):
            name = df_filtered.columns[i]
            current_price = df_filtered[name].iloc[-1]
            prev_price = df_filtered[name].iloc[-2]
            delta = current_price - prev_price
            col.metric(name, f"{current_price:,.2f}", f"{delta:,.2f}")

        st.divider()

        # 4. 좌우 차트 표시 (현재 선택된 기간: st.session_state.selected_period)
        st.write(f"### 📈 지수 추이 ({st.session_state.selected_period})")
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.write("#### NASDAQ")
            st.line_chart(df_filtered["NASDAQ"], color="#31333F")

        with chart_col2:
            st.write("#### S&P 500")
            st.line_chart(df_filtered["S&P 500"], color="#FF4B4B")

    except Exception as e:
        st.error(f"데이터를 처리하는 중 오류가 발생했습니다: {e}")

elif menu == "Main_Dashboard":
    st.title("🔍 데이터 분석 공간")
    
    # 샘플 데이터 생성
    chart_data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=['A', 'B', 'C']
    )

    # 레이아웃 분할
    left_col, right_col = st.columns(2)

    with left_col:
        st.write("### 라인 차트")
        st.line_chart(chart_data)

    with right_col:
        st.write("### 데이터 프레임")
        st.dataframe(chart_data, use_container_width=True)

    if check_val:
        st.write("### 상세 데이터 요약")
        st.write(chart_data.describe())

elif menu == "Settings":
    st.title("⚙️ 설정")
    st.write(f"현재 사용자: **{user_name}**")
    
    # 상태 바 예시
    if st.button("시스템 체크 시작"):
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress_bar.progress(i + 1)
        st.success("시스템이 정상입니다!")

# 4. 푸터 (Footer)
st.divider()
st.caption("© 2026 My Streamlit App. Built with ❤️")
