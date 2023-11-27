const chartElement = document.getElementById('tv_chart_container');
const chart = LightweightCharts.createChart(chartElement, {
    timeScale: {
        timeVisible: false,
        secondsVisible: false,
    },
    maxHeight: 800,
    maxWidth: 1400,
});
let candleSeries = null

let dayData = [];
let weekData = [];
let monthData = [];

// This function should be called once for when stock button is clicked
// to load data into the global arrays.


function loadAllDataSeries(symbol = "IBM"){
    fetchData(symbol);//default is TIME_SERIES_DAILY
    fetchData(symbol, "TIME_SERIES_WEEKLY");
    fetchData(symbol, "TIME_SERIES_MONTHLY");
    updateChart(dayData);
}
// switch demo api key to real ones after testing is done
function fetchData(symbol = "IBM", functionTable = "TIME_SERIES_DAILY") {
    fetch(`https://www.alphavantage.co/query?function=${functionTable}&symbol=${symbol}&apikey=E9HF2DALRYZKAIJC`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            let transformedData;
            switch (functionTable){
                case "TIME_SERIES_DAILY":
                    transformedData = transformData(data, "Time Series (Daily)").reverse();
                    dayData = [].concat(transformedData);
                    break;
                case "TIME_SERIES_WEEKLY":
                    transformedData = transformData(data, "Weekly Time Series").reverse();
                    weekData = [].concat(transformedData);
                    break;
                case "TIME_SERIES_MONTHLY":
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
    const weeklyData = jsonData[timeSeriesKey];
    const transformedData = [];

    for (const date in weeklyData) {
        if (weeklyData.hasOwnProperty(date)) {
            const entry = weeklyData[date];
            const transformedEntry = {
                time: date,
                open: parseFloat(entry["1. open"]),
                high: parseFloat(entry["2. high"]),
                low: parseFloat(entry["3. low"]),
                close: parseFloat(entry["4. close"]),
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

/*
TESTING CODE
 */

function createSimpleSwitcher(items, activeItem, activeItemChangedCallback) {
    let switcherElement = document.createElement('div');
    switcherElement.classList.add('switcher');

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
document.body.appendChild(switcherElement);

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