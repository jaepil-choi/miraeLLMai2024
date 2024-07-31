import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from customer import Customer
from clovagraphrag import get_clova_response

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

# Select Date
date_list = customer.cv.index.strftime('%Y-%m-%d').tolist()

date = st.select_slider(
    '분석할 날짜를 선택하세요',
    options=date_list
)

# Display text summary
st.write(f'{date}의 내 성과 분석')

daily_pnl_df = customer.cv_df - customer.cv_df.shift(1)
daily_pnl = daily_pnl_df.loc[date, :]

st.write('가장 많이 벌어준 BEST 3 종목들')
best3 = daily_pnl.sort_values(ascending=False).head(3)
best3.index = [customer.ticker_to_name[ticker] for ticker in best3.index]
best3 = [ (name, pnl) for name, pnl in best3.to_dict().items() ]


st.write(f'{best3[0][0]}: :green[+{best3[0][1]:.0f}원]')
best3_1 = st.button(f'{best3[0][0]}가 왜 올랐을까?', type='primary')

st.write(f'{best3[1][0]}: :green[+{best3[1][1]:.0f}원]')
best3_2 = st.button(f'{best3[1][0]}가 왜 올랐을까?', type='primary')

st.write(f'{best3[2][0]}: :green[+{best3[2][1]:.0f}원]')
best3_3 = st.button(f'{best3[2][0]}가 왜 올랐을까?', type='primary')

st.write('* 버튼을 누르고 답변이 생성될 때까지 잠시 기다려주세요.')

if best3_1:
    name = best3[0][0]
    response = get_clova_response(name, date, '상승')
    st.write(response)
elif best3_2:
    name = best3[1][0]
    response = get_clova_response(name, date, '상승')
    st.write(response)
elif best3_3:
    name = best3[2][0]
    response = get_clova_response(name, date, '상승')
    st.write(response)

####################

st.write('가장 많이 잃은 WORST 3 종목들')
worst3 = daily_pnl.sort_values(ascending=True).head(3)
worst3.index = [customer.ticker_to_name[ticker] for ticker in worst3.index]
worst3 = [ (name, pnl) for name, pnl in worst3.to_dict().items() ]

st.write(f'{worst3[0][0]}: :red[-{worst3[0][1]:.0f}원]')
worst3_1 = st.button(f'{worst3[0][0]}가 왜 떨어졌을까?', type='primary')

st.write(f'{worst3[1][0]}: :red[-{worst3[1][1]:.0f}원]')
worst3_2 = st.button(f'{worst3[1][0]}가 왜 떨어졌을까?', type='primary')

st.write(f'{worst3[2][0]}: :red[-{worst3[2][1]:.0f}원]')
worst3_3 = st.button(f'{worst3[2][0]}가 왜 떨어졌을까?', type='primary')

if worst3_1:
    name = worst3[0][0]
    response = get_clova_response(name, date, '하락')
    st.write(response)
elif worst3_2:
    name = worst3[1][0]
    response = get_clova_response(name, date, '하락')
    st.write(response)
elif worst3_3:
    name = worst3[2][0]
    response = get_clova_response(name, date, '하락')
    st.write(response)






