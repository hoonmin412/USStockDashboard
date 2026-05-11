import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def run_home(user_name):
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
        df_all, last_update_time = get_market_data_10y()

        header_col1, header_col2 = st.columns([2, 1])
        with header_col1:
            st.title(f"👋 반갑습니다 {user_name}님!")
        with header_col2:
            st.write("")
            st.write("")
            st.markdown(f"<p style='text-align: right; color: gray;'>last update : {last_update_time.strftime('%Y-%m-%d %H:%M:%S')}</p>", unsafe_allow_html=True)

        st.divider()

        if 'period_nasdaq' not in st.session_state: st.session_state.period_nasdaq = "1Month"
        if 'period_snp500' not in st.session_state: st.session_state.period_snp500 = "1Month"

        time_tabs = ["10Year", "5Year", "1Year", "1Month", "1Week"]
        period_map = {"10Year": 3650, "5Year": 1825, "1Year": 365, "1Month": 30, "1Week": 7}

        col_left, col_right = st.columns(2)

        # --- [NASDAQ] ---
        with col_left:
            current_nas = df_all["NASDAQ"].iloc[-1]
            prev_nas = df_all["NASDAQ"].iloc[-2]
            delta_nas = current_nas - prev_nas
            st.metric("NASDAQ (^IXIC)", f"{current_nas:,.2f}", f"{delta_nas:,.2f}")
            
            days_nas = period_map[st.session_state.period_nasdaq]
            df_nas_filtered = df_all["NASDAQ"][df_all.index >= (df_all.index[-1] - timedelta(days=days_nas))]
            st.line_chart(df_nas_filtered, color="#31333F", height=300)

            btn_cols_nas = st.columns(len(time_tabs))
            for i, tab in enumerate(time_tabs):
                if btn_cols_nas[i].button(tab, key=f"btn_nas_{tab}", use_container_width=True):
                    st.session_state.period_nasdaq = tab
                    st.rerun()

        # --- [S&P 500] ---
        with col_right:
            current_snp = df_all["S&P 500"].iloc[-1]
            prev_snp = df_all["S&P 500"].iloc[-2]
            delta_snp = current_snp - prev_snp
            st.metric("S&P 500 (^GSPC)", f"{current_snp:,.2f}", f"{delta_snp:,.2f}")
            
            days_snp = period_map[st.session_state.period_snp500]
            df_snp_filtered = df_all["S&P 500"][df_all.index >= (df_all.index[-1] - timedelta(days=days_snp))]
            st.line_chart(df_snp_filtered, color="#FF4B4B", height=300)

            btn_cols_snp = st.columns(len(time_tabs))
            for i, tab in enumerate(time_tabs):
                if btn_cols_snp[i].button(tab, key=f"btn_snp_{tab}", use_container_width=True):
                    st.session_state.period_snp500 = tab
                    st.rerun()

    except Exception as e:
        st.error(f"데이터 처리 중 오류 발생: {e}")
