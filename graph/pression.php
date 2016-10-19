<?php
// appel du script de connexion
require("mysqli_connect.php");

// Récupération des données sur les dernières 48 heures avec un tri ascendant sur le timestamp
$sql = "SELECT LogDateTime, press from Bourgoin";  
$query=mysqli_query($link, $sql);                   
$i=0;
while ($list = mysqli_fetch_assoc($query)) {      

$LogDateTime[$i]=$list['LogDateTime'];
$press[$i]=$list['press']*1;

$i++;
} 
?>

<script type="text/javascript"> 
eval(<?php echo "'var LogDateTime = ".json_encode($LogDateTime)."'" ?>);
eval(<?php echo "'var pression = ".json_encode($press)."'" ?>);
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
        $(function() {
            $('#container').highcharts({
		chart: {
                	zoomType: 'x'
            	},
                title: {
                    text: 'Evolution Pression',
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
                    categories: LogDateTime
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
                    valueSuffix: 'hPa'
                },
                legend: {
                    layout: 'vertical',
                    align: 'right',
                    verticalAlign: 'middle',
                    borderWidth: 0
                },
                series: [{
                    name: 'Pression',
                    data: pression
                }]
            });
        });
    </script>
  </head>
  <body>
    <div id="container" style="min-width: 400px; height: 400px; margin: 0 auto"></div>
  </body>
</html>
