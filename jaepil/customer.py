import pandas as pd

import pickle
from pathlib import Path

CWD = Path(__file__).parent
WORKSPACE_PATH = CWD.parent
DATA_PATH = WORKSPACE_PATH / 'data'

RETURNS_DF = pd.read_pickle(DATA_PATH / 'returns_df_top100.pkl')
CLOSE_DF = pd.read_pickle(DATA_PATH / 'close_df_top100.pkl')

with open(DATA_PATH / 'ticker_to_name.pkl', 'rb') as f:
    TICKER_TO_NAME = pickle.load(f)

with open(DATA_PATH / 'name_to_ticker.pkl', 'rb') as f:
    NAME_TO_TICKER = pickle.load(f)

# TODO: (refactoring) hidden method에 대응하는 get method들 만들어 property를 return하도록 고치기. (w/ "is_ticker=" 옵션)
class Customer:
    def __init__(self, name):
        self.returns_df = RETURNS_DF
        self.close_df = CLOSE_DF
        self.ticker_to_name = TICKER_TO_NAME
        self.name_to_ticker = NAME_TO_TICKER

        self.name = name
        self.df = pd.read_csv(DATA_PATH / f'customer_{name}.csv', index_col=0)

        self.df.fillna(0, inplace=True)
        self.df.columns = [self.name_to_ticker[col] for col in self.df.columns]
        self.df.index = pd.to_datetime(self.df.index)

        self.start_date = self.df.index[0]
        self.portfolio_universe = self._get_portfolio_universe(is_ticker=True)

        self.returns_df = self.returns_df.loc[self.start_date:, self.portfolio_universe].copy()
        self.close_df = self.close_df.loc[self.start_date:, self.portfolio_universe].copy()

        self.cv_df = self._get_cv_df(is_ticker=True)
        self.current_holdings = self._get_current_holdings(is_ticker=True)
        self.investment_df = self._get_investment_df(is_ticker=True)
        self.investments = self._get_investments()
        self.cv = self._get_cv()
        self.portfolio_returns = self._get_portfolio_returns()
        self.portfolio_returns_df = self._get_portfolio_returns_df(is_ticker=True)
    
    def _get_portfolio_universe(self, is_ticker=False): # 포트폴리오에 (한 번이라도) 포함된 종목들
        tickers = self.df.columns.tolist() 

        if is_ticker:
            return tickers
        else:
            return [self.ticker_to_name[ticker] for ticker in tickers]

    def _get_current_holdings(self, is_ticker=False): # 현재 보유 중인 주식
        current_holdings = self.df.sum().to_dict()

        if is_ticker:
            return current_holdings
        else:
            return {self.ticker_to_name[ticker]: shares for ticker, shares in current_holdings.items()}
    
    def _get_cumshares(self, is_ticker=False): # 주식 보유량의 누적합
        ticker_cumshares = self.df.cumsum()

        if is_ticker:
            return ticker_cumshares
        else:
            return ticker_cumshares.rename(columns=self.ticker_to_name)
    
    def _get_cv_df(self, is_ticker=False): # 주식 현재가치 (current value) ffill
        cumshares_df = self._get_cumshares(is_ticker=True)
        cumshares_ffill = cumshares_df.reindex(self.close_df.index).ffill()
        cv_df = cumshares_ffill * self.close_df

        if is_ticker:
            return cv_df
        else:
            return cv_df.rename(columns=self.ticker_to_name)
    
    # TODO: 매입 평가 방식, 실현 손익 빼버려야 함. 고치기. 
    # TODO: 일단 예시 자체를 매수/매입 반복 없애기로 했다. 매입금액 조절이 까다로워서. 
    def _get_investment_df(self, is_ticker=False): # 매입금액 (investment) ffill 
        investment_df = self.df.reindex(self.close_df.index) * self.close_df
        investment_df = investment_df.ffill()

        if is_ticker:
            return investment_df
        else:
            return investment_df.rename(columns=self.ticker_to_name)

    def _get_portfolio_returns_df(self, is_ticker=False): # 평가/매입 기준 수익률
        portfolio_returns = (self.cv_df / self.investment_df) - 1

        if is_ticker:
            return portfolio_returns
        else:
            return portfolio_returns.rename(columns=self.ticker_to_name)
    
    def _get_investments(self): # 전체 매입금액
        investment_s = self.investment_df.sum(axis=1)

        return investment_s

    def _get_cv(self): # 전체 현재가치
        cv_s = self.cv_df.sum(axis=1)

        return cv_s
    
    def _get_portfolio_returns(self): # 전체 수익률
        portfolio_returns_s = (self._get_cv() / self._get_investments()) - 1

        return portfolio_returns_s
        

    