<?php
set_time_limit(0);
ini_set('memory_limit', '2048M');
error_reporting(E_ALL | E_STRICT);
ini_set('display_errors', 1);
date_default_timezone_set('Israel'); //make sure to set the expected timezone
require_once (dirname(__FILE__) . '/php-kaltura-client/KalturaClient.php');
require 'vendor/autoload.php';
use PhpOffice\PhpSpreadsheet\Spreadsheet;
use PhpOffice\PhpSpreadsheet\Writer\Xlsx;

class KalturaContentAnalytics implements IKalturaLogger
{
    const PARENT_PARTNER_IDS = array( //replace the examples below with the PARENT partner IDs you wish to get usage for
        0000000 => 'API_ADMIN_SECRET',
        1111111 => 'API_ADMIN_SECRET',
    );
    
    const START_MONTH = '2020-10-01'; //The FIRST day of the month to BEGIN getting usage data from. Format: YYYY-MM-DD (e.g. 2000-01-25)
    const END_MONTH = '2020-10-31'; //The LAST day of the month to END the export of usage data on. Format: YYYY-MM-DD (e.g. 2000-01-25)
    
    const DEBUG_PRINTS = true; //Set to true if you'd like the script to output logging to the console (this is different from the KalturaLogger)
    const CYCLE_SIZES = 500; // Determines how many entries will be processed in each multi-request call - set it to whatever number works best for your server.
    const ERROR_LOG_FILE = 'kaltura_logger.txt'; //The name of the KalturaLogger export file
    // Defines a stop date for the entries iteration loop. Any time string supported by strtotime() can be passed. If this is set to null or -1, it will be ignored and the script will run through the entire library until it reaches the first created entry.
    const USER_ID = 'ListSubAccounts';
    const EXPIRY = 86400;
    const PRIVILEGES = '*';
    
    const HEADERS_FIELD_TYPES = array(
        array(
            'field' => 'status',
            'type' => 'KalturaPartnerStatus',
            'pretty' => 'Account Status',
            'show' => true,
            'divider' => null
        ),
        array(
            'field' => 'partner_name',
            'type' => 'string',
            'pretty' => 'Account Name',
            'show' => true,
            'divider' => null
        ),
        array(
            'field' => 'partner_id',
            'type' => 'string',
            'pretty' => 'Account ID',
            'show' => true,
            'divider' => 1
        ),
        array(
            'field' => 'created_at',
            'type' => 'unixtime',
            'pretty' => 'Creation Date',
            'show' => true,
            'divider' => null
        ),
        array(
            'field' => 'total_plays',
            'type' => 'int',
            'pretty' => 'Plays',
            'show' => true,
            'divider' => 1
        ),
        array(
            'field' => 'bandwidth_consumption',
            'type' => 'float',
            'pretty' => 'Bandwidth GB',
            'show' => true,
            'divider' => 1024
        ),
        array(
            'field' => 'average_storage',
            'type' => 'float',
            'pretty' => 'Storage GB',
            'show' => true,
            'divider' => 1024
        ),
        array(
            'field' => 'transcoding_consumption',
            'type' => 'float',
            'pretty' => 'Transcoding GB',
            'show' => true,
            'divider' => 1024
        ),
        array(
            'field' => 'total_entries',
            'type' => 'int',
            'pretty' => 'Entries',
            'show' => true,
            'divider' => 1
        ),
        array(
            'field' => 'total_end_users',
            'type' => 'int',
            'pretty' => 'Total User IDs',
            'show' => false,
            'divider' => 1
        ),
        array(
            'field' => 'total_views',
            'type' => 'int',
            'pretty' => 'Views',
            'show' => true,
            'divider' => 1
        ),
        array(
            'field' => 'origin_bandwidth_consumption',
            'type' => 'float',
            'pretty' => 'Origin Bandwidth GB',
            'show' => false,
            'divider' => 1024
        ),
        array(
            'field' => 'added_storage',
            'type' => 'float',
            'pretty' => 'Added Storage GB',
            'show' => false,
            'divider' => 1024
        ),
        array(
            'field' => 'deleted_storage',
            'type' => 'float',
            'pretty' => 'Deleted Storage GB',
            'show' => false,
            'divider' => 1024
        ),
        array(
            'field' => 'peak_storage',
            'type' => 'float',
            'pretty' => 'Peak Storage GB',
            'show' => false,
            'divider' => 1024
        ),
        array(
            'field' => 'unique_known_users',
            'type' => 'int',
            'pretty' => 'Unique IDs',
            'show' => true,
            'divider' => 1,
            'deduct' => 1
        )
    );

    public $jsonReport = null;
    public $arrayReport = null;

    public function log($message)
    {
        $errline = date('Y-m-d H:i:s') . ' ' . $message . "\n";
        file_put_contents(KalturaContentAnalytics::ERROR_LOG_FILE, $errline, FILE_APPEND);
    }

    public function run()
    {
        //Reset the log file:
        file_put_contents(KalturaContentAnalytics::ERROR_LOG_FILE, '');
        $this->log(
            "Here you'll find the log form the Kaltura Client library, in case issues occur you can use this file to investigate and report errors.\n"
        );

        //$startMonthDate = new DateTime(date("Y-m-d", strtotime(KalturaContentAnalytics::START_MONTH)));
        //$endMonthDate = new DateTime(date("Y-m-d", strtotime(KalturaContentAnalytics::END_MONTH)));
        $ts1 = strtotime(KalturaContentAnalytics::START_MONTH);
        $ts2 = strtotime(KalturaContentAnalytics::END_MONTH);
        $year1 = date('Y', $ts1);
        $year2 = date('Y', $ts2);
        $month1 = date('n', $ts1);
        $month2 = date('n', $ts2);
        $totalMonths = (($year2 - $year1) * 12) + ($month2 - $month1);
        
        $this->arrayReport = array();
        $timeZoneOffset = isset($_GET['tzOffset']) ? $_GET['tzOffset'] : -180; //if not specified use Israel
        for ($mon = 0; $mon <= $totalMonths; ++$mon) {
            $procsMonth = strtotime('+'.$mon.' month', $ts1);
            $monthName = date('M', $procsMonth);
            $yearNum = date('Y', $procsMonth);
            $startDayStr = strval(date("Ymd", strtotime('first day of '.$monthName.' '.$yearNum)));
            $endDayStr = strval(date("Ymd", strtotime('last day of '.$monthName.' '.$yearNum)));
            $monthStr = strval(date("Y-n-j", strtotime('first day of '.$monthName.' '.$yearNum)));
            //$startDayStr = strval(date("Ymd", strtotime('first day of this month')));
            //$endDayStr = strval(date("Ymd", strtotime('last day of this month')));
            //$monthStr = strval(date("Y-m-d", strtotime('first day of this month')));
            echo PHP_EOL.'Getting data for month ' . $monthStr;

            foreach (KalturaContentAnalytics::PARENT_PARTNER_IDS as $pid => $adminSecret) {
                $config = new KalturaConfiguration($pid);
                $config->serviceUrl = 'https://cdnapisec.kaltura.com';
                $client = new KalturaClient($config);
                $ks = $client
                    ->session
                    ->start(
                        $adminSecret,
                        KalturaContentAnalytics::USER_ID,
                        KalturaSessionType::ADMIN,
                        $pid,
                        KalturaContentAnalytics::EXPIRY,
                        KalturaContentAnalytics::PRIVILEGES
                    );
                $client->setKS($ks);
                echo PHP_EOL . "\t" . 'Getting all sub-accounts for parent: ' . $pid . '...' . PHP_EOL;
                $allSubAccounts = $this->getAllSubAccounts($client);
                $allsusb = $this->getListOfIds($allSubAccounts);
                $totalSubAccounts = count($allsusb);
                $listsOfSubAccounts = array_chunk($allsusb, KalturaContentAnalytics::CYCLE_SIZES);
                $curActs = 0;
                foreach ($listsOfSubAccounts as $subAccounts) {
                    $curActs += count($subAccounts);
                    echo $this->progress_bar($curActs, $totalSubAccounts, ' ' . $curActs . ' / ' . $totalSubAccounts);
                    $objectIds = implode(',', $subAccounts);
                    
                    $this->log('getting data for month: ' . $monthStr . ' of accounts: ' . $pid . ' [ ' . $objectIds . ' ]');
                    
                    $reportType = KalturaReportType::VPAAS_USAGE_MULTI;
                    $pager = new KalturaFilterPager();
                    $pager->pageSize = 500;
                    $order = "";
                    $responseOptions = new KalturaReportResponseOptions();
                    $responseOptions->skipEmptyDates = false;
                    $reportInputFilter = new KalturaReportInputFilter();
                    $reportInputFilter->fromDay = $startDayStr;
                    $reportInputFilter->toDay = $endDayStr;
                    $reportInputFilter->timeZoneOffset = $timeZoneOffset;
                    $reportInputFilter->interval = KalturaReportInterval::MONTHS;
                    $reportTable = $this->presistantApiRequest(
                        $client->report,
                        'getTable',
                        array(
                            $reportType,
                            $reportInputFilter,
                            $pager,
                            $order,
                            $objectIds,
                            $responseOptions
                        ),
                        5
                    );
                    //$reportTable = $client->report->getTable($reportType, $reportInputFilter, $pager, $order, $objectIds, $responseOptions);
                    //$reportTable = $client->report->getTotal($reportType, $reportInputFilter, $objectIds, $responseOptions);
                    $subsUsageTalbe = explode(';', $reportTable->data);
                    foreach ($subsUsageTalbe as $subUsageRow) {
                        if (trim($subUsageRow) != '') {
                            $subUsage = explode(',', $subUsageRow);
                            $subPartnerId = $subUsage[2];
                            $tRowObj = new \stdClass();
                            for ($i = 0; $i < count($subUsage); ++$i) {
                                $showField = KalturaContentAnalytics::HEADERS_FIELD_TYPES[$i]['show'];
                                if ($showField == true) {
                                    $prettyFieldName = KalturaContentAnalytics::HEADERS_FIELD_TYPES[$i]['pretty'];
                                    $cellType = KalturaContentAnalytics::HEADERS_FIELD_TYPES[$i]['type'];
                                    $cellVal = $this->formatString($subUsage[$i], $cellType, KalturaContentAnalytics::HEADERS_FIELD_TYPES[$i]['divider']);
                                    if ($cellVal > 1 && array_key_exists('deduct', KalturaContentAnalytics::HEADERS_FIELD_TYPES[$i])) $cellVal = $cellVal - KalturaContentAnalytics::HEADERS_FIELD_TYPES[$i]['deduct'];
                                    if ($cellType == 'unixtime') $cellType = 'string';
                                    $tRowObj->{$prettyFieldName} = new \stdClass();
                                    $tRowObj->{$prettyFieldName}->value = $cellVal;
                                    $tRowObj->{$prettyFieldName}->type = $cellType;
                                }
                            }
                            $prettyHeader = 'Parent ID';
                            $tRowObj->{$prettyHeader} = new \stdClass();
                            $tRowObj->{$prettyHeader}->value = $pid;
                            $tRowObj->{$prettyHeader}->type = 'string';
                            $prettyHeader = 'Month Usage';
                            $tRowObj->{$prettyHeader} = new \stdClass();
                            $tRowObj->{$prettyHeader}->value = $monthStr;
                            $tRowObj->{$prettyHeader}->type = 'string';
                            $this->arrayReport[] = $tRowObj;
                        }
                    }
                }
            }
        }

        //$this->jsonReport = json_encode($this->arrayReport, JSON_PRETTY_PRINT);
        $this->log('finished proceessing report, now printing:\n' . $this->jsonReport);
    }

    private function getListOfIds($accounts)
    {
        $actIds = array();
        foreach ($accounts as $subpartner) {
            $actIds[] = $subpartner->id;
        }
        return $actIds;
    }

    private function getAllSubAccounts($client)
    {
        $filter = new KalturaPartnerFilter();
        $filter->orderBy = KalturaPartnerOrderBy::ID_ASC;
        $filter->statusIn = "1,2,3";
        $filter->idGreaterThan = 0;
        $pager = new KalturaFilterPager();
        $pager->pageIndex = 1;
        $pager->pageSize = 500;
        //$result = $client->partner->listAction($filter, $pager);
        $result = $this->presistantApiRequest(
            $client->partner,
            'listAction',
            array(
                $filter,
                $pager
            ),
            5
        );
        $accounts = $result->objects;
        $N = count($result->objects);
        while ($N > 0) {
            $filter->idGreaterThan = $result->objects[$N - 1]->id;
            //$result = $client->partner->listAction($filter, $pager);
            $result = $this->presistantApiRequest(
                $client->partner,
                'listAction',
                array(
                    $filter,
                    $pager
                ),
                5
            );
            $N = count($result->objects);
            $accounts = array_merge($accounts, $result->objects);
        }
        return $accounts;
    }

    private function formatString($str, $varType, $divider)
    {
        switch ($varType) {
            case 'int':
            case 'int_noformat':
                return intval($str) / $divider;
                break;

            case 'float':
                return round(floatval($str) / $divider, 2);
                break;

            case 'string':
                return $str;
                break;

            case 'unixtime':
                return gmdate("Y-n-j", intval($str));
                break;

            case 'datestring':
                return substr_replace($str, '-', 4, 0);
                break;

            case 'KalturaPartnerStatus':
                if ($str == '0') return 'DELETED';
                elseif ($str == '1') return 'ACTIVE';
                elseif ($str == '2') return 'BLOCKED';
                elseif ($str == '3') return 'FULL_BLOCK';
                break;

            default:
                return $str;
        }
    }

    public function writeXLSX($filename, $rows, $keys = [], $formats = []) {
        // instantiate the class
        $doc = new \PhpOffice\PhpSpreadsheet\Spreadsheet();
        \PhpOffice\PhpSpreadsheet\Cell\Cell::setValueBinder( new \PhpOffice\PhpSpreadsheet\Cell\AdvancedValueBinder() );
        $locale = 'en-US';
        $validLocale = \PhpOffice\PhpSpreadsheet\Settings::setLocale($locale);
        $sheet = $doc->getActiveSheet();

        // $keys are for the header row.  If they are supplied we start writing at row 2
        if ($keys) {
            $offset = 2;
        } else {
            $offset = 1;
        }

        // write the rows
        $i = 0;
        foreach($rows as $row) {
            $doc->getActiveSheet()->fromArray($row, null, 'A' . ($i++ + $offset), true);
        }

        // write the header row from the $keys
        if ($keys) {
            $doc->setActiveSheetIndex(0);
            $doc->getActiveSheet()->fromArray($keys, null, 'A1', true);
        }

        // get last row and column for formatting
        $last_column = $doc->getActiveSheet()->getHighestColumn();
        $last_row = $doc->getActiveSheet()->getHighestRow();

        // autosize all columns to content width
        for ($i = 'A'; $i <= $last_column; $i++) {
            $doc->getActiveSheet()->getColumnDimension($i)->setAutoSize(true);
        }

        // if $keys, freeze the header row and make it bold
        if ($keys) {
            $doc->getActiveSheet()->freezePane('A2');
            $doc->getActiveSheet()->getStyle('A1:' . $last_column . '1')->getFont()->setBold(true);
        }
        
        // format all columns as text
        $doc->getActiveSheet()->getStyle('A2:' . $last_column . $last_row)->getNumberFormat()->setFormatCode(\PhpOffice\PhpSpreadsheet\Style\NumberFormat::FORMAT_TEXT);
        if ($formats) {
            // if there are user supplied formats, set each column format accordingly
            // $formats should be an array with column letter as key and one of the PhpOffice constants as value
            // https://phpoffice.github.io/PhpSpreadsheet/1.2.1/PhpOffice/PhpSpreadsheet/Style/NumberFormat.html
            // EXAMPLE:
            // ['C' => \PhpOffice\PhpSpreadsheet\Style\NumberFormat::FORMAT_NUMBER_00, 'D' => \PhpOffice\PhpSpreadsheet\Style\NumberFormat::FORMAT_NUMBER_00]
            foreach ($formats as $col => $format) {
                $doc->getActiveSheet()->getStyle($col . $offset . ':' . $col . $last_row)->getNumberFormat()->setFormatCode($format);
            }
        }

        // write and save the file
        $writer = new PhpOffice\PhpSpreadsheet\Writer\Xlsx($doc);
        $writer->save($filename);
    }

    private function presistantApiRequest($service, $actionName, $paramsArray, $numOfAttempts)
    {
        $attempts = 0;
        $lastError = null;
        do {
            try {
                $response = call_user_func_array(
                    array(
                        $service,
                        $actionName
                    ),
                    $paramsArray
                );
                if ($response === false) {
                    $this->log("Error Processing API Action: " . $actionName);
                    throw new Exception("Error Processing API Action: " . $actionName, 1);
                }
            } catch (Exception $e) {
                $lastError = $e;
                ++$attempts;
                sleep(10);
                continue;
            }
            break;
        } while ($attempts < $numOfAttempts);
        if ($attempts >= $numOfAttempts) {
            $this->log('======= API BREAKE =======' . PHP_EOL);
            $this->log('Message: ' . $lastError->getMessage() . PHP_EOL);
            $this->log('Last Kaltura client headers:' . PHP_EOL);
            $this->log(
                print_r(
                    $this
                        ->client
                        ->getResponseHeaders()
                )
            );
            $this->log('===============================');
        }
        return $response;
    }

    private function progress_bar($done, $total, $info = "", $width = 50)
    {
        $perc = round(($done * 100) / $total);
        $bar = round(($width * $perc) / 100);
        return sprintf("\t%s%%[%s>%s]%s\r", $perc, str_repeat("=", $bar), str_repeat(" ", $width - $bar), $info);
    }
}

$time_start = microtime(true);

$instance = new KalturaContentAnalytics();
$instance->run();
//$instance->jsonReport;
//$instance->arrayReport;
//create the excel file
$header = array(
    'Account Status',
    'Account Name',
    'Account ID',
    'Creation Date',
    'Plays',
    'Bandwidth GB',
    'Storage GB',
    'Transcoding GB',
    'Entries',
    'Views',
    'Unique IDs',
    'Parent ID',
    'Month Usage'
);
$data = array();
foreach ($instance->arrayReport as $pidUsage) {
    $row = array();
    foreach ($header as $col) {
        $row[] = $pidUsage->{$col}->value;
    }
    array_push($data, $row);
}
/*
$xls = new Excel_XML('UTF-8', false, 'Kaltura Usage');
$xls->addArray($data);
$xls->generateSavedXML('oracle-usage');
*/
$formats = [
        'A' => '',
        'B' => '',
        'C' => '0',
        'D' => 'dd/mm/yyyy',
        'E' => '#,##0',
        'F' => '#,##0.00',
        'G' => '#,##0.00',
        'H' => '#,##0.00',
        'I' => '#,##0',
        'J' => '#,##0',
        'K' => '#,##0',
        'L' => '0',
        'M' => '[$-en-US]mmmm-yy;@'
    ];
$instance->writeXLSX('oracle-usage.xls', $data, $header, $formats);


echo 'Successfully exported data!' . PHP_EOL;
echo 'File name: ' . 'oracle-usage.xls' . PHP_EOL;

$time_end = microtime(true);
$execution_time = ($time_end - $time_start)/60;
echo 'Total Execution Time: '.$execution_time.' Mins';
