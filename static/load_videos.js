
document.addEventListener('DOMContentLoaded', function() {

    fetch('/api/videos')
        .then(response => response.json())
        .then(data => {
            const videos = JSON.stringify(data);
            for (let video of data['videos']) {
                add_video(video[0], video[1])
            }
        })
        .catch(error => console.error('Error fetching videos:', error));

});

const add_video = function(identifier, state) {
    const feed = document.getElementById('feed');
    const video_element = document.createElement('div');
    video_element.innerHTML = `
        <div id="video-container">
            <iframe id="video" src="https://www.youtube.com/embed/${identifier}?mute=1&showinfo=0"></iframe>
            <img id="state-together" src="static/state_together.png" width="50px" height="50px" onclick="update_state(event, 1)">
            <img id="state-alone"    src="static/state_alone.png"    width="50px" height="50px" onclick="update_state(event, 2)">
            <img id="state-deny" src="static/deny.png" width="50px" height="50px" onclick="update_state(event, 3)">
            <div hidden id="identifier">${identifier}</div>
            <div hidden id="state">${state}</div>
        </div>
    `;
    feed.appendChild(video_element);
    highlight_video(video_element.querySelector("#video-container"));
};

const update_state = function(event, new_state) {
    const video_container = event.target.parentElement;
    const identifier = video_container.querySelector("#identifier").innerText;
    video_container.querySelector("#state").innerText = new_state;

    // update local state
    if (new_state == 3) {
        video_container.remove();
    } else {
        highlight_video(video_container);
    }

    // update remote state
    fetch(`/api/update?video_id=${identifier}&state=${new_state}`);
}

const highlight_video = function(video_container) {

  // fetch state
  const state = video_container.querySelector("#state").textContent;
  let state_color = "#333";

  // find color for state
  switch (state) {
    case "0": state_color = "#333"; break;
    case "1": state_color = "#ff0000"; break;
    case "2": state_color = "#0000ff"; break;
  }

  // style video
  const video = video_container.querySelector("#video");
  video.style.border = `0.3vh solid ${state_color}`;
  video_container.style.background = `radial-gradient(circle, ${state_color}aa, rgba(0, 0, 0, 0))`;

}

