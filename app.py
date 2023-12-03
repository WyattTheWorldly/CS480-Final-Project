from dotenv import load_dotenv
import os
import json
from flask import Flask, render_template, jsonify, request, after_this_request
from extensions import db, create_session
from getData import fetch_and_store_time_series_daily_data, fetch_and_store_stock_data
from databaseRetrieval import get_company_overview, get_daily_time_series, get_intraday_time_series

# This loads the environment variables from .env
# pip install python-dotenv
load_dotenv()  

app = Flask(__name__)

# old database configuration
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Cs480@localhost/postgres'

# AMAZON RDS database configutation
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql://{os.getenv('DATABASE_USER')}:{os.getenv('DATABASE_PASS')}@"
    f"{os.getenv('DATABASE_HOST')}:{os.getenv('DATABASE_PORT')}/"
    f"{os.getenv('DATABASE_NAME')}?sslmode=require"
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the Flask app
db.init_app(app)

# Create the database and tables
with app.app_context():
    try:
        with app.app_context():
            db.create_all()
    except Exception as e:
        print(f"Error creating the database: {str(e)}")

# Routes
@app.route('/fetch_data/<symbol>')
def fetch_data(symbol):
    try:
        # Call the function from getData.py with the symbol from the URL
        overview = get_company_overview(symbol)
        return jsonify(
            {
                "status": "success", 
                "symbol"                : overview.symbol,
                "name"                  : overview.name,
                "asset_type"            : overview.asset_type,
                "description"           : overview.description,
                "exchange"              : overview.exchange,
                "currency"              : overview.currency,
                "country"               : overview.country,
                "sector"                : overview.sector,
                "industry"              : overview.industry,
                "fiscal_year_end"       : overview.fiscal_year_end,
                "latest_quarter"        : overview.latest_quarter,
                "timestamp"             : overview.timestamp,
            }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Listen for POST requests to the /stock_data route
# Primarily for use in JS file for graph views
@app.route("/stock_data", methods = ['POST'])
def stock_data():
    @after_this_request
    def add_header(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    # Get the symbol & functionTable from the POST request
    postData = request.get_json()
    symbol = postData['symbol']
    functionTable = postData['function']

    # This is called reverse engeneering at its worst
    daily_time_series = get_daily_time_series(symbol)
    #Converts the data into dictionary format
    daily_time_series = [d.__dict__ for d in daily_time_series]
    #Drops symbol and _sa_instance_state
    for d in daily_time_series:
        d.pop('symbol', None)
        d.pop('_sa_instance_state', None)

    # Fetch and return the data as JSON
    return jsonify(daily_time_series), 200


@app.route('/fetch_daily_time_series/<symbol>')
def fetch_daily_time_series(symbol):
    fetch_and_store_time_series_daily_data(symbol)


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
