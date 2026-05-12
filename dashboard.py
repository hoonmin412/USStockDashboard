import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import requests
import io

# --- 1. 설정 및 데이터 로드 함수 ---
SHEET_ID = "1j70bcEEuSr-AuzNW-j4_Huzi-fOJ0tTV66uUTikS0hs"
# 발급받은 Apps Script 웹 앱 URL
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxlhwsYk3feGt-8FFFme76g4gqgRyVPXNhd1VKvY5dqGQkmJ-aYVvExoNsel2z6RXeo/exec"

def load_gsheet_data(sheet_id):
    """구글 시트에서 데이터를 안전하게 읽어옴 (한글 인코딩 해결)"""
    try:
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
        response = requests.get(url)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.text))
            df.columns = [c.strip().capitalize() for c in df.columns]
            
            if 'Ticker' in df.columns and 'Sector' in df.columns:
                return df[['Sector', 'Ticker']].dropna()
            else:
                st.error("시트 헤더를 확인하세요: 'Ticker', 'Sector' 열이 필요합니다.")
                return pd.DataFrame(columns=['Sector', 'Ticker'])
        else:
            return pd.DataFrame(columns=['Sector', 'Ticker'])
    except Exception as e:
        st.error(f"구글 시트 연결 에러: {e}")
        return pd.DataFrame(columns=['Sector', 'Ticker'])

def save_to_gsheet(df):
    """구글 시트에 데이터를 실제로 저장 (Apps Script POST 요청)"""
    try:
        # 데이터프레임을 JSON 리스트로 변환
        data_to_send = df.to_dict('records')
        # Apps Script는 Redirect를 사용하므로 allow_redirects 옵션 확인 (requests는 기본이 True)
        response = requests.post(APPS_SCRIPT_URL, json=data_to_send)
        if response.status_code == 200 or "Success" in response.text:
            return True
        else:
            st.error(f"저장 실패: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"저장 중 오류 발생: {e}")
        return False

def calculate_rsi(data, window=14):
    """최근 종가 데이터를 이용해 RSI 계산"""
    if len(data) < window: return 0.0
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def get_stock_info(sector, symbol):
    """yfinance를 이용해 종목 정보 추출"""
    try:
        ticker = yf.Ticker(str(symbol).strip().upper())
        info = ticker.info
        
        company_name = info.get('longName', symbol)
        current_price = info.get('currentPrice', info.get('regularMarketPrice', 0.0))
        per = info.get('forwardPE', info.get('trailingPE', 0.0))
        eps = info.get('forwardEps', info.get('trailingEps', 0.0))
        
        hist = ticker.history(period="1mo")
        rsi_val = calculate_rsi(hist['Close']) if not hist.empty else 0.0
        
        earnings_date = "N/A"
        try:
            calendar = ticker.calendar
            if calendar is not None and 'Earnings Date' in calendar:
                dt = calendar['Earnings Date'][0]
                kst_dt = dt + timedelta(hours=9)
                earnings_date = kst_dt.strftime('%Y-%m-%d %H:%M')
        except:
            earnings_date = "N/A"

        return {
            "Sector": str(sector),
            "Ticker": str(symbol).upper(),
            "Company": str(company_name),
            "Price": float(current_price) if current_price else 0.0,
            "PER": float(per) if per else 0.0,
            "EPS": float(eps) if eps else 0.0,
            "RSI": round(float(rsi_val), 2) if rsi_val else 0.0,
            "Earnings(KST)": earnings_date
        }
    except:
        return None

# --- 2. 메인 실행 함수 ---
def run_dashboard(check_val):
    st.header("📊 실시간 종목 관리 대시보드")

    # 세션 상태 초기화 (최초 1회 시트 데이터 로드)
    if 'edit_df' not in st.session_state:
        st.session_state.edit_df = load_gsheet_data(SHEET_ID)

    # 1. 인터랙티브 종목 관리 (테이블에서 직접 추가/삭제)
    st.subheader("🛠 종목 리스트 관리")
    st.caption("표 하단의 (+) 버튼으로 추가, 행 선택 후 [Delete] 키로 삭제 가능합니다.")
    
    new_edit_df = st.data_editor(
        st.session_state.edit_df,
        num_rows="dynamic",
        width="stretch", 
        key="main_editor",
        column_config={
            "Sector": st.column_config.TextColumn("섹터", required=True),
            "Ticker": st.column_config.TextColumn("티커", required=True),
        }
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        # [변경] 단순 적용이 아닌 구글 시트 저장 로직 연결
        if st.button("💾 시트에 저장"):
            with st.spinner('구글 시트에 데이터를 저장하는 중...'):
                if save_to_gsheet(new_edit_df):
                    st.session_state.edit_df = new_edit_df
                    st.success("구글 시트에 성공적으로 저장되었습니다!")
                    st.rerun()
    with col2:
        if st.button("🔄 시트에서 새로고침"):
            st.session_state.edit_df = load_gsheet_data(SHEET_ID)
            st.rerun()

    st.divider()

    # 2. 데이터 처리 및 출력
    if not st.session_state.edit_df.empty:
        with st.spinner('실시간 시장 데이터를 분석 중...'):
            results = []
            for _, row in st.session_state.edit_df.iterrows():
                if pd.notna(row['Ticker']):
                    data = get_stock_info(row['Sector'], row['Ticker'])
                    if data: results.append(data)
            
            if results:
                final_df = pd.DataFrame(results)
                
                # --- 섹터 필터링 및 정렬 UI ---
                st.subheader("📈 실시간 지표 분석")
                f_col1, f_col2 = st.columns(2)
                
                with f_col1:
                    all_sectors = ["전체"] + sorted(final_df['Sector'].unique().tolist())
                    selected_sector = st.selectbox("📂 섹터 필터링", all_sectors)
                
                with f_col2:
                    sort_options = {"티커": "Ticker", "현재가": "Price", "PER": "PER", "RSI": "RSI"}
                    selected_sort = st.selectbox("🔢 정렬 기준", list(sort_options.keys()))
                
                # 필터링 적용
                if selected_sector != "전체":
                    final_df = final_df[final_df['Sector'] == selected_sector]
                
                # 정렬 적용
                is_ascending = (selected_sort == "티커")
                final_df = final_df.sort_values(by=sort_options[selected_sort], ascending=is_ascending)

                # 최종 결과 테이블 출력
                st.dataframe(
                    final_df, 
                    width="stretch", 
                    hide_index=True,
                    column_config={
                        "Price": st.column_config.NumberColumn("현재가", format="$%.2f"),
                        "RSI": st.column_config.ProgressColumn("RSI", min_value=0, max_value=100, format="%.2f"),
                        "PER": st.column_config.NumberColumn("PER", format="%.2f"),
                        "EPS": st.column_config.NumberColumn("EPS", format="%.2f"),
                    }
                )
                
                if check_val:
                    st.info("💡 **Tip:** 위 관리 테이블에서 종목을 변경한 후 '시트에 저장' 버튼을 눌러주세요.")
            else:
                st.error("입력된 티커에서 데이터를 가져올 수 없습니다.")
    else:
        st.warning("종목 리스트가 비어있습니다. 관리 테이블에 종목을 추가하세요.")