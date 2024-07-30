import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from customer import Customer

# Set up the layout
st.set_page_config(layout="centered")

st.title('MY자산 > 투자수익')

st.divider()

# Create customer data
customer = Customer('김증권')

# Define investment information

investments = int(customer.investments[-1])
portfolio_returns = round(customer.portfolio_returns[-1] * 100, 2)
cv = int(customer.cv[-1])
profit = cv - investments

investment_info = {
    "매입금액": f"{investments}원",
    "투자수익률": f"{portfolio_returns}%",
    "평가금액": f"{cv}원",
    "투자수익": f"{profit}원"
}

# Display investment information
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.metric('매입금액', investment_info['매입금액'], -1)
        st.metric('투자수익률', investment_info['투자수익률'], -2)
    with col2:
        st.metric('평가금액', investment_info['평가금액'], +3)
        st.metric('투자수익', investment_info['투자수익'], +6)

st.divider()

# Center the plot

st.line_chart(customer.portfolio_returns, use_container_width=False)

# Display winner stocks


# Display text summary
DATE = '2024-07-17'
st.write(f'{DATE}의 내 성과 분석') # 폭락

st.write('가장 큰 손실을 일으킨 종목들')
# 1. 한미반도체 A042700


# 2. SK하이닉스 A000660

# 3. 삼성전자 A005930






