// Example class_id value
const class_id = 123; // This should be dynamically set based on the application's logic

// Construct the WebSocket URL using the class_id
const wsURL = `ws://127.0.0.1:9090/ws/class/${class_id}/`;

// Create a new WebSocket connection using the constructed URL
const socket = new WebSocket(wsURL);

socket.onopen = function (e) {
    console.log('Connected to the class WebSocket');
    // The socket is now open, and you can send messages or set up additional event listeners
};

socket.onmessage = function (event) {
    console.log('Message from server:', event.data);
};

socket.onerror = function (error) {
    console.error('WebSocket error:', error);
};

// Remember to handle socket closure and any other events you're interested in










// background logic

// request
function changeBackground(backgroundId) {
    if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({
            type: 'change_background',
            background_id: backgroundId
        }));
    }
}

// handle the response from the server to apply the new background:
socket.onmessage = function (event) {
    const data = JSON.parse(event.data);
    if (data.type === 'background_changed') {
        const imageUrl = data.image_url;
        // Apply the background image URL to the video call UI
        applyBackgroundImage(imageUrl);
    }
};
// background logic





// file message
const fileInput = document.querySelector('#fileInput');
const senderId = '123'; // Sender's user ID
const classId = 'abc123'; // Class ID

fileInput.addEventListener('change', async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async (e) => {
        const binaryData = e.target.result;

        // Send file type as 'file' or 'voice_message' based on your logic
        const messageType = file.type.startsWith('audio/') ? 'voice_message' : 'file';

        // Sending metadata as text data
        socket.send(JSON.stringify({
            type: messageType,
            sender_id: senderId,
            class_id: classId,
        }));

        // Then send the binary file data
        socket.send(binaryData);
    };
    reader.readAsArrayBuffer(file);
});
// file message



// text message
function sendTextMessage(socket, senderId, classId, messageText) {
    const messageData = {
        type: 'text',
        sender_id: senderId,
        class_id: classId,
        message: messageText
    };
    socket.send(JSON.stringify(messageData));
}
// text message



document.addEventListener("DOMContentLoaded", function () {
    const classId = 'class_id'; // above
    const socket = new WebSocket(`ws://127.0.0.1:9090/ws/class/${classId}/`);

    socket.onopen = function (e) {
        console.log("Connected to the chat");
    };

    socket.onmessage = function (event) {
        const data = JSON.parse(event.data);
        if (data.type === 'chat_message') {
            displayMessage(data.message, data.file_url);
        }
    };

    socket.onerror = function (error) {
        console.error("WebSocket Error: ", error);
    };

    function displayMessage(messageText, fileUrl = null) {

        const messageContainer = document.getElementById("messages"); // Your chat message container
        const messageElement = document.createElement("div");

        // If the message includes a file, create a link to the file
        if (fileUrl) {
            const fileLink = document.createElement("a");
            fileLink.href = fileUrl;
            fileLink.textContent = "View File";
            fileLink.target = "_blank";
            messageElement.appendChild(fileLink);
        }

        // Add the text content
        const textContent = document.createElement("p");
        textContent.textContent = messageText;
        messageElement.appendChild(textContent);

        // Append the message element to the container
        messageContainer.appendChild(messageElement);


    }
});
