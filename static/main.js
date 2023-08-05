const room_name = document.getElementById("room-name-input")
const hostname = document.getElementById("username")
const form = document.getElementById("room-name-form");
const box = document.getElementById("box");
const roomNameInput = document.getElementById("room-name-input");
const container = document.getElementById("video-container");
let num_of_participants = 0;

const startRoom = async (event) => {
  num_of_participants += 1;
  console.log("working");
  //Increments number of participants
  num_of_participants += 1;
  // prevents losing the session ID on submission
  event.preventDefault();
  // hide the join form when submitted

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
  const tableDiv = document.getElementById("myTableDiv");
  tableDiv.style.display = "none";

  // retrieve the room name
  const roomName = roomNameInput.value;
  
  const response = await fetch("/join-room", {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ room_name: roomName }),
  });
  const { token } = await response.json();

  const room = await joinVideoRoom(roomName, token);

  handleConnectedParticipant(room.localParticipant);
  room.participants.forEach(handleConnectedParticipant);
  room.on("participantConnected", handleConnectedParticipant);

  room.on("participantDisconnected", handleDisconnectedParticipant);
  window.addEventListener("pagehide", () => room.disconnect());
  window.addEventListener("beforeunload", () => room.disconnect());
};

const handleConnectedParticipant = (participant) => {

  const participantCollection = document.createElement("div");
  participantCollection.setAttribute("id", "collection");
  container.appendChild(participantCollection);

  const participantDiv = document.createElement("div");
  participantDiv.setAttribute("id", participant.identity);
  document.getElementById("collection").style.height = "100vh";
  participantCollection.appendChild(participantDiv);

  const participantName = document.createElement("div");
  participantName.innerHTML = document.getElementById("username").value;
  participantName.setAttribute("id", "participantName1");
  participantCollection.appendChild(participantName);

  participant.tracks.forEach((trackPublication) => {
    handleTrackPublication(trackPublication, participant);
  });

  participant.on("trackPublished", handleTrackPublication);
};

const handleTrackPublication = (trackPublication, participant) => {
  function displayTrack(track) {
    const participantDiv = document.getElementById(participant.identity);
    participantDiv.append(track.attach());
  }

  if (trackPublication.track) {
    displayTrack(trackPublication.track);
  }

  trackPublication.on("subscribed", displayTrack);
};

const handleDisconnectedParticipant = (participant) => {
  participant.removeAllListeners();
  const participantDiv = document.getElementById(participant.identity);
  participantDiv.remove();
};

const joinVideoRoom = async (roomName, token) => {
  // join the video room with the Access Token and the given room name
  const room = await Twilio.Video.connect(token, {
    room: roomName,
  });
  return room;
};

form.addEventListener("submit", startRoom);