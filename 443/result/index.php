<?php session_start();

require_once ("../config.php");
require_once (ROOT . "/libs.php");

$user = auth () or die ();
echo "<pre>";



$languages = getLanguages ();
$problems = getProblems ();



$lang = @$_POST['selected-language'];
$problem = @$_POST['selected-problem'];
$source = @$_POST['source-code'];
$username = $user->username;

if (! isset ($_POST['selected-language'], $_POST['selected-problem'], $_POST['source-code']))
  header("Location: /");

# language check
if (!isset($languages->$lang))
    header("Location: /?e=lang");
$langInfo = (object)$languages->$lang;

# problem check
if (!isset($problems->$problem))
    header("Location: /?e=problem");
$problemInfo = (object)$problems->$problem;


# preparing paths
$location = RESULT_ROOT . "/$problem/$username/";
mkdirs ($location);



$attemptNo = getNextAttempt ($location);
$saveLoc = $location . formatLocation ($username, $problem, $attemptNo);
$filename = "main.$langInfo->extension";
$mainFileLoc = "$saveLoc/$filename";

mkdirs ($saveLoc);
saveFile ($mainFileLoc, $source);






ob_end_flush();
ob_start();
// set_time_limit(0);
// error_reporting(0);

// $scriptlocation = ROOT . '/scripts/test.py';
// print shell_exec('python '. $scriptlocation);
// $result = (object) process ($saveLoc, $filename, $user, $problemInfo, $langInfo, $attemptNo);
// print_r ($result);

?>

<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
    <title>TGH - zpracování</title>

    <!-- Bootstrap -->
    <link href="/css/bootstrap.min.css" rel="stylesheet">
    <link href="/styles/default.css" rel="stylesheet" >
    <link href="/css/main.css" rel="stylesheet">

    <!-- HTML5 shim and Respond.js for IE8 support of HTML5 elements and media queries -->
    <!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/html5shiv/3.7.2/html5shiv.min.js"></script>
      <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
    <![endif]-->
  </head>
  <body>
    <nav class="navbar navbar-default">
      <div class="container-fluid">
        <!-- Brand and toggle get grouped for better mobile display -->
        <div class="navbar-header">
          <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#bs-example-navbar-collapse-1">
            <span class="sr-only">Toggle nav</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
          <a class="navbar-brand" href="/">TGH</a>
        </div>

        <!-- Collect the nav links, forms, and other content for toggling -->
        <div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
          <ul class="nav navbar-nav">
          </ul>
          <ul class="nav navbar-nav navbar-right">
            <li><a href="/logout"><?php showLogout ($user); ?></a></li>
          </ul>
        </div><!-- /.navbar-collapse -->
      </div><!-- /.container-fluid -->
    </nav>

    <div class="jumbotron">
      <div class="container" id="main-cont">
        <h1>TGH <small data-prefix=" úloha " class="problem-name"></small></h1>


        <div class="well" id="processing">Probíhá zpracování...
          <div class="progress">
            <div class="progress-bar progress-bar-success progress-bar-striped active" role="progressbar" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style="width: 100%">
              <span class="sr-only">running</span>
            </div>
          </div>
        </div>


        <div class="alert alert-success" role="alert" id="output-holder" style="display: none;">
          <strong id="output-header"></strong>
          <pre id="output"><code class="nohighlight"><?php 
              // ob_implicit_flush(1);
              // ob_start();
              ob_flush();
              flush();
              $result = (object) process ($saveLoc, $filename, $user, $problemInfo, $langInfo, $attemptNo);
              $lastLine = array_pop ($result->output);
              $info = json_decode ($lastLine);             
              if ($info === null) {
                $info = (object)array('exit' => 1, 'outputs' => array());
              }
              if (sizeof ($result->output) < 5) {
                  $result->output[] = $lastLine;
              }
              echo implode("\n", $result->output);
              echo "<span id='exit-code' style='display: none;'>$info->exit</span>";
           ?></code></pre>
         </div>


          <div class="btn-group" role="group" aria-label="..." id="output-download">
            <?php
            $i = 0;
            foreach ($info->outputs as $output) {
                $path = str_replace (ROOT, '', $output->path);
                $cls = $output->exit == '0' ? 'success' : 'danger';
                printf ("<a href='%s' class='btn btn-%s'>výstup sady %02d</a>", $path, $cls, ++$i);
            }
            ?>
          </div>



      </div>
    </div>



    <!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
    <script type="text/javascript" src="/js/jquery-2.1.3.min.js"></script>
    <script type="text/javascript" src="/js/bootstrap.min.js"></script>
    <script type="text/javascript" src="/js/highlight.pack.js"></script>
    <script type="text/javascript" src="/js/result.js"></script>
    <script type="text/javascript">hljs.initHighlighting()</script>
  </body>
</html>
