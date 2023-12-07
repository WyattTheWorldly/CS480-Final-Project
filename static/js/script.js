let chart; // Global variable to hold the first chart instance
let currentSymbol = 'AAPL'; // Default symbol
let currentInterval = 'Yearly Averages'; // Default interval
let currentField = 'All'

let intradayData = [];
let dailyData = [];
let weeklyAveragesData = [];
let monthlyAveragesData = [];
let yearlyAveragesData = [];

// Function to fetch data from the Flask route
async function fetchGraphData(symbol, timeInterval) {
    console.log("Executing fetchGraphData function");
    
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

// Function to process data for line graph
function processDataForLineGraph(field, selectedData) {
    
    console.log("Executing processDataForLineGraph function");
    console.log('Field:', field)
    console.log('Selected Data:', selectedData)  
    
    // Check if selectedData is an array
    if (!Array.isArray(selectedData)) {
        return []; // Return an empty array to avoid further errors
    }

    const processedData = selectedData.map(entry => ({
            time: entry.date,
            value: entry[field]
    }));

    console.log('Processed data for line graph:', processedData);
    return processedData;
}

// Function to display a line graph
function displayLineGraph(field, selectedData) {
    console.log('Executing displayLineGraph function');
    console.log('Selected Data:', selectedData)
    if (!selectedData.length) {
        console.error(`No valid data to render the line graph for ${field}.`);
        return;
    }
    let lineChart = renderChart('tv_chart_container', 'line');
    updateChartWithData(lineChart, selectedData, 'line');
    updateChartTitleAndLabels();
}

// Function to process data for histogram
function processDataForHistogram(selectedData) {
    console.log('Executing processDataForHistogram function');
    console.log('Selected Data:', selectedData);
    
    // Check if selectedData is an array
    if (!Array.isArray(selectedData)) {
        return []; // Return an empty array to avoid further errors
    }

    const processedData = selectedData.map(entry => ({
        time: entry.date,
        volume: entry.volume
    }));

    console.log('Processed Data for Histogram:', processedData);
    return processedData;
}

// Function to display a histogram
function displayHistogram(selectedData) {

    console.log('displayHistogram');
    
    if (!selectedData.length) {
        console.error('No valid data to render the histogram.');
        return;
    }
    let histogramChart = renderChart('tv_chart_container', 'histogram');
    updateChartWithData(histogramChart, selectedData, 'histogram');
    updateChartTitleAndLabels();
}

// Function to process data for candlestick chart
function processDataForCandleStick(selectedData) {
    
    console.log("Executing processDataForCandleStick function");

    // Check if selectedData is an array
    if (!Array.isArray(selectedData)) {
        return { candlestickData: [], volumeData: [] }; // Return empty arrays to avoid further errors
    }

    const candlestickData = [];
    const volumeData = [];

    selectedData.forEach(entry => {
        if (
            entry.date &&
            entry.open_price !== undefined &&
            entry.high_price !== undefined &&
            entry.low_price !== undefined &&
            entry.close_price !== undefined &&
            entry.volume !== undefined
        ) {
            candlestickData.push({
                time: entry.date,
                open: entry.open_price,
                high: entry.high_price,
                low: entry.low_price,
                close: entry.close_price
            });
            volumeData.push({
                time: entry.date,
                value: entry.volume,
                color: entry.close_price >= entry.open_price ? 'rgba(76, 175, 80, 0.5)' : 'rgba(255, 82, 82, 0.5)'
            });
        } else {
            console.log('Skipped entry due to missing fields:', entry);
        }
    });

    console.log('Processed Data for Candlestick Chart:', { candlestickData, volumeData });

    return { candlestickData, volumeData };
}

// Function to display a candlestick chart
function displayCandlestickChart(selectedData) {
    console.log('Executing displayCandleStickChart function');
    console.log('SelectedData:', selectedData);

    if (!selectedData || !selectedData.candlestickData || !selectedData.volumeData) {
        console.error('No valid data to render the candlestick chart.');
        return;
    }
    if (!chart) {
        chart = renderChart('tv_chart_container', 'candlestick');
    }
    console.log('SelectedData:', selectedData);
    updateChartWithData(chart, selectedData, 'candlestick');
    updateChartTitleAndLabels();
}

// Define custom options with colors
const customOptions = {
    layout: {
        backgroundColor: '#1f2533', // Background color
        textColor: 'rgba(255, 255, 255, 0.9)', // Text color
    },
    grid: {
        vertLines: {
            color: 'rgba(99, 110, 123, 0.5)', // Vertical grid lines color
        },
        horzLines: {
            color: 'rgba(99, 110, 123, 0.5)', // Horizontal grid lines color
        },
    },
    timeScale: {
        borderColor: 'rgba(99, 110, 123, 1)', // Time scale border color
    },
};

// Define default options with default colors
const defaultOptions = {
    layout: {
        backgroundColor: '#1f2533', // Default background color
        textColor: 'rgba(255, 255, 255, 0.9)', // Default text color
    },
    grid: {
        vertLines: {
            color: 'rgba(99, 110, 123, 0.5)', // Default vertical grid lines color
        },
        horzLines: {
            color: 'rgba(99, 110, 123, 0.5)', // Default horizontal grid lines color
        },
    },
    timeScale: {
        borderColor: 'rgba(99, 110, 123, 1)', // Default time scale border color
    },
};


// Merge the custom options with default options
const options = { ...defaultOptions, ...customOptions }; // Use defaultOptions here

const CrosshairMode = {
    Normal: 0,
    Magnet: 1,
    NormalWithVLines: 2,
    MagnetWithVLines: 3,
};

function createNewChartInstance(chartContainerId, seriesType, options = {}) {
    console.log('Creating new chart instance');
    console.log(`Series type: ${seriesType}`);

    const chartContainer = document.getElementById(chartContainerId);
    if (!chartContainer) {
        console.error(`Chart container with ID '${chartContainerId}' not found.`);
        return null;
    }

    // Check if there's an existing chart instance in the container and remove it
    if (chartContainer.chartInstance) {
        chartContainer.chartInstance.remove();
    }

    // Create the chart instance with merged options
    const chartInstance = LightweightCharts.createChart(chartContainer, {
        width: chartContainer.offsetWidth,
        height: chartContainer.offsetHeight,
        ...options, // Use merged options here
    });

    console.log('Chart instance created');

    // Based on the seriesType, add the appropriate series
    switch (seriesType) {
        case 'candlestick':
            // Add a volume series as a histogram to the chart instance
            chartInstance.addHistogramSeries({
                color: 'rgba(44, 143, 206, 0.8)',
                priceFormat: {
                    type: 'volume',
                },
                scaleMargins: {
                    top: 0.8,
                    bottom: 0,
                },
            });

            // Add candlestick series with colors
            chartInstance.addCandlestickSeries({
                upColor: '#4bffb5',
                downColor: '#ff4976',
                borderDownColor: '#ff4976',
                borderUpColor: '#4bffb5',
                wickDownColor: '#838ca1',
                wickUpColor: '#838ca1',
            });
            break;
        case 'line':
            // Add line series with custom options
            chartInstance.addLineSeries({
                color: 'rgba(44, 143, 206, 0.8)',
                // Add other custom options specific to the series if needed
            });
            break;
        case 'histogram':
            // Add histogram series with custom options
            chartInstance.addHistogramSeries({
                color: 'rgba(44, 143, 206, 0.8)',
                // Add other custom options specific to the series if needed
            });
            break;
        default:
            console.error(`Invalid chart type: ${seriesType}`);
            return null;
    }

    // Store the chart instance in the container for future reference
    chartContainer.chartInstance = chartInstance;

    return chartInstance;
}


function renderChart(chartContainerId, seriesType) {
    
    console.log('Executing renderChart function');
    
    let chartInstance = createNewChartInstance(chartContainerId, seriesType);
    if (!chartInstance) {
        console.error(`Failed to create chart instance in container: ${chartContainerId}`);
        return;
    }

    switch (seriesType) {
        case 'candlestick':
            chartInstance.candleSeries = chartInstance.addCandlestickSeries();
            break;
        case 'line':
            chartInstance.lineSeries = chartInstance.addLineSeries();
            break;
        case 'histogram':
            chartInstance.histogramSeries = chartInstance.addHistogramSeries();
            break;
        default:
            console.error('Unknown series type:', seriesType);
            return;
    }

    return chartInstance;
}

function updateChartWithData(chartInstance, selectedData, seriesType) {
    console.log('Executing updateChartWithData function');
    console.log('Selected Data:', selectedData);
    
    if (!chartInstance) {
        console.error('No chart instance provided for updating data.');
        return;
    }

    if (seriesType === 'candlestick' && chartInstance.candleSeries) {
        if (selectedData && selectedData.candlestickData && selectedData.volumeData) {
            chartInstance.candleSeries.setData(selectedData.candlestickData);
            
            // Check if volumeSeries exists in the chart instance
            if (chartInstance.volumeSeries) {
                chartInstance.volumeSeries.setData(selectedData.volumeData);
            } else {
                console.error('Volume series not found in chart instance.');
            }
        } else {
            console.error('Invalid data format for candlestick series.');
        }
    } else if (seriesType === 'line' && chartInstance.lineSeries) {
        if (selectedData && selectedData.length) {
            chartInstance.lineSeries.setData(selectedData);
        } else {
            console.error('Invalid or empty data for line series.');
        }
    } else if (seriesType === 'histogram' && chartInstance.histogramSeries) {
        if (selectedData && selectedData.length) {
            chartInstance.histogramSeries.setData(selectedData);
        } else {
            console.error('Invalid or empty data for histogram series.');
        }
    } else {
        console.error(`Unknown series type or series not found: ${seriesType}`);
    }
    chartInstance.timeScale().fitContent();
}

function handleFieldSelectionChange(selectedField) {
    console.log('Executing handleFieldSelectChange function');
    console.log('Current interval:', currentInterval)
    console.log('Current field:', selectedField)
    
    let selectedData;

    switch (currentInterval) {
        case '5 min Increments':
            selectedData = intradayData;
            break;
        case 'Daily':
            selectedData = dailyData;
            break;
        case 'Weekly Averages':
            selectedData = weeklyAveragesData;
            break;
        case 'Monthly Averages':
            selectedData = monthlyAveragesData;
            break;
        case 'Yearly Averages':
            selectedData = yearlyAveragesData;
            break;
        default:
            console.error(`Unknown interval: ${interval}`);
            return [];
        }

    console.log('Selected Data:', selectedData)

    switch(selectedField) {
        case 'All':
            currentField = 'All';
            displayCandlestickChart(processDataForCandleStick(selectedData));
            break;
        case 'Open Price':
            currentField = 'open_price';
            displayLineGraph(currentField, processDataForLineGraph(currentField, selectedData));
            break;
        case 'High Price':
            currentField = 'high_price';
            displayLineGraph(currentField, processDataForLineGraph(currentField, selectedData));
            break;
        case 'Low Price':
            currentField = 'low_price';
            displayLineGraph(currentField, processDataForLineGraph(currentField, selectedData));
            break;
        case 'Close Price':
            currentField = 'close_price';
            displayLineGraph(currentField, processDataForLineGraph(currentField, selectedData));
            break;
        case 'Stock Volume':
            currentField = 'volume'
            displayHistogram(processDataForHistogram(selectedData));
            break;
        default:
            console.error('Invalid field selection');
            return [];
    }
}

// Function to select the appropriate data array based on the interval
function handleIntervalSelectionChange(selectedInterval) {
    console.log('Executing handleIntervalSelectionChange function');
    console.log('Current interval:', selectedInterval)
    console.log('Current field:', currentField)
    
    currentInterval = selectedInterval;

    console.log('Current interval:', currentInterval);
    console.log('Current field:', currentField);

    let selectedData;
    
    switch (selectedInterval) {
        case '5 min Increments':
            selectedData = intradayData;
            break;
        case 'Daily':
            selectedData = dailyData;
            break;
        case 'Weekly Averages':
            selectedData = weeklyAveragesData;
            break;
        case 'Monthly Averages':
            selectedData = monthlyAveragesData;
            break;
        case 'Yearly Averages':
            selectedData = yearlyAveragesData;
            break;
        default:
            console.error(`Unknown interval: ${selectedInterval}`);
            return [];
    }

    console.log('Current interval:', currentInterval);
    console.log('Current field:', currentField);

    if (currentField === 'All') {
        // Handle 'All' as an object
        if (typeof selectedData !== 'object') {
            console.error(`Data for interval ${selectedInterval} is not in the expected format.`, selectedData);
            return [];
        }
    } else {
        // Handle other fields as an array
        if (!Array.isArray(selectedData)) {
            console.error(`Data for interval ${selectedInterval} is not an array.`, selectedData);
            return [];
        }
    }

    console.log('Current interval:', currentInterval);
    console.log('Current field:', currentField);


    switch(currentField) {
        case 'All':
        case 'intraday':
            displayCandlestickChart(processDataForCandleStick(selectedData));
            break;
        case 'Open Price':
        case 'open_price':
        case 'High Price':
        case 'high_price':
        case 'Low Price':
        case 'Low Price':
        case 'Close Price':
        case 'close_price':
            displayLineGraph(currentField, processDataForLineGraph(currentField, selectedData));
            break;
        case 'Stock Volume':
        case 'volume':
            displayHistogram(processDataForHistogram(selectedData));
            break;
        default:
            console.error('Invalid field selection:');
            return [];
    }
}

// Function to update chart title and labels
function updateChartTitleAndLabels() {
    const { title } = getTitlesAndLabels(currentField, currentInterval);
    let xAxisLabel = '';
    let yAxisLabel = '';

    if (currentField == 'Volume') {
        xAxisLabel = 'Time'
        yAxisLabel = 'Volume'
    }
    else {
        xAxisLabel = 'Time'
        yAxisLabel = 'Value'
    }

    // Update the elements with the new values
    document.getElementById('chart-title').textContent = title || '';
    document.getElementById('x-axis-label').textContent = xAxisLabel || '';
    document.getElementById('y-axis-label').textContent = yAxisLabel || '';
}

function getTitlesAndLabels(currentField, currentInterval) {
    const key = `${currentField}_${currentInterval}`;
    console.log('Current Field:', currentField);
    console.log('Current Interval:', currentInterval);
    console.log('Title:', combinations[key]);
    return combinations[key] || {};
}

// Define titles and labels for all combinations
const combinations = {
    'all_5 min Increments': {
        title: 'Intraday Timeseries Daily Data'
    },
    'all_Daily': {
        title: 'Daily Timeseries Data'
    },
    'all_Weekly Averages': {
        title: 'Weekly Averages'
    },
    'all_Monthly Averages': {
        title: 'Monthly Averages'
    },
    'all_Yearly Averages': {
        title: 'Yearly Averages'
    },
    'open_price_5 min Increments': {
        title: 'Intraday Timeseries Daily for Open Price'
    },
    'open_price_Daily Averages': {
        title: 'Daily Timeseries for Open Price'
    },
    'open_price_Weekly Averages': {
        title: 'Weekly Averages for Open Price'
    },
    'open_price_Monthly Averages': {
        title: 'Monthly Averages for Open Price'
    },
    'open_price_Yearly Averages': {
        title: 'Yearly Averages for Open Price'
    },
    'high_price_5 min Increments': {
        title: 'Intraday Timeseries Daily Data for High Price'
    },
    'high_price_Daily Averages': {
        title: 'Daily Timeseries for High Price '
    },
    'high_price_Weekly Averages': {
        title: 'Weekly Averages for High Price'
    },
    'high_price_Monthly Averages': {
        title: 'Monthly Averages for High Price'
    },
    'high_price_Yearly Averages': {
        title: 'Yearly Averages for High Price'
    },
    'low_price_5 min Increments': {
        title: 'Intraday Timeseries Daily Data for Low Price'
    },
    'low_price_Daily Averages': {
        title: 'Daily Timeseries for Low Price'
    },
    'low_price_Weekly Averages': {
        title: 'Weekly Averages for Low Price'
    },
    'low_price_Monthly Averages': {
        title: 'Monthly Averages for Low Price'
    },
    'low_price_Yearly Averages': {
        title: 'Yearly Averages for Low Price'
    },
    'close_price_5 min Increments': {
        title: 'Intraday Timeseries Daily Data for Close Price'
    },
    'close_price_Daily Averages': {
        title: 'Daily Timerseries for Close Price'
    },
    'close_price_Weekly Averages': {
        title: 'Weekly Averages for Close Price'
    },
    'close_price_Monthly Averages': {
        title: 'Monthly Averages for Close Price'
    },
    'close_price_Yearly Averages': {
        title: 'Yearly Averages for Close Price'
    },
    'volume_5 min Increments': {
        title: 'Intraday Timeseries Daily Data for Volume'
    },
    'volume_Daily Averages': {
        title: 'Daily Time Series for Volume'
    },
    'volume_Weekly Averages': {
        title: 'Weekly Averages for Volume'
    },
    'volume_Monthly Averages': {
        title: 'Monthly Averages for Volume'
    },
    'volume_Yearly Averages': {
        title: 'Yearly Averages for Volume'
    },
};

// This function should be called once for when stock button is clicked
// to load data into the global arrays.
async function loadAllDataSeries(symbol) {
    console.log('Executing loadAllDataSeries function');
    
    currentSymbol = symbol;
    
    showLoadingGraphic();
    
    fetchOverviewData(symbol)

    // Use await for fetching data and processing it
    dailyData = await fetchGraphData(symbol, 'daily');
    weeklyAveragesData = await fetchGraphData(symbol, 'weekly');
    monthlyAveragesData = await fetchGraphData(symbol, 'monthly');
    yearlyAveragesData = await fetchGraphData(symbol, 'yearly');

    // Call the function to display the chart for the first time
    // Use the default interval (or any other logic you prefer)
    displayCandlestickChart(processDataForCandleStick(yearlyAveragesData));

    hideLoadingGraphic();
}

function fetchOverviewData(symbol){
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

function showLoadingGraphic() {
    document.getElementById('loadingGraphic').style.display = 'block';
}

function hideLoadingGraphic() {
    document.getElementById('loadingGraphic').style.display = 'none';
}

function positionLoadingGraphic() {
    var chartContainer = document.getElementById('tv_chart_container');
    var loadingGraphic = document.getElementById('loadingGraphic');

    if (chartContainer && loadingGraphic) {
        var rect = chartContainer.getBoundingClientRect();
        var topPosition = rect.top + window.scrollY; // Get the top position relative to the viewport

        loadingGraphic.style.top = topPosition + 'px'; // Set the top position of the loading graphic
    }
}

window.onload = function() {
    loadAllDataSeries(currentSymbol); // Existing function call
};

window.onresize = function() {
    positionLoadingGraphic();
};

// Function to create simple switcher
function createSimpleSwitcher(items, activeItem, activeItemChangedCallback, switcherElementId) {
    console.log("Switcher Element ID: ", switcherElementId);
    let switcherElement = document.getElementById(switcherElementId);
    console.log("Found Element: ", switcherElement);
    if (!switcherElement) {
        console.error(`No element found with ID '${switcherElementId}'`);
        return null;
    }

    let intervalElements = items.map(function (item) {
        let itemEl = document.createElement('button');
        itemEl.innerText = item;
        itemEl.classList.add('switcher-item');
        itemEl.classList.toggle('switcher-active-item', item === activeItem);
        itemEl.addEventListener('click', function () {
            onItemClicked(item);
        });
        switcherElement.appendChild(itemEl);
        return itemEl;
    });

    function onItemClicked(item) {
        if (item === activeItem) {
            return;
        }

        intervalElements.forEach(function (element, index) {
            element.classList.toggle('switcher-active-item', items[index] === item);
        });

        activeItem = item;

        if (activeItemChangedCallback) {
            activeItemChangedCallback(item);
        }
    }

    return switcherElement;
}

// Function to create the interval switcher
function createIntervalSwitcher() {
    const intervals = ['5 min Increments', 'Daily', 'Weekly Averages', 'Monthly Averages', 'Yearly Averages'];
    return createSimpleSwitcher(intervals, intervals[0], handleIntervalSelectionChange, 'interval-switcher');
}

// Function to create the field switcher
function createFieldSwitcher() {
    const fields = ['All', 'Open Price', 'High Price', 'Low Price', 'Close Price', 'Stock Volume'];
    return createSimpleSwitcher(fields, fields[0], handleFieldSelectionChange, 'field-switcher');
}

// Define global variables for interval and field switchers
let intervalSwitcher;
let fieldSwitcher;

document.addEventListener('DOMContentLoaded', function () {
    // Create interval and field switchers and append them to their containers
    intervalSwitcher = createIntervalSwitcher();
    fieldSwitcher = createFieldSwitcher();
    
    // Get interval and field switcher containers
    const intervalSwitcherContainer = document.getElementById('interval-switcher');
    const fieldSwitcherContainer = document.getElementById('field-switcher');

    // Function to create and append a switcher if it's not already present
    function createAndAppendSwitcher(container, switcherFunction) {
        if (!container.querySelector('.switcher-item')) {
            container.innerHTML = ''; // Clear the container's content
            const switcher = switcherFunction();
            container.appendChild(switcher);
        }
    }

    // Create and append interval and field switchers if they are not present
    createAndAppendSwitcher(intervalSwitcherContainer, createIntervalSwitcher);
    createAndAppendSwitcher(fieldSwitcherContainer, createFieldSwitcher);
});







