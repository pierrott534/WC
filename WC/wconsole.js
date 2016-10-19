// CumulusWeatherConsole
//
// by David A Jamieson
// daj@findmyinbox.co.uk
//
// Version 1.2 - 12 Jan 2010
//

// Edit the next two lines.  The first to note the location of your cumulus realtime.txt file on your web server
// the second line notes how often to refresh the display in seconds.  

var realtime_location="realtime.txt";
var jour_location="sunbird.txt";
var update_seconds=15;


// DO NOT change anything below here.
// ---------------------------------------------------------------------------------------------------------------
//


var tick_counter=0;
var first_run=1;
setInterval('getlivedata()', 1000); 

function getlivedata() {

if (tick_counter <= 0) {


// read realtime.txt file and parse it using a space

 var d = new Date();
 var realdata = $.ajax({url: realtime_location + "?" + d.getTime(), async: false, dataType: "html" }).responseText;
 var jourdata = $.ajax({url: jour_location + "?" + d.getTime(), async: false, dataType: "html" }).responseText;


 if (jourdata.indexOf(jour_location) == -1 ) {    
 var rawdata=jourdata.split('|');
 // Set all IDs to their values
 $("#matin").html(rawdata[2]);
 $("#soir").html(rawdata[3]);}


 if (realdata.indexOf(realtime_location) == -1 ) {    
 var rawdata=realdata.split(' ');
 // Set all IDs to their values
 $("#temp").html(rawdata[2]+" &deg;"+rawdata[14]);
 $("#intemp").html(rawdata[22]+" &deg;"+rawdata[14]);
 $("#tempss").html(rawdata[55]+" &deg;"+rawdata[14]);
 $("#temptrend").html(rawdata[25]);
 $("#hum").html(rawdata[3]+"%");
 $("#inhum").html(rawdata[23]+" %");

 
 
 $("#rainrate").html(rawdata[8]+" "+rawdata[16]+"/hr");
 $("#raintoday").html(rawdata[9]+" "+rawdata[16]);
 $("#rainhour").html(rawdata[47]+" "+rawdata[16]);
 
 $("#windavg").html(rawdata[5]+" "+rawdata[13]);
 $("#windlatest").html(rawdata[6]+" "+rawdata[13]);
 $("#winddir").html(rawdata[11]);
 $("#pressure").html(rawdata[10]+" "+rawdata[15]);
 $("#presstrend").html(rawdata[18]);
 
 $("#today-temphigh").html(rawdata[26] +" &agrave "+ rawdata[27]);
 $("#today-templow").html(rawdata[28] +" &agrave "+ rawdata[29]);
 $("#today-windgust").html(rawdata[32] +" &agrave "+ rawdata[33]);
 $("#today-windavg").html(rawdata[30] +" &agrave "+ rawdata[31]);
 $("#today-presshigh").html(rawdata[34] +" &agrave "+ rawdata[35]);
 $("#today-presslow").html(rawdata[36] +" &agrave "+ rawdata[37]);

 
 $("#last_contact").html(rawdata[0] +" &agrave "+ rawdata[1]);
 
 // Calculate the Beaufort desc
var beau = rawdata[12];
if (beau=="0"){var bdesc="Calm";} else
if (beau=="1"){var bdesc="Light Air";} else
if (beau=="2"){var bdesc="Light Breeze";} else
if (beau=="3"){var bdesc="Gentle Breeze";} else
if (beau=="4"){var bdesc="Moderate breeze";} else
if (beau=="5"){var bdesc="Fresh breeze";} else
if (beau=="6"){var bdesc="Strong breeze";} else
if (beau=="7"){var bdesc="Near gale";} else
if (beau=="8"){var bdesc="Gale";} else
if (beau=="9"){var bdesc="Strong Gale";} else
if (beau=="10"){var bdesc="Storm";} else
if (beau=="11"){var bdesc="Violent Storm";} else
if (beau=="12"){var bdesc="Hurricane";} else
{ var bdesc="";}
$("#beaufort").html(bdesc);

 // Calculate the forecast
var fcast = rawdata[48];
if (fcast=="0"){var fdesc="unknown!";} else
if (fcast=="1"){var fdesc="Settled fine";} else
if (fcast=="2"){var fdesc="Fine weather";} else
if (fcast=="3"){var fdesc="Becoming fine";} else
if (fcast=="4"){var fdesc="Fine, becoming less settled";} else
if (fcast=="5"){var fdesc="Fine, possible showers";} else
if (fcast=="6"){var fdesc="Fairly fine, improving";} else
if (fcast=="7"){var fdesc="Fairly fine, possible showers early";} else
if (fcast=="8"){var fdesc="Fairly fine, showery later";} else
if (fcast=="9"){var fdesc="Showery early, improving";} else
if (fcast=="10"){var fdesc="Changeable, mending";} else
if (fcast=="11"){var fdesc="Fairly fine, showers likely";} else
if (fcast=="12"){var fdesc="Rather unsettled clearing later";} else
if (fcast=="13"){var fdesc="Unsettled, probably improving";} else
if (fcast=="14"){var fdesc="Showery, bright intervals";} else
if (fcast=="15"){var fdesc="Showery, becoming less settled";} else
if (fcast=="16"){var fdesc="Changeable, some precipitation";} else
if (fcast=="17"){var fdesc="Unsettled, short fine intervals";} else
if (fcast=="18"){var fdesc="Unsettled, precipitation later";} else
if (fcast=="19"){var fdesc="Unsettled, some precipitation";} else
if (fcast=="20"){var fdesc="Mostly very unsettled";} else
if (fcast=="21"){var fdesc="Occasional precipitation, worsening";} else
if (fcast=="22"){var fdesc="Precipitation at times, very unsettled";} else
if (fcast=="23"){var fdesc="Precipitation at frequent intervals";} else
if (fcast=="24"){var fdesc="Precipitation, very unsettled";} else
if (fcast=="25"){var fdesc="Stormy, may improve";} else
if (fcast=="26"){var fdesc="Stormy, much precipitation";} else
{ var fdesc="";}
if (fdesc == "" || fdesc == "unknown!") {
	$("#forecast").hide();
	}
else
	{
	$("#forecast").show();
	}
$("#forecast").html("Forecast: " + fdesc);


if (first_run == "1") {
	$("#wait-msg").hide('');
	$("#c_int").fadeIn('slow');
	$("#c_out").fadeIn('slow');
	$("#c_press").fadeIn('slow');
	$("#c_ephmer").fadeIn('slow');
	$("#c_rain").fadeIn('slow');
	$("#c_wind").fadeIn('slow');
	$("#c_today").fadeIn('slow');
	$("#footer").fadeIn('slow');
	firstrun="0";
}
}
else  // can't load the data file
{
if (first_run == 1)  // only show the error if this is the first attempt at loading it
{
	$("#wait-msg").html('Unable to find the data file');
	}
}


tick_counter=update_seconds;
}
else
{
tick_counter--;
$("#refresh_in").html(tick_counter);
}

}

function popup(mylink, windowname)
{
if (! window.focus)return true;
var href;
if (typeof(mylink) == 'string')
   href=mylink;
else
   href=mylink.href;
window.open(href, windowname, 'width=700,height=560,scrollbars=no');
return false;
}
