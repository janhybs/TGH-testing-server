<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
<pre><?php

define ('ROOT', realpath($_SERVER["DOCUMENT_ROOT"]));
define ('PROBLEM_ROOT', ROOT . "/problems");

function scan ($dir) {
    $r = scandir($dir);
    $r = array_diff ($r, array('.', '..'));
    return $r;
}

function scanf ($dir) {
    $r = scan ($dir);
    $rr = array ();
    foreach ($r as $file) {
        if (is_file ($dir . '/' . $file))
            $rr[] = $file;
    }
    return $rr;
}


function scand ($dir) {
    $r = scan ($dir);
    $rr = array ();
    foreach ($r as $file) {
        if (is_dir ($dir . '/' . $file))
            $rr[] = $file;
    }
    return $rr;
}

$json = array();
$problems_data = array(
        "TEST"      => array("id" => "TEST",     "name" => "pokusná úloha"),
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

$problems = scand (PROBLEM_ROOT);

foreach ($problems as $problem) {
    $id = $problems_data[$problem]['id'];
    $json[$id] = array();
    $json[$id]['id'] = $problems_data[$problem]['id'];
    $json[$id]['name'] = $problems_data[$problem]['name'];
    $json[$id]['ref_script'] = "../generic";
    $json[$id]['input'] = array();

    $inputs = scanf (PROBLEM_ROOT . '/' . $id . '/' . 'input');
    foreach ($inputs as $input) {
        $name = rtrim ($input, '.in');
        $json[$id]['input'][] = array ('id' => $name, 'time' => 60);
    }
}
// print_r ($json);

print json_encode ($json, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);