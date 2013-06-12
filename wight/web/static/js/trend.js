var addLineGraph = function(element, data) {
    nv.addGraph(function() {
        var chart = nv.models.lineChart();
        chart.margin({ left: 100, bottom: 80 });
        chart.xAxis.tickFormat(function(d) {
            if (d % 1 == 0) {
                return "Test #" + d;
            }
        });
        chart.yAxis.tickFormat(function(d) { return floatFormat(d) + " secs"; });
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

addLineGraph(".pps svg", getData(concurrentUsers, testsQuantity, ppsValues));
addLineGraph(".response-time svg", getData(concurrentUsers, testsQuantity, averageResponseTimeValues));
