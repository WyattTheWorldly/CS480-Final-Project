from alpha_vantage.fundamentaldata import FundamentalData
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# Create instance of the SQLAlchemy database
db = SQLAlchemy()

# Key that allows access to API
API_key = 'N8LVC6JOGADHP6RE'

# Defining tables for database
class CompanyInformation(db.Model):
    symbol = db.Column(db.String(10), unique=True, primary_key=True)
    name = db.Column(db.String(100))  
    asset_type = db.Column(db.String(50))
    description = db.Column(db.String(1000))
    exchange = db.Column(db.String(10))
    currency = db.Column(db.String(10))
    country = db.Column(db.String(50)) 
    sector = db.Column(db.String(50))  
    industry = db.Column(db.String(100))  
    fiscal_year_end = db.Column(db.String(20))  
    latest_quarter = db.Column(db.String(20))  
    timestamp = db.Column(db.DateTime)
    
class FinancialMetrics(db.Model):
    symbol = db.Column(db.String(10), unique=True, primary_key=True)
    market_capitalization = db.Column(db.BigInteger)  
    ebitda = db.Column(db.Float)  
    pe_ratio = db.Column(db.Float)  
    peg_ratio = db.Column(db.Float)  
    earnings_per_share = db.Column(db.Float)  
    revenue_per_share_ttm = db.Column(db.Float)  
    profit_margin = db.Column(db.Float)  
    operating_margin_ttm = db.Column(db.Float)  
    return_on_assets_ttm = db.Column(db.Float)  
    return_on_equity_ttm = db.Column(db.Float)  
    revenue_ttm = db.Column(db.Float)  
    gross_profit_ttm = db.Column(db.Float)  
    quarterly_earnings_growth_yoy = db.Column(db.Float)  
    quarterly_revenue_growth_yoy = db.Column(db.Float)  
    week_52_high = db.Column(db.Float) 
    week_52_low = db.Column(db.Float)  
    timestamp = db.Column(db.DateTime)
    
# Function to get stock data from the AlphaVantage API
def get_stock_data(symbol):
    # Create an AlphaVantage client
    ov = FundamentalData(key=API_key, output_format='pandas')
    
    # Retrieve company overview data from the given symbol
    data, meta_data = ov.get_company_overview(symbol=symbol)
    
    return data, meta_data

# Function to update a table entry with new data
def update_table_entry(table, symbol, data):
    try:
        # Check to see if entry already exists for symbol
        entry = table.query.filter_by(symbol = symbol).first()
        # If entry for symbol does not already exist, create a new one
        if not entry:
            entry = table(symbol = symbol)

        # Check the type of table and update the fields accordingly
        if table == CompanyInformation:
            # Update fields specific to CompanyInformation
            entry.name = data['Name'].iloc[0] if data['Name'].iloc[0] is not None else None
            entry.description = data['Description'].iloc[0] if data['Description'].iloc[0] is not None else None
            entry.asset_type = data['AssetType'].iloc[0] if data['AssetType'].iloc[0] is not None else None
            entry.exchange = data['Exchange'].iloc[0] if data['Exchange'].iloc[0] is not None else None
            entry.currency = data['Currency'].iloc[0] if data['Currency'].iloc[0] is not None else None
            entry.country = data['Country'].iloc[0] if data['Country'].iloc[0] is not None else None
            entry.sector = data['Sector'].iloc[0] if data['Sector'].iloc[0] is not None else None
            entry.industry = data['Industry'].iloc[0] if data['Industry'].iloc[0] is not None else None
            entry.fiscal_year_end = data['FiscalYearEnd'].iloc[0] if data['FiscalYearEnd'].iloc[0] is not None else None
            entry.latest_quarter = data['LatestQuarter'].iloc[0] if data['LatestQuarter'].iloc[0] is not None else None
        
        elif table == FinancialMetrics:
            # Update fields specific to FinancialMetrics
            entry.market_capitalization = data['MarketCapitalization'].iloc[0] if data['MarketCapitalization'].iloc[0] is not None else None
            entry.ebitda = data['EBITDA'].iloc[0] if data['EBITDA'].iloc[0] is not None else None
            entry.pe_ratio = data['PERatio'].iloc[0] if data['PERatio'].iloc[0] is not None else None
            entry.peg_ratio = data['PEGRatio'].iloc[0] if data['PEGRatio'].iloc[0] is not None else None
            entry.earnings_per_share = data['EPS'].iloc[0] if data['EPS'].iloc[0] is not None else None
            entry.revenue_per_share_ttm = data['RevenuePerShareTTM'].iloc[0] if data['RevenuePerShareTTM'].iloc[0] is not None else None
            entry.profit_margin = data['ProfitMargin'].iloc[0] if data['ProfitMargin'].iloc[0] is not None else None
            entry.operating_margin_ttm = data['OperatingMarginTTM'].iloc[0] if data['OperatingMarginTTM'].iloc[0] is not None else None
            entry.return_on_assets_ttm = data['ReturnOnAssetsTTM'].iloc[0] if data['ReturnOnAssetsTTM'].iloc[0] is not None else None
            entry.return_on_equity_ttm = data['ReturnOnEquityTTM'].iloc[0] if data['ReturnOnEquityTTM'].iloc[0] is not None else None
            entry.revenue_ttm = data['RevenueTTM'].iloc[0] if data['RevenueTTM'].iloc[0] is not None else None
            entry.gross_profit_ttm = data['GrossProfitTTM'].iloc[0] if data['GrossProfitTTM'].iloc[0] is not None else None
            entry.quarterly_earnings_growth_yoy = data['QuarterlyEarningsGrowthYOY'].iloc[0] if data['QuarterlyEarningsGrowthYOY'].iloc is not None else None
            entry.quarterly_revenue_growth_yoy = data['QuarterlyRevenueGrowthYOY'].iloc[0] if data['QuarterlyRevenueGrowthYOY'].iloc is not None else None
            entry.week_52_high = data['52WeekHigh'].iloc[0] if data['52WeekHigh'].iloc[0] is not None else None
            entry.week_52_low = data['52WeekLow'].iloc[0] if data['52WeekLow'].iloc[0] is not None else None
    
        # Set the timestamp to the current datetime
        entry.timestamp = datetime.now()

        # Add the entry to the SQLAlchemy session and commit it to the database
        db.session.add(entry)
        db.session.commit()
        print(f"Success!")
    
    # Handle IntegrityError, likely due to conflicts with unique constraints
    except IntegrityError:
        db.session.rollback()
        print(f"Integrity error for {symbol}. Data was not updated.")
    # Handle SQLAlchemyError, a general database error
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Database error for {symbol}: {str(e)}")
     # Handle other exceptions
    except Exception as e:
        print(f"Error updating data for {symbol}: {str(e)}")

# Function to check if data for a symbol is up-to-date within the last week
def is_data_up_to_date(symbol, table):
    try:
        # Retrieve the entry for the symbol
        entry = table.query.filter_by(symbol = symbol).first()
        if entry:
            # Check if the entry's timestamp is within the last week
            last_week = datetime.now() - timedelta(days=7)
            return entry.timestamp >= last_week
        # If no entry exists, data is not up-to-date
        return False

    # Handle SQLAlchemyError
    except SQLAlchemyError as e:
        print(f"Database error for {symbol}: {str(e)}")
        return False
    # Handle other exceptions
    except Exception as e:
        print(f"Error checking data for {symbol}: {str(e)}")
        return False

# Function to fetch and store stock data
def fetch_and_store_stock_data(symbol):
    if is_data_up_to_date(symbol, CompanyInformation) and is_data_up_to_date(symbol, FinancialMetrics):
        print(f"Using existing data for {symbol}")
        return

    data, _ = get_stock_data(symbol)
    update_table_entry(CompanyInformation, symbol, data)
    update_table_entry(FinancialMetrics, symbol, data)
    print(f"Data for {symbol} has been updated")