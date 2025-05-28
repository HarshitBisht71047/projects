const socket = io();

    const playerInput = document.getElementById("playerSearch");
    const bidInput = document.getElementById("bidAmount");
    const nameInput = document.getElementById("bidder");
    const bidStatus = document.getElementById("bid-status");

    document.getElementById("placeBid").addEventListener("click", () => {
      const player = playerInput.value;
      const amount = parseInt(bidInput.value);
      const bidder = nameInput.value;

      if (!player || !bidder || isNaN(amount)) {
        alert("Please fill all fields correctly.");
        return;
      }

      socket.emit("new_bid", {
        player,
        amount,
        bidder
      });
    });

    socket.on("update_bid", (data) => {
      bidStatus.innerHTML = `Highest Bid: <strong>${data.amount}</strong> by <em>${data.bidder}</em>`;
    });

    socket.on("bid_rejected", (data) => {
      alert(data.message);
    });