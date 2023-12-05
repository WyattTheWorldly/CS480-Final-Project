/*
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
*/

let candlestickChart; // Global variable to hold the first chart instance
let currentSymbol = 'AAPL'; // Default symbol
let currentField = 'open_price'; // Default field
let currentInterval = 'Yearly Averages'; // Default interval

let intervals = ['5 min Increments','Daily Averages', 'Weekly Averages', 'Monthly Averages', 'Yearly Averages'];

// Create a simple switcher (assuming createSimpleSwitcher function exists)
let switcherElement = createSimpleSwitcher(intervals, intervals[0], syncToInterval);

// Update the data for the chart to the correct interval
// Update the data for the chart to the correct interval
async function syncToInterval(interval) {
    console.log(`Switching to interval: ${interval}`);
    let timeIncrement; // Use a different variable name to avoid conflict
    switch (interval) {
        case '5 min Increments':
            timeIncrement = 'intraday';
            break;
        case 'Daily Averages':
            timeIncrement = 'daily';
            break;
        case 'Weekly Averages':
            timeIncrement = 'weekly';
            break;
        case 'Monthly Averages':
            timeIncrement = 'monthly';
            break;
        case 'Yearly Averages':
            timeIncrement = 'yearly';
            break;
        default:
            console.error(`Unknown interval: ${interval}`);
            return;
    }

    currentInterval = timeIncrement; // Update currentInterval based on the selected interval

    console.log(`At end of syncToInterval the current field is: ${currentInterval}`); // Debugging to check the current field value

    await updateCandlstickChart(currentSymbol, timeIncrement);
}

// Function to update the main chart
// Function to update the main chart
async function updateCandlstickChart(symbol, timeInterval) {
    console.log('Executing updateChart function');
    const data = await fetchGraphData(symbol, timeInterval);
    const processedData = processData(data); 
    candlestickChart = renderChart(processedData, candlestickChart, 'tv_chart_container');
}

// Function to fetch data from the Flask route
async function fetchGraphData(symbol, timeInterval) {
    try {
        const url = `/graph_data_retrieval/${symbol}/${timeInterval}`;
        console.log(`Attempting to fetch data from: ${url}`);
        const response = await fetch(url);
        if (response.ok) {
            const data = await response.json();
            console.log("Fetched Data:", data);  // Log the fetched data
            return data;
        }
    } catch (error) {
        console.error('Fetch error:', error);
        return [];
    }
}


function processData(data) {
    console.log("Executing processData function");

    const processedData = data.reduce((acc, entry) => {
        if (entry.date && entry.open_price && entry.high_price && entry.low_price && entry.close_price) {
            acc.push({
                time: entry.date, // Assuming entry.date is already in Unix timestamp format
                open: entry.open_price,
                high: entry.high_price,
                low: entry.low_price,
                close: entry.close_price
            });
        } else {
            console.error("Invalid entry skipped:", entry);
        }
        return acc;
    }, []);

    console.log("Processed Data:", processedData);
    return processedData;
}


// Function to render or update the chart using lightweight-charts
function renderChart(data, chartInstance, chartContainerId) {
    console.log("Executing renderChart function");

    // Log the received data
    console.log("Received data for rendering:", data);

    // Find the container where the chart will be drawn
    const chartContainer = document.getElementById(chartContainerId);
    if (!chartContainer) {
        console.error(`Chart container with ID '${chartContainerId}' not found.`);
        return;
    }
    console.log(`Chart container found: ${chartContainerId}`);

    // If a chart instance does not exist, create a new one
    if (!chartInstance) {
        console.log('Creating new chart instance');
        chartInstance = LightweightCharts.createChart(chartContainer, {
            width: chartContainer.offsetWidth,
            height: chartContainer.offsetHeight,
            layout: {
                backgroundColor: '#ffffff',
                textColor: 'rgba(33, 56, 77, 1)',
            },
            grid: {
                vertLines: {
                    color: 'rgba(197, 203, 206, 0.5)',
                },
                horzLines: {
                    color: 'rgba(197, 203, 206, 0.5)',
                },
            },
            timeScale: {
                borderColor: 'rgba(197, 203, 206, 1)',
            },
        });
        console.log('Chart instance created');

        // Create a candlestick series
        const candleSeries = chartInstance.addCandlestickSeries({
            upColor: 'rgba(255, 144, 0, 1)',
            downColor: 'rgba(0, 144, 255, 1)',
            borderVisible: false,
            wickVisible: true,
            borderColor: '#000000',
            wickColor: '#000000',
            borderUpColor: 'rgba(255, 144, 0, 1)',
            borderDownColor: 'rgba(0, 144, 255, 1)',
            wickUpColor: 'rgba(255, 144, 0, 1)',
            wickDownColor: 'rgba(0, 144, 255, 1)',
        });
        console.log('Candlestick series added to chart');

        // Store the series in the chartInstance for future updates
        chartInstance.candleSeries = candleSeries;
    } else {
        console.log('Using existing chart instance');
    }
    
    
    console.log('Updating chart with new data');
    console.log('Chart instance:', chartInstance);
    console.log('Candlestick series:', chartInstance.candleSeries);

    if (!data.length) {
        console.error('No valid data to render the chart.');
        return chartInstance; // Prevent further execution if data is invalid
    }

    // Log each data point before setting it to the chart
    data.forEach((d, index) => {
        console.log(`Data point ${index}:`, d);
        // Additional checks can be added here if needed
    });

    try {
        chartInstance.candleSeries.setData(data);
        console.log('Data set to the chart successfully');
    } catch (error) {
        console.error('Error setting data to the chart:', error);
    }
    
    return chartInstance;
}

// This function should be called once for when stock button is clicked
// to load data into the global arrays.
function loadAllDataSeries(symbol){
    console.log("Executing loadAllDataSeries function");

    updateOverview(symbol);
    // fetchData(symbol);//default is TIME_SERIES_DAILY
    // fetchData(symbol, "TIME_SERIES_WEEKLY");
    // fetchData(symbol, "TIME_SERIES_MONTHLY");
    // Assuming these are your possible fields and time increments
    currentSymbol = symbol;
    syncToInterval(intervals[0]);
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


// this can be deleted, simply random data not needed

function updateChartOld(data) {

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

/*
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
*/