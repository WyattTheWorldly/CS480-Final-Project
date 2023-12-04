import datetime
import pandas as pd
from alpha_vantage.fundamentaldata import FundamentalData
from alpha_vantage.timeseries import TimeSeries
from flask import current_app
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from extensions import create_session
from models import OverviewData, TimeSeriesDailyData, TimeSeriesIntraDayData

# This file is for retrieving data from the API
# and creating and updating table entries

# Key that allows access to API
API_key = 'N8LVC6JOGADHP6RE'

# Alernate API keys
# API_key = 'E9HF2DALRYZKAIJC'
# API_key = 'QEFVQOMF9QYHO5D8'
# API_key = 'XYSQVCSGU04NSAVY'
# API_key = 'OPTLDARI9EHVIFD9'
# API_key = 'OZXGSCWUKIBQFGCV'


# Global variable to keep track of API calls
api_call_count = 0

def track_api_call():
    global api_call_count
    api_call_count += 1

    # Print warning messages at specific thresholds
    if api_call_count == 10:
        print("Warning: Only 15 API calls remaining.")
    elif api_call_count == 20:
        print("Warning: Only 5 API calls remaining.")

# Function that validates the field value against the expected data type.
# Returns None if the value is NaN
# Converts value to expected type if it isn't already.
def validate_field(value, expected_type):
    # Handle null or empty string values
    if value is None or pd.isnull(value) or value == '':
        return None

    # If the value is already of the expected type, return it as-is
    if isinstance(value, expected_type):
        return value

    # Ensure expected_type is a tuple for consistency in processing
    if not isinstance(expected_type, tuple):
        expected_type = (expected_type,)

    # Conversion for string values
    if isinstance(value, str):
        # Handling conversion to numeric types (int or float)
        if int in expected_type or float in expected_type:
            try:
                # Try converting to int first
                return int(value)
            except ValueError:
                try:
                    # If int conversion fails, try converting to float
                    return float(value)
                except ValueError:
                    pass

        # Handling conversion to datetime types
        elif datetime.datetime in expected_type or datetime.date in expected_type:
            try:
                return datetime.datetime.strptime(value, '%Y-%m-%d')
            except ValueError:
                pass

    # Conversion for numeric values to string
    elif isinstance(value, (int, float)) and str in expected_type:
        return str(value)

    # Conversion from datetime.date to datetime.datetime
    elif isinstance(value, datetime.date) and datetime.datetime in expected_type:
        return datetime.datetime.combine(value, datetime.time())

    # If conversion is not successful or not applicable, print error and return None
    print(f"Type mismatch or conversion error. Value: {value}, Expected Type: {expected_type}")
    return None

# Functions to get stock data from the AlphaVantage API
# Retrieves data from Company Overview data
def get_stock_ov_data(symbol):
    track_api_call()

    # Create an AlphaVantage client
    ov = FundamentalData(key=API_key, output_format='pandas')

    # Retrieve company overview data from the given symbol
    data, meta_data = ov.get_company_overview(symbol=symbol)

    return data, meta_data

# Retrieves Time Series Daily data
def get_daily_time_series_data(symbol):
    track_api_call()

    # Create an AlphaVantage client
    ts = TimeSeries(key=API_key, output_format='pandas')

    # Retrieve full daily time series data for the given symbol
    data, meta_data = ts.get_daily(symbol=symbol, outputsize='full')

    return data, meta_data

# Retrieves Time Series Intraday data
def get_intraday_time_series_data(symbol, interval='5min'):
    track_api_call()

    # Create an AlphaVantage client
    ts = TimeSeries(key=API_key, output_format='pandas')

    # Retrieve intraday time series data for the given symbol
    data, meta_data = ts.get_intraday(symbol=symbol, interval=interval, outputsize='full')

    return data, meta_data

# Function to update a table entry with new data
# Creates and updates entries on the CompanyInformation and FinancialMetrics table,
# as they are both store data from the same API call
def update_table_entry_ov(symbol, data):
    
    print(f"Starting update to the OverviewData table for {symbol}.")
    
    # Create a new database session
    session = create_session()

    try:
        # Check to see if entry already exists for symbol
        entry = session.query(OverviewData).filter_by(symbol=symbol).first()

        # If entry for symbol does not already exist, create a new one
        if not entry:
            entry = OverviewData(symbol=symbol)
            session.add(entry)

        # Update fields specific to OverviewData
        entry.name                          = validate_field(data['Name'].iloc[0], str)
        entry.description                   = validate_field(data['Description'].iloc[0], str)
        entry.asset_type                    = validate_field(data['AssetType'].iloc[0], str)
        entry.exchange                      = validate_field(data['Exchange'].iloc[0], str)
        entry.currency                      = validate_field(data['Currency'].iloc[0], str)
        entry.country                       = validate_field(data['Country'].iloc[0], str)
        entry.sector                        = validate_field(data['Sector'].iloc[0], str)
        entry.industry                      = validate_field(data['Industry'].iloc[0], str)
        entry.fiscal_year_end               = validate_field(data['FiscalYearEnd'].iloc[0], str)
        entry.latest_quarter                = validate_field(data['LatestQuarter'].iloc[0], datetime.datetime)
        entry.market_capitalization         = validate_field(data['MarketCapitalization'].iloc[0], (int, float))
        entry.ebitda                        = validate_field(data['EBITDA'].iloc[0], float)
        entry.pe_ratio                      = validate_field(data['PERatio'].iloc[0], float)
        entry.peg_ratio                     = validate_field(data['PEGRatio'].iloc[0], float)
        entry.earnings_per_share            = validate_field(data['EPS'].iloc[0], float)
        entry.revenue_per_share_ttm         = validate_field(data['RevenuePerShareTTM'].iloc[0], float)
        entry.profit_margin                 = validate_field(data['ProfitMargin'].iloc[0], float)
        entry.operating_margin_ttm          = validate_field(data['OperatingMarginTTM'].iloc[0], float)
        entry.return_on_assets_ttm          = validate_field(data['ReturnOnAssetsTTM'].iloc[0], float)
        entry.return_on_equity_ttm          = validate_field(data['ReturnOnEquityTTM'].iloc[0], float)
        entry.revenue_ttm                   = validate_field(data['RevenueTTM'].iloc[0], float)
        entry.gross_profit_ttm              = validate_field(data['GrossProfitTTM'].iloc[0], float)
        entry.quarterly_earnings_growth_yoy = validate_field(data['QuarterlyEarningsGrowthYOY'].iloc[0], float)
        entry.quarterly_revenue_growth_yoy  = validate_field(data['QuarterlyRevenueGrowthYOY'].iloc[0], float)
        entry.week_52_high                  = validate_field(data['52WeekHigh'].iloc[0], float)
        entry.week_52_low                   = validate_field(data['52WeekLow'].iloc[0], float)

        # Set the timestamp to the current datetime
        entry.timestamp = datetime.datetime.now()

        # Commit the session after all updates
        session.commit()
    
        print(f"Company Overview data for {symbol} has been updated")

    # Rollback the session in case of integrity error
    except IntegrityError:
        session.rollback()
        print("During the execution of update_table_entry_ov function there was a")
        print(f"integrity error for {symbol}. Data was not updated.")
    # Rollback the session in case of other SQLAlchemy errors
    except SQLAlchemyError as e:
        session.rollback()
        print("During the execution of update_table_entry_ov function there was a")
        print(f"database error for {symbol}: {str(e)}")
    # Rollback the session for any other exceptions
    except Exception as e:
        session.rollback()
        print("During the execution of update_table_entry_ov function there was an")
        print(f"error updating data for {symbol}: {str(e)}")
    # Ensure the session is closed after operation
    finally:
        session.close()

# Creates and updates entries on the TimeSeriesDailyData table
def update_table_entry_ts(symbol, data):
    
    print(f"Starting update to the TimeSeriesDailyData table for {symbol}.")
    
    # Create a new database session
    session = create_session()

    # Sort data in descending order by date,
    # so that newest to oldest data is checked first
    data = data.sort_index(ascending=False)

    # Initialize a counter to keep track of iterations
    counter = 0

    # Initialize a counter for existing entries
    existing_entries_count = 0

    # Placeholder for the last checked date
    last_checked_date = None
    
    commit = 0

    try:
        # Iterate over all rows in the DataFrame
        for index, row in data.iterrows():
            current_date = pd.to_datetime(index).normalize()

            # Check for existing entry
            existing_entry = session.query(TimeSeriesDailyData).filter_by(
                symbol=symbol, date=current_date).first()

            # If entry exists
            if existing_entry:
                # If the current date is exactly one day after the last checked date,
                # it means data is consecutive. In this case, increment the count.
                if last_checked_date and current_date == last_checked_date - pd.Timedelta(days=1):
                    existing_entries_count += 1

                # If the current date is not consecutive, reset the count to 1
                # as this is a new sequence of data.
                else:
                    existing_entries_count = 1

                # If there are 30 consecutive existing entries, it's assumed that
                # there is unlikely to be new data to add. So, the loop is broken
                # to stop further unnecessary processing.
                if existing_entries_count >= 30:
                    print("30 consecutive existing entries found, aborting.")
                    break

            # Entry does not exist, create a new one
            else:
                new_entry = TimeSeriesDailyData(
                    symbol      = symbol,
                    date        = current_date,
                    open_price  = validate_field(row['1. open'], float),
                    high_price  = validate_field(row['2. high'], float),
                    low_price   = validate_field(row['3. low'], float),
                    close_price = validate_field(row['4. close'], float),
                    volume      = validate_field(row['5. volume'], float),
                    timestamp   = datetime.datetime.now()
                )
                session.add(new_entry)

            # Update the last checked date
            last_checked_date = current_date

            # Commit every 500 records to avoid a large transaction
            if counter % 500 == 0:
                session.commit()
                
                # Provide terminal feedback to show that the function is executing 
                commit += 1
                print("Commitment #" + str(commit))

            # Increment the counter at the end of each loop iteration
            counter += 1

        # Commit the final batch
        session.commit()

        print(f"Daily Time Series data for {symbol} has been updated")

    # Rollback the session in case of integrity error
    except IntegrityError:
        session.rollback()
        print("During the execution of update_table_entry_ts function there was a")
        print(f"integrity error for {symbol}. Data was not updated.")
    # Rollback the session in case of other SQLAlchemy errors
    except SQLAlchemyError as e:
        session.rollback()
        print("During the execution of update_table_entry_ts function there was a")
        print(f"database error for {symbol}: {str(e)}")
    # Rollback the session for any other exceptions
    except Exception as e:
        session.rollback()
        print("During the execution of update_table_entry_ts function there was a")
        print(f"error updating data for {symbol}: {str(e)}")
    # Ensure the session is closed after operation
    finally:
        session.close()

# Creates and updates entries on the TimeSeriesIntraDayData table
def update_table_entry_intraday(symbol, data):
    
    print(f"Starting update to the TimeSeriesIntraDayData table for {symbol}.")
    
    # Create a new database session
    session = create_session()

    # Sort data in descending order by date,
    # so that newest to oldest data is checked first
    data = data.sort_index(ascending=False)

    # Initialize a counter to keep track of iterations
    counter = 0

    # Initialize a counter for existing entries
    existing_entries_count = 0

    # Placeholder for the last checked date
    last_checked_datetime = None
    
    commit = 0

    try:
        # Iterate over all rows in the DataFrame
        for index, row in data.iterrows():
            current_datetime = pd.to_datetime(index)

            # Check for existing entry
            existing_entry = session.query(TimeSeriesIntraDayData).filter_by(
                symbol = symbol, datetime=current_datetime).first()

            # If entry exists
            if existing_entry:
                # Check if the current datetime is exactly 5 minutes after the last checked datetime
                if last_checked_datetime and current_datetime == last_checked_datetime - pd.Timedelta(minutes=5):
                    # Increment the count for consecutive entries
                    existing_entries_count += 1
                else:
                    # Reset the count if the entries are not consecutive
                    existing_entries_count = 1

                # If there are 288 (equates to 3 business day's worth of 5 min increments)
                # consecutive existing entries, it's assumed that
                # there is unlikely to be new data to add. So, the loop is broken
                # to stop further unnecessary processing.
                if existing_entries_count >= 288:
                    print("288 consecutive existing entries found, aborting.")
                    break

            # Entry does not exist, create a new one
            else:
                new_entry = TimeSeriesIntraDayData(
                    symbol      = symbol,
                    datetime    = current_datetime,
                    open_price  = validate_field(row['1. open'], float),
                    high_price  = validate_field(row['2. high'], float),
                    low_price   = validate_field(row['3. low'], float),
                    close_price = validate_field(row['4. close'], float),
                    volume      = validate_field(row['5. volume'], float),
                    timestamp   = datetime.datetime.now()
                )
                session.add(new_entry)

            # Update the last checked date
            last_checked_datetime = current_datetime

            # Commit every 500 records to avoid a large transaction
            if counter % 500 == 0:
                session.commit()
                
                # Provide terminal feedback to show that the function is executing 
                commit += 1
                print("Commitment #" + str(commit))
            
            counter += 1

        # Commit the final batch
        session.commit()
       
        print(f"Intraday Time Series data for {symbol} has been updated")

    # Rollback the session in case of integrity error
    except IntegrityError:
        session.rollback()
        print("During the execution of update_table_entry_intraday function there was a")
        print(f"integrity error for {symbol}. Data was not updated.")
    # Rollback the session in case of other SQLAlchemy errors
    except SQLAlchemyError as e:
        session.rollback()
        print("During the execution of update_table_entry_intraday function there was a")
        print(f"database error for {symbol}: {str(e)}")
    # Rollback the session for any other exceptions
    except Exception as e:
        session.rollback()
        print("during the execution of update_table_entry_intraday function there was a")
        print(f"Error updating data for {symbol}: {str(e)}")
    # Ensure the session is closed after operation
    finally:
        session.close()

# Function to check if data for a symbol is up-to-date
def is_data_up_to_date(symbol, table):
    # Create a session using the configured "Session" class
    session = create_session()

    # check to see when the entry was last updated
    try:

        entry = table.query.filter_by(symbol=symbol).first()

        # check to see when the entry was last updated for TimeSeriesDailyData
        if table == TimeSeriesDailyData:
            # retrieve the most recent entry for the symbol from TimeSeriesDailyData
            entry = session.query(table).filter_by(
                symbol=symbol).order_by(table.date.desc()).first()

            # Check if the entry's timestamp is within the same day
            if entry:
                today = datetime.datetime.now().replace(
                    hour=0, minute=0, second=0, microsecond=0)
                return entry.timestamp >= today

        # check to see when the entry was last updated for CompanyInformation or FinancialMetrics
        else:
            # retrieve entry with same symbol
            entry = session.query(table).filter_by(symbol=symbol).first()

            if entry:
                # Check if the entry's timestamp is within the last week
                last_week = datetime.datetime.now() - datetime.timedelta(days=7)
                return entry.timestamp >= last_week

        # If no entry exists, data is not up-to-date
        return False

    # Rollback the session in case of other SQLAlchemy errors
    except SQLAlchemyError as e:
        print(f"Database error for {symbol}: {str(e)}")
        return False
    # Rollback the session for any other exceptions
    except Exception as e:
        print(f"Error checking data for {symbol}: {str(e)}")
        return False
    # Ensure the session is closed after operation
    finally:
        session.close()

# Function to fetch and store company overview and financial metrics data
def fetch_and_store_company_overview_data(symbol):
    # Ensure that this function is always called within an application context
    with current_app.app_context():
        # Check if overview data is up-to-date,
        # API call will only be done if the data has not been updated within the last week
        if not is_data_up_to_date(symbol, OverviewData) or not is_data_up_to_date(symbol, OverviewData):
            # Fetch and update overview data
            data_ov, _ = get_stock_ov_data(symbol)
            update_table_entry_ov(symbol, data_ov)
        else:
            print(f"Using existing overview data for {symbol}")

# Function to fetch and store daily time series data
def fetch_and_store_time_series_daily_data(symbol):
    # Ensure that this function is always called within an application context
    with current_app.app_context():
        # Check if daily time series data is up-to-date,
        # API call will only be done if the data has not been updated within the same day
        if not is_data_up_to_date(symbol, TimeSeriesDailyData):
            data_ts, _ = get_daily_time_series_data(symbol)
            update_table_entry_ts(symbol, data_ts)
        else:
            print(f"Using existing time series data {symbol}")

# Function to fetch and store intraday time series data
def fetch_and_store_time_series_intraday_data(symbol):
    # Ensure that this function is always called within an application context
    with current_app.app_context():
        # Available asynchronously, no checking to see when it was last updated.
        data_intraday, _ = get_intraday_time_series_data(symbol)
        update_table_entry_intraday(symbol, data_intraday)

# Function to fetch and store stock data and time series data
def fetch_and_store_stock_data(symbol):
    # Ensure that this function is always called within an application context
    with current_app.app_context():
        # Fetch and update overview data
        fetch_and_store_company_overview_data(symbol)

        # Fetch and update time series daily data
        fetch_and_store_time_series_daily_data(symbol)

        # Fetch and update time series intraday data
        fetch_and_store_time_series_intraday_data(symbol)
