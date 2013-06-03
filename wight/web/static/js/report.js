    var getResponseTimeData = function(data) {
        var results = [
            { key: "Min", values: [] },
            { key: "p10", values: [] },
            { key: "Median", values: [] },
            { key: "Average", values: [] },
            { key: "p90", values: [] },
            { key: "p95", values: [] },
            { key: "Max", values: [] }
        ];
        var fields = ["min", "p10", "med", "avg", "p90", "p95", "max"];

        for (var i=0; i<data.length; i++) {
            var cu = data[i][0];

            for (var fieldIndex=0; fieldIndex < fields.length; fieldIndex++) {
                results[fieldIndex].values.push({
                    x: cu,
                    y: data[i][fieldIndex + 1]
                });
            }
        }

        return results;
    };

    var drawResponseGraph = function(element, data) {
        nv.addGraph(function() {
            var chart = nv.models.multiBarChart()
                .showControls(false)
                .reduceXTicks(false);

            chart.margin({
                left: 100,
                bottom: 80
            });

            chart.xAxis
                .axisLabel("Concurrent users")
                .showMaxMin(true)
                .tickFormat(d3.format(',f'));

            chart.yAxis
                .axisLabel("Duration (s)")
                .showMaxMin(true)
                .tickFormat(d3.format(',.1f'));

            var results = getResponseTimeData(data);

            d3.select(element)
                .datum(results)
                .transition().duration(500).call(chart);

            nv.utils.windowResize(chart.update);

            return chart;
        });
    };

    var drawResultGraph = function(element, data, xLabel, yLabel) {
        nv.addGraph(function() {
            var chart = nv.models.lineChart();

            chart.margin({
                left: 100,
                bottom: 80
            });

            chart.xAxis
                .tickFormat(d3.format(',r'));

            if (xLabel != null) {
                chart.xAxis.axisLabel(xLabel);
            }

            chart.yAxis
                .axisLabel(yLabel)
                .tickFormat(d3.format('.02f'));

            d3.select(element)
                .datum(data)
                .transition().duration(500)
                .call(chart);

            nv.utils.windowResize(function() { d3.select(element).call(chart) });
            return chart;
        });
    };

    var testData = [
        { values: testSuccessData, key: "Successful tests per second", color: "#597800" },
        { values: testFailedData, key: "Failed tests per second", color: "#ca0000" }
    ];

    var pageData = [
        { values: pageSuccessData, key: "Successful tests per second", color: "#597800" },
        { values: pageFailedData, key: "Failed tests per second", color: "#ca0000" }
    ];

    var requestData = [
        { values: requestSuccessData, key: "Successful tests per second", color: "#597800" },
        { values: requestFailedData, key: "Failed tests per second", color: "#ca0000" }
    ];

    var apdex = [
        { key: "Concurrent Users", values: apdexData }
    ];

    drawResultGraph('.test-stats svg', testData, 'Concurrent users', 'Tests per second');
    drawResultGraph('.page-stats svg', pageData, null, 'Pages per second');
    drawResultGraph('.request-stats svg', requestData, 'Concurrent users', 'Requests per second');
    drawResponseGraph('.page-response-time svg', pageResponseTimeData);
    drawResponseGraph('.request-response-time svg', requestResponseTimeData);

    nv.addGraph(function() {
        var chart = nv.models.discreteBarChart()
            .x(function(d) { return d.label })
            .y(function(d) { return d.value })
            .staggerLabels(true)
            .tooltips(false)
            .showValues(true);

        chart.margin({
            left: 100,
            bottom: 80
        });

        chart.xAxis
            .axisLabel("Concurrent users");

        chart.yAxis
            .axisLabel("Apdex 1.5")
            .showMaxMin(false)
            .tickFormat(d3.format('.02f'));

        d3.select('.page-apdex svg')
            .datum(apdex)
            .transition().duration(500)
            .call(chart);

        nv.utils.windowResize(chart.update);

        return chart;
    });
