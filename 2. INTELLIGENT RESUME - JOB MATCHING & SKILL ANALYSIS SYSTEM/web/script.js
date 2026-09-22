const resumeInput =
document.getElementById("resumeInput");

const chooseFile =
document.getElementById("chooseFile");

const uploadBox =
document.getElementById("uploadBox");

const fileText =
document.getElementById("fileText");

const jobDescription =
document.getElementById("jobDescription");

const targetRole =
document.getElementById("targetRole");

const characterCount =
document.getElementById("characterCount");

const analyzeButton =
document.getElementById("analyzeButton");

const buttonText =
document.getElementById("buttonText");

const buttonArrow =
document.getElementById("buttonArrow");

const loading =
document.getElementById("loading");

const loadingText =
document.getElementById("loadingText");

const errorMessage =
document.getElementById("errorMessage");

const results =
document.getElementById("results");

/* ================= FILE ================= */

chooseFile.addEventListener(
"click",
function () {
resumeInput.click();
}
);

uploadBox.addEventListener(
"dragover",
function (event) {
event.preventDefault();


    uploadBox.style.transform =
        "translateY(-5px)";
}


);

uploadBox.addEventListener(
"dragleave",
function () {
uploadBox.style.transform = "";
}
);

uploadBox.addEventListener(
"drop",
function (event) {

    event.preventDefault();

    uploadBox.style.transform = "";

    const files =
        event.dataTransfer.files;

    if (files.length > 0) {

        resumeInput.files =
            files;

        updateFileName();
    }
}


);

resumeInput.addEventListener(
"change",
updateFileName
);

function updateFileName() {


if (!resumeInput.files.length) {

    fileText.textContent =
        "PDF format · Maximum 10 MB";

    return;
}


const file =
    resumeInput.files[0];


if (
    !file.name
        .toLowerCase()
        .endsWith(".pdf")
) {

    showError(
        "Please upload a PDF resume."
    );

    resumeInput.value = "";

    return;
}


if (
    file.size >
    10 * 1024 * 1024
) {

    showError(
        "Resume must be smaller than 10 MB."
    );

    resumeInput.value = "";

    return;
}


fileText.textContent =
    file.name;


}

/* ================= JD COUNT ================= */

jobDescription.addEventListener(
"input",
function () {


    const count =
        jobDescription.value.length;

    characterCount.textContent =
        `${count.toLocaleString()} characters`;
}


);

/* ================= ANALYSIS ================= */

analyzeButton.addEventListener(
"click",
analyzeResume
);

async function analyzeResume() {

hideError();


if (!resumeInput.files.length) {

    showError(
        "Please upload your resume first."
    );

    return;
}


if (!targetRole.value) {

    showError(
        "Please select the role you want to apply for."
    );

    targetRole.focus();

    return;
}


if (
    !jobDescription.value.trim()
) {

    showError(
        "Please paste the job description."
    );

    jobDescription.focus();

    return;
}


const resume =
    resumeInput.files[0];


const formData =
    new FormData();


formData.append(
    "resume",
    resume
);


formData.append(
    "job_description",
    jobDescription.value
);


formData.append(
    "target_role",
    targetRole.value
);


setLoading(true);


try {

    const response =
        await fetch(
            "/api/analyze",
            {
                method: "POST",
                body: formData
            }
        );


    const data =
        await response.json();


    if (!response.ok) {

        throw new Error(
            data.error ||
            "Something went wrong."
        );
    }


    displayResults(data);

}


catch (error) {

    showError(
        error.message
    );

}


finally {

    setLoading(false);
}


}

/* ================= LOADING ================= */

function setLoading(state) {


if (state) {

    analyzeButton.disabled =
        true;

    buttonText.textContent =
        "Analyzing...";

    buttonArrow.textContent =
        "●";


    loading.classList.add(
        "active"
    );


    const messages = [

        "Reading your resume...",

        "Checking the selected role...",

        "Extracting relevant skills...",

        "Comparing job requirements...",

        "Running the ML model...",

        "Preparing your analysis..."

    ];


    let index = 0;


    loadingText.textContent =
        messages[0];


    window.loadingInterval =
        setInterval(
            function () {

                index =
                    (index + 1)
                    % messages.length;

                loadingText.textContent =
                    messages[index];

            },
            1000
        );

}


else {

    analyzeButton.disabled =
        false;

    buttonText.textContent =
        "Analyze Resume";

    buttonArrow.textContent =
        "→";


    loading.classList.remove(
        "active"
    );


    clearInterval(
        window.loadingInterval
    );
}


}

/* ================= RESULTS ================= */

function displayResults(data) {

results.classList.add(
    "visible"
);


const score =
    Math.round(
        Number(data.match_probability) || 0
    );


/*
 * FIX:
 * Only update elements that actually exist
 * in index.html.
 */

document.getElementById(
    "score"
).textContent =
    score;


animateScore(score);


document.getElementById(
    "resultStatus"
).textContent =
    data.status
        ? data.status.toUpperCase()
        : "MATCH ANALYSIS";


document.getElementById(
    "resultMessage"
).textContent =
    data.message || "—";


document.getElementById(
    "resultSummary"
).textContent =
    data.summary || "—";


document.getElementById(
    "modelName"
).textContent =
    data.model || "HistGradientBoosting";


document.getElementById(
    "prediction"
).textContent =
    data.prediction === 1
        ? "MATCH"
        : "NON-MATCH";


renderSkills(
    "matchedSkills",
    data.matched_skills,
    "✓"
);


renderSkills(
    "missingSkills",
    data.missing_skills,
    "×"
);


results.scrollIntoView({
    behavior: "smooth"
});


}

/* ================= SCORE ANIMATION ================= */

function animateScore(target) {


const scoreElement =
    document.getElementById(
        "score"
    );


if (!scoreElement) {
    return;
}


let current = 0;


if (target <= 0) {

    scoreElement.textContent =
        "0";

    return;
}


const interval =
    setInterval(
        function () {

            current++;

            scoreElement.textContent =
                current;


            if (current >= target) {

                clearInterval(
                    interval
                );
            }

        },
        15
    );


}

/* ================= SKILLS ================= */

function renderSkills(
elementId,
skills,
icon
) {


const container =
    document.getElementById(
        elementId
    );


if (!container) {
    return;
}


container.innerHTML = "";


if (
    !skills ||
    skills.length === 0
) {

    const item =
        document.createElement(
            "span"
        );


    item.textContent =
        "No major skills detected.";


    container.appendChild(
        item
    );


    return;
}


skills.forEach(
    function (skill) {

        const item =
            document.createElement(
                "span"
            );


        item.textContent =
            `${icon} ${skill}`;


        container.appendChild(
            item
        );
    }
);


}

/* ================= ERRORS ================= */

function showError(message) {


errorMessage.textContent =
    message;


errorMessage.classList.add(
    "active"
);


errorMessage.scrollIntoView({
    behavior: "smooth",
    block: "center"
});


}

function hideError() {


errorMessage.classList.remove(
    "active"
);

}
