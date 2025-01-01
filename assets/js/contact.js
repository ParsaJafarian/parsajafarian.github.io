document.getElementById('contact-form').addEventListener('submit', function (event) {
    event.preventDefault();

    emailjs.init("your-user-id"); // Replace with your EmailJS user ID

    emailjs.send("your-service-id", "your-template-id", {
        name: document.getElementById("cname").value,
        email: document.getElementById("cemail").value,
        message: document.getElementById("cmessage").value,
    })
        .then(function (response) {
            alert("Message sent successfully!");
        }, function (error) {
            alert("Failed to send message. Please try again later.");
        });
});
