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
    if menu == "홈":
    # 1. 데이터 가져오기 (최대 10년치 캐싱)
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
        return data, end_date

    try:
        # 데이터와 업데이트 시각 가져오기
        df_all, last_update_time = get_market_data_10y()

        # 상단 타이틀 및 업데이트 시각 표시
        header_col1, header_col2 = st.columns([2, 1])
        with header_col1:
            st.title(f"👋 {user_name}님, 시장 현황")
        with header_col2:
            # 우상단 업데이트 시각 표시
            st.write("") # 간격 조절용
            st.write("")
            st.markdown(f"<p style='text-align: right; color: gray;'>last update : {last_update_time.strftime('%Y-%m-%d %H:%M:%S')}</p>", unsafe_allow_html=True)

        st.divider()

        # 각 차트별 기간 설정을 위한 세션 상태 초기화
        if 'period_nasdaq' not in st.session_state:
            st.session_state.period_nasdaq = "1Month"
        if 'period_snp500' not in st.session_state:
            st.session_state.period_snp500 = "1Month"

        time_tabs = ["10Year", "5Year", "1Year", "1Month", "1Week"]
        period_map = {"10Year": 3650, "5Year": 1825, "1Year": 365, "1Month": 30, "1Week": 7}

        # 메인 레이아웃 (좌: NASDAQ / 우: S&P 500)
        col_left, col_right = st.columns(2)

        # --- [왼쪽: NASDAQ] ---
        with col_left:
            # 1. 등락 정보 (차트 위)
            current_nas = df_all["NASDAQ"].iloc[-1]
            prev_nas = df_all["NASDAQ"].iloc[-2]
            delta_nas = current_nas - prev_nas
            st.metric("NASDAQ (^IXIC)", f"{current_nas:,.2f}", f"{delta_nas:,.2f}")

            # 2. 데이터 필터링 및 차트
            days_nas = period_map[st.session_state.period_nasdaq]
            df_nas_filtered = df_all["NASDAQ"][df_all.index >= (df_all.index[-1] - timedelta(days=days_nas))]
            st.line_chart(df_nas_filtered, color="#31333F", height=300)

            # 3. 차트 하단 기간 선택 버튼
            btn_cols_nas = st.columns(len(time_tabs))
            for i, tab in enumerate(time_tabs):
                if btn_cols_nas[i].button(tab, key=f"btn_nas_{tab}", use_container_width=True):
                    st.session_state.period_nasdaq = tab
                    st.rerun()

        # --- [오른쪽: S&P 500] ---
        with col_right:
            # 1. 등락 정보 (차트 위)
            current_snp = df_all["S&P 500"].iloc[-1]
            prev_snp = df_all["S&P 500"].iloc[-2]
            delta_snp = current_snp - prev_snp
            st.metric("S&P 500 (^GSPC)", f"{current_snp:,.2f}", f"{delta_snp:,.2f}")

            # 2. 데이터 필터링 및 차트
            days_snp = period_map[st.session_state.period_snp500]
            df_snp_filtered = df_all["S&P 500"][df_all.index >= (df_all.index[-1] - timedelta(days=days_snp))]
            st.line_chart(df_snp_filtered, color="#FF4B4B", height=300)

            # 3. 차트 하단 기간 선택 버튼
            btn_cols_snp = st.columns(len(time_tabs))
            for i, tab in enumerate(time_tabs):
                if btn_cols_snp[i].button(tab, key=f"btn_snp_{tab}", use_container_width=True):
                    st.session_state.period_snp500 = tab
                    st.rerun()

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
