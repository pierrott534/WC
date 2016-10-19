<?php
$server="localhost";
$user="cumulus";
$pass="6T6mtok";
$db="meteo";
mysqli_connect($server,$user,$pass) or die ("Erreur SQL : ".mysql_error() );
mysql_select_db($db) or die ("Erreur SQL : ".mysql_error() );
?>
