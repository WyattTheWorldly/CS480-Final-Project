from alpha_vantage.fundamentaldata import FundamentalData
from alpha_vantage.timeseries import TimeSeries
from datetime import datetime, timedelta
from extensions import db, create_session
import pandas as pd
from flask import current_app
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# This file is for retrieving data from the API, creating tables in the datebase, 
# and creating and updating table entries

# Key that allows access to API
API_key = 'N8LVC6JOGADHP6RE'

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
# Returns None if the value is NaN or not of the expected type.
def validate_field(value, expected_type):
    if pd.isnull(value):
        return None
    elif isinstance(value, expected_type):
        return value
    else:
        return None

# Defining tables for database
class CompanyInformation(db.Model):
    symbol          = db.Column(db.String(10), unique=True, primary_key=True)
    name            = db.Column(db.String(100))  
    asset_type      = db.Column(db.String(50))
    description     = db.Column(db.String(1000))
    exchange        = db.Column(db.String(10))
    currency        = db.Column(db.String(10))
    country         = db.Column(db.String(50)) 
    sector          = db.Column(db.String(50))  
    industry        = db.Column(db.String(100))  
    fiscal_year_end = db.Column(db.String(20))  
    latest_quarter  = db.Column(db.String(20))  
    timestamp       = db.Column(db.DateTime)
    def __str__(self):
        return str(f"<{self.symbol}>" + '\n' + f"<{self.name}>" + '\n' + f"<{self.asset_type}>" + '\n' + f"<{self.description}>" + '\n' + f"<{self.exchange}>" + '\n' + f"<{self.currency}>" + '\n' + f"<{self.country}>" + '\n' + f"<{self.sector}>" + '\n' + f"<{self.industry}>" + '\n' + f"<{self.fiscal_year_end}>" + '\n' + f"<{self.latest_quarter}>" + '\n' + f"<{self.timestamp}>")
    
class FinancialMetrics(db.Model):
    symbol                          = db.Column(db.String(10), unique=True, primary_key=True)
    market_capitalization           = db.Column(db.BigInteger)  
    ebitda                          = db.Column(db.Float)  
    pe_ratio                        = db.Column(db.Float)  
    peg_ratio                       = db.Column(db.Float)  
    earnings_per_share              = db.Column(db.Float)  
    revenue_per_share_ttm           = db.Column(db.Float)  
    profit_margin                   = db.Column(db.Float)  
    operating_margin_ttm            = db.Column(db.Float)  
    return_on_assets_ttm            = db.Column(db.Float)  
    return_on_equity_ttm            = db.Column(db.Float)  
    revenue_ttm                     = db.Column(db.Float)  
    gross_profit_ttm                = db.Column(db.Float)  
    quarterly_earnings_growth_yoy   = db.Column(db.Float)  
    quarterly_revenue_growth_yoy    = db.Column(db.Float)  
    week_52_high                    = db.Column(db.Float) 
    week_52_low                     = db.Column(db.Float)  
    timestamp                       = db.Column(db.DateTime)
    def __str__(self):
        return str(f"<{self.symbol}>" + '\n' + f"<{self.market_capitalization}>" + '\n' + f"<{self.ebitda}>" + '\n' + f"<{self.pe_ratio}>" + '\n' + f"<{self.peg_ratio}>" + '\n' + f"<{self.earnings_per_share}>" + '\n' + f"<{self.revenue_per_share_ttm}>" + '\n' + f"<{self.profit_margin}>" + '\n' + f"<{self.operating_margin_ttm}>" + '\n' + f"<{self.return_on_assets_ttm}>" + '\n' + f"<{self.return_on_equity_ttm}>" + '\n' + f"<{self.revenue_ttm}>" + '\n' + f"<{self.gross_profit_ttm}>" + '\n' + f"<{self.quarterly_earnings_growth_yoy}>" + '\n' + f"<{self.quarterly_revenue_growth_yoy}>" + '\n' + f"<{self.week_52_high}>" + '\n' + f"<{self.week_52_low}>" + '\n' + f"<{self.timestamp}>")
    
class TimeSeriesDailyData(db.Model):
    symbol      = db.Column(db.String(10), primary_key=True)
    date        = db.Column(db.DateTime, primary_key=True)
    open_price  = db.Column(db.Float)
    high_price  = db.Column(db.Float)
    low_price   = db.Column(db.Float)
    close_price = db.Column(db.Float)
    volume      = db.Column(db.Float)
    timestamp   = db.Column(db.DateTime)

class TimeSeriesIntraDayData(db.Model):
    symbol      = db.Column(db.String(10), primary_key=True)
    datetime    = db.Column(db.DateTime, primary_key=True)
    open_price  = db.Column(db.Float)
    high_price  = db.Column(db.Float)
    low_price   = db.Column(db.Float)
    close_price = db.Column(db.Float)
    volume      = db.Column(db.Float)
    timestamp   = db.Column(db.DateTime)

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
def update_table_entry_ov(table, symbol, data):
    
    # Create a new database session
    session = create_session()
    
    try:
        # Check to see if entry already exists for symbol
        entry = session.query(table).filter_by(symbol=symbol).first()
        
        # If entry for symbol does not already exist, create a new one
        if not entry:
            entry = table(symbol=symbol)
            session.add(entry)

        # Check the type of table and update the fields accordingly
        if isinstance(entry, CompanyInformation):
            # Update fields specific to CompanyInformation
            entry.name = validate_field(data['Name'].iloc[0], str)
            entry.description = validate_field(data['Description'].iloc[0], str)
            entry.asset_type = validate_field(data['AssetType'].iloc[0], str)
            entry.exchange = validate_field(data['Exchange'].iloc[0], str)
            entry.currency = validate_field(data['Currency'].iloc[0], str)
            entry.country = validate_field(data['Country'].iloc[0], str)
            entry.sector = validate_field(data['Sector'].iloc[0], str)
            entry.industry = validate_field(data['Industry'].iloc[0], str)
            entry.fiscal_year_end = validate_field(data['FiscalYearEnd'].iloc[0], str)
            entry.latest_quarter = validate_field(data['LatestQuarter'].iloc[0], str)
        
        elif table == FinancialMetrics:
            # Update fields specific to FinancialMetrics
            entry.market_capitalization = validate_field(data['MarketCapitalization'].iloc[0], (int, float))
            entry.ebitda = validate_field(data['EBITDA'].iloc[0], float)
            entry.pe_ratio = validate_field(data['PERatio'].iloc[0], float)
            entry.peg_ratio = validate_field(data['PEGRatio'].iloc[0], float)
            entry.earnings_per_share = validate_field(data['EPS'].iloc[0], float)
            entry.revenue_per_share_ttm = validate_field(data['RevenuePerShareTTM'].iloc[0], float)
            entry.profit_margin = validate_field(data['ProfitMargin'].iloc[0], float)
            entry.operating_margin_ttm = validate_field(data['OperatingMarginTTM'].iloc[0], float)
            entry.return_on_assets_ttm = validate_field(data['ReturnOnAssetsTTM'].iloc[0], float)
            entry.return_on_equity_ttm = validate_field(data['ReturnOnEquityTTM'].iloc[0], float)
            entry.revenue_ttm = validate_field(data['RevenueTTM'].iloc[0], float)
            entry.gross_profit_ttm = validate_field(data['GrossProfitTTM'].iloc[0], float)
            entry.quarterly_earnings_growth_yoy = validate_field(data['QuarterlyEarningsGrowthYOY'].iloc[0], float)
            entry.quarterly_revenue_growth_yoy = validate_field(data['QuarterlyRevenueGrowthYOY'].iloc[0], float)
            entry.week_52_high = validate_field(data['52WeekHigh'].iloc[0], float)
            entry.week_52_low = validate_field(data['52WeekLow'].iloc[0], float)
    
        # Set the timestamp to the current datetime
        entry.timestamp = datetime.now()

        # Commit the session after all updates
        session.commit()
    
    # Rollback the session in case of integrity error
    except IntegrityError:
        session.rollback() 
        print(f"Integrity error for {symbol}. Data was not updated.")
    # Rollback the session in case of other SQLAlchemy errors
    except SQLAlchemyError as e:
        session.rollback() 
        print(f"Database error for {symbol}: {str(e)}")
    # Rollback the session for any other exceptions
    except Exception as e:
        session.rollback() 
        print(f"Error updating data for {symbol}: {str(e)}")
    # Ensure the session is closed after operation
    finally:
        session.close() 

# Creates and updates entries on the TimeSeriesDailyData table
def update_table_entry_ts(symbol, data):
    
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
    
    try:
        # Iterate over all rows in the DataFrame
        for index, row in data.iterrows():
            current_date = pd.to_datetime(index).normalize()
            
            # Check for existing entry
            existing_entry = session.query(TimeSeriesDailyData).filter_by(symbol=symbol, date=current_date).first()
        
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
                    symbol = symbol,
                    date = current_date,
                    open_price = validate_field(row['1. open'], float),
                    high_price = validate_field(row['2. high'], float),
                    low_price = validate_field(row['3. low'], float),
                    close_price = validate_field(row['4. close'], float),
                    volume = validate_field(row['5. volume'], float),
                    timestamp = datetime.now()
                )
                session.add(new_entry)
                
            # Update the last checked date
            last_checked_date = current_date
            
            # Commit every 500 records to avoid a large transaction
            if counter % 500 == 0:
                session.commit()

            # Increment the counter at the end of each loop iteration
            counter += 1  

        # Commit the final batch
        session.commit()
        print(f"Daily Time Series data for {symbol} has been updated")

    # Rollback the session in case of integrity error
    except IntegrityError:
        session.rollback() 
        print(f"Integrity error for {symbol}. Data was not updated.")
    # Rollback the session in case of other SQLAlchemy errors
    except SQLAlchemyError as e:
        session.rollback() 
        print(f"Database error for {symbol}: {str(e)}")
    # Rollback the session for any other exceptions
    except Exception as e:
        session.rollback() 
        print(f"Error updating data for {symbol}: {str(e)}")
    # Ensure the session is closed after operation
    finally:
        session.close() 

# Creates and updates entries on the TimeSeriesIntraDayData table
def update_table_entry_intraday(symbol, data):
    
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

    try:
        # Iterate over all rows in the DataFrame
        for index, row in data.iterrows():
            current_datetime = pd.to_datetime(index)

            # Check for existing entry
            existing_entry = session.query(TimeSeriesIntraDayData).filter_by(symbol=symbol, datetime=current_datetime).first()

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
                    symbol=symbol,
                    datetime=current_datetime,
                    open_price=validate_field(row['1. open'], float),
                    high_price=validate_field(row['2. high'], float),
                    low_price=validate_field(row['3. low'], float),
                    close_price=validate_field(row['4. close'], float),
                    volume=validate_field(row['5. volume'], float),
                    timestamp=datetime.now()
                )
                session.add(new_entry)

            # Update the last checked date
            last_checked_datetime = current_datetime

            # Commit every 500 records to avoid a large transaction
            if counter % 500 == 0:
                session.commit()
            counter += 1

        # Commit the final batch
        session.commit()
        print(f"Intraday Time Series data for {symbol} has been updated")

    # Rollback the session in case of integrity error
    except IntegrityError:
        session.rollback()
        print(f"Integrity error for {symbol}. Data was not updated.")
    # Rollback the session in case of other SQLAlchemy errors
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error for {symbol}: {str(e)}")
    # Rollback the session for any other exceptions
    except Exception as e:
        session.rollback()
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
            entry = session.query(table).filter_by(symbol=symbol).order_by(table.date.desc()).first()
            
            # Check if the entry's timestamp is within the same day
            if entry:
                today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                return entry.timestamp >= today
            
        # check to see when the entry was last updated for CompanyInformation or FinancialMetrics
        else:
            # retrieve entry with same symbol
            entry = session.query(table).filter_by(symbol=symbol).first()
            
            if entry:
                # Check if the entry's timestamp is within the last week
                last_week = datetime.now() - timedelta(days=7)
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
        if not is_data_up_to_date(symbol, CompanyInformation) or not is_data_up_to_date(symbol, FinancialMetrics):
            # Fetch and update overview data
            data_ov, _ = get_stock_ov_data(symbol)
            update_table_entry_ov(CompanyInformation, symbol, data_ov)
            update_table_entry_ov(FinancialMetrics, symbol, data_ov)
            print(f"Company Overview data for {symbol} has been updated")
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
        
        