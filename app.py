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
        ["Home", "Main_Dashboard", "설정"]
    )
    
    st.divider()
    
    # 사용자 입력 예시
    user_name = st.text_input("사용자 이름", value="Guest")
    check_val = st.checkbox("데이터 상세 보기")

# 3. 메인 페이지 로직
if menu == "홈":
    st.title(f"👋 {user_name}님, 시장 현황입니다.")
    
    # 1. 데이터 가져오기 (NASDAQ & S&P 500)
    @st.cache_data(ttl=3600) # 1시간 동안 캐시 유지하여 속도 향상
    def get_market_data():
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # NASDAQ(^IXIC), S&P 500(^GSPC) 티커 사용
        tickers = {"NASDAQ": "^IXIC", "S&P 500": "^GSPC"}
        data = pd.DataFrame()
        
        for name, ticker in tickers.items():
            df = yf.download(ticker, start=start_date, end=end_date)
            data[name] = df['Close']
        return data

    try:
        df_market = get_market_data()

        # 2. 메트릭스 표시 (현재가 및 전일 대비 등락 간단 계산)
        col1, col2 = st.columns(2)
        
        for i, col in enumerate([col1, col2]):
            name = df_market.columns[i]
            current_price = df_market[name].iloc[-1]
            prev_price = df_market[name].iloc[-2]
            delta = current_price - prev_price
            col.metric(name, f"{current_price:,.2f}", f"{delta:,.2f}")

        # 3. 꺾은선 그래프 시각화
        st.write("### 📈 최근 30일 지수 추이")
        
        # 두 지수의 단위가 다르므로 전처리 후 보여주거나 멀티 차트 활용
        # 여기서는 깔끔하게 Streamlit 기본 차트 사용
        st.line_chart(df_market)

        # 4. 데이터 표 출력 (선택 사항)
        with st.expander("상세 데이터 보기"):
            st.dataframe(df_market.sort_index(ascending=False))

    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")

elif menu == "데이터 분석":
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

elif menu == "설정":
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
