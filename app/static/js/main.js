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
        const togglePassword = document.querySelector('.toggle-password');
        const toggleConfirmPassword = document.querySelector('.toggle-confirm-password');
        const passwordField = document.getElementById('password');
        const confirmPasswordField = document.getElementById('confirmPassword');

        togglePassword.addEventListener('click', function () {
            const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordField.setAttribute('type', type);
            togglePassword.classList.toggle('fa-eye');
            togglePassword.classList.toggle('fa-eye-slash');
        });

        toggleConfirmPassword.addEventListener('click', function () {
            const type = confirmPasswordField.getAttribute('type') === 'password' ? 'text' : 'password';
            confirmPasswordField.setAttribute('type', type);
            toggleConfirmPassword.classList.toggle('fa-eye');
            toggleConfirmPassword.classList.toggle('fa-eye-slash');
        });
    });