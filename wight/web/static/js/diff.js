var floatFormat = function(num) {
    return Math.round(num * 100) / 100;
};

var addLineGraph = function(element, data, yLabel, yTickLabel) {
    nv.addGraph(function() {
        var chart = nv.models.lineChart();
        chart.margin({
            left: 100,
            bottom: 80
        });
        chart.xAxis
            .tickFormat(function(d) { return d.toString() + " users" });

        chart.yAxis
            .axisLabel(yLabel)
            .tickFormat(function(d) { return floatFormat(d).toString() + yTickLabel });

        d3.select(element)
            .datum(data)
            .transition().duration(500)
            .call(chart);

        nv.utils.windowResize(chart.update);

        return chart;
    });
};

var addDiscreteBarGraph = function(element, data, yLabel, yTickLabel) {
    nv.addGraph(function() {
        var chart = nv.models.discreteBarChart()
            .x(function(d) { return d.label })
            .y(function(d) { return d.value })
            .staggerLabels(true)
            .tooltips(false)
            .showValues(false);

        chart.margin({
            left: 100,
            bottom: 80
        });

        chart.xAxis
            .tickFormat(function(d) { return d.toString() + " users" });

        chart.yAxis
            .axisLabel(yLabel)
            .tickFormat(function(d) { return floatFormat(d).toString() + yTickLabel });

        d3.select(element)
            .datum(data)
            .transition().duration(500)
            .call(chart);

        nv.utils.windowResize(chart.update);

        return chart;
    });
};

var getPercentage = function(index, data) {
    return ((data[1].values[index].y - data[0].values[index].y) / data[0].values[index].y) * 100;
};

var createPercentageData = function(cycles, data) {
    var values = [];
    for (var i = 0; i < cycles; i++) {
        values.push({
            label: data[0].values[i].x,
            value: getPercentage(i, data)
        })
    }
    return [{
        key: "Percentage of Improvement",
        values: values
    }];
};

var getData = function(referenceValues, challengerValues) {
    return [
        {key: 'Reference Report', color: '#5c8800', values: referenceValues},
        {key: 'Challenger Report', color: '#ff7f00', values: challengerValues}
    ]
};

var requestData = getData(referenceRequestPerSecondValues, challengerRequestPerSecondValues);
var requestAverageData = getData(referenceResponseTimeAverageValues, challengerResponseTimeAverageValues);

addLineGraph('.request-rps svg', requestData, "Requests per second", " rps");
addDiscreteBarGraph('.request-percentage svg', createPercentageData(cycles, requestData), "Improvement %", "%");
addLineGraph('.request-average svg', requestAverageData, "Response time - Average", " sec");
addDiscreteBarGraph('.request-average-percentage svg', createPercentageData(cycles, requestAverageData), "Improvement %", "%");

addLineGraph('.request-median svg', getData(referenceResponseTimeMedianValues, challengerResponseTimeMedianValues), "Response time - Median", " sec");
addLineGraph('.request-p90 svg', getData(referenceResponseTimeP90Values, challengerResponseTimeP90Values), "Response time - p90", " sec");
addLineGraph('.request-max svg', getData(referenceResponseTimeMaxValues, challengerResponseTimeMaxValues), "Response time - Max", " sec");
addLineGraph('.page-pps svg', getData(referencePagePerSecondsValues, challengerPagePerSecondsValues), "Pages per second", " pps");
