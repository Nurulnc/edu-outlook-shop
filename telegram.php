<?php
$token = "8411734378:AAFO3dg2EaYrMBxBmlzQXEnbtwRSLzUiO08";  // তোমার বট টোকেন
$chat_id = "1651695602";  // তোমার টেলিগ্রাম আইডি

$data = json_decode(file_get_contents('php://input'), true);

$message = "NEW ORDER\n\n" .
           "Product: {$data['product']}\n" .
           "Quantity: {$data['quantity']}\n" .
           "Total: ৳{$data['total']}\n" .
           "Username: {$data['username']}\n" .
           "TXID: {$data['txid']}\n\n" .
           "ডেলিভারি দিয়ে দাও";

file_get_contents("https://api.telegram.org/bot$token/sendMessage?chat_id=$chat_id&text=" . urlencode($message));
?>
