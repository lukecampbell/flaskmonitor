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
            console.debug(data);
            drawChart(data,comp);
        }
    });
}


function initialize() {
    vars.forEach(function(val) { 
        getData(val);
    });
}

function redraw() { 
    if(initialized) {
        initialize();
    }
}

function onLoad(delay) {
    window.setInterval(redraw, delay);
}

