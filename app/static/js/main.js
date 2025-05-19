// document.addEventListener('DOMContentLoaded', function () {
//     const localVideo = document.getElementById('localVideo');
//     const remoteVideo = document.getElementById('remoteVideo');
//     const callButton = document.getElementById('callButton');
//     const answerButton = document.getElementById('answerButton');
//     let localStream;
//     let peerConnection;

//     const socket = io.connect(window.location.origin, {
//         query: "user_id= {{ session['user_id'] }}"
//     });

//     navigator.mediaDevices.getUserMedia({ audio: true })
//         .then(stream => {
//             localVideo.srcObject = stream;
//             localStream = stream;
//         })
//         .catch(error => console.error('Error accessing media devices.', error));

//     callButton.onclick = () => {
//         startCall();
//     };

//     answerButton.onclick = () => {
//         answerCall();
//     };

//     function startCall() {
//         const configuration = {
//             'iceServers': [{'urls': 'stun:stun.l.google.com:19302'}]
//         };
//         peerConnection = new RTCPeerConnection(configuration);

//         localStream.getTracks().forEach(track => {
//             peerConnection.addTrack(track, localStream);
//         });

//         peerConnection.onicecandidate = event => {
//             if (event.candidate) {
//                 socket.emit('ice_candidate', { candidate: event.candidate, conversation_id: "{{ conversation_id }}" });
//             }
//         };

//         peerConnection.ontrack = event => {
//             remoteVideo.srcObject = event.streams[0];
//         };

//         peerConnection.createOffer()
//             .then(offer => peerConnection.setLocalDescription(offer))
//             .then(() => {
//                 socket.emit('call_user', { offer: peerConnection.localDescription, conversation_id: "{{ conversation_id }}" });
//             });
//     }

//     function answerCall() {
//         const configuration = {
//             'iceServers': [{'urls': 'stun:stun.l.google.com:19302'}]
//         };
//         peerConnection = new RTCPeerConnection(configuration);

//         localStream.getTracks().forEach(track => {
//             peerConnection.addTrack(track, localStream);
//         });

//         peerConnection.onicecandidate = event => {
//             if (event.candidate) {
//                 socket.emit('ice_candidate', { candidate: event.candidate, conversation_id: "{{ conversation_id }}" });
//             }
//         };

//         peerConnection.ontrack = event => {
//             remoteVideo.srcObject = event.streams[0];
//         };

//         peerConnection.setRemoteDescription(new RTCSessionDescription(data.offer))
//             .then(() => peerConnection.createAnswer())
//             .then(answer => peerConnection.setLocalDescription(answer))
//             .then(() => {
//                 socket.emit('answer_call', { answer: peerConnection.localDescription, conversation_id: "{{ conversation_id }}" });
//             });
//     }

//     socket.on('receive_call', data => {
//         answerButton.style.display = 'block';
//     });

//     socket.on('call_answered', data => {
//         peerConnection.setRemoteDescription(new RTCSessionDescription(data.answer));
//     });

//     socket.on('ice_candidate', data => {
//         const candidate = new RTCIceCandidate(data.candidate);
//         peerConnection.addIceCandidate(candidate);
//     });
// });


document.addEventListener('DOMContentLoaded', function () {
    const loginTogglePassword = document.getElementById('login-toggle-password');
    const loginPasswordField = document.getElementById('login-password');
    if (loginTogglePassword) {
        loginTogglePassword.addEventListener('click', function () {
            const type = loginPasswordField.getAttribute('type') === 'password' ? 'text' : 'password';
            loginPasswordField.setAttribute('type', type);
            loginTogglePassword.classList.toggle('fa-eye');
            loginTogglePassword.classList.toggle('fa-eye-slash');
        });
    }

    const resetToggleConfirmPassword = document.getElementById('reset-toggle-confirm-password');
    const resetConfirmPasswordField = document.getElementById('reset-confirm-password');
    const resetPasswordField = document.getElementById('reset-password');
    const resetTogglePassword = document.getElementById('reset-toggle-password');


    if (resetToggleConfirmPassword) {
        resetToggleConfirmPassword.addEventListener('click', function () {
            const type = resetConfirmPasswordField.getAttribute('type') === 'password' ? 'text' : 'password';
            resetConfirmPasswordField.setAttribute('type', type);
            resetToggleConfirmPassword.classList.toggle('fa-eye');
            resetToggleConfirmPassword.classList.toggle('fa-eye-slash');
        });
    }

    if (resetTogglePassword) {
        resetTogglePassword.addEventListener('click', function () {
            const type = resetPasswordField.getAttribute('type') === 'password' ? 'text' : 'password';
            resetPasswordField.setAttribute('type', type);
            resetTogglePassword.classList.toggle('fa-eye');
            resetTogglePassword.classList.toggle('fa-eye-slash');
        });
    }
});