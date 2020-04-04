isLiveLoadOn = false;
notificationId = 0;
request_id = 0;
requestTimes = {};

function mmAjax(site, data) {
    this.request_id++;
    // TODO: Find better solution than overwriting web server status or not overwriting it when offline
    this.updateWebServerStatus(null);

    var req = new XMLHttpRequest();
    req.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            responseHandler(JSON.parse(this.responseText));
        } else {
            // console.log("Error (readyState: " + this.readyState + "; status: " + this.status + ")");
        }
    }
    req.open('POST', "/" + site, true);
    req.setRequestHeader('content-type', 'application/x-www-form-urlencoded;charset=UTF-8');
    req.send("request_id=" + this.request_id + "&" + data);
    this.requestTimes[this.request_id] = Date.now();
}

function mmAjaxStatus(cmd) {
    data = "";
    if (cmd != "") {
        data += "cmd=" + cmd;
    }
    mmAjax("ajaxStatus", data);
}

function mmAjaxSignUp(form) {
    /*var elements = form.elements;
    var obj ={};
    for(var i = 0 ; i < elements.length ; i++){
            var item = elements.item(i);
            if(item.tagName == "INPUT"){
                obj[item.name] = item.value;
            }
        }
    console.log(JSON.stringify(obj));
    mmAjax("ajaxSignUp", JSON.stringify(obj));*/

    var elements = form.elements;
    var data = "";
    for (var i = 0; i < elements.length; i++) {
        var item = elements.item(i);
        if (item.tagName == "INPUT") {
            data += item.name + "=" + item.value + "&";
        }
    }
    data = data.substring(0, data.length - 1);
    //console.log(data);
    mmAjax("ajaxSignUp", data);
}

function mmLiveLoad() {
    if (isLiveLoadOn) {
        mmAjax("ajaxStatus", "");
        setTimeout(function () {
            mmLiveLoad();
        }, 1000);
    }
}

function mmLiveLoadOn() {
    isLiveLoadOn = true;
    mmLiveLoad();
}

function mmLiveLoadOff() {
    isLiveLoadOn = false;
}

function responseHandler(res) {
    //console.log(res);

    // Show full JSON Text on status page
    var fullStatusJsonTextElement = document.getElementById("fullStatusJsonText");
    if (fullStatusJsonTextElement != null) {
        fullStatusJsonTextElement.innerHTML = JSON.stringify(res);
    }

    this.updateWebServerStatus(res.request_id);

    for (var obj in res) {
        if (obj == "notification") {
            for (var notification in res[obj]) {
                //console.log(res[obj][notification].msg);
                nid = notificationId++;
                document.getElementById("notification").innerHTML += '<div id="notification' + nid + '" class="alert ' + res[obj][notification].type + ' alert-dismissible fade show" role="alert">' + res[obj][notification].msg + '<button type="button" class="close fade show" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>';
                setTimeout(dismissNotification, 3000, nid);
            }
        } else if (obj == "database") {
            this.updateDatabaseStatus(res.database);
            this.updateStartupPage(res.database);
        } else if (obj == "arduino") {
            this.updateArduinoStatus(res.arduino);
        } else if (obj == "gpio_in") {
            for (var gpio_in in res[obj]) {
                if (res[obj][gpio_in].name == "Scale") {
                    // Waage
                    var inputTextScaleWeight = document.getElementById("inputTextScaleWeight");
                    if (inputTextScaleWeight != null) {
                        inputTextScaleWeight.value = res[obj][gpio_in].value;
                    }
                }
            }
        } else if (obj == "gpio_out") {

        }
    }
}

function updateWebServerStatus(request_id) {
    // Show response time on status page
    var indicatorInnerHTML = "";
    var statusInnerHTML = "";
    if (request_id && request_id in this.requestTimes) {
        //console.log(this.requestTimes)
        var responseTime = Date.now() - this.requestTimes[request_id];
        delete this.requestTimes[request_id];
        indicatorInnerHTML = "<i class='fas fa-server text-success' aria-hidden='true'></i>";
        statusInnerHTML = " &mdash; response time: " + responseTime + " ms";
    } else {
        indicatorInnerHTML = "<i class='fas fa-server text-danger' aria-hidden='true'></i>";
        statusInnerHTML = " &mdash; disconnected";
        updateDatabaseStatus(-1);
        updateArduinoStatus(-1);
    }
    var webserverStatusIndicatorElements = document.getElementsByClassName("webserverStatusIndicator");
    if (webserverStatusIndicatorElements != null) {
        for (var i = 0; i < webserverStatusIndicatorElements.length; i++) {
            webserverStatusIndicatorElements[i].innerHTML = indicatorInnerHTML;
        }
    }
    var webserverStatusTextElement = document.getElementById("webserverStatusText");
    if (webserverStatusTextElement != null) {
        webserverStatusTextElement.innerHTML = statusInnerHTML;
    }
}

function updateDatabaseStatus(status) {
    var indicatorInnerHTML = "";
    var statusInnerHTML = "";
    switch (status) {
        case 0: // 0 => disconnected
            indicatorInnerHTML = "<i class='fas fa-database text-danger' aria-hidden='true'></i>";
            statusInnerHTML = " &mdash; disconnected";
            break;
        case 1: // 1 => connecting
            indicatorInnerHTML = "<i class='fas fa-database text-warning' aria-hidden='true'></i>";
            statusInnerHTML = " &mdash; connecting...";
            break;
        case 2: // 2 => setting up
            indicatorInnerHTML = "<i class='fas fa-database text-info' aria-hidden='true'></i>";
            statusInnerHTML = " &mdash; setting up...";
            break;
        case 3: // 3 => connected
            indicatorInnerHTML = "<i class='fas fa-database text-success' aria-hidden='true'></i>";
            statusInnerHTML = "";
            break;
        default:
            indicatorInnerHTML = "<i class='fas fa-database text-muted' aria-hidden='true'></i>";
            statusInnerHTML = "";
            break;
    }
    var databaseStatusIndicatorElements = document.getElementsByClassName("databaseStatusIndicator");
    if (databaseStatusIndicatorElements != null) {
        for (var i = 0; i < databaseStatusIndicatorElements.length; i++) {
            databaseStatusIndicatorElements[i].innerHTML = indicatorInnerHTML;
        }
    }
    var databaseStatusTextElement = document.getElementById("databaseStatusText");
    if (databaseStatusTextElement != null) {
        databaseStatusTextElement.innerHTML = statusInnerHTML;
    }
}

function updateArduinoStatus(status) {
    var indicatorInnerHTML = "";
    var statusInnerHTML = "";
    switch (status) {
        case 0: // 0 => disconnected
            indicatorInnerHTML = "<i class='fas fa-infinity text-danger' aria-hidden='true'></i>";
            statusInnerHTML = " &mdash; disconnected";
            break;
        case 1: // 1 => connecting
            indicatorInnerHTML = "<i class='fas fa-infinity text-warning' aria-hidden='true'></i>";
            statusInnerHTML = " &mdash; connecting...";
            break;
        case 2: // 2 => setting up
            indicatorInnerHTML = "<i class='fas fa-infinity text-info' aria-hidden='true'></i>";
            statusInnerHTML = " &mdash; setting up...";
            break;
        case 3: // 3 => connected
            indicatorInnerHTML = "<i class='fas fa-infinity text-success' aria-hidden='true'></i>";
            statusInnerHTML = "";
            break;
        default:
            indicatorInnerHTML = "<i class='fas fa-infinity text-muted' aria-hidden='true'></i>";
            statusInnerHTML = "";
            break;
    }
    var arduinoStatusIndicatorElements = document.getElementsByClassName("arduinoStatusIndicator");
    if (arduinoStatusIndicatorElements != null) {
        for (var i = 0; i < arduinoStatusIndicatorElements.length; i++) {
            arduinoStatusIndicatorElements[i].innerHTML = indicatorInnerHTML;
        }
    }
    var arduinoStatusTextElement = document.getElementById("arduinoStatusText");
    if (arduinoStatusTextElement != null) {
        arduinoStatusTextElement.innerHTML = statusInnerHTML;
    }
}

function updateStartupPage(db_status) {
    let startup_db_status_text_element = document.getElementById("startup-db-status-text");
    if (startup_db_status_text_element != null) {
        switch (db_status) {
            case 0: // 0 => disconnected
                startup_db_status_text_element.innerHTML = 'Database is disconnected.';
                break;
            case 1: // 1 => connecting
                startup_db_status_text_element.innerHTML = 'Database is connecting...';
                break;
            case 2: // 2 => setting up
                startup_db_status_text_element.innerHTML = 'Database is setting up...';
                break;
            case 3: // 3 => connected
                startup_db_status_text_element.innerHTML = 'Database is connected.';
                location.reload();
                break;
            default:
                // startup_db_status_text_element.innerHTML = '';
                break;
        }
    }
}