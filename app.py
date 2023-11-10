from flask import Flask, render_template, jsonify
from extensions import db, create_session
from getData import fetch_and_store_stock_data

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
        fetch_and_store_stock_data(symbol)
        return jsonify({"status": "success", "message": f"Data for {symbol} has been updated"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
