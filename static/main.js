const form = document.getElementById("room-name-form");
const roomNameInput = document.getElementById("room-name-input");
const container = document.getElementById("video-container");
const table = document.getElementById("myTable");
const box = document.getElementById("box");
const writing = document.getElementById("writing");
const body = document.body;
const utilityButtonsDiv = document.getElementById("utility-buttons")

let participantIdentities = [];

const startRoom = async (event) => {
  // prevent a page reload when a user submits the form
  event.preventDefault();
  // hide the join form

  // Gleans form data to be passed into post method
  const form = event.target;
  const formData = new FormData(form);

  // Calls the POST method through fetch
  try {
      const response = await fetch('/call', {
          method: 'POST',
          body: formData
      });

      if (response.ok) {
          const responseData = await response.json();
          // Handle successful response data
          console.log(responseData);
      } else if (response.status === 403) {
          // Handle unauthorized access
          console.error('Not an expert, Forbidden');
      } else {
          // Handle other errors
          console.error('Error:', response.statusText);
      }
  } catch (error) {
      // Handle network errors
      console.error('Error:', error);
  }

  form.style.display = "none";
  box.style.display = "none";
  writing.style.display = "none";
  const tableDiv = document.getElementById("myTableDiv");
  tableDiv.style.display = "none";
  body.style.backgroundColor = "black";
  utilityButtonsDiv.style.display = "block";

  // retrieve the room name
  const roomName = roomNameInput.value;

  // fetch an Access Token from the join-room route
  const response = await fetch("/join-room", {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ room_name: roomName }),
  });
  const { token } = await response.json();

  // join the video room with the token
  const room = await joinVideoRoom(roomName, token);
  
  // render the local and remote participants' video and audio tracks
  handleConnectedParticipant(room.localParticipant, room);
  room.participants.forEach((participant) => handleConnectedParticipant(participant, room));
  room.on("participantConnected", (participant) => handleConnectedParticipant(participant, room));

  // handle cleanup when a participant disconnects
  room.on("participantDisconnected", handleDisconnectedParticipant);
  window.addEventListener("pagehide", () => room.disconnect());
  window.addEventListener("beforeunload", () => room.disconnect());

  // Function to disconnect from the room
  const disconnectFromRoom = () => {
    // Disconnect the room
    if (room) {
      room.disconnect();
      handleDisconnectedParticipant(room.localParticipant, room)
      window.location.href = "/";
    }

    const shareScreen = document.getElementById('share_screen');
    var screenTrack;
    shareScreen.addEventListener('click', shareScreenHandler);

    function shareScreenHandler() {
      event.preventDefault();
      if (!screenTrack) {
          navigator.mediaDevices.getDisplayMedia().then(stream => {
              screenTrack = new Twilio.Video.LocalVideoTrack(stream.getTracks()[0]);
              room.localParticipant.publishTrack(screenTrack);
              shareScreen.innerHTML = 'Stop sharing';
              screenTrack.mediaStreamTrack.onended = () => { shareScreenHandler() };
          }).catch(() => {
              alert('Could not share the screen.');
          });
      }
      else {
          room.localParticipant.unpublishTrack(screenTrack);
          screenTrack.stop();
          screenTrack = null;
          shareScreen.innerHTML = 'Share screen';
      }
  };
};

navigator.mediaDevices.getDisplayMedia

const muteAudio = () => {
  // closes audio track 

  if (muteAudioButton.classList.contains("muted")) {
    room.localParticipant.audioTracks.forEach(track => {
      track.track.enable();
    });

    muteAudioButtonImage.src = "static/unmute-audio.png";
    muteAudioButton.classList.remove("muted");
  }
  else {
    room.localParticipant.audioTracks.forEach(track => {
      track.track.disable();
    });

    muteAudioButtonImage.src = "static/mute-audio.png";
    muteAudioButton.classList.add("muted");
  }
};

const muteVideo = () => {
  // closes video track
  if (muteVideoButton.classList.contains("muted")) {
    room.localParticipant.videoTracks.forEach(track => {
      track.track.enable();
    });

    muteVideoButtonImage.src = "static/mute-video.png";
    muteVideoButton.classList.remove("muted");
  }
  else {
    room.localParticipant.videoTracks.forEach(track => {
      track.track.disable();
    });

    muteVideoButtonImage.src = "static/unmute-video.png";
    muteVideoButton.classList.add("muted");
  }
};

const disconnectButton = document.getElementById("disconnect-button");
disconnectButton.addEventListener("click", disconnectFromRoom);

const muteAudioButton = document.getElementById("audio-button");
const muteAudioButtonImage = document.getElementById("audio-button-img");
muteAudioButton.addEventListener("click", muteAudio);

const muteVideoButton = document.getElementById("video-button");
const muteVideoButtonImage = document.getElementById("video-button-img");
muteVideoButton.addEventListener("click", muteVideo);
};

const handleConnectedParticipant = (participant, room) => {
  // create a div for this participant's tracks
  const participantDiv = document.createElement("div");
  participantDiv.setAttribute("id", participant.identity);
  container.appendChild(participantDiv);

  // iterate through the participant's published tracks and
  // call `handleTrackPublication` on them
  participant.tracks.forEach((trackPublication) => {
    handleTrackPublication(trackPublication, participant);
  });

  // listen for any new track publications
  participant.on("trackPublished", handleTrackPublication);

  console.log(`${participant.identity} has joined the room.`);

  participantIdentities.push(participant.identity);

  console.log(participantIdentities);

  if (participantIdentities.length == 2) {
    const participantDiv1 = document.getElementById(participantIdentities[0]);
    if (participantDiv1) {
      participantDiv1.classList.add("participant-2-div");
    }
    const participantDiv2 = document.getElementById(participantIdentities[1]);
    if (participantDiv2) {
      participantDiv2.classList.add("participant-1-div");
    }
  }
};

const handleTrackPublication = (trackPublication, participant) => {
  function displayTrack(track) {
    // append this track to the participant's div and render it on the page
    const participantDiv = document.getElementById(participant.identity);
    // track.attach creates an HTMLVideoElement or HTMLAudioElement
    // (depending on the type of track) and adds the video or audio stream
    participantDiv.append(track.attach());
  }

  // check if the trackPublication contains a `track` attribute. If it does,
  // we are subscribed to this track. If not, we are not subscribed.
  if (trackPublication.track) {
    displayTrack(trackPublication.track);
  }

  // listen for any new subscriptions to this track publication
  trackPublication.on("subscribed", displayTrack);
};

const handleDisconnectedParticipant = async (participant, room) => {
  // stop listening for this participant
  participant.removeAllListeners();
  // remove this participant's div from the page
  const participantDiv = document.getElementById(participant.identity);
  participantDiv.remove();

  if (room.participants.size == 0) {

    try {
      const response = await fetch('/delete-room', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ roomName: room.name }), // Send the room name to be deleted
      });

      if (response.ok) {
        console.log('Room deleted successfully');
      } else {
        console.error('Failed to delete room');
      }
    }
    catch (error) {
      console.error('Error:', error);
    }
  }
};

const joinVideoRoom = async (roomName, token) => {
  // join the video room with the Access Token and the given room name
  const room = await Twilio.Video.connect(token, {
    room: roomName,
  });
  return room;
};

form.addEventListener("submit", startRoom);