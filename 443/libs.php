<?php

function auth () {
    # no session? go to login section
    if (isset ($_SESSION['user']) && is_object ($_SESSION['user'])) {
        $user = $_SESSION['user'];

        # user check
        if (defined('ALLOWED_USERS')) {
            $users = unserialize (ALLOWED_USERS);
            $username = $user->username;

            # if not in array denied
            if (array_search ($username, $users) === FALSE)
                header ("Location: /denied");
        }

        return $user;

    } else
        header("Location: /secure");
    die ('just in case');
}

function getNextAttempt ($dir) {
    $files = scandir($dir);
    $maxNo = 0;
    foreach ($files as $filename) {
        if ($filename == '.' || $filename == '..')
            continue;

        $value = parseAttempt ($filename);
        if ($value > $maxNo)
            $maxNo = $value;
    }
    return $maxNo + 1;
}

function saveFile ($location, $source) {
    return file_put_contents($location, $source);
}


function join_paths() {
    $paths = array();

    foreach (func_get_args() as $arg) {
        if ($arg !== '') { $paths[] = $arg; }
    }

    return preg_replace('#/+#','/',join('/', $paths));
}

function change_extension ($filename, $new_extension) {
    $info = pathinfo($filename);
    return $info['filename'] . '.' . $new_extension;
}

/**
 * 
 */
function formatLocation ($user, $problem, $attemptNo) {
    return sprintf("%02d-%s", $attemptNo, $user);
}

/**
 * 
 */
function parseAttempt ($name) {
    $values = explode('-', $name);
    return intval($values[0]);
}


function mkdirs ($location, $mode = 0774) {
    if (is_dir($location))
        return;

    $old = umask (000); 
    mkdir ($location, $mode, true); 
    umask ($old); 
}



function copyJobFiles ($jobDir, $problemInfo, $langInfo, $user, $source, $attemptNo) {
    $jobInputDir        = join_paths ($jobDir, 'input');
    $jobOutputDir       = join_paths ($jobDir, 'output');
    $jobErrorDir        = join_paths ($jobDir, 'error');
    $jobRefDir          = join_paths ($jobDir, 'ref');

    $problemDir         = join_paths (PROBLEM_ROOT, $problemInfo->id);
    $problemInputDir    = join_paths ($problemDir, 'input');
    $problemOutputDir   = join_paths ($problemDir, 'output');

    $inputNamesObj      = $problemInfo->input;
    $inputNames         = array ();
    foreach ($inputNamesObj as $inputName) {
        $inputNames[] = $inputName->id . '.in';
    }

    $inputNames         = array_diff ($inputNames, array('.', '..'));
    $inputNames         = array_values ($inputNames);

    $filename           = 'main.' . $langInfo->extension;
    $sourceCodeLoc      = join_paths ($jobDir, $filename);
    $resultFile         = join_paths ($jobDir, 'result.json') ;
    $configFile         = join_paths ($jobDir, 'config.json') ;

    mkdirs ($jobInputDir, 0777);
    mkdirs ($jobOutputDir, 0777);
    mkdirs ($jobErrorDir, 0777);
    mkdirs ($jobRefDir, 0777);

    # copy files
    foreach ($inputNames as $inputName) {
        copy  (join_paths($problemInputDir, $inputName), join_paths($jobInputDir, $inputName));
        chmod (join_paths($jobInputDir, $inputName), 0777);

        $outputName = change_extension ($inputName, 'out');
        copy  (join_paths($problemOutputDir, $outputName), join_paths($jobRefDir, $outputName));
        chmod (join_paths($jobRefDir, $outputName), 0777);
    }
    
    #source_code
    file_put_contents ($sourceCodeLoc, $source);
    chmod ($sourceCodeLoc, 0777);

    $json = (object)array();

    $json->root     = $jobDir;
    $json->result   = $resultFile;
    $json->config   = $configFile;
    $json->filename = $filename;
    $json->attempt  = $attemptNo;
    $json->user     = $user;
    $json->lang     = $langInfo;
    $json->problem  = $problemInfo;
    $json->problem->input = $problemInfo->input;
  
    $json_data = utf8_encode (json_encode($json));
    file_put_contents($configFile, $json_data);
    chmod ($configFile, 0777);

    return $json;
}

function copyResultFiles ($jobDir, $resultDir, $sourceFilename, $resultText) {
    $jobOutputDir       = join_paths ($jobDir, 'output');
    $jobErrorDir        = join_paths ($jobDir, 'error');

    $jobOutputFiles     =  scandir ($jobOutputDir);
    $jobOutputFiles     = array_diff ($jobOutputFiles, array('.', '..'));

    $jobErrorFiles      =  scandir ($jobErrorDir);
    $jobErrorFiles      = array_diff ($jobErrorFiles, array('.', '..'));

    $resultOutputDir   = join_paths ($resultDir, 'output');
    $resultErrorDir    = join_paths ($resultDir, 'error');

    mkdirs ($resultOutputDir, 0775);
    mkdirs ($resultErrorDir,  0775);



    # copy output
    foreach ($jobOutputFiles as $filename) {
        copy  (join_paths ($jobOutputDir,    $filename), join_paths ($resultOutputDir, $filename));
        chmod (join_paths ($resultOutputDir, $filename), 0664);
    }


    # copy output
    foreach ($jobErrorFiles as $filename) {
        copy  (join_paths ($jobErrorDir,  $filename), join_paths ($resultErrorDir, $filename));
        chmod (join_paths ($resultErrorDir, $filename), 0664);
    }

    # copy source
    copy (join_paths ($jobDir, $sourceFilename), join_paths ($resultDir, $sourceFilename));
    chmod (join_paths ($resultDir, $sourceFilename), 0664);


    # copy result text
    file_put_contents (join_paths ($resultDir, 'result.txt'), $resultText);
    chmod (join_paths ($resultDir, 'result.txt'), 0664);
}

function waitForResult ($configLoc, $resultLoc) {
    $wait = 0;
    $sleep = .25;
    while ($wait < 60) {
        if (file_exists ($configLoc)) {
            # monitor present of config.json

            sleep ($sleep);
            $wait += $sleep;
            # increment duration
            $sleep += $sleep;
            if ($sleep > 5)
                $sleep = 5;
        } else {
            # if config is gone it means job was processed

            if (file_exists ($resultLoc)) {
                # result is present so decode it

                $data = file_get_contents ($resultLoc);
                $json = json_decode ($data);
                return $json;
            } else {
                # if there is no file, something horrible happaned

                return (object)array('exit' => -1, 'result' => 'no result data generated');
            }
        }
    }

    # no response in 60sec
    # something even worse happaned
    return (object)array('exit' => -1, 'result' => 'Server did not respond within the timeout period');
}

function rrmdir($dir) { 
   if (is_dir($dir)) { 
     $objects = scandir($dir); 
     foreach ($objects as $object) { 
       if ($object != "." && $object != "..") { 
         if (filetype($dir."/".$object) == "dir") rrmdir($dir."/".$object); else unlink($dir."/".$object); 
       } 
     } 
     reset($objects); 
     rmdir($dir); 
   } 
} 

function cleanJobFiles ($jobDir) {
    rrmdir ($jobDir);
}


function process ($saveLoc, $filename, $user, $problemInfo, $langInfo, $attemptNo) {
    sleep(1);
    $info = (object)array();
    $info->root = $saveLoc;
    $info->filename = $filename;
    $info->user = $user;
    $info->problem = $problemInfo;
    $info->problem->root = PROBLEM_ROOT.'/'.$info->problem->id;
    $info->lang = $langInfo;
    $info->attempt = $attemptNo;

    $json = utf8_encode (json_encode($info));
    file_put_contents("$saveLoc/config.json", $json);
    // print "Running py\n";
    // print 'python "' . ROOT . '"/scripts/process.py "' . "$saveLoc/config.json" . '"' . "\n";
    $output = array();
    $command = sprintf('%s "%s" "%s"', PYTHON_PATH, ROOT . '/scripts/process.py', "$saveLoc/config.json");
    exec ($command, $output, $exit);

    return array('output' => $output, 'exit' => $exit);
    // print_r ($GLOBALS);
}

function showLogout ($user) {
    ?>
        Logout <strong><?php echo $user->username; ?></strong>@<strong><?php echo $user->domain; ?></strong><br />
        <small><?php echo implode (', ', $user->groups); ?></small>
    <?php
}