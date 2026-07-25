Title: Live Content

Description: Fetched live

Source: https://data.egovoc.com/

---

<!DOCTYPE html>
<html lang="en" ng-app="openocApp">
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="">
    <meta name="author" content="">
    <link rel="icon" href="favicon.ico">
    <title>OpenOC Data Tool - County of Orange</title>
    <link href="bower_components/bootstrap/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="bower_components/bootstrap-table/dist/bootstrap-table.min.css" rel="stylesheet">
    <link href="dashboard.css" rel="stylesheet">
</head>
<body>
<nav class="navbar navbar-inverse navbar-fixed-top">
    <div class="container-fluid">
        <div class="navbar-header">
            <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#sidebar" aria-expanded="false" aria-controls="sidebar">
                <span class="sr-only">Toggle navigation</span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
            </button>
            <a class="navbar-brand" href="#/Main">OpenOC Data Tool - County of Orange</a>
        </div>
        <div id="navbar" class="navbar-collapse collapse">
            <img class="nav navbar-nav navbar-right" src="oc_head_seal.png"/>
        </div>
    </div>
</nav>

<div class="container-fluid">
    <div class="row">
        <div class="col-sm-3 col-md-2 sidebar" id="sidebar">
                            <h3>Top Data Sets</h3>
                <ul class="nav nav-sidebar" id="topNav">
                    <li id="t0"><a href="#/t0">Total Annual County Expenditures</a></li>
                    <li id="t1"><a href="#/t1">Total Salaries &amp; Benefits Expenditures</a></li>
                    <li id="t2"><a href="#/t2">Total Services &amp; Supplies Expenditures</a></li>
                    <li id="t3"><a href="#/t3">Capital Assets Expenditures</a></li>
                    <li id="t4"><a href="#/t4">Total Annual County Revenues - By department</a></li>
                    <li id="t5"><a href="#/t5">Total Annual County Revenues - By revenue type</a></li>
                    <li id="t6"><a href="#/t6">General Purpose Revenue</a></li>
                    <li id="t7"><a href="#/t7">Property Tax Revenue</a></li>
                    <li id="t8"><a href="#/t8">Public Safety Sales Tax Revenue</a></li>
					<li id="t10"><a href="#/t10">Realignment Revenue</a></li>
					<li id="t11"><a href="#/t11">Mental Health Services Act Revenue</a></li>
					<li id="t12"><a href="#/t12">Orange County Opioid Settlement Fund Revenue</a></li>
                    <li id="t9"><a href="#/t9">Net County Cost</a></li>
                </ul>
                <script>
                    var timePeriod = null;
                </script>
                        </div>
        <div class="col-sm-9 col-sm-offset-3 col-md-10 col-md-offset-2 main" ng-view>
        </div>
    </div>
</div>
<script src="bower_components/jquery/dist/jquery.min.js"></script>
<script src="bower_components/bootstrap/dist/js/bootstrap.min.js"></script>
<script src="bower_components/bootstrap-table/dist/bootstrap-table.min.js"></script>
<script src="bower_components/bootstrap-table/dist/locale/bootstrap-table-en-US.min.js"></script>
<script src="bower_components/tableExport.jquery.plugin/tableExport.min.js"></script>
<script src="bower_components/file-saver.js/FileSaver.js"></script>
<script src="bower_components/html2canvas/build/html2canvas.min.js"></script>
<script src="bower_components/jspdf/dist/jspdf.min.js"></script>
<script src="bower_components/jspdf-autotable/dist/jspdf.plugin.autotable.js"></script>
<script src="bower_components/bootstrap-table/dist/extensions/export/bootstrap-table-export.min.js"></script>
<script src="bower_components/angular/angular.js"></script>
<script src="bower_components/angular-route/angular-route.js"></script>
<script src="bower_components/highcharts/highcharts.js"></script>
<script src="bower_components/highcharts/modules/data.js"></script>
<script src="bower_components/highcharts/modules/drilldown.js"></script>
<script src="bower_components/highcharts/modules/exporting.js"></script>
<script src="js/openoc.js"></script>
<script src="js/app.js"></script>
<script src="js/controllers.js"></script>
<script>
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','//www.google-analytics.com/analytics.js','ga');
ga('create', 'UA-69442401-1', 'auto');
ga('send', 'pageview');
</script>
</body>
</html>


