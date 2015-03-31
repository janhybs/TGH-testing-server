<?php
define ('ROOT', realpath($_SERVER["DOCUMENT_ROOT"]));
define ('RESULT_ROOT',  ROOT . "/data");
define ('PROBLEM_ROOT', ROOT . "/problems");
define ('PYTHON_PATH', 'python2.7');
define ('ALLOWED_USERS', serialize (array('jan.hybs', 'jan.brezina', 'jiri.hnidek', 'superego')));

function arrayToObject ($array) { return json_decode (json_encode ($array));}

function getLanguages () {
    $v =  array(
        "cs"        => array("id" => "cs",       "extension" => "cs",    "name" => 'C#',     "version" => 'Mono 3.0.7'),
        "c"         => array("id" => "c",        "extension" => "c",     "name" => 'C',      "version" => 'gcc 4.7.2.5'),
        "cpp"       => array("id" => "cpp",      "extension" => "cpp",   "name" => 'C++',    "version" => 'g++ 4.7.2.5'),
        "java"      => array("id" => "java",     "extension" => "java",  "name" => 'Java',   "version" => 'java 1.8.0_31'),
        "pascal"    => array("id" => "pascal",   "extension" => "pas",   "name" => 'Pascal', "version" => 'fpc 2.4.0'),
        "python27"  => array("id" => "python27", "extension" => "py",    "name" => 'Python', "version" => 'python 2.7.6')
    );
    return arrayToObject($v);
}


function getProblems () {
    $v = array(
        "TEST"      => array("id" => "TEST",     "name" => "pokusná úloha", "input" => array('1.in', '2.in')),
        "BIGLOKO1"  => array("id" => "BIGLOKO1", "name" => "Zeleznicni plan"),
        "MINOS"     => array("id" => "MINOS",    "name" => "Bludiste"),
        "MINSPILL"  => array("id" => "MINSPILL", "name" => "Přelévání nádob"),
        "WEBISL"    => array("id" => "WEBISL",   "name" => "Web stranky"),
        "ELECTRIC"  => array("id" => "ELECTRIC", "name" => "Eletrika"),
        "SUDOGOB"   => array("id" => "SUDOGOB",  "name" => "Sudkou"),
        "IDOS"      => array("id" => "IDOS",     "name" => "IDOS"),
        "SEGMENT"   => array("id" => "SEGMENT",  "name" => "Segmentace obrazu"),
        "RELCONN"   => array("id" => "RELCONN",  "name" => "Nejspolehlivejsi cesta"),
        "ARRMERGE"  => array("id" => "ARRMERGE", "name" => "Merge two sorted arrays"),
        "GOSTRVI"   => array("id" => "GOSTRVI",  "name" => "Google Street View"),
        "TWOMISS"   => array("id" => "TWOMISS",  "name" => "Two missing from a sequence")
    );
    return arrayToObject($v);
}



