import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_datareader as pdr
from datetime import datetime, timedelta

def calculate_rsi(data, window=14):
    """최근 종가 데이터를 이용해 RSI 계산"""
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def get_stock_info(sector, symbol):
    """yfinance를 이용해 종목의 상세 정보 추출"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # 기본 정보
        company_name = info.get('longName', 'N/A')
        current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
        per = info.get('forwardPE', info.get('trailingPE', 0))
        eps = info.get('forwardEps', info.get('trailingEps', 0))
        
        # RSI 계산 (최근 1개월 데이터 기반)
        hist = ticker.history(period="1mo")
        rsi_val = calculate_rsi(hist['Close']) if not hist.empty else 0
        
        # 실적 발표일 처리 (한국 시간 변환: UTC+9)
        calendar = ticker.calendar
        earnings_date = "N/A"
        if calendar is not None and 'Earnings Date' in calendar:
            # 보통 여러 날짜가 리스트로 들어옴
            dt = calendar['Earnings Date'][0]
            # 한국 시간으로 변환 (+9시간)
            kst_dt = dt + timedelta(hours=9)
            earnings_date = kst_dt.strftime('%Y-%m-%d %H:%M')

        return {
            "섹터": sector,
            "종목": symbol.upper(),
            "기업 명": company_name,
            "현재 주가": f"${current_price:,.2f}",
            "PER": round(per, 2) if per else "N/A",
            "EPS": round(eps, 2) if eps else "N/A",
            "RSI": round(rsi_val, 2) if rsi_val else "N/A",
            "다음 실적 발표 (KST)": earnings_date
        }
    except Exception as e:
        return None

def run_dashboard(check_val):
    st.title("🔍 종목 대시보드")

    # 1. 세션 상태에 종목 리스트 초기화
    if 'stock_list' not in st.session_state:
        st.session_state.stock_list = [
            {"sector": "Tech", "symbol": "AAPL"},
            {"sector": "Tech", "symbol": "NVDA"},
            {"sector": "Index", "symbol": "QQQ"}
        ]

    # 2. 종목 추가 및 삭제 인터페이스
    with st.expander("➕ 종목 관리 (추가/삭제)"):
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            new_sector = st.text_input("섹터 입력", placeholder="예: 반도체")
        with col2:
            new_symbol = st.text_input("티커 입력", placeholder="예: TSLA")
        with col3:
            st.write(" ") # 레이아웃 정렬용
            if st.button("추가", use_container_width=True):
                if new_sector and new_symbol:
                    st.session_state.stock_list.append({"sector": new_sector, "symbol": new_symbol.upper()})
                    st.rerun()
                else:
                    st.warning("섹터와 티커를 모두 입력하세요.")

        st.divider()
        
        # 삭제 기능
        st.write("현재 등록된 종목 (삭제하려면 선택)")
        if st.session_state.stock_list:
            # 삭제할 종목을 멀티셀렉트로 선택
            delete_targets = st.multiselect(
                "삭제할 종목을 선택하세요",
                options=[f"{s['sector']} - {s['symbol']}" for s in st.session_state.stock_list]
            )
            if st.button("선택 종목 삭제"):
                st.session_state.stock_list = [
                    s for s in st.session_state.stock_list 
                    if f"{s['sector']} - {s['symbol']}" not in delete_targets
                ]
                st.rerun()
        else:
            st.info("등록된 종목이 없습니다.")

    # 3. 데이터 로딩 및 출력
    if st.session_state.stock_list:
        with st.spinner('실시간 데이터를 수집 중입니다...'):
            results = []
            for stock in st.session_state.stock_list:
                data = get_stock_info(stock['sector'], stock['symbol'])
                if data:
                    results.append(data)
            
            if results:
                df = pd.DataFrame(results)
                
                # 테이블 출력
                st.write("### 📊 나의 관심 종목 지표")
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # 상세 보기 체크박스 로직 (app.py에서 전달받은 값)
                if check_val:
                    st.write("#### 💡 투자 지표 가이드")
                    st.info("""
                    - **PER**: 주가수익비율. 낮을수록 저평가 상태일 가능성이 있음.
                    - **RSI**: 70 이상이면 과매수, 30 이하이면 과매도 구간으로 해석.
                    - **Earnings Date**: 한국 시간(KST) 기준으로 표시됩니다.
                    """)
            else:
                st.error("데이터를 불러올 수 있는 종목이 없습니다. 티커를 확인해 주세요.")
    else:
        st.warning("먼저 종목을 추가해 주세요.")
