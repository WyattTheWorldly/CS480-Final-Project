from flask import (current_app, jsonify)
from sqlalchemy.exc import (IntegrityError, SQLAlchemyError)
from sqlalchemy import (func, extract, desc)
import datetime
from extensions import (db, create_session)
from getData import (fetch_and_store_company_overview_data, fetch_and_store_time_series_daily_data, fetch_and_store_time_series_intraday_data, is_data_up_to_date)
from models import (OverviewData, TimeSeriesDailyData, TimeSeriesIntraDayData, AverageWeeklyDailyData, AverageMonthlyDailyData, AverageYearlyDailyData)
from dailyTimeSeriesCalculations import (update_average_daily_data)

# This file is for functions that have to do with retrieving data from the database

def get_data_by_symbol(symbol, table):
    # Create a new database session
    session = create_session()
    try:
        if table == OverviewData:
            # Retrieve entries for the table that match the given symbol
            results = session.query(table).filter_by(symbol=symbol).all()
            print(f"Data successfully retrieved from {table} for {symbol}.")
            return results
        elif table == TimeSeriesIntraDayData:
            results = session.query(table).filter_by(symbol=symbol).order_by(table.datetime.asc()).all()
            print(f"Data successfully retrieved from {table} for {symbol}.")
            return results
        
        else:
            # Retrieve entries for the table that match the given symbol and sort by date
            results = session.query(table).filter_by(symbol=symbol).order_by(table.date.asc()).all()
            print(f"Data successfully retrieved from {table} for {symbol}.")
            return results

    except SQLAlchemyError as e:
        print(f"Database error for {symbol}: {str(e)}")
        return None

    finally:
        session.close()

# Function to get company overview from the database by symbol. This function also
# calls the fetch_and_store_stock_data function if the data is not up-to-date.
def get_company_overview(symbol):
    with current_app.app_context():
        # Fetch and update overview data
        fetch_and_store_company_overview_data(symbol)
        # Get the company overview data from the database
        return get_data_by_symbol(symbol, OverviewData)[0]

# Function to get the daily time series from the database by symbol. This function
# also calls the fetch_and_store_stock_data function if the data is not up-to-date.
def get_daily_time_series(symbol):
    with current_app.app_context():
        # Fetch and update overview data
        fetch_and_store_time_series_daily_data(symbol)
        # Get the daily time series data from the database
        data = get_data_by_symbol(symbol, TimeSeriesDailyData)
        # Convert each item in the data to a dictionary
        return [timeseries_data_to_dict(item) for item in data]

# Function to get the intraday time series from the database by symbol.
def get_intraday_time_series(symbol):
    with current_app.app_context():
        # Fetch and update overview data
        fetch_and_store_time_series_intraday_data(symbol)
        # Get the intraday time series data from the database
        data = get_data_by_symbol(symbol, TimeSeriesIntraDayData)
        # Convert each item in the data to a dictionary
        return [timeseries_data_to_dict(item) for item in data]

# Function to retrieve the calculated weekly averages using the TimeSeriesDailyData set
# from the AverageWeeklyDailyData table
def get_average_weekly_daily_data(symbol):
    # Check to see that data is up to date, and update it if it is not,
    # before it is retrieved
    update_average_daily_data(symbol, AverageWeeklyDailyData)
    # Get the weekly daily averages data from the database
    data = get_data_by_symbol(symbol, AverageWeeklyDailyData)
    # Convert each item in the data to a dictionary
    return [timeseries_data_to_dict(item) for item in data]

# Function to retrieve the calculated monthly averages using the TimeSeriesDailyData set
# from the AverageMonthlyMonthlyData table
def get_average_monthly_daily_data(symbol):
    # Check to see that data is up to date, and update it if it is not,
    # before it is retrieved
    update_average_daily_data(symbol, AverageMonthlyDailyData)
    # Get the monthly daily averages data from the database
    data = get_data_by_symbol(symbol, AverageMonthlyDailyData)
    # Convert each item in the data to a dictionary
    return [timeseries_data_to_dict(item) for item in data]

# Function to retrieve the calculated yearly averages using the TimeSeriesDailyData set
# from the AverageYearlyDailyData table
def get_average_yearly_daily_data(symbol):
    # Check to see that data is up to date, and update it if it is not,
    # before it is retrieved
    update_average_daily_data(symbol, AverageYearlyDailyData)
    # Get the yearly daily averages data from the database
    data = get_data_by_symbol(symbol, AverageYearlyDailyData)
    # Convert each item in the data to a dictionary
    return [timeseries_data_to_dict(item) for item in data]

def timeseries_data_to_dict(data):
    try:
        # Determine the correct date attribute based on the data's class
        date_field = 'datetime' if isinstance(data, TimeSeriesIntraDayData) else 'date'
        date_value = getattr(data, date_field)

        # Convert date to UNIX timestamp, use 0 if missing
        unix_timestamp = int(date_value.timestamp()) if date_value else 0

        # Set default values for other fields if they are missing
        return {
            "symbol": data.symbol,
            "date": unix_timestamp,
            "open_price": data.open_price if data.open_price is not None else 0,
            "high_price": data.high_price if data.high_price is not None else 0,
            "low_price": data.low_price if data.low_price is not None else 0,
            "close_price": data.close_price if data.close_price is not None else 0,
            "volume": data.volume if data.volume is not None else 0,
            "timestamp": data.timestamp.strftime("%Y-%m-%d %H:%M:%S") if data.timestamp else 'N/A'
        }
    
    except AttributeError as e:
        print(f"Attribute error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


