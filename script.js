let selected = { name: "", price: 0 };

// তোমার বটের টোকেন আর চ্যাট আইডি এখানে বসাও
const BOT_TOKEN = "8411734378:AAFO3dg2EaYrMBxBmlzQXEnbtwRSLzUiO08";
const CHAT_ID = "1651695602";  // তোমার টেলিগ্রাম আইডি

function selectProduct(type, price) {
    const names = { 
        edu: ".EDU Mail", 
        outlook: "Outlook Premium", 
        hotmail: "Hotmail Old" 
    };
    selected = { name: names[type], price: price };
    document.getElementById("selectedProduct").textContent = selected.name + " (৳" + price + "/mail" + ")";
    document.getElementById("orderForm").style.display = "block";
    calculateTotal();
    window.scrollTo({ top: document.getElementById("orderForm").offsetTop - 100, behavior: 'smooth' });
}

function calculateTotal() {
    const qty = parseInt(document.getElementById("quantity").value) || 1;
    const total = qty * selected.price;
    document.getElementById("totalAmount").textContent = "৳" + total;
}

function cancelOrder() {
    document.getElementById("orderForm").style.display = "none";
    selected = { name: "", price: 0 };
}

function placeOrder() {
    const qty = document.getElementById("quantity").value;
    const username = document.getElementById("username").value.trim();
    const txid = document.getElementById("txid").value.trim();

    if (!username.startsWith("@")) {
        alert("Telegram username @ দিয়ে লিখো!");
        return;
    }
    if (txid.length < 5) {
        alert("Transaction ID সঠিকভাবে লিখো");
        return;
    }

    const total = qty * selected.price;

    const message = escape(`
🟢 নতুন অর্ডার এসেছে!

📦 প্রোডাক্ট: ${selected.name}
🔢 কোয়ান্টিটি: ${qty} টা
💰 মোট টাকা: ৳${total}
👤 ইউজারনেম: ${username}
🧾 TXID: ${txid}

⏰ সময়: ${new Date().toLocaleString('en-GB', { timeZone: 'Asia/Dhaka' })}
    `);

    const url = `https://api.telegram.org/bot\( {BOT_TOKEN}/sendMessage?chat_id= \){CHAT_ID}&text=${message}&parse_mode=HTML`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.ok) {
                alert("অর্ডার সফল! ৫-১৫ মিনিটে ডেলিভারি পাবে");
                cancelOrder();
            } else {
                alert("নোটিফিকেশন পাঠাতে সমস্যা হয়েছে। আবার চেষ্টা করো।");
            }
        })
        .catch(() => {
            alert("ইন্টারনেট চেক করো। তারপর আবার চেষ্টা করো।");
        });
}
