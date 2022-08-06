# SwiftGrasp

A web app to help you quickly digest the key financial statement information and the stock performance for a publicly traded company.

## Completed
* Functionality to input ticker by pre set dropdown list
* Functionality to input ticker by text input
* Functionality to check whether ticker is valid
* Functionlity to pull the financial statement data
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
* Functionality to perform causual inference of whether there're statistical significant change by the statement posting date, achieved by Bayesian structural time series model.
* Front end interface by streamlit, deployed locally.
## ToDo
* Need to create an auto system to calculate/update the structural baysesian time series.
* ^Maybe create a database to store some calculated data will be helpful to the first bullet point.
* Add analytic support for financial statement date (hopefully find more data).
* Deploy to Heroku.