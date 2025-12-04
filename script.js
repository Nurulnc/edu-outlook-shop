let selected = { name: "", price: 0 };

function selectProduct(type, price) {
    const names = { edu: ".EDU Mail", outlook: "Outlook Premium", hotmail: "Hotmail Old" };
    selected = { name: names[type], price: price };
    document.getElementById("selectedProduct").textContent = selected.name + " (৳" + price + "/mail)";
    document.getElementById("orderForm").style.display = "block";
    calculateTotal();
    window.scrollTo(0, document.getElementById("orderForm").offsetTop - 100);
}

function calculateTotal() {
    const qty = document.getElementById("quantity").value || 1;
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

    if (!username.startsWith("@") || username.length < 3) {
        alert("Telegram username দাও (@ দিয়ে)");
        return;
    }
    if (txid.length < 5) {
        alert("Transaction ID দাও");
        return;
    }

    const data = {
        product: selected.name,
        quantity: qty,
        total: (qty * selected.price),
        username: username,
        txid: txid
    };

    fetch('telegram.php', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(() => {
        alert("অর্ডার সফলভাবে পাঠানো হয়েছে! ৫-১৫ মিনিটের মধ্যে ডেলিভারি পাবে।");
        cancelOrder();
    })
    .catch(() => alert("Error! আবার চেষ্টা করো"));
}
