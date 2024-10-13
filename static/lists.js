
document.addEventListener('DOMContentLoaded', function() {

    fetch('/api/lists')
        .then(response => response.json())
        .then(data => {
            const lists = JSON.stringify(data);
            for (let list of data['lists']) {
                add_list(list[0], list[1]);
            }
        })
        .catch(error => console.error('Error fetching lists:', error));

});

const add_list = function(list_name, role) {
    const lists = document.getElementById('lists');
    const list_element = document.createElement('div');
    list_element.innerHTML = `
        <div id="list-container">
            <div id="list-name" onclick="view_list(event)">${list_name}</div>
            <img id="delete-list" src="static/assets/delete.png" width="50px" height="50px" onclick="delete_list(event)">
            <div hidden id="role" value="${role}"></div>
        </div>
    `;
    lists.appendChild(list_element);
};

const view_list = function(event) {
    const list_name = event.target.innerText;
    window.location.href = `/view-list?list_id=${list_name}`;
}

const delete_list = function(event) {
    const list_container = event.target.parentElement;
    const identifier = list_container.querySelector("#list-name").innerText;

    // remove list from local state
    list_container.remove();

    // update remote state
    fetch(`/api/delete-list?list_id=${identifier}`);
}

