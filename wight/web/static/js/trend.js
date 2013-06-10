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
        for (var test=1; test < tests; test++) {
            cycle.values.push({
                x: test,
                y: values[index][test]
            });
        }
    }

    return testData;
};

var getResponseTimeTestData = function() {
    var testData = [];

    for (var cu=20; cu < 160; cu += 20) {
        var cycle = {
            key: cu + " Concurrent Users",
            values:[]
        };
        testData.push(cycle);

        for (var test=1; test < 37; test++) {
            cycle.values.push({
                x: test,
                y: 0.2 + Math.random() + cu / 100
            });
        }
    }

    return testData;
};

addLineGraph(".pps svg", getData(ppsConcurrentUsers, ppsTests, ppsValues), d3.format(',r'), d3.format('.02f'));
addLineGraph(".response-time svg", getResponseTimeTestData(), function(d) { return "Test #" + d; }, function(d) { return floatFormat(d) + " secs"; });
