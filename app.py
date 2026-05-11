import streamlit as st
import pandas as pd
import numpy as np
import time

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
        ["홈", "데이터 분석", "설정"]
    )
    
    st.divider()
    
    # 사용자 입력 예시
    user_name = st.text_input("사용자 이름", value="Guest")
    check_val = st.checkbox("데이터 상세 보기")

# 3. 메인 페이지 로직
if menu == "홈":
    # st.title(f"👋 환영합니다, {user_name}님!")
    st.title(f"👋 환영합니다, HMJ 쀼님!")
    st.subheader("이 앱은 Streamlit 표준 템플릿입니다.")
    
    # 메트릭스 표시 (대시보드 상단 느낌)
    col1, col2, col3 = st.columns(3)
    col1.metric("방문자 수", "1,200명", "12%")
    col2.metric("성능", "98%", "0.4%")
    col3.metric("오류율", "0.2%", "-0.1%")

    st.markdown("""
    ---
    ### 📝 사용 방법
    1. 왼쪽 **사이드바**에서 메뉴를 선택하세요.
    2. 데이터 분석 탭에서 가상의 데이터를 확인하세요.
    3. 원하는 로직을 `app.py`에 추가하여 배포할 수 있습니다.
    """)

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
