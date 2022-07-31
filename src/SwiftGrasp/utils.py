import datetime
from tracemalloc import start
from typing import Union
import pandas as pd
from yahoofinancials import YahooFinancials
from dateutil.relativedelta import relativedelta
import warnings

class CheckTicker:
    def __init__(self, ticker:str) -> None:
        self.ticker = ticker
        self._yf = None
        self.first_trade_date = None

    def _validate_dtype(self):
        if not isinstance(self.ticker, str):
            raise TypeError("Ticker has to be string type.")
    
    def _validate_value(self):
        self._yf = YahooFinancials(self.ticker)
        
        _tst = self._yf.get_financial_stmts(frequency = 'Quarterly', statement_type = 'income')
        if list(_tst.values())[0][self.ticker] is None:
            raise ValueError(f"Cannot get info of ticker {self.ticker}, it probably does not exist.")

    def validate(self):
        self._validate_dtype()
        self._validate_value()
        #ToDo [future]: check whether ticker already in the databse

    def _pull_first_trade_date(self):
        today = datetime.datetime.today()
        seven_days_ago = today - relativedelta(days=8)
        today_prices = self._yf.get_historical_price_data(seven_days_ago.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'), 'weekly')
        
        #! Assume that ticker is already checked, no need for the check below
        # if len(today_prices[self.ticker].keys()) > 1 or len(today_prices[self.ticker]['eventsData'])>0 :
        self.first_trade_date = today_prices[self.ticker]['firstTradeDate']['formatted_date'] 
        # else:
        #     raise ValueError("Can't find the input ticker from database, please check the spelling or try another ticker.")

    def get_first_trade_date(self):
        if self.first_trade_date is None:
            self._pull_first_trade_date()
        
        return self.first_trade_date

class FinancialStatementData:
    __table_prefix_dict__ = {
        'balance':'balanceSheet'
        ,'income':'incomeStatement'
        ,'cash':'cashflowStatement'
        }
    
    def __init__(self
        ,ticker:str
        ,frequency:Union[str,None] = None
        ) -> None:
        
        ct = CheckTicker(ticker)
        ct.validate()
        self.ticker = ticker
        
        self.frequency = self._validate_input_frequency(frequency)
        self._balance = None
        self._income = None
        self._cash = None
        
        self._yf = YahooFinancials(self.ticker)
        
        self._pull_data()
        
    def _pull_data(self):
        self._balance = self._format_financial_data('balance')
        self._income = self._format_financial_data('income')
        self._cash = self._format_financial_data('cash')
        ## examples
        # all_statement_data_qt =  yf.get_financial_stmts('quarterly', ['income', 'cash', 'balance'])
        # apple_earnings_data = yf.get_stock_earnings_data()
        # apple_net_income = yf.get_net_income()

    def _get_table_suffix(self):
        if self.frequency == 'quarterly':
            return 'Quarterly'
        else:
            # if 'annual'
            return ''

    def _get_json_header_name(self, abbr:str):
        if abbr in self.__table_prefix_dict__.keys():
            suf = self._get_table_suffix()
            return self.__table_prefix_dict__.get(abbr)+'History'+suf
    
    def _format_financial_data(self, abbr:str):
        jsn = self._yf.get_financial_stmts(frequency = self.frequency, statement_type = abbr)

        result_list = []
        header = self._get_json_header_name(abbr)
        obj = jsn[header][self.ticker]
        for i in range(len(obj)):
            df_temp = pd.DataFrame(obj[i].values(), index = obj[i].keys())
            result_list.append(df_temp)

        return pd.concat(result_list)

    @staticmethod
    def _validate_input_frequency(obj):
        if obj is None:
            return "quarterly"
        elif not isinstance(obj, str):
            raise TypeError("Input needs to be either None or String type.")
        elif obj in ('annual','quarterly'):
            return obj
        else:
            return ValueError("The input string has to be either 'quarterly" or 'annual.')
    
    def get_balance_sheet(self):
        return self._balance
    
    def get_income_statement(self):
        return self._income
    
    def get_cash_statement(self):
        return self._cash

class StockData:
    def __init__(self
        ,ticker:str
        ,start_date:Union[str, None] = None
        ,end_date:Union[str, None] = None
        ,frequency:Union[str, None] = None
        ) -> None:
        
        ct = CheckTicker(ticker)
        ct.validate()
        self.ticker = ticker
        self.first_trade_date = ct.get_first_trade_date()
        self._yf = ct._yf

        if frequency is None:
            self.frequency = 'daily'
        else:
            self.frequency = self._validate_frequency(frequency)

        today = datetime.datetime.today()
        
        if end_date is None:
            self.end_date = today.strftime('%Y-%m-%d')
        else:
            self.end_date = self._validate_date(end_date)
        
        if start_date is None:
            # just make the default start time as 3 years ago for now
            # or the first trade date, whichever is later
            three_yrs_ago = today - relativedelta(years=3)
            self.start_date = max(three_yrs_ago.strftime('%Y-%m-%d'), self.first_trade_date)
        else:
            self.start_date = max(self._validate_date(start_date), self.first_trade_date)

        self._check_date_logic()

        self._stock_obj = None
        self._set_obj()
        
        self._stock = None
        self._dividend = None
        self._split = None

    def _set_obj(self):
        self._stock_obj = self._yf.get_historical_price_data(self.start_date, self.end_date, self.frequency)

    def _pull_stock(self):
        self._stock = pd.DataFrame(self._stock_obj[self.ticker]['prices'])
    
    def _pull_dividend(self):
        self._dividend = pd.DataFrame(self._stock_obj[self.ticker]['eventsData']['dividends']).transpose()

    def _pull_split(self):
        if len(self._stock_obj[self.ticker]['eventsData']['splits'])>0:
            self._split = pd.DataFrame(self._stock_obj[self.ticker]['eventsData']['splits']).transpose()
        else:
            warnings.warn(f"There're no split events in the specified timeframe ({self.start_date} to {self.end_date}).")

    @staticmethod
    def _validate_type_str(obj):
        if not isinstance(obj, str):
            raise TypeError(f"Input {obj} type must be str.")
    
    def _validate_date(self, obj):
        self._validate_type_str(obj)
        try:
            _ = datetime.datetime.strptime(obj, '%Y-%m-%d')
            return obj
        except:
            raise ValueError("Input {obj} value format must be YYYY-MM-DD.")
    
    def _validate_frequency(self, obj):
        self._validate_type_str(obj)
        if obj not in ('daily', 'weekly', 'monthly'):
            raise ValueError("Parameter frequency can only be one of the element of ('daily', 'weekly', 'monthly').")
        else:
            return obj

    def _check_date_logic(self):
        if self.end_date < self.start_date:
            raise ValueError(f"Start date (current value {self.start_date}) must be earlier than end date (current value {self.end_date}).")
    
    def get_stock(self):
        if self._stock is None:
            self._pull_stock()
        return self._stock

    def get_devidend(self):
        if self._dividend is None:
            self._pull_dividend()
        return self._dividend

    def get_split(self):
        if self._split is None:
            self._pull_split()
        return self._split

class AnalyzeRelationship:
    def __init__(self
        ,ticker:str) -> None:
        self.ticker = ticker
        self._f_data = None
        self._s_data = None
        self._load_data()
        
    def _load_data(self):
        fs = FinancialStatementData(self.ticker)
        self.f_data = fs.get_balance_sheet()
        
        sd = StockData(self.ticker)
        self.s_data = sd.get_stock()

    def _analyze(self):
        raise NotImplementedError()

    def plot(self):
        raise NotImplementedError()

class FactPlots:
    def __init__(self
        ,df:pd.DataFrame
        ,datetime_col:str
        ,value_col:str
        ) -> None:
        self._df = self._validate_dtype_df(df)
        self._datetime_col = self._validate_col_in_df(datetime_col)
        self._value_col = self._validate_col_in_df(value_col)

    def _validate_dtype_df(self, obj):
        assert isinstance(obj, pd.DataFrame)
    
    def _validate_col_in_df(self, col:str):
        assert col in self._df.columns

    def _process(self):
        raise NotImplementedError()

    def plot(self):
        raise NotImplementedError()
