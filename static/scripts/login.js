async function login() {
    const form = new FormData();
    form.append("username", document.querySelector('#username').value);
    form.append("password", document.querySelector('#password').value);

    const res = await fetch("/login", {
            method: "POST",
            body: form,
    });
    if (res.ok) {
        const data = await res.json();
        window.location.reload();
    }
}

async function logout() {
    const res = await fetch("/logout");
    if (res.ok) {
        const data = await res.json();
        window.location.reload();
    }
}