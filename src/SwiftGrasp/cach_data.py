import os
import pickle
import matplotlib.pyplot as plt
from utils import FinancialStatementData, StockData, StructuralChange

cach_folder = "./cached"

frequency_dict = {
    "Q": "quarterly",
    "Y": "annual",
}


def load_data(filename: str):
    with open(os.path.join(cach_folder, f"{filename}.p"), "rb") as pf:
        obj = pickle.load(pf)
    return obj


def get_fsd(ticker, frequency: str = "Q"):
    fname = f"fsd_{ticker}_{frequency}"

    if os.path.exists(os.path.join(cach_folder, f"{fname}.p")):
        fsd = load_data(fname)
    else:
        fsd = FinancialStatementData(  # fmt: off
            ticker, frequency_dict.get(frequency)  # fmt: off
        )
        with open(os.path.join(cach_folder, f"{fname}.p"), "wb") as pf:
            pickle.dump(fsd, pf, protocol=4)

    return fsd


def get_stock(ticker, fsd):
    df_financial = fsd.get_all_data()

    sd = StockData(ticker)
    df_stock = sd.get_stock()

    df_stock = df_stock.loc[:, [fsd._colname_date, "close"]]

    df_stock_fill = (
        df_stock.drop_duplicates(subset=fsd._colname_date, keep="last")
        .set_index(fsd._colname_date)
        .sort_index()
    )
    df_stock_fill = df_stock_fill.resample("D").fillna("nearest")

    change_dt_list = (
        df_financial[fsd._colname_date]  # fmt: off
        .dt.strftime("%Y-%m-%d")
        .to_list()  # fmt: off
    )  # fmt: off

    return df_stock_fill, change_dt_list


def cach_struc_chg(
    ticker,  # fmt: off
    df_stock_fill,  # fmt: off
    change_dt_list,  # fmt: off
    frequency: str = "Q",  # fmt: off
):
    sc = StructuralChange(df_stock_fill, change_dt_list)
    sc.analyze()

    # save summary
    fname = f"struc_change_{ticker}_{frequency}_summary"
    with open(os.path.join(cach_folder, f"{fname}.p"), "wb") as pf:
        pickle.dump(sc._df_summary, pf, protocol=4)

    # save plots
    for td in sc._ci_dict.keys():
        ci_select = sc._ci_dict.get(td)
        ci_select.plot(show=False)
        fig = plt.gcf()

        fname = f"struc_change_{ticker}_{frequency}_fig{td}"
        with open(os.path.join(cach_folder, f"{fname}.p"), "wb") as pf:
            pickle.dump(fig, pf, protocol=4)


if __name__ == "__main__":
    for ticker in ("AAPL", "AMZN"):
        frequency = "Y"

        fsd = get_fsd(ticker, frequency)
        df_stock_fill, change_dt_list = get_stock(ticker, fsd)
        cach_struc_chg(ticker, df_stock_fill, change_dt_list, frequency)
