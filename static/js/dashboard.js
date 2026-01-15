const selectAll = document.getElementById('select-all');
const checkboxes = document.querySelectorAll('input[name="cities"]');

selectAll.addEventListener('change', () => {
    checkboxes.forEach(cb => cb.checked = selectAll.checked);
});

function submitExport(url, errorEl) {
    const formData = new FormData(document.getElementById("cityForm"));
    errorEl.textContent = "";

    fetch(url, {
        method: "POST",
        body: formData
    })
    .then(async res => {
        if (!res.ok) {
            const data = await res.json();
            throw new Error(data.error);
        }
        return res.blob();
    })
    .then(blob => {
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = "";
        document.body.appendChild(a);
        a.click();
        a.remove();
    })
    .catch(err => {
        errorEl.textContent = err.message;
    });
}

document.getElementById("csvBtn").onclick = () =>
    submitExport("/export_csv", document.getElementById("csvError"));

document.getElementById("plotBtn").onclick = () =>
    submitExport("/export_plot", document.getElementById("plotError"));