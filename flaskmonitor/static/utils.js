/*
 * File: flaskmonitor/static/utils.js
 * Author: Luke Campbell
 * Date: Tue Jan  8 11:27:45 EST 2013
 */


function timedRefresh(timeoutPeriod) {
    setTimeout("location.reload(true);", timeoutPeriod);
}

function redirectTo(url, timeoutPeriod) {
    setTimeout("location.replace('" + url + "');", timeoutPeriod); 
}
