<?php
$tarih = date("m/d/Y") . " 00:00:00";
$encodedDate = urlencode($tarih);
$url = "https://www.digiturk.com.tr/Ajax/GetTvGuideFromDigiturk?Day={$encodedDate}";

$curl = curl_init();
curl_setopt_array($curl, [
    CURLOPT_URL => $url,
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_HTTPHEADER => [
        "accept: */*",
        "referer: https://www.digiturk.com.tr/yayin-akisi",
        "user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "x-requested-with: XMLHttpRequest"
    ],
]);
$response = curl_exec($curl);
$error = curl_error($curl);
curl_close($curl);

if ($error) {
    header('Content-Type: text/plain; charset=utf-8');
    echo "cURL Hatası: $error";
    exit;
}

libxml_use_internal_errors(true);
$dom = new DOMDocument();
$dom->loadHTML('<?xml encoding="utf-8" ?>' . $response);
libxml_clear_errors();

$xpath = new DOMXPath($dom);

$kanalDivs = $xpath->query('//div[contains(@class,"swiper-slide") and contains(@class,"channelContent")]');

$epg = new DOMDocument('1.0', 'UTF-8');
$epg->formatOutput = true;
$tv = $epg->createElement('tv');
$epg->appendChild($tv);

$channelCounter = 1;
$programCounter = 1;

function formatStartTime($baseDate, $timeStr) {
    $dt = DateTime::createFromFormat('m/d/Y H:i:s', $baseDate);
    if (!$dt) return null;
    $parts = explode(':', $timeStr);
    if (count($parts) === 2) {
        $dt->setTime((int)$parts[0], (int)$parts[1], 0);
        return $dt->format('YmdHis O');
    }
    return null;
}

foreach ($kanalDivs as $kanalDiv) {
    $kanalNode = $xpath->query('.//h3[contains(@class,"tvguide-channel-name")]', $kanalDiv);
    $kanalAdi = $kanalNode->length > 0 ? trim($kanalNode->item(0)->textContent) : "Bilinmeyen Kanal";
    $channelId = (string)$channelCounter++;
    $channelElem = $epg->createElement('channel');
    $channelElem->setAttribute('id', $channelId);

    $displayName = $epg->createElement('display-name', htmlspecialchars($kanalAdi));
    $channelElem->appendChild($displayName);
    $tv->appendChild($channelElem);

    $programNodes = $xpath->query('.//div[contains(@class,"tvGuideResult-box-wholeDates") and contains(@class,"channelDetail")]', $kanalDiv);

    foreach ($programNodes as $programNode) {
        $saatNode = $xpath->query('.//span[contains(@class,"tvGuideResult-box-wholeDates-time-hour")]', $programNode);
        $sureNode = $xpath->query('.//span[contains(@class,"tvGuideResult-box-wholeDates-time-totalMinute")]', $programNode);
        $baslikNode = $xpath->query('.//span[contains(@class,"tvGuideResult-box-wholeDates-title")]', $programNode);

        $startTimeStr = $saatNode->length > 0 ? trim($saatNode->item(0)->textContent) : null;
        $sureStr = $sureNode->length > 0 ? trim($sureNode->item(0)->textContent) : null;

        $baslik = "Bilinmeyen Program";
        if ($baslikNode->length > 0) {
            $node = $baslikNode->item(0);
            $attrTitle = $node->getAttribute('title');
            $baslik = !empty($attrTitle) ? trim($attrTitle) : trim($node->textContent);
        }

        if (!$startTimeStr) continue;
        $start = formatStartTime($tarih, $startTimeStr);
        if (!$start) continue;
        preg_match('/(\d+)/', $sureStr, $matches);
        $durationMinutes = isset($matches[1]) ? (int)$matches[1] : 30;

        $dtStart = DateTime::createFromFormat('YmdHis O', $start);
        if (!$dtStart) continue;
        $dtEnd = clone $dtStart;
        $dtEnd->modify("+{$durationMinutes} minutes");
        $stop = $dtEnd->format('YmdHis O');
        $programId = "program" . $programCounter++;
        $programmeElem = $epg->createElement('programme');
        $programmeElem->setAttribute('start', $start);
        $programmeElem->setAttribute('stop', $stop);
        $programmeElem->setAttribute('channel', $channelId);
        $programmeElem->setAttribute('id', $programId);

        $titleElem = $epg->createElement('title', htmlspecialchars($baslik));
        $programmeElem->appendChild($titleElem);

        $tv->appendChild($programmeElem);
    }
}

$dosyaAdi = 'digiphpepg.xml';
$epg->save($dosyaAdi);

header('Content-Type: application/xml; charset=utf-8');
echo $epg->saveXML();

//Sakultah tarafından yapılmıştır iyi kullanımlar :)
