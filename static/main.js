document.addEventListener("DOMContentLoaded", () => {
    const flagButtons = document.querySelectorAll(".flag-btn");

    flagButtons.forEach(button => {
        button.addEventListener("click", async (event) => {
            event.preventDefault();
            const id = button.getAttribute("data-id");

            try {
                const response = await fetch(`/api/measurements/${id}/flag`, {
                    method: "POST"
                });

                if (!response.ok) {
                    console.error("Failed to toggle flag");
                    return;
                }

                const data = await response.json();
                if (data.success) {
                    // For simplicity, just reload to reflect changes
                    window.location.reload();
                }
            } catch (err) {
                console.error("Error calling flag API:", err);
            }
        });
    });
});
