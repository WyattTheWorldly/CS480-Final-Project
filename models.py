from extensions import db

# This file is for defining database tables

# Defining tables for database
class OverviewData(db.Model):
    symbol                          = db.Column(db.String(10), unique=True, primary_key=True)
    name                            = db.Column(db.String(100))
    asset_type                      = db.Column(db.String(50))
    description                     = db.Column(db.String(1000))
    exchange                        = db.Column(db.String(10))
    currency                        = db.Column(db.String(10))
    country                         = db.Column(db.String(50))
    sector                          = db.Column(db.String(50))
    industry                        = db.Column(db.String(100))
    fiscal_year_end                 = db.Column(db.String(20))
    latest_quarter                  = db.Column(db.DateTime)
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
        # Combine the string representations from both original classes
        return (f"<{self.symbol}>\n<Company Information>\n"
                f"Name: {self.name}, Asset Type: {self.asset_type}, "
                f"Description: {self.description}, Exchange: {self.exchange}, "
                f"Currency: {self.currency}, Country: {self.country}, "
                f"Sector: {self.sector}, Industry: {self.industry}, "
                f"Fiscal Year End: {self.fiscal_year_end}, Latest Quarter: {self.latest_quarter}\n"
                f"<Financial Metrics>\n"
                f"Market Capitalization: {self.market_capitalization}, EBITDA: {self.ebitda}, "
                f"PE Ratio: {self.pe_ratio}, PEG Ratio: {self.peg_ratio}, "
                f"Earnings Per Share: {self.earnings_per_share}, Revenue Per Share TTM: {self.revenue_per_share_ttm}, "
                f"Profit Margin: {self.profit_margin}, Operating Margin TTM: {self.operating_margin_ttm}, "
                f"Return on Assets TTM: {self.return_on_assets_ttm}, Return on Equity TTM: {self.return_on_equity_ttm}, "
                f"Revenue TTM: {self.revenue_ttm}, Gross Profit TTM: {self.gross_profit_ttm}, "
                f"Quarterly Earnings Growth YoY: {self.quarterly_earnings_growth_yoy}, "
                f"Quarterly Revenue Growth YoY: {self.quarterly_revenue_growth_yoy}, "
                f"Week 52 High: {self.week_52_high}, Week 52 Low: {self.week_52_low}, "
                f"Timestamp: {self.timestamp}")

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

class AverageWeeklyDailyData(db.Model):
    symbol      = db.Column(db.String(10), primary_key=True)
    date        = db.Column(db.DateTime, primary_key=True)
    open_price  = db.Column(db.Float)
    high_price  = db.Column(db.Float)
    low_price   = db.Column(db.Float)
    close_price = db.Column(db.Float)
    volume      = db.Column(db.Float)
    timestamp   = db.Column(db.DateTime)
    
class AverageMonthlyDailyData(db.Model):
    symbol      = db.Column(db.String(10), primary_key=True)
    date        = db.Column(db.DateTime, primary_key=True)
    open_price  = db.Column(db.Float)
    high_price  = db.Column(db.Float)
    low_price   = db.Column(db.Float)
    close_price = db.Column(db.Float)
    volume      = db.Column(db.Float)
    timestamp   = db.Column(db.DateTime) 

class AverageYearlyDailyData(db.Model):
    symbol      = db.Column(db.String(10), primary_key=True)
    date        = db.Column(db.DateTime, primary_key=True)
    open_price  = db.Column(db.Float)
    high_price  = db.Column(db.Float)
    low_price   = db.Column(db.Float)
    close_price = db.Column(db.Float)
    volume      = db.Column(db.Float)
    timestamp   = db.Column(db.DateTime) 