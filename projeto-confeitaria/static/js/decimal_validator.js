document.querySelectorAll(".only-numbers").forEach((input) => {
        input.addEventListener("input", () => {
            if (input.inputMode === "decimal") {
                let value = input.value.replace(/[^\d.,]/g, "");
                value = value.replace(",", ".");
                const parts = value.split(".");
                if (parts.length > 2) {
                    value = parts[0] + "." + parts.slice(1).join("");
                }
                input.value = value;
                return;
            }

            input.value = input.value.replace(/\D/g, "");
        });
    });