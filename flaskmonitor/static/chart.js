/*
 * flaskmonitor/static/chart.js
 * Author: Luke Campbell
 * Dependencies:
 * 
        <script type='text/javascript' src='http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js'> </script>
        <script type="text/javascript" src="https://www.google.com/jsapi"></script>
 */

google.load("visualization", "1", {packages:["corechart"]});
google.setOnLoadCallback(initialize);

var initialized = false;
function drawChart(rawData, variable) {
    var data = google.visualization.arrayToDataTable(rawData.values);
    var options = {
               title: variable,
               hAxis: {title: "Time", minValue: 0, maxValue: 5},
               vAxis: {title: variable, minValue: rawData.min, maxValue: rawData.max},
        legend: "none"
    };

    var chart = new google.visualization.ScatterChart(document.getElementById(variable + "_div"));
    google.visualization.events.addListener(chart, 'select', function(e) {
        window.location = '/data/' + pid + '/' + variable + '.csv';
    });
    chart.draw(data, options);
    initialized = true;
}
function getData(comp) {
    $.ajax({
        url: "/data/"+ pid +"/" + comp + ".json",
        type: "GET",
        contentType: "application/json;charset=utf-8",
        dataType: "json",
        beforeSend: function(x) {
            if ( x && x.overrideMimeType) {
                x.overrideMimeType("application/json;charset=utf-8");
            }
        },
        success: function(data) {
            drawChart(data,comp);
        }
    });
}

function updateStat(stat,value) {
    $('#' + stat).text(value);
}

function refreshStats() {
    $.ajax({
        url: "/stat/" + pid + ".json",
        type: "GET",
        contentType: "application/json;charset=utf-8",
        dataType: "json",
        beforeSend: function(x) {
            if (x && x.overrideMimeType) {
                x.overrideMimeType("application/json;charset=utf-8");
            }
        },
        success: function(data) {
            Object.keys(data).forEach(function(key) { 
                updateStat(key, data[key]);
            });
        }
    });
}


function initialize() {
    vars.forEach(function(val) { 
        getData(val);
    });
    refreshStats();
}

function redraw() { 
    if(initialized) {
        initialize();
    }
}

function onLoad(delay) {
    window.setInterval(redraw, delay);
}

