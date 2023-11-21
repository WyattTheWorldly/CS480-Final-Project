from flask import Flask, render_template, jsonify
from extensions import db, create_session
from getData import fetch_and_store_stock_data
from databaseRetrieval import get_company_overview, get_financial_metrics, get_daily_time_series, get_intraday_time_series

app = Flask(__name__)

# configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Cs480@localhost/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the Flask app
db.init_app(app)

# Create the database and tables
with app.app_context():
    db.create_all()


# Routes
@app.route('/fetch_data/<symbol>')
def fetch_data(symbol):
    try:
        # Call the function from getData.py with the symbol from the URL
        overview = get_company_overview(symbol)
        return jsonify(
            {
                "status": "success", 
                "symbol"          : overview.symbol,
                "name"            : overview.name,
                "asset_type"      : overview.asset_type,
                "description"     : overview.description,
                "exchange"        : overview.exchange,
                "currency"        : overview.currency,
                "country"         : overview.country,
                "sector"          : overview.sector,
                "industry"        : overview.industry,
                "fiscal_year_end" : overview.fiscal_year_end,
                "latest_quarter"  : overview.latest_quarter,
                "timestamp"       : overview.timestamp,
            }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# Renders the stock_views page, the <stockv> is the stock name to render
# Refer to base.html for examples of use in navbar
@app.route('/stock_view/<stockv>')
def stock_view(stockv):
    if stockv == 'AAPL':
        return render_template('APPL.html', stockv=stockv)
    elif stockv == 'AMZN':
        return render_template('AMZN.html', stockv=stockv)
    else:
        return render_template('index.html', stockv=stockv)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
