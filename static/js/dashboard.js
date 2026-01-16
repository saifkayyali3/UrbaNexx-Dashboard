document.addEventListener("DOMContentLoaded", () => {
    const selectAll = document.getElementById("select-all");
    const checkboxes = document.querySelectorAll('input[name="cities"]');

    if (selectAll) {
        selectAll.addEventListener("change", () => {
          checkboxes.forEach(cb => cb.checked = selectAll.checked);
        });
    }

    function handleExport(formId, errorId) {
        const form = document.getElementById(formId);
        const errorBox = document.getElementById(errorId);

        if (!form) return;

        form.addEventListener("submit", async (e) => {
            e.preventDefault(); // stop page reload
            errorBox.textContent = "";

            const formData = new FormData(form);

            try {
                const response = await fetch(form.action, {method: "POST",body: formData});

                if (!response.ok) {
                    const data = await response.json();
                    errorBox.textContent = data.error;
                    return;
                }

                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement("a");

                a.href = url;
                a.download = response.headers.get("Content-Disposition")?.split("filename=")[1]?.replace(/"/g, "") || "download";

                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);

            } catch (err) {
                errorBox.textContent = "Unexpected error. Try again.";
            }
        });
    }
    checkboxes.forEach(cb => {
        cb.addEventListener("change", () => {
            const csvError = document.getElementById("csvError");
            if (csvError) csvError.textContent = "";
        });
    });

    handleExport("csvForm", "csvError");
    handleExport("plotForm", "plotError");

});
