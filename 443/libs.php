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


function mkdirs ($location) {
    if (is_dir($location))
        return;

    $old = umask (000); 
    mkdir ($location, 0774, true); 
    umask ($old); 
}



function process ($saveLoc, $filename, $user, $problemInfo, $langInfo, $attemptNo) {
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