async function fetchUserData() {
    const userId = document.getElementById('userId').value;
    if (!userId) {
        alert('Please enter a user ID.');
        return;
    }

    let res = await fetch(`http://localhost:5000/hello/${userId}`);
    if (res.ok) {
        let data = await res.json();
        console.log(data);

        if (data.error) {
            document.getElementById('userDetails').innerHTML = `<p>${data.error}</p>`;
            document.getElementById('titleName').innerText = "Guest";
        } else {
            document.getElementById('userDetails').innerHTML = `
                <p><strong>ID:</strong> ${data.id}</p>
                <p><strong>Name:</strong> ${data.name}</p>
                <p><strong>Email:</strong> ${data.email}</p>
                <p><strong>Status:</strong> ${data.is_active ? 'Active' : 'Inactive'}</p>
            `;
            document.getElementById('titleName').innerText = data.name;
        }
    } else {
        alert("Incorrect User Id");
    }
}
