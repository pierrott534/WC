<?php
//-----------------------------------------------------------------
// Import Cumulus Monthly Log file into MySql database
// Author: David A Jamieson, daj@findmyinbox.co.uk
//
// Ver 1.1b - 04/02/10
// Ver 1.1c - 11/03/10
// ver 1.2  - 06/05/11, Mark Crossley, updated for Cumulus 1.9.1
// ver 1.3  - 27/11/12, Mark Crossley, updated for Cumulus b1050
// ver 1.3a - 30/11/12, Mark Crossley, added line breaks to text output
// ver 1.3b - 30/11/12, Mark Crossley, changed so ALL missing values from
//            from the dayfile are entered into the table as NULL. If you have
//            used the Cumulus editor, then they will be present in the file as
//            blank fields.
// ver 1.4  - 04/12/12, Mark Crossley, added realtime logging
// ver 1.4a - 04/12/12, Mark Crossley Fixed syntax errors, added parameter presence checking.
// ver 1.4b - 07/12/12, Mark Crossley Tidying
// ver 2.0  - 20/12/12, Mark Crossley
//           * Change monthly and realtime tables to use combined date/time columns rather than separate
//           * Added optional retention time for realtime table. Records older than
//             the specified age will be deleted. retainVal=NNN retainUnit=XXXX
//           * Added checking to allow running of the script from a command line as well as via http
//           * Added 'extra' columns to record wind directions as compass points where they are only provided as bearings:
//              Dayfile:  Added the following columns:- HWindGBearSym, DomWindDirSym
//              Monthly:  Added the following columns:- WindbearingSym, CurrWindBearingSym
// ver 2.1  - 29/03/13, Mark Crossley
//           * Fixed typo in day file table field name LowDewPint -> LowDewPoint
// ver 2.2  - 21/05/13, Mark Crossley
//           * Made dayfile UV a decimal(3,1) field rather than varchar(4)
// ver 2.3  - 05/06/13, Mark Crossley
//           * Fixed dayfile & monthfile table column HoursSun was decimal(2,1) to decimal(3,1)
// ver 2.4  - 23/10/13, Mark Crossley
//           * Changed day file humidity fields from varchar(3) to decimal(4,1)
// ver 2.5  - 03/12/13, Mark Crossley
//           * Changed day file HighSolarRad from varchar(5) to decimal(5,1)
//              To alter an existing table...
//              ALTER TABLE `dayfile` CHANGE `HighSolarRad` `HighSolarRad` DECIMAL(5,1) NULL DEFAULT NULL
// ver 2.6  - 02/04/14, Mark Crossley
//           * Fixed PHP vulnerability that could reveal the passcode
// ver 2.7  - 22/02/15, Mark Crossley
//           * Fixed realtime/monthly/day tables creates, to make rainfall 2dp to allow for inches
//           * Fixed monthly table create, to make evapotrans 2 dp
//           * Converted from depreciated mysql to mysqli
//-----------------------------------------------------------------
//
// USING THIS SCRIPT
//
// Currently you can import two file types from Cumulus -- the dayfile and the Monthly log files.
//
// Firstly decide the table to be populated in your SQL database.  If the table does not exist
// the script will create it.  Typically you have one table for the dayfile, and one or more for the
// Monthly Logs.  You could import every monthly log file into one large SQL table.
// If you re-import existing data the script will update the data in the table so you can run the
// import every day on the same file, dayfile, for example
//
//
// You must pass several options with your URL...
// They can be in any order but the first one must start with ? other with &
//
// type=xxxx
//    this must be either the phrase dayfile, monthly, or realtime
//
// file=xxxxx
//    the location on your webserver, relative to this script location, of your Cumulus File
//    example file=dayfile.txt  or file=../data/dayfile.txt
//
// table=xxxx
//    the table within SQL to import the data.  If it does not exist the script will create it
//
// key=xxxxx
//    A security key, unique to you, to pass as part of the URL.  This stops others from
//    running the script on your server if the do not know the key.
//
// retainVal=nnn [optional]
//    The elapsed of 'retainUnit's to keep in the realtime table. Records older than nnnUnits will be deleted.
//
// retainUnit=xxxx [optional, mandatory if retainVal supplied]
//    The units to be applied to retainVal, valid values are: second, minute, hour, day, week, month, quarter, or year
//
//  Example URLs...
//    htp://www.myserver.com/ImportCumulusFile.php?type=dayfile&key=letmein&table=Dayfile&file=/data/dayfile.txt
//    htp://www.myserver.com/ImportCumulusFile.php?type=monthly&key=letmein&table=Monthly&file=/data/oct12log.txt
//    htp://www.myserver.com/ImportCumulusFile.php?type=realtime&key=letmein&table=Realtime&file=/realtime.txt&retainVal=10&retainUnit=hour
//
// COMMAND LINE
// It is also possible to run this script from a PHP command line, eg via a cron job in Linux, or a scheduled task in Windows.
// Example of a 'Windows' command line...
//    php importcumulusfile.php file=realtime.txt table=Realtime type=realtime key=letmein retainVal=48 retainUnit=hour
//

// EDIT THIS NEXT SECTION CAREFULLY
// ----------------------------------------------------------------
// Your security key you will pass in the URL, change this to
// something unique to you
$key = 'letmein';
//
// The server host name or number running your MySQL database
// usually 127.0.0.1 or localhost will suffice
$dbhost = '127.0.0.1';
//
// The username used to log-in to your database server
$dbuser = 'cumulus';
//
// The password used to log-in to your database server
$dbpassword = '6T6mtok';
//
// The name of the MySQL database we will store the tables in
$database = 'meteo';
//
// A better way of entering your login details is to put them in a separate script
// and include this here. This script should be placed in an area accessible to PHP
// but not web users. Your login details will not then beexposed by crashing this
// script.
// e.g. ...
include ('db_ro_details.php');

//
// Enable debug messages? Disable for production use
$debug = false;

//
// The following three variables tell the system about how your
// data file is structure.
// They are set to the UK format, however if you are in another
// country please consider these carefully
//
// You need to tell the script how your file is delimited -- That is,
// how each entry in the line of the file is separated
// in the UK this is a comma.  It may be a semi-colon or something else
// Also consider how your date is delimited.  In the UK this is a slash
// but it may be a dash.  Look at the file you are importing
//
// You need to also note what your decimal separator is, either a comma
// or a dot
//

$field_delimiter = ',';
$date_delimiter = '/';
$date_format = 'DMY'; //or MDY or YMD
$decimal_separator = '.';
$compassp = array('N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW');

//
//
// --------- Nothing to edit below here ---------------------------
//-----------------------------------------------------------------
$validtypes = array('dayfile', 'monthly', 'realtime');
$validunits = array('second', 'minute', 'hour', 'day', 'week', 'month', 'quarter', 'year');
$mandatoryVars = array('file', 'table', 'type', 'key');
$param_retainVal = 0;
// ---- Validation checks ----

// Are we running from a command line?
if (PHP_SAPI === 'cli') {
    // Running from command line, push arguments into http argument $_GET array
    // format so that we use one set of parameter checking code
    parse_str(implode('&', array_slice($argv, 1)), $_GET);
    $lf = "\n";
    if ($debug) echo 'Running from CLI'.$lf;
} else {
    $lf = '<br />';
    if ($debug) echo 'Running from web server'.$lf;
}

// scan for the mandatory script parameters
foreach($mandatoryVars as $p) {
    if (isset($_GET[$p])) {
        // store param value in variable prefixed with 'param_' + name
        ${"param_$p"} = $_GET[$p];
        // PHP 5.4 - isset() no longer returns false is value is null, so explicitly check it
        if (${"param_$p"} === '') {
            die("Error: You must supply a value for the '$p' parameter");
        }
    } else {
        die("Error: You must supply a '$p' parameter/value");
    }
}

// check type param value is valid
if (!in_array($param_type, $validtypes)) {
    die("Error: Invalid import 'type' supplied - '$param_type'");
}

// check for optional realtime parameters
if ($param_type === 'realtime') {
    if (isset($_GET['retainVal'])) {
        $param_retainVal = $_GET['retainVal'];
        // if retainVal is supplied, then retainUnit is mandatory
        if (isset($_GET['retainUnit'])) {
            $param_retainUnit = strtolower($_GET['retainUnit']);
        } else {
            die('Error: If you supply "retainVal", then "retainUnit" must also be provided');
        }
    }
}

// check for the 'security' key
if ($key !== '' && $param_key !== $key) {
    die('Error: Failed security key check:' . $param_key);
}

// ---- End validation checks ----


echo date('d/m/y - H:i:s', time()) . $lf;
echo "Importing to table: $param_table ...$lf";

// Setup the variables depending on what type of file we are importing -- Day file or Monthly Log

if ($param_type === 'dayfile') {
    echo "Processing dayfile: $param_file $lf";
    $CreateQuery = "CREATE TABLE $param_table (LogDate date NOT NULL ,HighWindGust decimal(4,1) NOT NULL,HWindGBear varchar(3) NOT NULL,THWindG varchar(5) NOT NULL,MinTemp decimal(5,1) NOT NULL,TMinTemp varchar(5) NOT NULL,MaxTemp decimal(5,1) NOT NULL,TMaxTemp varchar(5) NOT NULL," .
        "MinPress decimal(6,2) NOT NULL,TMinPress varchar(5) NOT NULL,MaxPress decimal(6,2) NOT NULL,TMaxPress varchar(5) NOT NULL,MaxRainRate decimal(4,2) NOT NULL,TMaxRR varchar(5) NOT NULL,TotRainFall decimal(6,2) NOT NULL,AvgTemp decimal(4,2) NOT NULL,TotWindRun decimal(5,1) NOT NULL," .
        "HighAvgWSpeed decimal(3,1),THAvgWSpeed varchar(5),LowHum decimal(4,1),TLowHum varchar(5),HighHum decimal(4,1),THighHum varchar(5),TotalEvap decimal(5,2),HoursSun decimal(3,1),HighHeatInd decimal(4,1),THighHeatInd varchar(5),HighAppTemp decimal(4,1),THighAppTemp varchar(5),LowAppTemp decimal(4,1)," .
        "TLowAppTemp varchar(5),HighHourRain decimal(4,2),THighHourRain varchar(5),LowWindChill decimal(4,1),TLowWindChill varchar(5),HighDewPoint decimal(4,1),THighDewPoint varchar(5),LowDewPoint decimal(4,1),TLowDewPoint varchar(5),DomWindDir varchar(3),HeatDegDays decimal(4,1),CoolDegDays decimal(4,1)," .
        "HighSolarRad decimal(5,1),THighSolarRad varchar(5),HighUV decimal(3,1),THighUV varchar(5),HWindGBearSym varchar(3),DomWindDirSym varchar(3),PRIMARY KEY(LogDate) ) COMMENT = \"Dayfile from Cumulus\"";
    $WindBearField = array(2, 39);
    $StartOfInsertSQL = "INSERT IGNORE INTO $param_table (LogDate,HighWindGust,HWindGBear,THWindG,MinTemp,TMinTemp,MaxTemp,TMaxTemp,MinPress,TMinPress,MaxPress,TMaxPress,MaxRainRate,TMaxRR,TotRainFall,AvgTemp,TotWindRun,HighAvgWSpeed,THAvgWSpeed,LowHum,TLowHum,HighHum,THighHum,TotalEvap,HoursSun," .
        "HighHeatInd,THighHeatInd,HighAppTemp,THighAppTemp,LowAppTemp,TLowAppTemp,HighHourRain,THighHourRain,LowWindChill,TLowWindChill,HighDewPoint,THighDewPoint,LowDewPoint,TLowDewPoint,DomWindDir,HeatDegDays,CoolDegDays,HighSolarRad,THighSolarRad,HighUV,THighUV,HWindGBearSym,DomWindDirSym)";
    $EndFieldCount = 45;
} elseif ($param_type === 'monthly') {
    echo "Processing monthfile: $param_file $lf";
    $CreateQuery = "CREATE TABLE $param_table (LogDateTime DATETIME NOT NULL,Temp decimal(4,1) NOT NULL,Humidity decimal(4,1) NOT NULL,Dewpoint decimal(4,1) NOT NULL,Windspeed decimal(4,1) NOT NULL,Windgust decimal(4,1) NOT NULL,Windbearing VARCHAR(3) NOT NULL," .
        "RainRate decimal(4,2) NOT NULL,TodayRainSoFar decimal(4,2) NOT NULL,Pressure decimal(6,2) NOT NULL,Raincounter decimal(6,2) NOT NULL,InsideTemp decimal(4,1) NOT NULL,InsideHumidity decimal(4,1) NOT NULL,LatestWindGust decimal(5,1) NOT NULL,WindChill decimal(4,1) NOT NULL," .
        "HeatIndex decimal(4,1) NOT NULL,UVindex decimal(4,1),SolarRad decimal(5,1),Evapotrans decimal(4,2),AnnualEvapTran decimal(5,2),ApparentTemp decimal(4,1),MaxSolarRad decimal(5,1),HrsSunShine decimal(3,1),CurrWindBearing varchar(3),RG11rain decimal(4,2),WindbearingSym varchar(3),CurrWindBearingSym varchar(3),PRIMARY KEY (LogDateTime)) COMMENT = \"Monthly logs from Cumulus\"";
    $WindBearField = array(7, 24);
    $StartOfInsertSQL = "INSERT IGNORE INTO $param_table (LogDateTime,Temp,Humidity,Dewpoint,Windspeed,Windgust,Windbearing,RainRate,TodayRainSoFar,Pressure,Raincounter,InsideTemp,InsideHumidity,LatestWindGust,WindChill,HeatIndex,UVindex,SolarRad,Evapotrans,AnnualEvapTran,ApparentTemp,MaxSolarRad,HrsSunShine,CurrWindBearing,RG11rain,WindbearingSym,CurrWindBearingSym)";
    $EndFieldCount = 25;
} elseif ($param_type === 'realtime') {
    echo "Processing realtimefile: $param_file $lf";
    $field_delimiter = ' ';	//fixed delimiter in realtime.txt, so over-ride any user setting
    $date_format = 'DMY'; 	//fixed date format in realtime.txt, so over-ride any user setting
    $CreateQuery = "CREATE TABLE $param_table (LogDateTime DATETIME NOT NULL,temp decimal(4,1) NOT NULL,hum decimal(4,1) NOT NULL,dew decimal(4,1) NOT NULL,wspeed decimal(4,1) NOT NULL,wlatest decimal(4,1) NOT NULL,bearing VARCHAR(3) NOT NULL,rrate decimal(4,2) NOT NULL," .
        "rfall decimal(4,2) NOT NULL,press decimal(6,2) NOT NULL,currentwdir varchar(3) NOT NULL,beaufortnumber varchar(2) NOT NULL,windunit varchar(4) NOT NULL,tempunitnodeg varchar(1) NOT NULL,pressunit varchar(3) NOT NULL,rainunit varchar(2) NOT NULL,windrun decimal(4,1) NOT NULL," .
        "presstrendval varchar(6) NOT NULL,rmonth decimal(4,2) NOT NULL,ryear decimal(4,2) NOT NULL,rfallY decimal(4,2) NOT NULL,intemp decimal(4,1) NOT NULL,inhum decimal(4,1) NOT NULL,wchill decimal(4,1) NOT NULL,temptrend varchar(5) NOT NULL,tempTH decimal(4,1) NOT NULL,TtempTH varchar(5) NOT NULL," .
        "tempTL decimal(4,1) NOT NULL,TtempTL varchar(5) NOT NULL,windTM decimal(4,1) NOT NULL,TwindTM varchar(5) NOT NULL,wgustTM decimal(4,1) NOT NULL,TwgustTM varchar(5) NOT NULL,pressTH decimal(6,2) NOT NULL,TpressTH varchar(5) NOT NULL,pressTL decimal(6,2) NOT NULL,TpressTL varchar(5) NOT NULL," .
        "version varchar(8) NOT NULL,build varchar(5) NOT NULL,wgust decimal(4,1) NOT NULL,heatindex decimal(4,1) NOT NULL,humidex decimal(4,1) NOT NULL,UV decimal(3,1) NOT NULL,ET decimal(4,2) NOT NULL,SolarRad decimal(5,1) NOT NULL,avgbearing varchar(3) NOT NULL,rhour decimal(4,2) NOT NULL," .
        "forecastnumber varchar(2) NOT NULL,isdaylight varchar(1) NOT NULL,SensorContactLost varchar(1) NOT NULL,wdir varchar(3) NOT NULL,cloudbasevalue varchar(5) NOT NULL,cloudbaseunit varchar(2) NOT NULL,apptemp decimal(4,1) NOT NULL,SunshineHours decimal(3,1) NOT NULL,CurrentSolarMax decimal(5,1) NOT NULL," .
        "IsSunny varchar(1) NOT NULL,PRIMARY KEY (LogDateTime)) COMMENT = \"Realtime log\"";
    $StartOfInsertSQL = "INSERT IGNORE INTO $param_table (LogDateTime,tstamp,temp,hum,dew,wspeed,wlatest,bearing,rrate,rfall,press,currentwdir,beaufortnumber,windunit,tempunitnodeg,pressunit,rainunit,windrun,presstrendval,rmonth,ryear,rfallY,intemp,inhum,wchill,temptrend,tempTH,TtempTH,tempTL," .
        "TtempTL,windTM,TwindTM,wgustTM,TwgustTM,pressTH,TpressTH,pressTL,TpressTL,version,build,wgust,heatindex,humidex,UV,ET,SolarRad,avgbearing,rhour,forecastnumber,isdaylight,SensorContactLost,wdir,cloudbasevalue,cloudbaseunit,apptemp,SunshineHours,CurrentSolarMax,IsSunny)";
    $WindBearField = null;
    $EndFieldCount = 57;
    if ($param_retainVal > 0) {
        $DeleteEntries = "DELETE IGNORE FROM $param_table WHERE LogDateTime < DATE_SUB(NOW(), INTERVAL $param_retainVal $param_retainUnit )";
    }
}

$handle = @fopen($param_file, 'r');
if ($handle) {
    // Connect to the database
    $mysqli = new mysqli($dbhost, $dbuser, $dbpassword, $database);
    if ($mysqli->connect_errno) {
        die('Failed to connect to the database server - ' . $mysqli->connect_error);
    } elseif ($debug) {
        echo 'Connected to db'.$lf;
    }

    if (!$mysqli->query("SET time_zone='+00:00'")) {
        die("ERROR - TZ Statement");
    } elseif ($debug) {
        echo 'Set TZ'.$lf;
    }

    // check if the table is available
    $result = $mysqli->query("SHOW TABLES LIKE '$param_table'");
    if ($result->num_rows == 0) {
        // no table, so create it
        echo "Table does not exist, creating it...$lf";
        if(!$mysqli->query($CreateQuery)) {
            die('Failed to create table: ' . $CreateQuery);
        }
    } elseif ($debug) {
        echo 'Table exists'.$lf;
    }
    $result->close();

    echo 'Inserting data... ';
    while (!feof($handle)) {
        $buffer = fgets($handle);
        $buf_arr = explode($field_delimiter, $buffer);
        $recs = count($buf_arr);
        if ($buf_arr[0] != '') {
            // format the date -- this assume dd/mm/yy but will convert to a format for SQL: yy-mm-dd
            $datearr = explode($date_delimiter, $buf_arr[0]);
	    $timearr = explode(":", $buf_arr[1]);
	    $ts = mktime( $timearr[0], $timearr[1], $timearr[2], $datearr[1], $datearr[0], $datearr[2] + 2000);
 
            if ($date_format === 'DMY') {
                $dtimestamp = $datearr[2] . '-' . $datearr[1] . '-' . $datearr[0];
            } elseif ($date_format === 'MDY') {
                $dtimestamp = $datearr[2] . '-' . $datearr[0] . '-' . $datearr[1];
            } elseif ($date_format === 'YMD') {
                $dtimestamp = $datearr[0] . '-' . $datearr[1] . '-' . $datearr[2];
            }
            if ($param_type === 'realtime' || $param_type === 'monthly') {
                // realtime & monthly tables have a single combined date-time column
                $dtimestamp .= " $buf_arr[1]";
                $i = 2;
            } else {
                $i = 1;
            }
            // start building the SQL INSERT statement
            $insert = $StartOfInsertSQL;
            $insert  .= " Values('$dtimestamp','$ts',";
            for (; $i <= $EndFieldCount ; $i++) {
                if ($i >= $recs or trim($buf_arr[$i]) === '') {  // no data in file
                    $insert .= 'null';
                } else { // we have some data
                    // fix decimal separation to . for SQL
                    if ($decimal_separator === ',') {
                        // remove .  replace decimal , with .
                        $buf_arr[$i] = str_replace('.', '', $buf_arr[$i]);
                        $buf_arr[$i] = str_replace(',', '.', $buf_arr[$i]);
                    }
                    if ($decimal_separator === '.') {
                        // remove ,
                        $buf_arr[$i] = str_replace(',', '', $buf_arr[$i]);
                    }

                    $insert .= "'$buf_arr[$i]'";
                }
                if ($i !== $EndFieldCount) {
                    $insert .=  ',';
                }
            }
            // Append extra columns for wind directions as symbols
            if ($param_type === 'dayfile' || $param_type === 'monthly') {
                $count = count($WindBearField);
                for ($i = 0; $i < $count; $i++) {
                    $insert .=  ',';
                    // Calculate the compass points based on the bearings
                    if ($WindBearField[$i] >= $recs or trim($buf_arr[$WindBearField[$i]]) === '') {
                        $insert .= 'NULL';
                    } else {
                        $insert .= "'" . $compassp[((((int)$buf_arr[$WindBearField[$i]] + 11) / 22.5) % 16 )] . "'";
                    }
                    if ($i === $count - 1) {
                        $insert .=  ')';
                    }
                }
            } else {
                $insert .=  ')';
            }
            if (!$mysqli->query($insert)) {
                echo "Error: Failed to insert data:$lf $insert $lf";
            }
        }
    }
    fclose($handle);
    echo "done.$lf";
    if ($param_type === 'realtime' && $param_retainVal > 0) {
        echo 'Deleting old realtime records...';
        if (!$mysqli->query($DeleteEntries)) {
            echo "Error: Failed to delete records:$lf $DeleteEntries $lf";
        } else {
            echo "done.$lf";
        }
    }
    $mysqli->close();
} else {
    echo "Error: Failed to open file: $param_file $lf";
}
echo date('d/m/y - H:i:s', time()) . $lf;
?>

