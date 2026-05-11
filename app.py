import streamlit as st

# 분리한 파일(모듈)들을 불러오기
from home import run_home
from dashboard import run_dashboard
from settings import run_settings

# 1. 페이지 설정
st.set_page_config(
    page_title="US Stock Dashboard",
    page_icon="📊",
    layout="wide"
)

# 2. 사이드바 구성
with st.sidebar:
    st.title("Menu")
    menu = st.radio(
        "이동할 페이지",
        ["Home", "Main_Dashboard", "Settings"]
    )
    st.divider()
    user_name = st.text_input("사용자 이름", value="Guest")
    check_val = st.checkbox("데이터 상세 보기")

# 3. 메인 로직 (모듈 함수 호출)
if menu == "Home":
    run_home(user_name)

elif menu == "Main_Dashboard":
    run_dashboard(check_val)

elif menu == "Settings":
    run_settings(user_name)

# 4. 푸터
st.divider()
st.caption("© 2026 My Streamlit App. Built with ❤️")
