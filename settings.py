import streamlit as st
import time

def run_settings(user_name):
    st.title("⚙️ 설정")
    st.write(f"현재 사용자: **{user_name}**")
    
    if st.button("시스템 체크 시작"):
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress_bar.progress(i + 1)
        st.success("시스템이 정상입니다!")
