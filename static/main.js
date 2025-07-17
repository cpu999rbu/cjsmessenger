document.addEventListener("DOMContentLoaded", () => {
  const socket = io();
  const messageInput = document.getElementById("message-input");
  const sendButton = document.getElementById("send-btn");
  const messagesContainer = document.getElementById("messages");
  const recordBtn = document.getElementById("record-btn");
  const callBtn = document.getElementById("call-btn");
  let recorder;

  sendButton.addEventListener("click", sendMessage);
  messageInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  function sendMessage() {
    const message = messageInput.value.trim();
    if (message) {
      socket.emit("send_message", { room: chatId, message: message, sender_id: userId, receiver_id: peerId });
      messageInput.value = "";
    }
  }

  socket.on("receive_message", (data) => {
    addMessage(data.message, data.sender_id == userId);
  });

  function addMessage(msg, self = false) {
    const div = document.createElement("div");
    div.classList.add("max-w-[75%]", "p-4", "rounded-2xl", "shadow-sm");
    div.classList.add(self ? "self-end" : "self-start");
    div.classList.add(self ? "bg-blue-500" : "bg-gray-200");
    div.classList.add(self ? "text-white" : "text-gray-800");
    div.classList.add(self ? "rounded-br-md" : "rounded-bl-md");
    div.innerHTML = `<p>${msg}</p>`;
    messagesContainer.appendChild(div);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  recordBtn.addEventListener("click", () => {
    if (!recorder) {
      navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
        recorder = RecordRTC(stream, { type: "audio" });
        recorder.startRecording();
        recordBtn.textContent = "Остановить запись";
      });
    } else {
      recorder.stopRecording(() => {
        let blob = recorder.getBlob();
        let formData = new FormData();
        formData.append("voice_message", blob, "voice_message.wav");
        formData.append("peer_id", peerId);
        fetch("/upload_voice", { method: "POST", body: formData })
          .then(response => response.json())
          .then(data => {
            if (data.success) addMessage("[Голосовое сообщение]", true);
          });
        recorder = null;
        recordBtn.textContent = "Записать голосовое";
      });
    }
  });

  const peer = new Peer(userId, { host: "peerjs.com", port: 443, path: "/myapp" });
  peer.on("open", id => console.log("My peer ID is: " + id));
  peer.on("call", call => {
    navigator.mediaDevices.getUserMedia({ video: true, audio: true }).then(stream => {
      call.answer(stream);
      const videoContainer = document.getElementById("video-container");
      videoContainer.classList.remove("hidden");
      const remoteVideo = document.createElement("video");
      remoteVideo.srcObject = call.remoteStream;
      remoteVideo.autoplay = true;
      videoContainer.appendChild(remoteVideo);
      const localVideo = document.createElement("video");
      localVideo.srcObject = stream;
      localVideo.autoplay = true;
      localVideo.muted = true;
      videoContainer.appendChild(localVideo);
    });
  });

  callBtn.addEventListener("click", () => {
    navigator.mediaDevices.getUserMedia({ video: true, audio: true }).then(stream => {
      const call = peer.call(peerId, stream);
      const videoContainer = document.getElementById("video-container");
      videoContainer.classList.remove("hidden");
      const localVideo = document.createElement("video");
      localVideo.srcObject = stream;
      localVideo.autoplay = true;
      localVideo.muted = true;
      videoContainer.appendChild(localVideo);
      call.on("stream", remoteStream => {
        const remoteVideo = document.createElement("video");
        remoteVideo.srcObject = remoteStream;
        remoteVideo.autoplay = true;
        videoContainer.appendChild(remoteVideo);
      });
    });
  });
});