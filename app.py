from flask import Flask, render_template
from getData import db, fetch_and_store_stock_data, CompanyInformation, FinancialMetrics
import getData

app = Flask(__name__)

# configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:groupD@localhost/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the Flask app
db.init_app(app)

# Create the database and tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/fetch_data/<symbol>')
def fetch_data(symbol):
    # Call the function from getData.py with the symbol from the URL
    getData.fetch_and_store_stock_data(symbol)
    return f"Data for {symbol} has been updated"

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)