isLiveLoadOn = false;
notificationId = 0;

function mmAjax(site, data) {
    var req = new XMLHttpRequest();
    req.onreadystatechange = function()
    {
      if(this.readyState == 4 && this.status == 200) {
        responseHandler(JSON.parse(this.responseText));
      } else {
    	  	console.log("Error");
      }
    }
    req.open('POST', "/" + site, true);
    req.setRequestHeader('content-type', 'application/x-www-form-urlencoded;charset=UTF-8');
    req.send(data);
}

function mmAjaxStatus(cmd) {
    data = "";
    if(cmd != ""){
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
    for(var i = 0 ; i < elements.length ; i++){
    		var item = elements.item(i);
    		if(item.tagName == "INPUT"){
    			data += item.name + "=" + item.value + "&";
    		}
    	}
    data = data.substring(0, data.length-1);
    console.log(data);
    mmAjax("ajaxSignUp", data);
}

function mmLiveLoad(){
	if(isLiveLoadOn){
		mmAjax("ajaxStatus","");
		setTimeout(function() {
		    mmLiveLoad();
		}, 1000);
	}
}

function mmLiveLoadOn(){
	isLiveLoadOn = true;
	mmLiveLoad();
}

function mmLiveLoadOff(){
	isLiveLoadOn = false;
}

function responseHandler(res){
	console.log(res);
	
	for(var obj in res){
		if(obj == "notification"){
			for (var notification in res[obj]){
				console.log(res[obj][notification].msg);
				nid = notificationId++;
				document.getElementById("notification").innerHTML += '<div id="notification' + nid + '" class="alert ' + res[obj][notification].type + ' alert-dismissible fade show" role="alert">' + res[obj][notification].msg + '<button type="button" class="close fade show" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>';
				setTimeout(dismissNotification, 3000, nid);
			}
		}else if(obj == "gpioin"){
			for (var gpioin in res[obj]){
				if(res[obj][gpioin].name == "Scale"){
					// Waage
					var inputTextScaleWeight = document.getElementById("inputTextScaleWeight");
					if(inputTextScaleWeight != null){
						inputTextScaleWeight.value = res[obj][gpioin].value;
					}
				}
			}
		}else if(obj == "gpioout"){
			
		}
	}
}

function dismissNotification(nid) {
	n = document.getElementById("notification" + nid);
	if(n != null){
		$("#notification" + nid).alert("close")
	}
}