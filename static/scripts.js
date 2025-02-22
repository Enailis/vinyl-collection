// Function to toggle the visibility of the tracklist
function toggleTracklist(album, button) {
    const tracklistContainer = document.getElementById('tracklist-container-' + album.id);
    const tracklistList = tracklistContainer.querySelector('ul');

    // Check if the tracklist is already visible
    if (tracklistContainer.style.display === "none" || tracklistContainer.style.display === "") {
        // Display the tracklist
        tracklistContainer.style.display = "block";

        // Populate the tracklist
        tracklistList.innerHTML = '';
        album.tracklist.forEach((track) => {
            const listItem = document.createElement('li');
            listItem.textContent = track;
            tracklistList.appendChild(listItem);
        });

        // Change the button text to "Hide Tracklist"
        button.textContent = "Hide Tracklist";
    } else {
        // Hide the tracklist
        tracklistContainer.style.display = "none";

        // Change the button text back to "Show Tracklist"
        button.textContent = "Show Tracklist";
    }
}



// Function to add a vinyl to the collection (Main Page)
function addVinyl() {
    const upc = document.getElementById('upc').value;
    if (upc) {
        fetch('/add_album', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `upc=${upc}`,
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    showNotification('success')
                    location.reload();  // Reload the page to show the new album
                } else if (data.status === 'error') {
                    alert(data.message)
                } else {
                    showNotification('error')
                    alert('An error occured, please try again');
                }
            });
    } else {
        alert('Please enter a UPC code');
    }
}

// Function to delete an album from the collection (Main Page)
function deleteAlbum(album) {
    if (confirm('Are you sure you want to delete this album from your collection?')) {
        fetch('/delete_album', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `album_id=${album.id}`,  // Subtract 1 because of 0-based index
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert('Album deleted from collection!');
                    location.reload();  // Reload the page to reflect the changes
                } else {
                    alert('Failed to delete album');
                }
            });
    }
}

function renderAlbums() {
    const container = document.getElementById('albums-container');
    container.innerHTML = '';

    albums.forEach((album, index) => {
        const albumElement = document.createElement('div');
        albumElement.classList.add('album');
        albumElement.innerHTML = `
            <img src="${album.cover}" alt="${album.name}">
            <h3>${album.name}</h3>
            <p>${album.artist} (${album.release_date})</p>
            <button class="show-tracklist" onclick="toggleTracklist(album, this)">Show Tracklist</button>
            <button class="delete" onclick="deleteAlbum(${album})">Delete</button>
            <div class="tracklist-container" id="tracklist-container-${album.id}" style="display: none;">
                <ul></ul>
            </div>
        `;
        container.appendChild(albumElement);

    });
}

function toggleAddVinyl() {
    var addVinylDiv = document.querySelector('.add-vinyl');
    // Toggle the visibility of the .add-vinyl div
    addVinylDiv.style.display = (addVinylDiv.style.display === 'none' || addVinylDiv.style.display === '') ? 'block' : 'none';
}

function showNotification(type) {
    const bottomBar = document.getElementById("bottom-bar");
    const message = document.getElementById("message");

    // Set the message based on the event type (success/error)
    if (type === "success") {
        message.textContent = "Success! Operation completed successfully.";
        bottomBar.className = "visible success";  // Add 'success' class
        bottomBar.style.display = "block";
    } else if (type === "error") {
        message.textContent = "Error! Something went wrong.";
        bottomBar.className = "visible error";  // Add 'error' class
        bottomBar.style.display = "block";
    }

    // Show the bottom bar and hide it after 3 seconds
    setTimeout(() => {
        bottomBar.style.display = "none";
    }, 3000);  // 3 seconds delay
}
