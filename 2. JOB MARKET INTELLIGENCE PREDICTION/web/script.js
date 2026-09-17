const descriptionInput =
    document.getElementById("jobDescription");

const analyzeButton =
    document.getElementById("analyzeButton");

const clearButton =
    document.getElementById("clearButton");

const charCount =
    document.getElementById("charCount");

const results =
    document.getElementById("results");

const loading =
    document.getElementById("loading");

const prediction =
    document.getElementById("prediction");

const confidence =
    document.getElementById("confidence");

const confidenceBar =
    document.getElementById("confidenceBar");

const topPredictions =
    document.getElementById("topPredictions");


// --------------------------------------------------
// Character counter
// --------------------------------------------------

descriptionInput.addEventListener("input", () => {

    charCount.textContent =
        descriptionInput.value.length;

});


// --------------------------------------------------
// Clear
// --------------------------------------------------

clearButton.addEventListener("click", () => {

    descriptionInput.value = "";

    charCount.textContent = "0";

    results.classList.add("hidden");

    descriptionInput.focus();

});


// --------------------------------------------------
// Analyze
// --------------------------------------------------

analyzeButton.addEventListener("click", async () => {

    const description =
        descriptionInput.value.trim();


    if (!description) {

        descriptionInput.focus();

        descriptionInput.style.borderColor =
            "rgba(255,255,255,0.5)";

        setTimeout(() => {
            descriptionInput.style.borderColor = "";
        }, 500);

        return;
    }


    // Show loading
    loading.classList.remove("hidden");

    results.classList.add("hidden");

    analyzeButton.disabled = true;

    analyzeButton.querySelector(".button-text").textContent =
        "ANALYZING...";


    try {

        const response = await fetch("/predict", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                description: description
            })

        });


        const data = await response.json();


        if (!response.ok) {
            throw new Error(
                data.error || "Prediction failed."
            );
        }


        // ------------------------------------------
        // Prediction
        // ------------------------------------------

        prediction.textContent =
            data.prediction;


        // ------------------------------------------
        // Confidence
        // ------------------------------------------

        confidence.textContent =
            `${data.confidence}%`;

        setTimeout(() => {

            confidenceBar.style.width =
                `${data.confidence}%`;

        }, 100);


        // ------------------------------------------
        // Other predictions
        // ------------------------------------------

        topPredictions.innerHTML = "";


        const predictions =
            data.top_predictions;


        // Find score range for visualization
        const scores =
            predictions.map(item => item.score);

        const maxScore =
            Math.max(...scores);

        const minScore =
            Math.min(...scores);


        predictions.forEach((item, index) => {

            const row =
                document.createElement("div");

            row.className = "role-row";


            let percentage = 20;


            if (maxScore !== minScore) {

                percentage =
                    ((item.score - minScore) /
                    (maxScore - minScore)) * 80 + 20;

            }


            row.innerHTML = `

                <div class="role-name">
                    ${item.role}
                </div>

                <div class="role-bar">
                    <div
                        class="role-bar-fill"
                        style="width: ${percentage}%">
                    </div>
                </div>

                <div class="role-score">
                    ${item.score.toFixed(2)}
                </div>

            `;


            topPredictions.appendChild(row);

        });


        // Show result
        loading.classList.add("hidden");

        results.classList.remove("hidden");


        // Scroll smoothly to results
        setTimeout(() => {

            results.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

        }, 100);


    } catch (error) {

        console.error(error);

        alert(
            error.message ||
            "Unable to analyze the job description."
        );

        loading.classList.add("hidden");

    }


    analyzeButton.disabled = false;

    analyzeButton.querySelector(".button-text").textContent =
        "ANALYZE ROLE";

});


// --------------------------------------------------
// Ctrl / Cmd + Enter
// --------------------------------------------------

descriptionInput.addEventListener(
    "keydown",
    (event) => {

        if (
            (event.ctrlKey || event.metaKey) &&
            event.key === "Enter"
        ) {

            analyzeButton.click();

        }

    }
);