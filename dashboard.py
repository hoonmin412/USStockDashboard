import streamlit as st
import pandas as pd
import numpy as np

def run_dashboard(check_val):
    st.title("🔍 데이터 분석 공간")
    chart_data = pd.DataFrame(np.random.randn(20, 3), columns=['A', 'B', 'C'])

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
