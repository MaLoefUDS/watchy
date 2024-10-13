
document.addEventListener('DOMContentLoaded', function() {

    const list_id = document.querySelector("#list_id").value;
    const role = document.querySelector("#role").innerText;
    fetch(`/api/videos?list_id=${list_id}`)
        .then(response => response.json())
        .then(data => {
            const videos = JSON.stringify(data);
            for (let video of data['videos']) {
                add_video(role, video[0], video[1])
            }
        })
        .catch(error => console.error('Error fetching videos:', error));

    const create_invite = document.getElementById('invite');
    create_invite.addEventListener('click', function() {
        fetch(`/api/create-invite?list_id=${list_id}&role=1`)
            .then(response => response.json())
            .then(data => {
                const invite_token = data['invite'];
                alert(`Invite link: ${window.location.origin}/api/join-list?token=${invite_token}`);
            })
            .catch(error => console.error('Error creating invite:', error));
    });

});

const add_video = function(role, identifier, state) {
    const feed = document.getElementById('feed');

    const video_element = document.createElement('div');
    video_element.id = "video-element";
    const video_container = document.createElement('div');
    video_container.id = "video-container";

    // create youtube video embed
    const video = document.createElement('iframe');
    video.src = `https://www.youtube.com/embed/${identifier}?mute=1&showinfo=0`;
    video.id = "video";
    video_container.appendChild(video);

    // create watch together button
    const watch_together = document.createElement('img');
    watch_together.id = "watch-together";
    watch_together.classList.add("watch-state-button");
    watch_together.src = "static/assets/watch_together.png";
    watch_together.onclick = function(event) { update_state(event, 1); }
    video_container.appendChild(watch_together);

    // create watch alone button
    const watch_alone = document.createElement('img');
    watch_alone.id = "watch-alone";
    watch_alone.classList.add("watch-state-button");
    watch_alone.src = "static/assets/watch_alone.png";
    watch_alone.onclick = function(event) { update_state(event, 2); }
    video_container.appendChild(watch_alone);

    // create remove video button
    // viewers cannot remove videos
    // this is enforced in backend and only here for styling purposes
    if (role !== "1") {
        const remove_video = document.createElement('img');
        remove_video.id = "remove-video";
        remove_video.classList.add("watch-state-button");
        remove_video.src = "static/assets/delete.png";
        remove_video.onclick = function(event) { update_state(event, 3); }
        video_container.appendChild(remove_video);
    }

    // create hidden elements
    const hidden_identifier = document.createElement('div');
    hidden_identifier.id = "identifier";
    hidden_identifier.hidden = true;
    hidden_identifier.innerText = identifier;
    video_container.appendChild(hidden_identifier);
    const hidden_state = document.createElement('div');
    hidden_state.id = "state";
    hidden_state.hidden = true;
    hidden_state.innerText = state;
    video_container.appendChild(hidden_state);

    video_element.appendChild(video_container);
    feed.appendChild(video_element);
    highlight_video(video_container);
};

const update_state = function(event, new_state) {
    const video_container = event.target.parentElement;
    const identifier = video_container.querySelector("#identifier").innerText;
    const list_id = document.querySelector("#list_id").value;

    // toggle state
    const state = video_container.querySelector("#state").innerText;
    if (new_state == state) {
        new_state = 0;
    }

    // update local state
    if (new_state == 3) {
        video_container.remove();
    } else {
        video_container.querySelector("#state").innerText = new_state;
        highlight_video(video_container);
    }

    // update remote state
    fetch(`/api/update-video?list_id=${list_id}&video_id=${identifier}&state=${new_state}`);
}

const highlight_video = function(video_container) {

  // fetch state
  const state = video_container.querySelector("#state").textContent;
  let state_color = "#333333";

  // find color for state
  switch (state) {
    case "0": break;
    case "1": state_color = "#ff0000"; break;
    case "2": state_color = "#0000ff"; break;
  }

  // style video
  const video = video_container.querySelector("#video");
  video.style.border = `0.3vh solid ${state_color}`;
  video_container.style.background = `radial-gradient(circle, ${state_color}aa, rgba(0, 0, 0, 0))`;

}

