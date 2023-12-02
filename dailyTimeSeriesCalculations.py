import datetime
from itertools import groupby
from sqlalchemy import func, desc
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from extensions import create_session
from models import TimeSeriesDailyData, AverageWeeklyDailyData, AverageMonthlyDailyData, AverageYearlyDailyData

# Function to calculate and store average weekly daily data
# from the time series daily api call 
def calculate_and_store_weekly_averages(symbol):
    # Create a new database session
    session = create_session()

    # Define the start and end years for data processing
    start_year = 2000
    end_year = 2023

    try:
        # Loop through each year from start_year to end_year
        for year in range(start_year, end_year + 1):

            # Calculate the start (January 1st) and end (December 31st) dates for the current year
            start_date = datetime.datetime(year, 1, 1)
            end_date = datetime.datetime(year, 12, 31)

            # Query the database to retrieve daily data for the given symbol within the current year range
            # and order the results by date
            data_query = session.query(TimeSeriesDailyData)\
                .filter(TimeSeriesDailyData.symbol == symbol,
                        TimeSeriesDailyData.date >= start_date,
                        TimeSeriesDailyData.date <= end_date)\
                .order_by(TimeSeriesDailyData.date)

            # Execute the query and store the results in daily_data
            daily_data = data_query.all()

            # If no data is retrieved for the year, skip the rest of the loop and continue with the next year
            if not daily_data:
                continue

             # Group the daily data by week
            weekly_data = group_by_week(daily_data)

            # Iterate over each group of weekly data
            for week_data_iter in weekly_data:
                # Convert the group iterator to a list for processing
                week_data_list = list(week_data_iter)

                # Calculate the weekly average for the current group of data
                avg_data = calculate_weekly_average(week_data_list)

                # If avg_data is None (indicating empty week_data_list), skip to the next iteration
                if avg_data is None:
                    continue

                # Calculate the date of the Monday of the week for the current group of data
                monday_date = week_data_list[0].date - \
                    datetime.timedelta(days=week_data_list[0].date.weekday())

                # Store the calculated monthtly averages in the database
                new_avg = AverageWeeklyDailyData(
                    symbol=avg_data['symbol'],
                    date=monday_date,
                    open_price=avg_data['open_avg'],
                    high_price=avg_data['high_avg'],
                    low_price=avg_data['low_avg'],
                    close_price=avg_data['close_avg'],
                    volume=avg_data['volume_avg'],
                    timestamp=datetime.datetime.now()
                )

                # Add or update the record in the database
                session.merge(new_avg)

            # Commit the changes to the database after processing each year
            session.commit()

        # Inform that the process is successfully completed for all years
        print("Weekly daily time series averages successfully calculated and stored.")

    # Rollback the session in case of integrity error
    except IntegrityError as e:
        session.rollback()
        print(f"Integrity error for {symbol}: {e.orig}")
    # Rollback the session in case of other SQLAlchemy errors
    except SQLAlchemyError as e:
        session.rollback()
        print(f"SQLAlchemy error for {symbol}: {str(e)}")
    # Rollback the session for any other exceptions
    except Exception as e:
        session.rollback()
        print(f"Error for {symbol}: {str(e)}")
    # Ensure the session is closed after operation
    finally:
        session.close()

# Function to group data by weeks
def group_by_week(daily_data):
    # Sort the data by date to ensure correct grouping
    daily_data.sort(key=lambda x: x.date)

    # Group by week
    for _, week_data in groupby(daily_data, key=lambda x: x.date.isocalendar()[1]):
        yield week_data

# Function to calcute averages for weekly data
def calculate_weekly_average(week_data):
    # Convert iterable to list for multiple iterations
    week_data_list = list(week_data)

    # Check if the week_data_list is empty
    if not week_data_list:
        return None

    # Calculate averages
    open_avg = sum(d.open_price for d in week_data_list) / len(week_data_list)
    high_avg = sum(d.high_price for d in week_data_list) / len(week_data_list)
    low_avg = sum(d.low_price for d in week_data_list) / len(week_data_list)
    close_avg = sum(d.close_price for d in week_data_list) / \
        len(week_data_list)
    volume_avg = sum(d.volume for d in week_data_list) / len(week_data_list)

    # Return the calculated averages in a dictionary
    return {
        'symbol': week_data_list[0].symbol,
        'open_avg': open_avg,
        'high_avg': high_avg,
        'low_avg': low_avg,
        'close_avg': close_avg,
        'volume_avg': volume_avg
    }

# function to calculate and store average monthly daily data
# from the time series daily api call 
def calculate_and_store_monthly_averages(symbol):
    # Create a new database session
    session = create_session()

    # Define the start and end years for data processing
    start_year = 2000
    end_year = 2023

    try:
        # Loop through each year from start_year to end_year
        for year in range(start_year, end_year + 1):

            # Calculate the start (January 1st) and end (December 31st) dates for the current year
            start_date = datetime.datetime(year, 1, 1)
            end_date = datetime.datetime(year, 12, 31)

            # Query the database to retrieve daily data for the given symbol within the current year range
            # and order the results by date
            data_query = session.query(TimeSeriesDailyData)\
                .filter(TimeSeriesDailyData.symbol == symbol,
                        TimeSeriesDailyData.date >= start_date,
                        TimeSeriesDailyData.date <= end_date)\
                .order_by(TimeSeriesDailyData.date)

            # Execute the query and store the results in daily_data
            daily_data = data_query.all()

            # If no data is retrieved for the year, skip the rest of the loop and continue with the next year
            if not daily_data:
                continue

            # Group the daily data by month
            monthly_data = group_by_month(daily_data)

            # Iterate over each group of weekly data
            for monthy_data_iter in monthly_data:
                # Convert the group iterator to a list for processing
                month_data_list = list(monthy_data_iter)

                # Calculate the weekly average for the current group of data
                avg_data = calculate_monthly_average(month_data_list)

                # If avg_data is None (indicating empty week_data_list), skip to the next iteration
                if avg_data is None:
                    continue

                # Store the calculated monthtly averages in the database
                new_avg = AverageMonthlyDailyData(
                    symbol=avg_data['symbol'],
                    date=datetime.datetime(
                        avg_data['year'], avg_data['month'], 1),
                    open_price=avg_data['open_avg'],
                    high_price=avg_data['high_avg'],
                    low_price=avg_data['low_avg'],
                    close_price=avg_data['close_avg'],
                    volume=avg_data['volume_avg'],
                    timestamp=datetime.datetime.now()
                )
                # Add or update the record in the database
                session.merge(new_avg)

            # Commit the changes to the database after processing each year
            session.commit()

        # Inform that the process is successfully completed for all years
        print("Monthly daily time series averages succesfully calculated and stored.")

    # Rollback the session in case of integrity error
    except IntegrityError as e:
        session.rollback()
        print(f"Integrity error for {symbol}: {e.orig}")
    # Rollback the session in case of other SQLAlchemy errors
    except SQLAlchemyError as e:
        session.rollback()
        print(f"SQLAlchemy error for {symbol}: {str(e)}")
    # Rollback the session for any other exceptions
    except Exception as e:
        session.rollback()
        print(f"Error for {symbol}: {str(e)}")
    # Ensure the session is closed after operation
    finally:
        session.close()

# Function to group data by months
def group_by_month(daily_data):
    # Sort the data by date to ensure correct grouping
    daily_data.sort(key=lambda x: (x.date.year, x.date.month))

    # Group by month
    for (_, month), month_data in groupby(daily_data, key=lambda x: (x.date.year, x.date.month)):
        yield month_data

# Function to calcute averages for monthly data
def calculate_monthly_average(month_data):
    # Convert iterable to list for multiple iterations
    month_data_list = list(month_data)

    # Check if the week_data_list is empty
    if not month_data_list:
        return None

    # Calculate averages
    open_avg = sum(d.open_price for d in month_data_list) / \
        len(month_data_list)
    high_avg = sum(d.high_price for d in month_data_list) / \
        len(month_data_list)
    low_avg = sum(d.low_price for d in month_data_list) / len(month_data_list)
    close_avg = sum(d.close_price for d in month_data_list) / \
        len(month_data_list)
    volume_avg = sum(d.volume for d in month_data_list) / len(month_data_list)

    # Return the calculated averages in a dictionary
    return {
        'symbol': month_data_list[0].symbol,
        'year': month_data_list[0].date.year,
        'month': month_data_list[0].date.month,
        'open_avg': open_avg,
        'high_avg': high_avg,
        'low_avg': low_avg,
        'close_avg': close_avg,
        'volume_avg': volume_avg
    }

# function to calculate and store average yearly daily data
# from the time series daily api call 
def calculate_and_store_yearly_averages(symbol):
    # Create a new database session
    session = create_session()

    # Define the start and end years for data processing
    start_year = 2000
    end_year = 2023

    try:
        # Loop through each year from start_year to end_year
        for year in range(start_year, end_year + 1):

            # Calculate the start (January 1st) and end (December 31st) dates for the current year
            start_date = datetime.datetime(year, 1, 1)
            end_date = datetime.datetime(year, 12, 31)

            # Query the database to retrieve daily data for the given symbol within the current year range
            # and order the results by date
            data_query = session.query(TimeSeriesDailyData)\
                .filter(TimeSeriesDailyData.symbol == symbol,
                        TimeSeriesDailyData.date >= start_date,
                        TimeSeriesDailyData.date <= end_date)\
                .order_by(TimeSeriesDailyData.date)

            # Execute the query and store the results in daily_data
            daily_data = data_query.all()

            # If no data is retrieved for the year, skip the rest of the loop and continue with the next year
            if not daily_data:
                continue

            # Calculate yearly averages
            yearly_avg = calculate_yearly_average(daily_data)

            # Store the calculated yearly averages in the database
            new_avg = AverageYearlyDailyData(
                symbol=yearly_avg['symbol'],
                # First day of the year
                date=datetime.datetime(yearly_avg['year'], 1, 1),
                open_price=yearly_avg['open_avg'],
                high_price=yearly_avg['high_avg'],
                low_price=yearly_avg['low_avg'],
                close_price=yearly_avg['close_avg'],
                volume=yearly_avg['volume_avg'],
                timestamp=datetime.datetime.now()
            )
            # Add or update the record in the database
            session.merge(new_avg)

            # Commit the changes to the database after processing each year
            session.commit()

        # Inform that the process is successfully completed for all years
        print("Yearly daily time series averages succesfully calculated and stored.")

    # Rollback the session in case of integrity error
    except IntegrityError as e:
        session.rollback()
        print(f"Integrity error for {symbol}: {e.orig}")
    # Rollback the session in case of other SQLAlchemy errors
    except SQLAlchemyError as e:
        session.rollback()
        print(f"SQLAlchemy error for {symbol}: {str(e)}")
    # Rollback the session for any other exceptions
    except Exception as e:
        session.rollback()
        print(f"Error for {symbol}: {str(e)}")
    # Ensure the session is closed after operation
    finally:
        session.close()

# Function to calcute averages for yearly data
def calculate_yearly_average(daily_data):
    # Calculate yearly averages
    open_avg = sum(d.open_price for d in daily_data) / len(daily_data)
    high_avg = sum(d.high_price for d in daily_data) / len(daily_data)
    low_avg = sum(d.low_price for d in daily_data) / len(daily_data)
    close_avg = sum(d.close_price for d in daily_data) / len(daily_data)
    volume_avg = sum(d.volume for d in daily_data) / len(daily_data)

    # Return the calculated averages in a dictionary
    return {
        # Assuming all entries have the same symbol
        'symbol': daily_data[0].symbol,
        'year': daily_data[0].date.year,
        'open_avg': open_avg,
        'high_avg': high_avg,
        'low_avg': low_avg,
        'close_avg': close_avg,
        'volume_avg': volume_avg
    }
