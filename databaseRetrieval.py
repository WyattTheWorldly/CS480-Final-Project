from flask import current_app
from extensions import db, create_session
from getData import fetch_and_store_company_overview_data, fetch_and_store_time_series_daily_data, fetch_and_store_time_series_intraday_data, is_data_up_to_date
from getData import CompanyInformation, FinancialMetrics, TimeSeriesDailyData, TimeSeriesIntraDayData
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# This file is for functions that have to do with retrieving data from the database

def get_data_by_symbol(symbol, table):
    session = create_session()
    try:
        # Retrieve entries for the table that match the given symbol
        return session.query(table).filter_by(symbol=symbol).all()
    except SQLAlchemyError as e:
        print(f"Database error for {symbol}: {str(e)}")
        return None
    finally:
        session.close()

# Function to get company overview from the database by symbol. This function also
#  calls the fetch_and_store_stock_data function if the data is not up-to-date.
def get_company_overview(symbol):
    with current_app.app_context():
        # Fetch and update overview data
        fetch_and_store_company_overview_data(symbol)
        # Get the company overview data from the database
        return get_data_by_symbol(symbol, CompanyInformation)[0]
        
# Function to get financial metrics from the database by symbol. This function also
#  calls the fetch_and_store_stock_data function if the data is not up-to-date.
def get_financial_metrics(symbol):
    with current_app.app_context():
        # Fetch and update financial metrics data
        fetch_and_store_company_overview_data(symbol)
        # Get the financial metrics data from the database
        return get_data_by_symbol(symbol, FinancialMetrics)[0]
        
# Function to get the daily time series from the database by symbol. This function 
#  also calls the fetch_and_store_stock_data function if the data is not up-to-date.
def get_daily_time_series(symbol):
    with current_app.app_context():
        # Fetch and update overview data
        fetch_and_store_time_series_daily_data(symbol)
        # Get the daily time series data from the database
        return get_data_by_symbol(symbol, TimeSeriesDailyData)
        
# Function to get the intraday time series from the database by symbol.
def get_intraday_time_series(symbol):
    with current_app.app_context():
        # Fetch and update overview data
        fetch_and_store_time_series_intraday_data(symbol)
        # Get the intraday time series data from the database
        return get_data_by_symbol(symbol, TimeSeriesIntraDayData)