
document.addEventListener('DOMContentLoaded', function() {

    fetch('/videos')
        .then(response => response.json())
        .then(data => {
            const videos = JSON.stringify(data);
            for (let video of data['videos']) {
                add_video(video);
            }
        })
        .catch(error => console.error('Error fetching videos:', error));

});

const add_video = function(video) {
    const feed = document.getElementById('feed');
    const video_element = document.createElement('div');
    video_element.innerHTML = `
        <div class="video">
            <iframe width="420" height="315"
              src="https://www.youtube.com/embed/${video}?mute=1">
            </iframe>
        </div>
    `;
    feed.appendChild(video_element);
};
