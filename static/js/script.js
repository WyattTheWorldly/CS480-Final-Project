const chartElement = document.getElementById('tv_chart_container');
const chart = LightweightCharts.createChart(chartElement, {
    timeScale: {
        timeVisible: false,
        secondsVisible: false,
    },
});
let candleSeries = null

let dayData = [];
let weekData = [];
let monthData = [];

// This function should be called once for when stock button is clicked
// to load data into the global arrays.

function loadAllDataSeries(symbol = "AAPL"){
    updateOverview(symbol);
    // fetchData(symbol);//default is TIME_SERIES_DAILY
    // fetchData(symbol, "TIME_SERIES_WEEKLY");
    // fetchData(symbol, "TIME_SERIES_MONTHLY");
}

function updateOverview(symbol = "AAPL"){
    fetch(`/fetch_data/${symbol}`)
        .then(response => {
            if (!response.ok) {
                console.log('Error attempting to connect');
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log(data);
            document.getElementById('description').innerText = data.description;
            document.getElementById('asset-type').innerText = data.asset_type;
            document.getElementById('exchange').innerText = data.exchange;
            document.getElementById('currency').innerText = data.currency;
            document.getElementById('country').innerText = data.country;
            document.getElementById('sector').innerText = data.sector;
            document.getElementById('industry').innerText = data.industry;
            document.getElementById('stock-title').innerText = data.name;
            document.getElementById('eps').innerText = data.earnings_per_share;
            document.getElementById('ebitda').innerText = data.ebitda;
            document.getElementById('fye').innerText = data.fiscal_year_end;
            document.getElementById('gpttm').innerText = data.gross_profit_ttm;
            document.getElementById('latest-quart').innerText = data.latest_quarter;
            document.getElementById('market-cap').innerText = data.market_capitalization;
            document.getElementById('op-mar-ttm').innerText = data.operating_margin_ttm;
            document.getElementById('pe-ratio').innerText = data.pe_ratio;
            document.getElementById('peg-ratio').innerText = data.peg_ratio;
            document.getElementById('profit-margin').innerText = data.profit_margin;
            document.getElementById('qegyoy').innerText = data.quarterly_earnings_growth_yoy;
            document.getElementById('qrgyoy').innerText = data.quarterly_revenue_growth_yoy;
            document.getElementById('roa-ttm').innerText = data.return_on_assets_ttm;
            document.getElementById('roq-ttm').innerText = data.return_on_equity_ttm;
            document.getElementById('rps-ttm').innerText = data.revenue_per_share_ttm;
            document.getElementById('revenue-ttm').innerText = data.revenue_ttm;
            document.getElementById('52-wh').innerText = data.week_52_high;
            document.getElementById('52-wl').innerText = data.week_52_low;
        })
        .catch(error => {
            // Handle errors during the fetch request
            console.error('There was a problem with the fetch operation:', error);
        });
}

function fetchData(symbol = "AAPL", functionTable = "TIME_SERIES_DAILY") {
    const url = 'http://127.0.0.1:5000/stock_data'
    let data = {
        "symbol": symbol,
        "function": functionTable
    }
    //fetching data from API
    fetch(url,
        {
            "method": 'POST',
            "headers": {
                'Content-Type': 'application/json'
            },
            "body": JSON.stringify(data),
        })
        .then(response => {
            if (!response.ok) {
                console.log('Error attempting to connect');
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            let transformedData;
            switch (functionTable){
                case "TIME_SERIES_DAILY":
                    console.log('Table: TIME_SERIES_DAILY')
                    transformedData = transformData(data, "Time Series (Daily)").reverse();
                    dayData = [].concat(transformedData);
                    break;
                case "TIME_SERIES_WEEKLY":
                    console.log('Table: TIME_SERIES_WEEKLY')
                    transformedData = transformData(data, "Weekly Time Series").reverse();
                    weekData = [].concat(transformedData);
                    break;
                case "TIME_SERIES_MONTHLY":
                    console.log('Table: TIME_SERIES_MONTHLY')
                    transformedData = transformData(data, "Monthly Time Series").reverse();
                    monthData = [].concat(transformedData);
                    break;
                default:
                    console.log(`Table: ${functionTable} does not match any tables in the API.`);
                    break;
            }
        })
        .catch(error => {
            // Handle errors during the fetch request
            console.error('There was a problem with the fetch operation:', error);
        });

}

//transforming data so it can be used by the chart
function transformData(jsonData, timeSeriesKey) {
    //console.log(jsonData)
    const weeklyData = jsonData[timeSeriesKey];
    const transformedData = [];
    console.log('Attempting to parse data')
    for (const date in weeklyData) {
        if (weeklyData.hasOwnProperty(date)) {
            const entry = weeklyData[date];
            const transformedEntry = {
                time: date,
                open: parseFloat(entry["open"]),
                high: parseFloat(entry["high_price"]),
                low: parseFloat(entry["low_price"]),
                close: parseFloat(entry["close_price"]),
            };
            transformedData.push(transformedEntry);
        }
    }

    return transformedData;
}


//this can be deleted, simply random data not needed
function updateChart(data) {

    //updating the data for chart
    //remove current series
    if (candleSeries) {
        chart.removeSeries(candleSeries);
        candleSeries = null;
    }
    candleSeries = chart.addCandlestickSeries();

    //setting the data
    candleSeries.setData(data);
    chart.timeScale().fitContent();
}

document.addEventListener('DOMContentLoaded', function () {
});


function createSimpleSwitcher(items, activeItem, activeItemChangedCallback) {
    let switcherElement = document.getElementById('switch');

    let intervalElements = items.map(function(item) {
        let itemEl = document.createElement('button');
        itemEl.innerText = item;
        itemEl.classList.add('switcher-item');
        itemEl.classList.toggle('switcher-active-item', item === activeItem);
        itemEl.addEventListener('click', function() {
            onItemClicked(item);
        });
        switcherElement.appendChild(itemEl);
        return itemEl;
    });

    function onItemClicked(item) {
        if (item === activeItem) {
            return;
        }

        intervalElements.forEach(function(element, index) {
            element.classList.toggle('switcher-active-item', items[index] === item);
        });

        activeItem = item;

        activeItemChangedCallback(item);
    }

    return switcherElement;
}

let intervals = ['1D', '1W', '1M'];

let switcherElement = createSimpleSwitcher(intervals, intervals[0], syncToInterval);

//Set the data for chart to the correct interval
function syncToInterval(interval) {
    switch (interval){
        case '1D':
            updateChart(dayData);
            break;
        case '1W':
            updateChart(weekData);
            break;
        case '1M':
            updateChart(monthData);
            break;
        default:
            console.log('hit def');
            break;
    }
}