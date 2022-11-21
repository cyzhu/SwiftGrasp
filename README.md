# SwiftGrasp

A web app to help you quickly digest the key financial statement information and the stock performance for a publicly traded company.

Notes: this is my graduation applied project for my master's program in Computer and Information Sciences major from Harrisburg University.

## Installation Guide
1. Install `poetry` if you don't have it yet
```
pip install poetry
```
Or, install as in the official website of Poetry.

2. Make sure that you're on the `base` environment if not already, you can do the command below to get to the `base` environment if you're on some other conda environment
```
conda deactivate
```
3. Create a new conda environment
```
conda create -n swift python=3.9
```
4. Activate the environment you just created
```
conda activate swift
```
5. Navigate to the unzipped `SwiftGraspWebApp` folder
```
cd ~/your/path/to/SwiftGraspWebApp
```
6. Install the dependencies by poetry
```
poetry install
```
7. Run the web app locally by
```
streamlit run src/SwiftGrasp/app.py
```

Now you should be able to see the web app up and running locally with the URL displayed on the terminal.

## Testing
After making changes to the code, run below lines from the main directory.
```
python -m pytest --cov=src tests/
```

## Project Status
### Completed
* Functionality to input ticker by pre set dropdown list
* Functionality to input ticker by text input
* Functionality to check whether ticker is valid
* Functionality to pull the financial statement data
  * Balance sheet
  * Income statement
  * Cash statement
* Functionality to pull the stock data
* Interactive plots
  * Wheel zoom (in/out) for plots
  * Reset plot
  * Drag plot
  * Input of what columns are of user's interest
  * Input of time range for data pulling and relationship calculation
* Functionality to perform causal inference of whether there're statistical significant change by the statement posting date, achieved by Bayesian structural time series model.
* Front end interface by streamlit, deployed locally.
* Consider adding fuzzy match feature on user text input.
* Add unit tests.
* Improved structural change load speed.
* Deployed to streamlit cloud: [https://swiftgrasp.streamlit.app/](https://swiftgrasp.streamlit.app/)
* Create a database to store some calculated data will be helpful to the first bullet point.

### ToDo
* Set up cron jobs to calculate/update the structural baysesian time series.

## Project structure
```
SwiftGraspWebApp
├─ .flake8
├─ .gitignore
├─ .pre-commit-config.yaml
├─ .streamlit
│  └─ secrets.toml
├─ .vscode
│  └─ launch.json
├─ README.md
├─ cached
│  ├─ fig_struc_change_AAPL_Q_2021-09-25.png
│  ├─ fig_struc_change_AAPL_Q_2021-12-25.png
│  ├─ fig_struc_change_AAPL_Q_2022-03-26.png
│  ├─ fig_struc_change_AAPL_Q_2022-06-25.png
│  ├─ fig_struc_change_AAPL_Q_2022-09-24.png
│  ├─ fig_struc_change_AAPL_Y_2020-09-26.png
│  ├─ fig_struc_change_AAPL_Y_2021-09-25.png
│  ├─ fig_struc_change_AAPL_Y_2022-09-24.png
│  ├─ fig_struc_change_AMZN_Q_2021-12-31.png
│  ├─ fig_struc_change_AMZN_Q_2022-03-31.png
│  ├─ fig_struc_change_AMZN_Q_2022-06-30.png
│  ├─ fig_struc_change_AMZN_Q_2022-09-30.png
│  ├─ fig_struc_change_AMZN_Y_2019-12-31.png
│  ├─ fig_struc_change_AMZN_Y_2020-12-31.png
│  ├─ fig_struc_change_AMZN_Y_2021-12-31.png
│  ├─ fig_struc_change_BILI_Q_2021-09-30.png
│  ├─ fig_struc_change_BILI_Q_2021-12-31.png
│  ├─ fig_struc_change_BILI_Q_2022-03-31.png
│  ├─ fig_struc_change_BILI_Q_2022-06-30.png
│  ├─ fig_struc_change_BILI_Y_2019-12-31.png
│  ├─ fig_struc_change_BILI_Y_2020-12-31.png
│  ├─ fig_struc_change_BILI_Y_2021-12-31.png
│  ├─ fig_struc_change_GOOGL_Q_2021-12-31.png
│  ├─ fig_struc_change_GOOGL_Q_2022-03-31.png
│  ├─ fig_struc_change_GOOGL_Q_2022-06-30.png
│  ├─ fig_struc_change_GOOGL_Q_2022-09-30.png
│  ├─ fig_struc_change_GOOGL_Y_2019-12-31.png
│  ├─ fig_struc_change_GOOGL_Y_2020-12-31.png
│  ├─ fig_struc_change_GOOGL_Y_2021-12-31.png
│  ├─ fig_struc_change_MSFT_Q_2021-12-31.png
│  ├─ fig_struc_change_MSFT_Q_2022-03-31.png
│  ├─ fig_struc_change_MSFT_Q_2022-06-30.png
│  ├─ fig_struc_change_MSFT_Q_2022-09-30.png
│  ├─ fig_struc_change_MSFT_Y_2020-06-30.png
│  ├─ fig_struc_change_MSFT_Y_2021-06-30.png
│  ├─ fig_struc_change_MSFT_Y_2022-06-30.png
│  ├─ fsd_AAPL_Q.p
│  ├─ fsd_AAPL_Y.p
│  ├─ fsd_AMZN_Q.p
│  ├─ fsd_AMZN_Y.p
│  ├─ fsd_BILI_Q.p
│  ├─ fsd_BILI_Y.p
│  ├─ fsd_GOOGL_Q.p
│  ├─ fsd_GOOGL_Y.p
│  ├─ fsd_MSFT_Q.p
│  ├─ fsd_MSFT_Y.p
│  ├─ struc_change_AAPL_Q_summary.p
│  ├─ struc_change_AAPL_Y_summary.p
│  ├─ struc_change_AMZN_Q_summary.p
│  ├─ struc_change_AMZN_Y_summary.p
│  ├─ struc_change_BILI_Q_summary.p
│  ├─ struc_change_BILI_Y_summary.p
│  ├─ struc_change_GOOGL_Q_summary.p
│  ├─ struc_change_GOOGL_Y_summary.p
│  ├─ struc_change_MSFT_Q_summary.p
│  └─ struc_change_MSFT_Y_summary.p
├─ notebooks
├─ poetry.lock
├─ pyproject.toml
├─ setup.py
├─ src
│  └─ SwiftGrasp
│     ├─ __init__.py
│     ├─ app.py
│     ├─ cach_data.py
│     ├─ plot_helper.py
│     ├─ preprocess_listing.py
│     ├─ resources
│     │  ├─ fuzzy_match.p
│     │  ├─ nasdaq-listed.csv
│     │  ├─ nyse-listed.csv
│     │  ├─ other-listed.csv
│     │  └─ processed_company_names.csv
│     ├─ save_to_db.py
│     └─ utils.py
└─ tests
   └─ test_utils.py
```

## Reference
* NASDAQ listing data source: https://github.com/datasets/nasdaq-listings
* NYSE and other listing data sources: https://github.com/datasets/nyse-other-listings

