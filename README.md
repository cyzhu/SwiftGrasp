# SwiftGrasp

A web app to help you quickly digest the key financial statement information and the stock performance for a publicly traded company.

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

### ToDo
* Need to create an auto system to calculate/update the structural baysesian time series.
* ^Maybe create a database to store some calculated data will be helpful to the first bullet point.
* Add analytic support for financial statement date (hopefully find more data).
* Deploy to Heroku.
* Add unit tests.

## Project structure

```
SwiftGraspWebApp
├─ .flake8
├─ .gitignore
├─ .pre-commit-config.yaml
├─ README.md
├─ README.pdf
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
