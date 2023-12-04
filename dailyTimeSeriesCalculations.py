import datetime
import traceback
from itertools import groupby
from sqlalchemy import func, desc
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from extensions import create_session
from models import TimeSeriesDailyData, AverageWeeklyDailyData, AverageMonthlyDailyData, AverageYearlyDailyData

# This file is for calculating averages from stored Time Series Daily Data.
# Weekly, monthly, and yearly averages are calculated by symbol.

# Function to group data by weeks
def group_by_week(daily_data):
    # Sort the data by date to ensure correct grouping
    daily_data.sort(key = lambda x: x.date)

    # Group by week
    for _, week_data in groupby(daily_data, key = lambda x: x.date.isocalendar()[1]):
        yield week_data

# Function to group data by months
def group_by_month(daily_data):
    # Sort the data by date to ensure correct grouping
    daily_data.sort(key = lambda x: (x.date.year, x.date.month))

    # Group by month
    for (_, month), month_data in groupby(daily_data, key=lambda x: (x.date.year, x.date.month)):
        yield month_data

# Function to calculate averages for weekly data
def calculate_weekly_average(week_data):
    # Convert iterable to list for multiple iterations
    week_data_list = list(week_data)

    # Check if the week_data_list is empty
    if not week_data_list:
        return None

    # Calculate the Monday date of the week
    # Assuming the first entry in the week_data_list represents a date within the week
    # and using its date to find the Monday of that week
    first_entry_date = week_data_list[0].date
    monday_date = first_entry_date - datetime.timedelta(days=first_entry_date.weekday())

    # Calculate averages
    open_avg    = sum(d.open_price for d in week_data_list) / len(week_data_list)
    high_avg    = sum(d.high_price for d in week_data_list) / len(week_data_list)
    low_avg     = sum(d.low_price for d in week_data_list) / len(week_data_list)
    close_avg   = sum(d.close_price for d in week_data_list) / len(week_data_list)
    volume_avg  = sum(d.volume for d in week_data_list) / len(week_data_list)

    # Return the calculated averages in a dictionary along with the Monday date
    return {
        'symbol'    : week_data_list[0].symbol,
        'date'      : monday_date,
        'open_avg'  : open_avg,
        'high_avg'  : high_avg,
        'low_avg'   : low_avg,
        'close_avg' : close_avg,
        'volume_avg': volume_avg
    }

# Function to calculate averages for monthly data
def calculate_monthly_average(month_data):
    # Convert iterable to list for multiple iterations
    month_data_list = list(month_data)

    # Check if the month_data_list is empty
    if not month_data_list:
        return None

    # Calculate the first day of the month
    # Assuming the first entry in the month_data_list represents a date within the month
    # and using its date to find the first day of that month
    first_entry_date = month_data_list[0].date
    first_day_of_month = datetime.datetime(first_entry_date.year, first_entry_date.month, 1)

    # Calculate averages
    open_avg    = sum(d.open_price for d in month_data_list) / len(month_data_list)
    high_avg    = sum(d.high_price for d in month_data_list) / len(month_data_list)
    low_avg     = sum(d.low_price for d in month_data_list) / len(month_data_list)
    close_avg   = sum(d.close_price for d in month_data_list) / len(month_data_list)
    volume_avg  = sum(d.volume for d in month_data_list) / len(month_data_list)

    # Return the calculated averages in a dictionary along with the first day of the month
    return {
        'symbol'        : month_data_list[0].symbol,
        'date'          : first_day_of_month,
        'open_avg'      : open_avg,
        'high_avg'      : high_avg,
        'low_avg'       : low_avg,
        'close_avg'     : close_avg,
        'volume_avg'    : volume_avg
    }

# Function to calculate averages for yearly data
def calculate_yearly_average(daily_data):
    # Check if the daily_data is empty
    if not daily_data:
        return None

    # Calculate the first day of the year
    first_entry_date = daily_data[0].date
    first_day_of_year = datetime.datetime(first_entry_date.year, 1, 1)

    # Calculate yearly averages
    open_avg    = sum(d.open_price for d in daily_data) / len(daily_data)
    high_avg    = sum(d.high_price for d in daily_data) / len(daily_data)
    low_avg     = sum(d.low_price for d in daily_data) / len(daily_data)
    close_avg   = sum(d.close_price for d in daily_data) / len(daily_data)
    volume_avg  = sum(d.volume for d in daily_data) / len(daily_data)

    # Return the calculated averages in a dictionary
    return {
        # Assuming all entries have the same symbol
        'symbol'        : daily_data[0].symbol,
        'date'          : first_day_of_year,
        'open_avg'      : open_avg,
        'high_avg'      : high_avg,
        'low_avg'       : low_avg,
        'close_avg'     : close_avg,
        'volume_avg'    : volume_avg
    }

# Function to calculate and store average daily data
# from the time series daily api call as specified by 
# the average_type of which there are weekly, monthly, 
# and yearly
def calculate_and_store_averages(symbol, average_type):
    # Determine the table and calculation function based on average_type
    # If the averages calculated should be weekly
    if average_type == 'weekly':
        specified_table = AverageWeeklyDailyData
        calculate_average = calculate_weekly_average
        group_data = group_by_week
        print_message = "weekly"
    
    # If the averages calculated should be monthly   
    elif average_type == 'monthly':
        specified_table = AverageMonthlyDailyData
        calculate_average = calculate_monthly_average
        group_data = group_by_month
        print_message = "monthly"
        
    # If the averages calculated should be yearly
    elif average_type == 'yearly':
        specified_table = AverageYearlyDailyData
        calculate_average = calculate_yearly_average
        group_data = lambda data: [data]  # For yearly, the entire data is a single group
        print_message = "yearly"
        
    # Else handle if an invalid average type is entered
    else:
        raise ValueError("Invalid average type specified")

    # Log the start of the update process
    print(f"Starting to update the {specified_table.__tablename__} table for {symbol}.")

    # Create a new database session
    session = create_session()

    # Initialize a variable to count database commits
    commit = 0

    try:
        # Query the most recent date in the specified table for the given symbol
        most_recent_date_in_specified_table = session.query(func.max(specified_table.date))\
                                                     .filter(specified_table.symbol == symbol)\
                                                     .scalar()

        # Query the oldest and most recent dates in TimeSeriesDailyData table for the given symbol
        oldest_date = session.query(func.min(TimeSeriesDailyData.date))\
                             .filter(TimeSeriesDailyData.symbol == symbol)\
                             .scalar()
        most_recent_date_in_timeseries = session.query(func.max(TimeSeriesDailyData.date))\
                                                .filter(TimeSeriesDailyData.symbol == symbol)\
                                                .scalar()

        # Determine start_year and end_year based on comparison
        # If the years match, process only the most recent year
        if most_recent_date_in_specified_table and most_recent_date_in_timeseries and \
           most_recent_date_in_specified_table.year == most_recent_date_in_timeseries.year:
            start_year = end_year = most_recent_date_in_specified_table.year
        # If years don't match or there's no data, process all available years
        else:
            start_year = oldest_date.year if oldest_date else None
            end_year = most_recent_date_in_timeseries.year if most_recent_date_in_timeseries else None

        if start_year and end_year:
            # Loop through each year in the determined range
            for year in range(start_year, end_year + 1):
                # Set the start and end dates for each year
                start_date = datetime.datetime(year, 1, 1)
                end_date = datetime.datetime(year, 12, 31)

                # Retrieve daily data for the given symbol within the current year range
                data_query = session.query(TimeSeriesDailyData)\
                    .filter(TimeSeriesDailyData.symbol == symbol,
                            TimeSeriesDailyData.date >= start_date,
                            TimeSeriesDailyData.date <= end_date)\
                    .order_by(TimeSeriesDailyData.date)

                # Execute the query and store the results
                daily_data = data_query.all()

                # Skip processing if no data is retrieved for the year
                if not daily_data:
                    continue

                # Use the assigned grouping function based on average_type
                if average_type in ['weekly', 'monthly']:
                    data_groups = group_data(daily_data)

                # For yearly averages, the data is already appropriately grouped
                else:
                    data_groups = [daily_data]
                
                for data_group in data_groups:
                    # Convert the group iterator to a list for processing
                    data_list = list(data_group)
                    # Calculate the average for the current group of data
                    avg_data = calculate_average(data_list)

                    # Skip to the next iteration if avg_data is None (indicating empty data_list)
                    if avg_data is None:
                        continue

                    # Create a new record with the calculated averages
                    new_avg = specified_table(
                        symbol      = avg_data['symbol'],
                        date        = avg_data['date'],
                        open_price  = avg_data['open_avg'],
                        high_price  = avg_data['high_avg'],
                        low_price   = avg_data['low_avg'],
                        close_price = avg_data['close_avg'],
                        volume      = avg_data['volume_avg'],
                        timestamp   = datetime.datetime.now()
                    )

                    # Merge the new record into the database (add or update)
                    session.merge(new_avg)

                # Commit the changes to the database after processing each year
                session.commit()
                # Increment the commit counter and log the commitment
                commit += 1
                print(f"Commitment #{commit}")

            # Log the successful completion of the process
            print(f"{print_message.capitalize()} daily time series averages successfully calculated and stored for {symbol}.")

        else:
            print(f"Insufficient data for processing {print_message} averages in TimeSeriesDailyData for {symbol}.")

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
        traceback.print_exc()  # This prints the full traceback
        print(f"Error for {symbol}: {e}")
    # Ensure the session is closed after operation
    finally:
        session.close()

# Function to check to see that data stored in the 
# average daily tables is up to date
# Function to check to see that data stored in the average daily tables is up to date
def update_average_daily_data(symbol, table):
    
    # Create a new database session
    session = create_session()
    
    try:
        # Retrieve the most recent entry for the symbol from TimeSeriesDailyData
        latest_time_series_entry = session.query(TimeSeriesDailyData).filter_by(
            symbol=symbol).order_by(TimeSeriesDailyData.timestamp.desc()).first()

        # Retrieve the most recent entry for the symbol from the specified table
        latest_other_entry = session.query(table).filter_by(
            symbol=symbol).order_by(table.timestamp.desc()).first()

        # Determine the type of average based on the table
        if table == AverageWeeklyDailyData:
            average_type = 'weekly'
        elif table == AverageMonthlyDailyData:
            average_type = 'monthly'
        elif table == AverageYearlyDailyData:
            average_type = 'yearly'
        else:
            raise ValueError("Invalid table specified for average calculation")

        # Check if update is needed and call the combined function
        if (latest_time_series_entry and not latest_other_entry) or \
           (latest_time_series_entry and latest_other_entry and 
            latest_time_series_entry.timestamp > latest_other_entry.timestamp):
            calculate_and_store_averages(symbol, average_type)
        else:
            print("Data already up to date")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        session.close()
