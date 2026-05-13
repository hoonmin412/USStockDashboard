import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta, timezone
import requests
import io

# --- 1. 설정 및 데이터 로드 함수 ---
SHEET_ID = "1j70bcEEuSr-AuzNW-j4_Huzi-fOJ0tTV66uUTikS0hs"
# 반드시 Apps Script에서 '모든 사용자(Anyone)'로 재배포한 새 URL을 넣으세요.
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycby35O_YtaGBK1YfYnKFs1dABcCBTioOpUip0nPvm06WtOXA1t5LKCiIwW1yHSw-UfR9/exec"

def load_gsheet_data(sheet_id):
    """구글 시트에서 데이터를 안전하게 읽어옴 (Sector, Ticker, Memo)"""
    try:
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
        response = requests.get(url)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.text))
            df.columns = [c.strip().capitalize() for c in df.columns]
            
            # Memo 컬럼이 없으면 빈 컬럼 생성 (구구형 시트 호환)
            if 'Memo' not in df.columns:
                df['Memo'] = ""
                
            if 'Ticker' in df.columns and 'Sector' in df.columns:
                # Memo까지 포함하여 반환 (결측치는 빈 문자열로 대체)
                return df[['Sector', 'Ticker', 'Memo']].fillna("")
            else:
                st.error("시트 헤더를 확인하세요: 'Ticker', 'Sector' 열이 필요합니다.")
                return pd.DataFrame(columns=['Sector', 'Ticker', 'Memo'])
        return pd.DataFrame(columns=['Sector', 'Ticker', 'Memo'])
    except Exception as e:
        return pd.DataFrame(columns=['Sector', 'Ticker', 'Memo'])

def save_to_gsheet(df):
    try:
        # 빈 값 제거 후 전송
        valid_df = df.dropna(subset=['Ticker', 'Sector'])
        data_to_send = valid_df.to_dict('records')
        headers = {"Content-Type": "application/json"}
        response = requests.post(APPS_SCRIPT_URL, json=data_to_send, headers=headers)
        # 구글 스크립트 특성상 200이 오거나 Success라는 텍스트가 포함되면 성공
        return response.status_code == 200 or "Success" in response.text
    except:
        return False

def calculate_rsi(data, window=14):
    if len(data) < window: return 0.0
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def get_stock_info(sector, symbol):
    if not symbol or pd.isna(symbol): return None
    try:
        ticker_symbol = str(symbol).strip().upper()
        ticker = yf.Ticker(ticker_symbol)
        # 중요: info를 가져올 때 에러가 나면 해당 종목은 건너뜀
        info = ticker.info
        
        # 주가 정보가 아예 없는 경우 방지
        current_price = info.get('currentPrice', info.get('regularMarketPrice', 0.0))
        if not current_price: return None

        company_name = info.get('longName', ticker_symbol)
        per = info.get('forwardPE', info.get('trailingPE', 0.0))
        eps = info.get('forwardEps', info.get('trailingEps', 0.0))
        
        hist = ticker.history(period="1mo")
        rsi_val = calculate_rsi(hist) if not hist.empty else 0.0
        
        earnings_date = "N/A"
        try:
            calendar = ticker.calendar
            if calendar is not None and 'Earnings Date' in calendar:
                dt = calendar['Earnings Date'][0]
                kst_dt = dt + timedelta(hours=9)
                earnings_date = kst_dt.strftime('%Y-%m-%d %H:%M')
        except:
            pass

        return {
            "Sector": str(sector),
            "Ticker": ticker_symbol,
            "Company": str(company_name),
            "Price": float(current_price),
            "PER": float(per) if per else 0.0,
            "EPS": float(eps) if eps else 0.0,
            "RSI": round(float(rsi_val), 2),
            "Earnings(KST)": earnings_date
        }
    except Exception as e:
        # 특정 종목 로딩 실패 시 로그 남기기
        # st.write(f"로그: {symbol} 데이터를 가져오지 못함") 
        return None

def run_dashboard(check_val):
    # 한국 시간 설정
    kst_now = datetime.now(timezone(timedelta(hours=9))).strftime('%Y-%m-%d %H:%M:%S')
    
    st.header("📊 실시간 종목 관리 대시보드")
    # 기존 우측 정렬 스타일 유지
    st.markdown(f"<p style='text-align: right; color: gray;'>last update (KST): {kst_now}</p>", unsafe_allow_html=True)

    if 'edit_df' not in st.session_state:
        st.session_state.edit_df = load_gsheet_data(SHEET_ID)

    # --- 1. 종목 리스트 관리 (Expander 적용 및 Memo 추가) ---
    with st.expander("🛠 종목 리스트 관리", expanded=False):
        # expander 내부에서도 기존 서브헤더 느낌을 위해 markdown 사용
        st.markdown("### 종목 리스트 편집")
        new_edit_df = st.data_editor(
            st.session_state.edit_df,
            num_rows="dynamic",
            width="stretch", 
            key="main_editor",
            column_config={
                "Sector": st.column_config.TextColumn("섹터", required=True),
                "Ticker": st.column_config.TextColumn("티커", required=True),
                "Memo": st.column_config.TextColumn("메모"), # 메모 컬럼 추가
            }
        )

        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("💾 시트에 저장"):
                with st.spinner('구글 시트 저장 중...'):
                    if save_to_gsheet(new_edit_df):
                        st.session_state.edit_df = new_edit_df
                        st.success("저장 완료!")
                        st.rerun()
                    else:
                        st.error("저장 실패 (Apps Script 설정을 확인하세요)")
        with col2:
            if st.button("🔄 새로고침"):
                st.session_state.edit_df = load_gsheet_data(SHEET_ID)
                st.rerun()

    st.divider()

    # --- 2. 지표 분석 결과 (가운데 정렬 및 데이터 병합) ---
    if not st.session_state.edit_df.empty:
        with st.spinner('실시간 시장 데이터를 분석 중...'):
            results = []
            for _, row in st.session_state.edit_df.iterrows():
                if pd.notna(row['Ticker']) and str(row['Ticker']).strip():
                    data = get_stock_info(row['Sector'], row['Ticker'])
                    if data: 
                        # 편집기에서 입력한 Memo를 결과 데이터에 합침
                        data["Memo"] = row.get('Memo', "")
                        results.append(data)
            
            if results:
                final_df = pd.DataFrame(results)
                
                st.subheader("📈 지표 분석 결과")
                f_col1, f_col2 = st.columns(2)
                with f_col1:
                    all_sectors = ["전체"] + sorted(final_df['Sector'].unique().tolist())
                    selected_sector = st.selectbox("📂 섹터 필터링", all_sectors)
                with f_col2:
                    sort_options = {"티커": "Ticker", "현재가": "Price", "PER": "PER", "RSI": "RSI"}
                    selected_sort = st.selectbox("🔢 정렬 기준", list(sort_options.keys()))
                
                if selected_sector != "전체":
                    final_df = final_df[final_df['Sector'] == selected_sector]
                
                final_df = final_df.sort_values(by=sort_options[selected_sort], ascending=(selected_sort == "티커"))

                # --- 가운데 정렬 설정 병합 ---
                # 모든 컬럼에 대해 기본적으로 가운데 정렬(alignment="center") 적용
                column_defs = {
                    col: st.column_config.Column(alignment="center") for col in final_df.columns
                }
                # 개별 컬럼 특성에 따른 추가 설정
                column_defs.update({
                    "Price": st.column_config.NumberColumn("현재가", format="$%.2f", alignment="center"),
                    "RSI": st.column_config.ProgressColumn("RSI", min_value=0, max_value=100, format="%.2f"),
                    "PER": st.column_config.NumberColumn("PER", format="%.2f", alignment="center"),
                    "EPS": st.column_config.NumberColumn("EPS", format="%.2f", alignment="center"),
                    "Memo": st.column_config.TextColumn("메모", alignment="center", width="medium"),
                })

                st.dataframe(
                    final_df, 
                    width="stretch", 
                    hide_index=True,
                    column_config=column_defs
                )
            else:
                st.warning("유효한 티커가 없거나 데이터를 불러올 수 없습니다. 티커 오타를 확인해 주세요.")