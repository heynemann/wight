var addLineGraph = function(element, data, xTickFormat, yTickFormat, yLabel) {
    nv.addGraph(function() {
        var chart = nv.models.lineChart();
        chart.margin({ left: 100, bottom: 80 });
        chart.xAxis.tickFormat(xTickFormat);
        chart.yAxis.tickFormat(yTickFormat);
        if (yLabel) {
            chart.yAxis.axisLabel(yLabel)
        }
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

addLineGraph(".pps svg", getData(concurrentUsers, testsQuantity, ppsValues), d3.format(',r'), d3.format('.02f'));
addLineGraph(".response-time svg", getData(concurrentUsers, testsQuantity, responseTimeValues), function(d) { return "Test #" + d; }, function(d) { return floatFormat(d) + " secs"; });
