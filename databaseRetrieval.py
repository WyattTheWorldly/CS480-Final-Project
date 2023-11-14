from extensions import db, create_session
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
