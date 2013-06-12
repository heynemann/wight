var floatFormat = function(num) {
    return Math.round(num * 100) / 100;
};

var addLineGraph = function(element, data, yTickLabelName, xTickValues, yTickValues) {
    if (!yTickLabelName) {
        yTickLabelName = "";
    }
    nv.addGraph(function() {
        var chart = nv.models.lineChart();
        chart.margin({ left: 100, bottom: 80 });
        chart.xAxis.tickFormat(function(d) {
            if (d % 1 == 0) {
                return "Test #" + d;
            }
        });
        chart.xAxis.tickValues(xTickValues);
        if (yTickValues) {
            chart.yAxis.tickValues(yTickValues);
        }
        var formatter = d3.format('.01f');
        chart.yAxis.tickFormat(function(d) { return formatter(d) + yTickLabelName; });
        d3.select(element)
            .datum(data)
            .transition().duration(500)
            .call(chart);
        nv.utils.windowResize(chart.update);
        return chart;
    });
};

var getData = function(concurrentUsers, tests, values) {
    var testData = [];

    for (var index in concurrentUsers) {
        var cycle = {
            key: concurrentUsers[index] + " Concurrent Users",
            values:[]
        };
        testData.push(cycle);
        for (var test=0; test < tests; test++) {
            cycle.values.push({
                x: test + 1,
                y: values[index][test]
            });
        }
    }

    return testData;
};

var testsNumbers = [];
for (var i = 1; i <= testsQuantity; i++) {
    testsNumbers.push(i);
}
var apdexRangeValues = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0];

addLineGraph(".apdex svg", getData(apdexConcurrentUsers, testsQuantity, apdexValues), "", testsNumbers, apdexRangeValues);
addLineGraph(".pps svg", getData(pageConcurrentUsers, testsQuantity, ppsValues), " pages", testsNumbers);
addLineGraph(".response-time svg", getData(pageConcurrentUsers, testsQuantity, averageResponseTimeValues), " secs", testsNumbers);
