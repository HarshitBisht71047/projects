document.querySelector(".buttoncontainer3 .button").addEventListener("click", function() {
    window.location.href = "/admin";
  });

const socket = io();

const form = document.getElementById("bidForm");
const bidAmountEl = document.getElementById("bidAmount");
const bidderNameEl = document.getElementById("bidderName");
const messageEl = document.getElementById("message");
const playerSelect = document.getElementById("playerSelect");
const playerBudgetEl = document.getElementById("playerBudget");
const auctionTimerEl = document.getElementById("auctionTimer");

// Emit request to get the bid when player changes
playerSelect.addEventListener("change", () => {
    const selectedPlayer = playerSelect.value;
    socket.emit("get_bid", selectedPlayer);
    messageEl.innerText = "";
    startTimer(selectedPlayer);
});

form.addEventListener("submit", (e) => {
    e.preventDefault();
    const bidder = document.getElementById("bidder").value;
    const bid = parseInt(document.getElementById("bid").value);
    const player = playerSelect.value;

    socket.emit("new_bid", {
        player: player,
        bidder: bidder,
        amount: bid
    });

    messageEl.innerText = ""; // Clear message
});

socket.on("update_bid", (data) => {
    if (data.player === playerSelect.value) {
        bidAmountEl.innerText = data.amount;
        bidderNameEl.innerText = data.bidder;
        playerBudgetEl.innerText = data.budget;
    }
});

socket.on("bid_rejected", (data) => {
    messageEl.innerText = data.message;
});

// Handle Timer Update
socket.on("update_timer", (data) => {
    if (data.player === playerSelect.value) {
        auctionTimerEl.innerText = Math.floor(data.remaining_time);
    }
});

// Function to start the timer for the selected player
function startTimer(player) {
    socket.emit("start_timer", player);
}


// Admin update budget
const updateBudgetForm = document.getElementById("updateBudgetForm");
updateBudgetForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const player = document.getElementById("updatePlayer").value;
    const budget = parseInt(document.getElementById("newBudget").value);

    fetch("/update_budget", {
        method: "POST",
        body: new URLSearchParams({
            "player": player,
            "budget": budget
        }),
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        }
    }).then(response => response.text())
    .then(data => console.log(data)); // You can add a success message here
});


