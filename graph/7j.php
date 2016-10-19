<?php
// appel du script de connexion
require("mysqli_connect.php");
// On récupère le timestamp du dernier enregistrement
$sql="select max(tstamp) from Bourgoin";
$query=mysqli_query($link, $sql);                  
$list=mysqli_fetch_array($query);
// On détermine le stop et le start de façon à récupérer dans la prochaine requête que les données des dernières xx heures
$stop=$list[0];
$start=$stop-(86400*7);//86400=24 heures donc 86400*2=48 heures
// Récupération des données sur les dernières 48 heures avec un tri ascendant sur le timestamp
$sql = "SELECT tstamp, temp, hum, press, wlatest FROM Bourgoin where tstamp >= '$start' and  tstamp <= '$stop' ORDER BY 1";  
$query=mysqli_query($link, $sql);                   
$i=0;
while ($list = mysqli_fetch_assoc($query)) {      
if (date("I",time())==0) { 
	$time[$i]=($list['tstamp']+3600)*1000;
	} 
else {
	$time[$i]=($list['tstamp']+7200)*1000;
  } 

$temp[$i]=$list['temp']*1;
$hum[$i]=$list['hum']*1;
$press[$i]=$list['press']*1;
$wlatest[$i]=$list['wlatest']*1;

$i++;
} 
 ?>

<script type="text/javascript"> 
eval(<?php echo  "'var time =  ".json_encode($time)."'" ?>);
eval(<?php echo  "'var temp =  ".json_encode($temp)."'" ?>);
eval(<?php echo  "'var hum =  ".json_encode($hum)."'" ?>);
eval(<?php echo  "'var press =  ".json_encode($press)."'" ?>);
eval(<?php echo  "'var wlatest =  ".json_encode($wlatest)."'" ?>);
</script>


<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
  <head>
    <title>
      Bourgoin Jallieu
    </title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">

    <script src="http://code.jquery.com/jquery-1.9.1.js" type="text/javascript"></script>
    <script src="http://code.highcharts.com/highcharts.js" type="text/javascript"></script>
    <script src="http://code.highcharts.com/modules/exporting.js" type="text/javascript"></script>
    <script type="text/javascript">

    function comArr(unitsArray) { 
        var outarr = [];
        for (var i = 0; i < time.length; i++) {
         outarr[i] = [time[i], unitsArray[i]];
        }
      return outarr;
    }


        $(function() {
            $('#container').highcharts({
		chart: {
                	zoomType: 'x'
            	},
                title: {
                    text: 'Météo des derniers 7 jours',
                    x: -20 //center
                },
                subtitle: {
                    text: 'Source: Meteo a Bourgoin Jallieu',
                    x: -20
                },
		credits: {
            		text: '© Evolution Météo Pierre TIROLE',
            		href: 'http://vps185773.ovh.net/graph/'
		},
                xAxis: {
//                    categories: time
			type:'datetime',
			startOnTick:false,
                },
                yAxis: {
                    title: {
                        text: 'Pression (hPa)'
                    },
                    plotLines: [{
                        value: 1013,
                        width: 1,
                        color: '#FF0000'
                    }]
                },
                tooltip: {
                    valueSuffix: '°C'
                },
                legend: {
                    layout: 'vertical',
                    align: 'right',
                    verticalAlign: 'middle',
                    borderWidth: 0
                },
                series: [{
                    name: 'Température',
                    data: comArr(temp)
		},{
                    name: 'Humidité',
                    data: comArr(hum)
		},{
                    name: 'Pression',
                    data: comArr(press)
		},{
                    name: 'Vitesse du vent',
                    data: comArr(wlatest)
                }]
            });
        });
    </script>
  </head>
  <body>
    <div id="container" style="min-width: 400px; height: 400px; margin: 0 auto"></div>
  </body>
</html>
