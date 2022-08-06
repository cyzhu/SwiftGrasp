import datetime
from tracemalloc import start
from typing import Union, List
import pandas as pd
import numpy as np
from yahoofinancials import YahooFinancials
from dateutil.relativedelta import relativedelta
import warnings

from causalimpact import CausalImpact


class CheckTicker:
    """
    A class to check whether the input ticker has the correct data
    type and whether it's a valid ticker that can be used to 
    retrieve financial statement data and/or stock data.

    It also has the functionality to get the ticker's first trade 
    date if the ticker is valid and has stock data.

    Parameters
    ----------
    ticker : str
        The input ticker object to be validated on.
    type : str, optional
        A parameter to specify what types of validation that the 
        ticker will be checked. It can only be "statement",
        "stock" or "both". 
        If "statement", it'll check whether the ticker has 
        financial statement data.
        If "stock", it will check whether the ticker has the
        stock price data.
        If "both", it will check whether it has financial
        statement data and also check for stock data.
        By default "statement".

    Examples
    --------
    Check whether the ticker is valid and has financial
    statement data:

    >>> ticker = 'AAPL'
    >>> ct = CheckTicker(ticker)
    >>> ct.has_statement
    True

    Note that the parameter has_stock would be False
    but that's not necessarily mean that the ticker
    does not have stock data. It's just unchecked.

    Check whether the ticker is valid and has the
    financial statement data and/or the stock data.

    >>> ticker = '^GSPC'
    >>> ct = CheckTicker(ticker, type = 'both')
    >>> ct.has_statement
    False
    >>> ct.has_stock
    True

    You can also get the first trade date of the
    ticker:
    >>> ct.get_first_trade_date()
    '1927-12-30'
    """
    def __init__(self, ticker:str, type:str = 'statement') -> None:
        self.ticker = ticker
        self._yf = None
        
        self.first_trade_date = None
        
        self.has_statement:bool = False
        self.has_stock:bool = False
        
        self._today_prices = None
        self._validate(type)

    def _validate_dtype_str(self):
        """
        Validate the data type of the input ticker object.

        Raises
        ------
        TypeError
            * If the input is not string type
        """
        if not isinstance(self.ticker, str):
            raise TypeError("Ticker has to be string type.")
    
    def _validate_statement(self):
        """
        Check whether the ticker has financial statement data.
        """
        _tst = self._yf.get_financial_stmts(
            frequency = 'Quarterly', 
            statement_type = 'income'
            )
        if list(_tst.values())[0][self.ticker] is not None:
            self.has_statement = True

    def _validate_stock(self):
        """
        Check whether the ticker has stock price data.
        """
        today = datetime.datetime.today()
        days_ago = today - relativedelta(days=8)
        self._today_prices = self._yf.get_historical_price_data(
            days_ago.strftime('%Y-%m-%d'), 
            today.strftime('%Y-%m-%d'), 
            'weekly'
            )
        
        #?? In what circumstances will eventsData is the only key 
        # and there're some data in eventsData? because if no 
        # circumstances like that, won't need the latter condition
        if len(self._today_prices[self.ticker].keys()) > 1 or \
            len(self._today_prices[self.ticker]['eventsData'])>0 :
            self.has_stock = True
        
    def _validate(self, type:str):
        """
        Main function to check whether the ticker input
        is correct data type, and if so, whether it's 
        valid and has financial statement data and/or
        stock price data.

        Parameters
        ----------
        type : str
            A parameter to specify what types of validation that the 
            ticker will be checked. It can only be "statement",
            "stock" or "both". 
            If "statement", it'll check whether the ticker has 
            financial statement data.
            If "stock", it will check whether the ticker has the
            stock price data.
            If "both", it will check whether it has financial
            statement data and also check for stock data.
            By default "statement".

        Raises
        ------
        ValueError
            If the parameter 'type' is not one of the value of 
            'statement','stock','both'.
        """
        self._validate_dtype_str()
        
        self._yf = YahooFinancials(self.ticker)

        if type == 'statement' or type == 'both':
            self._validate_statement()
        if type == 'stock' or type == 'both':
            self._validate_stock()
        if type not in ('statement','stock','both'):
            raise ValueError("Parameter type can only be \
                'statement', 'stock' or 'both'.")
        #ToDo [future]: check whether ticker already in the databse

    def _pull_first_trade_date(self):
        """
        Pull the first trade date if the ticker has stock 
        prices data.
        """
        if self._today_prices is None:
            self._validate(type='stock')
        if self.has_stock is True:
            self.first_trade_date = self._today_prices[
                self.ticker
                ]['firstTradeDate']['formatted_date'] 
        
    def get_first_trade_date(self):
        """
        Get the first trade date of this ticker.

        Returns
        -------
        str or None
            If the ticker has stock data, then it'll
            return a string in the format of 
            YYYY-MM-DD.
            If the ticker doesn't have stock data,
            it'll return None.
        """
        if self.first_trade_date is None:
            self._pull_first_trade_date()
        
        return self.first_trade_date

class FinancialStatementData:
    """
    Main class to pull and format the financial statement data,
    including balance sheet, income statement, and cash flow 
    statement data.

    Parameters
    ----------
    ticker : str
        A string that represents the ticker of the company.
    frequency : Union[str,None], optional
        The frequency of the financial statement data, it can only
        be either 'quarterly' or 'annual' or None.
        By default None. If None, it will be 'quarterly'.

    Examples
    --------
    Pull the quarterly balance sheet dataframe:

    >>> ticker = 'AAPL'
    >>> fsd = FinancialStatementData(ticker)
    >>> df1 = fsd.get_balance_sheet()

    Get the income statement dataframe:
    >>> df2 = fsd.get_income_statement()

    Get the cash flow statement dataframe:
    >>> df3 = fsd.get_cash_statement()

    Get the merged dataframe that has all financial statement data:

    >>> df4 = fsd.get_all_data()

    Pull the annual financial statement data of all:

    >>> ticker = 'AMZN'
    >>> fsd = FinancialStatementData(ticker, frequency = 'annual')
    >>> df = fsd.get_all_data()
    """
    __table_prefix_dict__ = {
        'balance':'balanceSheet'
        ,'income':'incomeStatement'
        ,'cash':'cashflowStatement'
        }
    
    def __init__(self
        ,ticker:str
        ,frequency:Union[str,None] = None
        ) -> None:
        ct = CheckTicker(ticker, type = 'statement')
        if ct.has_statement:
            self.ticker = ticker
        else:
            raise ValueError(f"This ticker {ticker} doesn't have \
                financial statement data in sources.")
        
        self.frequency = self._validate_input_frequency(frequency)
        self._balance = None
        self._income = None
        self._cash = None
        self._df_merge = None
        self._colname_date = 'formatted_date'
        
        self._yf = ct._yf
        
        self._pull_data()
        self._merge_data()
        
    def _pull_data(self):
        """
        A wrapper function to pull the balance sheet, the income
        statement, and the cash flow statement data.
        """
        self._balance = self._format_financial_data('balance')
        self._income = self._format_financial_data('income')
        self._cash = self._format_financial_data('cash')
    
    def _merge_data(self):
        """
        Process the duplicated columns from the financial dataframes
        and merge them into one dataframe.
        """
        self._income = self._drop_dup(self._balance, self._income)
        self._cash = self._drop_dup(self._balance, self._cash)
        self._cash = self._drop_dup(self._income, self._cash)

        self._df_merge = self._balance.merge(
            self._income, 
            on=self._colname_date, 
            how='outer'
            )
        self._df_merge = self._df_merge.merge(
            self._cash, 
            on=self._colname_date, 
            how='outer'
            )
        
    def _drop_dup(self, df1:pd.DataFrame, df2:pd.DataFrame):
        """
        Functionality to drop the duplicated columns given by the
        two input dataframes.

        Only the second dataframe will drop the duplicated columns.

        Parameters
        ----------
        df1 : pd.DataFrame
            The first dataframe to check the duplicated columns with
            the second dataframe.
        df2 : pd.DataFrame
            The second dataframe to check the duplicated columns with
            the first dataframe.

        Returns
        -------
        pd.DataFrame
            The second dataframe that dropped the duplicated columns,
            if there're any.
        """
        dup_list = list(set(df1.columns) & set(df2.columns))
        
        if len(dup_list)>1:
            cols = [i for i in dup_list if i != self._colname_date]
            return df2.drop(cols, axis=1)
        else:
            return df2

    def _get_table_suffix(self):
        """
        Generate the suffix of the json key name.

        The quarterly financial statement data json object usually
        has 'Quarterly' suffix in its json keys, whereas the annual
        financial statement data json object usually wouldn't have
        any suffix to indicate the frequency in the json keys.

        Returns
        -------
        str
            Suffix of the financial data json object keys.
        """
        if self.frequency == 'quarterly':
            return 'Quarterly'
        else:
            # if 'annual'
            return ''

    def _get_json_header_name(self, abbr:str):
        """
        Compile the full json header name, given by what type of
        financial data it is (i.e., 'balance', 'income', 'cash'),
        and by the frequency of the financial statement data (i.e.,
        quarterly or annual).

        Parameters
        ----------
        abbr : str
            The abbreviation of what type of the financial statement
            data it it, it can only be one of the keys of 
            self.__table_prefix_dict__

        Returns
        -------
        str
            The full json header name
        """
        if abbr in self.__table_prefix_dict__.keys():
            suf = self._get_table_suffix()
            return self.__table_prefix_dict__.get(abbr)+'History'+suf
    
    def _format_financial_data(self, abbr:str):
        """
        Pull the financial statement data from YahooFinancials
        and format the raw json data format to be the desired
        pandas dataframe output.

        Parameters
        ----------
        abbr : str
            The abbreviation of what type of the financial statement
            data it it, it can only be one of the keys of 
            self.__table_prefix_dict__

        Returns
        -------
        pd.DataFrame
            A pandas dataframe that has the corresponding financial
            statement data.
        """
        jsn = self._yf.get_financial_stmts(frequency = self.frequency, statement_type = abbr)

        result_list = []
        header = self._get_json_header_name(abbr)
        obj = jsn[header][self.ticker]
        for i in range(len(obj)):
            df_temp = pd.DataFrame(obj[i].values(), index = obj[i].keys()).reset_index()
            
            df_temp.rename(columns={'index':self._colname_date}, inplace=True)
            df_temp[self._colname_date] = pd.to_datetime(df_temp[self._colname_date])
            result_list.append(df_temp)

        return pd.concat(result_list)

    @staticmethod
    def _validate_input_frequency(obj):
        """
        Validate the input frequency parameter.
        
        It should be either None or str type.
        If None, it will be 'quarterly'.
        If it's str type, it can only be either 'annual' or
        'quarterly'.

        Parameters
        ----------
        obj : Any
            The input object to be validated on.
            Here specifically it's the 'frequency' parameter.

        Returns
        -------
        str
            The validated frequency parameter if the input object
            is valid.

        Raises
        ------
        TypeError
            * If the input is not None and it's not str type.
        ValueError
            * If the input is str type but is neither 'quarterly' 
              nor 'annual'
        """
        if obj is None:
            return "quarterly"
        elif not isinstance(obj, str):
            raise TypeError("Input needs to be either None or String type.")
        elif obj in ('annual','quarterly'):
            return obj
        else:
            return ValueError("The input string has to be either 'quarterly or 'annual'.")
    
    def get_balance_sheet(self):
        """
        Get the dataframe that contains the balance sheet data.

        Returns
        -------
        pd.DataFrame
            A dataframe that contains the balance sheet data.
        """
        return self._balance
    
    def get_income_statement(self):
        """
        Get the dataframe that contains the income statement data.

        Returns
        -------
        pd.DataFrame
            A dataframe that contains the income statement data.
        """
        return self._income
    
    def get_cash_statement(self):
        """
        Get the dataframe that contains the cash flow statement 
        data.

        Returns
        -------
        pd.DataFrame
            A dataframe that contains the cash flow statement 
            data.
        """
        return self._cash

    def get_all_data(self):
        """
        Get the dataframe that contains all the financial statement 
        data, including balance sheet, income statement, and cash
        flow statement data.

        Returns
        -------
        pd.DataFrame
            A dataframe that contains all the financial statement 
            data.
        """
        return self._df_merge

class StockData:
    def __init__(self
        ,ticker:str
        ,start_date:Union[str, None] = None
        ,end_date:Union[str, None] = None
        ,frequency:Union[str, None] = None
        ) -> None:
        
        ct = CheckTicker(ticker, type='stock')
        if ct.has_stock:
            self.ticker = ticker
        else:
            raise ValueError(f"This ticker {ticker} doesn't have \
                stock data in sources.")
        
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
            self.start_date = max(
                three_yrs_ago.strftime('%Y-%m-%d'), 
                self.first_trade_date
                )
        else:
            self.start_date = max(
                self._validate_date(start_date), 
                self.first_trade_date
                )

        self._check_date_logic()

        self._stock_obj = None
        self._set_obj()
        
        self._stock = None
        self._dividend = None
        self._split = None
        self._colname_date = 'formatted_date'

    def _set_obj(self):
        self._stock_obj = self._yf.get_historical_price_data(
            self.start_date, 
            self.end_date, 
            self.frequency
            )

    def _pull_stock(self):
        self._stock = pd.DataFrame(
            self._stock_obj[self.ticker]['prices']
            )
        self._stock[self._colname_date] = pd.to_datetime(
            self._stock[self._colname_date]
            )
        #ToDo: down cast float64 to float32
    
    def _pull_dividend(self):
        self._dividend = pd.DataFrame(self._stock_obj[self.ticker]['eventsData']['dividends']).transpose()
        self._dividend[self._colname_date] = pd.to_datetime(self._dividend[self._colname_date])
        self._dividend['amount'] = self._dividend['amount'].astype(np.float32)

    def _pull_split(self):
        if len(self._stock_obj[self.ticker]['eventsData']['splits'])>0:
            self._split = pd.DataFrame(self._stock_obj[self.ticker]['eventsData']['splits']).transpose()
            self._split[self._colname_date] = pd.to_datetime(self._split[self._colname_date])
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

class StructuralChange:
    def __init__(self
        ,df:pd.DataFrame
        ,possible_date_list:List[str]
        ) -> None:
        self._df = _validate_dtype_df(df)
        #ToDo: check df index as datetime
        #ToDo: check date list is list of str
        #?? Do I want to make sure that df only has one column?
        self.possible_date_list = possible_date_list

        self._df_index_min = self._df.index.min().strftime("%Y-%m-%d")
        self._df_index_max = self._df.index.max().strftime("%Y-%m-%d")

        self._df_summary= None

        self._ci_dict = {}
        
    #     self._load_data()
        
    # def _load_data(self):
    #     fs = FinancialStatementData(self.ticker)
    #     self._f_data = fs.get_balance_sheet()
        
    #     sd = StockData(self.ticker)
    #     self.s_data = sd.get_stock()
    
    def _analyze_one_date(self, dt:str):
        dt_m1 = (datetime.datetime.strptime(dt, '%Y-%m-%d') - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        if self._df_index_min < dt_m1 and self._df_index_max>dt:
            pre_period=[self._df_index_min, dt_m1]
            post_period=[dt, self._df_index_max]

            ci = CausalImpact(self._df, pre_period, post_period)
            self._ci_dict[dt] = ci

            res = ci.summary_data.loc[:,'average'].T
            res['p-value'] = ci.p_value
            res['change_date'] = dt
            return res
        else:
            return None

    def analyze(self):
        res_list = []
        for dt in self.possible_date_list:
            res = self._analyze_one_date(dt)
            if res is not None:
                res_list.append(res)

        self._df_summary = pd.concat(res_list, axis=1).T.set_index('change_date')

    def plot(self, dt:str, show:bool = True):
        self._ci_dict[dt].plot(show = show)


def _validate_dtype_df(obj):
    if not isinstance(obj, pd.DataFrame):
        raise TypeError(f"Input needs to be pandas DataFrame object. Received {type(obj)} instead.")
    else:
        return obj