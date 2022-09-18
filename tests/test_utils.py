import pytest
from unittest.mock import patch
import pandas as pd
from src.SwiftGrasp.utils import (
    # CheckTicker,
    # FinancialStatementData,
    # StockData,
    # StructuralChange,
    FuzzyMatch,
)


def input_df_comany():
    return pd.DataFrame(
        {
            "Company Name": [
                "American Airlines Group, Inc.",
                "Apple Inc.",
                "Amazon.com, Inc.",
                "Alphabet Inc.",
            ],
            "Ticker": ["AAL", "AAPL", "AMZN", "GOOGL"],
        }
    )


def mock_FuzzyMatch_init(self):
    self.df_company = None
    self.match_by_col = None
    self.list_choices = None


class TestFuzzyMatch:

    input_output_combinations = [
        (
            input_df_comany(),
            [
                "American Airlines Group, Inc.",
                "Apple Inc.",
                "Amazon.com, Inc.",
                "Alphabet Inc.",
            ],
            "Company Name",
            "apple",
            1,
            pd.DataFrame(
                [["Apple Inc.", 90, "AAPL"]],
                columns=["Company Name", "Matching Score", "Ticker"],
            ),
        ),
        (
            input_df_comany(),
            [
                "American Airlines Group, Inc.",
                "Apple Inc.",
                "Amazon.com, Inc.",
                "Alphabet Inc.",
            ],
            "Company Name",
            "airline",
            2,
            pd.DataFrame(
                [
                    ["American Airlines Group, Inc.", 90, "AAL"],
                    ["Apple Inc.", 50, "AAPL"],
                ],
                columns=["Company Name", "Matching Score", "Ticker"],
            ),
        ),
    ]

    @pytest.mark.parametrize(
        "df,list_choices,match_by_col,input_text,num_results,expected_df,",
        input_output_combinations,
    )
    @patch(
        "src.SwiftGrasp.utils.FuzzyMatch.__init__",
        mock_FuzzyMatch_init,
    )
    def test_match(
        self,
        df,
        list_choices,
        match_by_col,
        input_text,
        num_results,
        expected_df,
    ):
        fm = FuzzyMatch()
        fm.df_company = df
        fm.list_choices = list_choices
        fm.match_by_col = match_by_col
        df_res = fm.match(input_text, num_results)
        pd.testing.assert_frame_equal(df_res, expected_df)
