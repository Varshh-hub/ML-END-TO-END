/* ============================================================
   RESUMATCH - WORKING FRONTEND
   ============================================================ */

(() => {
    "use strict";

    document.addEventListener("DOMContentLoaded", init);

    function init() {

        // ========================================================
        // ANALYZER ELEMENTS
        // ========================================================

        const resumeInput = document.getElementById("resumeInput");
        const uploadBox = document.getElementById("uploadBox");
        const chooseFile = document.getElementById("chooseFile");
        const fileText = document.getElementById("fileText");

        const targetRole = document.getElementById("targetRole");
        const jobDescription = document.getElementById("jobDescription");
        const charCount = document.getElementById("charCount");

        const analyzeButton =
            document.getElementById("analyzeButton");

        const loading =
            document.getElementById("loading");

        const loadingText =
            document.getElementById("loadingText");

        const errorMessage =
            document.getElementById("errorMessage");


        // ========================================================
        // RESULTS
        // ========================================================

        const results =
            document.getElementById("results");

        const score =
            document.getElementById("score");

        const resultStatus =
            document.getElementById("resultStatus");

        const resultMessage =
            document.getElementById("resultMessage");

        const resultSummary =
            document.getElementById("resultSummary");

        const matchedSkills =
            document.getElementById("matchedSkills");

        const missingSkills =
            document.getElementById("missingSkills");

        const resumeRole =
            document.getElementById("resumeRole");

        const jobRole =
            document.getElementById("jobRole");

        const seniority =
            document.getElementById("seniority");

        const industry =
            document.getElementById("industry");

        const skillRatio =
            document.getElementById("skillRatio");

        const skillProgress =
            document.getElementById("skillProgress");

        const modelName =
            document.getElementById("modelName");

        const prediction =
            document.getElementById("prediction");

        const featureCount =
            document.getElementById("featureCount");


        // ========================================================
        // AI
        // ========================================================

        const aiButtons =
            document.querySelectorAll("[data-ai-action]");

        const aiAnalysisButton =
            document.querySelector(
                '[data-ai-action="analysis"]'
            );

        const aiChatCard =
            document.querySelector(".ai-chat-card");

        const aiAnalysisCard =
            document.querySelector(
                '[data-ai-action="analysis"]'
            )?.closest(".ai-card");

        const aiChatQuestion =
            document.getElementById("aiChatQuestion");

        const aiChatSend =
            document.getElementById("aiChatSend");

        const aiChatMessages =
            document.getElementById("aiChatMessages");

        const aiOutput =
            document.getElementById("aiOutput");

        const aiOutputContent =
            document.getElementById("aiOutputContent");

        const closeAiOutput =
            document.getElementById("closeAiOutput");


        // ========================================================
        // STATE
        // ========================================================

        let latestAnalysisResult = null;
        let latestResumeText = "";
        let latestJobDescription = "";
        let latestTargetRole = "";

        let loadingTimer = null;


        // ========================================================
        // INITIALIZE
        // ========================================================

        setAIInteractive(true);

        bindEvents();

        checkBackend();


        // ========================================================
        // EVENTS
        // ========================================================

        function bindEvents() {

            // --------------------------------------------
            // PDF INPUT
            // --------------------------------------------

            resumeInput?.addEventListener(
                "change",
                () => {
                    handleResumeFile(
                        resumeInput.files?.[0]
                    );
                }
            );


            // --------------------------------------------
            // CHOOSE FILE BUTTON
            // --------------------------------------------

            chooseFile?.addEventListener(
                "click",
                (event) => {
                    event.preventDefault();
                    event.stopPropagation();

                    resumeInput?.click();
                }
            );


            // --------------------------------------------
            // UPLOAD BOX
            // --------------------------------------------

            uploadBox?.addEventListener(
                "click",
                (event) => {

                    if (
                        event.target.closest("input") ||
                        event.target.closest("button") ||
                        event.target.closest("label")
                    ) {
                        return;
                    }

                    resumeInput?.click();
                }
            );


            // --------------------------------------------
            // DRAG OVER
            // --------------------------------------------

            uploadBox?.addEventListener(
                "dragover",
                (event) => {
                    event.preventDefault();

                    uploadBox.classList.add(
                        "dragging"
                    );
                }
            );


            // --------------------------------------------
            // DRAG LEAVE
            // --------------------------------------------

            uploadBox?.addEventListener(
                "dragleave",
                () => {

                    uploadBox.classList.remove(
                        "dragging"
                    );
                }
            );


            // --------------------------------------------
            // DROP PDF
            // --------------------------------------------

            uploadBox?.addEventListener(
                "drop",
                (event) => {

                    event.preventDefault();

                    uploadBox.classList.remove(
                        "dragging"
                    );

                    const file =
                        event.dataTransfer?.files?.[0];

                    if (!file) return;

                    try {

                        const transfer =
                            new DataTransfer();

                        transfer.items.add(file);

                        resumeInput.files =
                            transfer.files;

                    } catch (error) {

                        console.warn(
                            "Could not assign dropped file:",
                            error
                        );
                    }

                    handleResumeFile(file);
                }
            );


            // --------------------------------------------
            // JOB DESCRIPTION COUNTER
            // --------------------------------------------

            jobDescription?.addEventListener(
                "input",
                updateCharCount
            );

            updateCharCount();


            // --------------------------------------------
            // ANALYZE BUTTON
            // --------------------------------------------

            analyzeButton?.addEventListener(
                "click",
                (event) => {

                    event.preventDefault();

                    analyzeResume();
                }
            );


            // --------------------------------------------
            // GENAI
            // --------------------------------------------

            aiAnalysisButton?.addEventListener(
                "click",
                (event) => {

                    event.preventDefault();
                    event.stopPropagation();

                    runGenAIAnalysis();
                }
            );


            // --------------------------------------------
            // CHAT
            // --------------------------------------------

            aiChatSend?.addEventListener(
                "click",
                (event) => {

                    event.preventDefault();

                    sendChatMessage();
                }
            );


            // --------------------------------------------
            // CHAT ENTER
            // --------------------------------------------

            aiChatQuestion?.addEventListener(
                "keydown",
                (event) => {

                    if (
                        event.key === "Enter" &&
                        !event.shiftKey
                    ) {

                        event.preventDefault();

                        sendChatMessage();
                    }
                }
            );


            // --------------------------------------------
            // CLOSE AI OUTPUT
            // --------------------------------------------

            closeAiOutput?.addEventListener(
                "click",
                () => {

                    aiOutput?.classList.remove(
                        "visible"
                    );
                }
            );


            // --------------------------------------------
            // GENAI CARD CLICK
            // --------------------------------------------

            aiAnalysisCard?.addEventListener(
                "click",
                (event) => {

                    if (
                        event.target.closest("button")
                    ) {
                        return;
                    }

                    runGenAIAnalysis();
                }
            );


            // --------------------------------------------
            // CHAT CARD CLICK
            // --------------------------------------------

            aiChatCard?.addEventListener(
                "click",
                (event) => {

                    if (
                        event.target.closest("textarea") ||
                        event.target.closest("button")
                    ) {
                        return;
                    }

                    aiChatQuestion?.focus();
                }
            );
        }


        // ========================================================
        // PDF HANDLING
        // ========================================================

        function handleResumeFile(file) {

            hideError();

            if (!file) {
                return;
            }

            const isPDF =
                file.type === "application/pdf" ||
                file.name
                    .toLowerCase()
                    .endsWith(".pdf");

            if (!isPDF) {

                resetResumeInput();

                showError(
                    "Please choose a PDF resume only."
                );

                return;
            }


            // Maximum 10 MB

            if (
                file.size >
                10 * 1024 * 1024
            ) {

                resetResumeInput();

                showError(
                    "Your PDF must be smaller than 10 MB."
                );

                return;
            }


            // Display filename

            if (fileText) {

                fileText.textContent =
                    file.name;
            }


            uploadBox?.classList.add(
                "has-file"
            );


            console.log(
                "PDF selected:",
                file.name
            );
        }


        function resetResumeInput() {

            if (resumeInput) {

                resumeInput.value = "";
            }

            if (fileText) {

                fileText.textContent =
                    "PDF format · Maximum 10 MB";
            }

            uploadBox?.classList.remove(
                "has-file"
            );
        }


        // ========================================================
        // CHARACTER COUNTER
        // ========================================================

        function updateCharCount() {

            if (
                !charCount ||
                !jobDescription
            ) {
                return;
            }

            charCount.textContent =
                jobDescription.value.length;
        }


        // ========================================================
        // ANALYZE RESUME
        // ========================================================

        async function analyzeResume() {

            hideError();


            // --------------------------------------------
            // GET FILE
            // --------------------------------------------

            const file =
                resumeInput?.files?.[0];


            const role =
                targetRole?.value?.trim() || "";


            const jd =
                jobDescription?.value?.trim() || "";


            // --------------------------------------------
            // VALIDATE PDF
            // --------------------------------------------

            if (!file) {

                showError(
                    "Please upload your PDF resume first."
                );

                uploadBox?.scrollIntoView({
                    behavior: "smooth",
                    block: "center"
                });

                return;
            }


            if (
                !file.name
                    .toLowerCase()
                    .endsWith(".pdf")
            ) {

                showError(
                    "Please upload a PDF resume only."
                );

                return;
            }


            if (
                file.size >
                10 * 1024 * 1024
            ) {

                showError(
                    "Your PDF must be smaller than 10 MB."
                );

                return;
            }


            // --------------------------------------------
            // VALIDATE TARGET ROLE
            // --------------------------------------------

            if (!role) {

                showError(
                    "Please select a target role."
                );

                targetRole?.focus();

                return;
            }


            // --------------------------------------------
            // VALIDATE JOB DESCRIPTION
            // --------------------------------------------

            if (!jd) {

                showError(
                    "Please paste the job description."
                );

                jobDescription?.focus();

                return;
            }


            // --------------------------------------------
            // FORM DATA
            // --------------------------------------------

            const formData =
                new FormData();


            formData.append(
                "resume",
                file
            );


            formData.append(
                "target_role",
                role
            );


            formData.append(
                "job_description",
                jd
            );


            // --------------------------------------------
            // START LOADING
            // --------------------------------------------

            setLoading(true);


            console.log(
                "Sending resume to /api/analyze..."
            );


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
                    await parseResponse(
                        response
                    );


                console.log(
                    "Analysis response:",
                    data
                );


                if (!data.success) {

                    throw new Error(
                        data.message ||
                        data.error ||
                        "Resume analysis failed."
                    );
                }


                // --------------------------------------------
                // SAVE DATA
                // --------------------------------------------

                const result =
                    data.result || {};


                latestResumeText =
                    data.resume_text ||
                    result.resume_text ||
                    data.resume ||
                    result.resume ||
                    "";


                latestJobDescription =
                    data.job_description ||
                    jd;


                latestTargetRole =
                    data.target_role ||
                    result.selected_role ||
                    role;


                latestAnalysisResult =
                    result;


                // --------------------------------------------
                // DISPLAY RESULT
                // --------------------------------------------

                displayResults(result);


                // --------------------------------------------
                // AI READY
                // --------------------------------------------

                setAIInteractive(true);

                showAIReadyMessage();


                // --------------------------------------------
                // SCROLL RESULTS
                // --------------------------------------------

                results?.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });


            } catch (error) {

                console.error(
                    "Analysis error:",
                    error
                );


                showError(
                    error.message ||
                    "Could not connect to the ResuMatch backend."
                );


            } finally {

                setLoading(false);
            }
        }


        // ========================================================
        // DISPLAY RESULTS
        // ========================================================

        function displayResults(result) {

            results?.classList.add(
                "visible"
            );


            // --------------------------------------------
            // SKILL COVERAGE
            // --------------------------------------------

            const ratio =
                Number(
                    result.skill_match_ratio ?? 0
                );


            const ratioPercent =
                ratio <= 1
                    ? ratio * 100
                    : ratio;


            // --------------------------------------------
            // MATCH SCORE
            //
            // DISPLAY ONLY:
            // Match Score = Skill Coverage
            //
            // The ML model itself is NOT changed.
            // --------------------------------------------

            const displayMatchScore =
                Math.max(
                    0,
                    Math.min(
                        100,
                        Number(
                            result.display_match_score ??
                            ratioPercent
                        )
                    )
                );


            animateScore(
                displayMatchScore
            );


            // --------------------------------------------
            // BASIC RESULT DATA
            // --------------------------------------------

            setText(
                resultStatus,
                result.status ||
                "ANALYSIS COMPLETE"
            );


            setText(
                resultMessage,
                result.message ||
                "Resume analysis completed."
            );


            setText(
                resultSummary,
                result.summary ||
                ""
            );


            setText(
                resumeRole,
                result.resume_role ||
                "Not detected"
            );


            setText(
                jobRole,
                result.selected_role ||
                result.job_role ||
                latestTargetRole ||
                "Not detected"
            );


            setText(
                seniority,
                result.resume_seniority ||
                "Not detected"
            );


            setText(
                industry,
                result.resume_industry ||
                "Not detected"
            );


            setText(
                modelName,
                result.model ||
                "ResuMatch ML"
            );


            setText(
                prediction,
                result.prediction ??
                result.Prediction ??
                "—"
            );


            setText(
                featureCount,
                result.feature_count ??
                "—"
            );


            // --------------------------------------------
            // SKILL COVERAGE
            // --------------------------------------------

            setText(
                skillRatio,
                `${ratioPercent.toFixed(1)}%`
            );


            if (skillProgress) {

                setTimeout(() => {

                    skillProgress.style.width =
                        `${Math.max(
                            0,
                            Math.min(
                                100,
                                ratioPercent
                            )
                        )}%`;

                }, 100);
            }


            // --------------------------------------------
            // SKILLS
            // --------------------------------------------

            renderSkills(
                matchedSkills,
                result.matched_skills ||
                [],
                false
            );


            renderSkills(
                missingSkills,
                result.missing_skills ||
                [],
                true
            );
        }


        // ========================================================
        // SCORE ANIMATION
        // ========================================================

        function animateScore(value) {

            if (!score) {
                return;
            }


            const target =
                Math.max(
                    0,
                    Math.min(
                        100,
                        Number(value) || 0
                    )
                );


            const startTime =
                performance.now();


            const duration =
                800;


            function frame(now) {

                const progress =
                    Math.min(
                        (now - startTime) /
                        duration,
                        1
                    );


                const eased =
                    1 -
                    Math.pow(
                        1 - progress,
                        3
                    );


                score.textContent =
                    `${(
                        target * eased
                    ).toFixed(1)}%`;


                if (progress < 1) {

                    requestAnimationFrame(
                        frame
                    );
                }
            }


            requestAnimationFrame(
                frame
            );
        }


        // ========================================================
        // RENDER SKILLS
        // ========================================================

        function renderSkills(
            container,
            skills,
            isMissing
        ) {

            if (!container) {
                return;
            }


            container.innerHTML = "";


            if (
                !Array.isArray(skills) ||
                skills.length === 0
            ) {

                const empty =
                    document.createElement(
                        "span"
                    );


                empty.textContent =
                    isMissing
                        ? "No missing skills detected"
                        : "No matching skills detected";


                container.appendChild(
                    empty
                );


                return;
            }


            skills.forEach(
                (skill) => {

                    const item =
                        document.createElement(
                            "span"
                        );


                    item.textContent =
                        isMissing
                            ? `+ ${skill}`
                            : `✓ ${skill}`;


                    container.appendChild(
                        item
                    );
                }
            );
        }


        // ========================================================
        // GENAI ANALYSIS
        // ========================================================

        async function runGenAIAnalysis() {

            hideError();


            if (
                !latestAnalysisResult ||
                !latestResumeText
            ) {

                showAIOutput(`
                    <h4>Run Resume Analysis First</h4>

                    <p>
                        Upload your PDF, select a target role,
                        paste the job description and click
                        <strong>Analyze Resume</strong>.
                    </p>
                `);


                document
                    .querySelector("#analyzer")
                    ?.scrollIntoView({
                        behavior: "smooth",
                        block: "start"
                    });


                return;
            }


            setButtonBusy(
                aiAnalysisButton,
                true,
                "Generating AI Analysis..."
            );


            showAIOutput(`
                <p>
                    ResuMatch GenAI is analyzing your
                    completed ML result...
                </p>
            `);


            try {

                const response =
                    await fetch(
                        "/api/genai-analysis",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body:
                                JSON.stringify({
                                    resume:
                                        latestResumeText,

                                    job_description:
                                        latestJobDescription,

                                    result:
                                        latestAnalysisResult
                                })
                        }
                    );


                const data =
                    await parseResponse(
                        response
                    );


                if (!data.success) {

                    throw new Error(
                        data.message ||
                        data.error ||
                        "GenAI analysis failed."
                    );
                }


                const answer =
                    data.response ||
                    data.analysis ||
                    data.text ||
                    "No GenAI response was returned.";


                showAIOutput(
                    formatAIResponse(
                        answer
                    )
                );


            } catch (error) {

                console.error(
                    "GenAI error:",
                    error
                );


                showAIOutput(`
                    <h4>GenAI Error</h4>

                    <p class="ai-error">
                        ${escapeHTML(
                            error.message ||
                            "GenAI could not generate a response."
                        )}
                    </p>

                    <p>
                        Check the Flask terminal
                        for the exact Gemini error.
                    </p>
                `);


            } finally {

                setButtonBusy(
                    aiAnalysisButton,
                    false,
                    "Generate AI Analysis →"
                );
            }
        }


        // ========================================================
        // CHAT
        // ========================================================

        async function sendChatMessage() {

            hideError();


            const question =
                aiChatQuestion?.value?.trim() ||
                "";


            if (
                !latestAnalysisResult ||
                !latestResumeText
            ) {

                showChatMessage(
                    "ResuMatch",
                    "Run the resume analysis first. Then I can answer questions using your actual resume, job description and ML result.",
                    "assistant"
                );


                document
                    .querySelector("#analyzer")
                    ?.scrollIntoView({
                        behavior: "smooth",
                        block: "start"
                    });


                return;
            }


            if (!question) {

                showChatMessage(
                    "ResuMatch",
                    "Please type a question first.",
                    "assistant"
                );


                aiChatQuestion?.focus();


                return;
            }


            showChatMessage(
                "You",
                question,
                "user"
            );


            if (aiChatQuestion) {

                aiChatQuestion.value = "";
            }


            const thinking =
                showChatMessage(
                    "ResuMatch",
                    "Thinking...",
                    "assistant thinking"
                );


            setChatBusy(true);


            try {

                const response =
                    await fetch(
                        "/api/chat",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body:
                                JSON.stringify({

                                    resume:
                                        latestResumeText,

                                    job_description:
                                        latestJobDescription,

                                    result:
                                        latestAnalysisResult,

                                    question:
                                        question
                                })
                        }
                    );


                const data =
                    await parseResponse(
                        response
                    );


                thinking?.remove();


                if (!data.success) {

                    throw new Error(
                        data.message ||
                        data.error ||
                        "ResuMatch Chat failed."
                    );
                }


                const answer =
                    data.response ||
                    data.answer ||
                    data.text ||
                    "No response was returned.";


                showChatMessage(
                    "ResuMatch",
                    answer,
                    "assistant"
                );


            } catch (error) {

                console.error(
                    "Chat error:",
                    error
                );


                thinking?.remove();


                showChatMessage(
                    "ResuMatch",
                    error.message ||
                    "Chat could not generate a response.",
                    "assistant error"
                );


            } finally {

                setChatBusy(false);
            }
        }


        // ========================================================
        // CHAT MESSAGE
        // ========================================================

        function showChatMessage(
            sender,
            message,
            type
        ) {

            if (!aiChatMessages) {
                return null;
            }


            const wrapper =
                document.createElement(
                    "div"
                );


            wrapper.className =
                `chat-message ${type}`;


            const senderElement =
                document.createElement(
                    "span"
                );


            senderElement.className =
                "chat-sender";


            senderElement.textContent =
                sender;


            const bubble =
                document.createElement(
                    "div"
                );


            bubble.className =
                "chat-bubble";


            if (
                type.includes(
                    "assistant"
                )
            ) {

                bubble.innerHTML =
                    formatAIResponse(
                        message
                    );

            } else {

                bubble.textContent =
                    message;
            }


            wrapper.appendChild(
                senderElement
            );


            wrapper.appendChild(
                bubble
            );


            aiChatMessages.appendChild(
                wrapper
            );


            aiChatMessages.scrollTop =
                aiChatMessages.scrollHeight;


            return wrapper;
        }


        // ========================================================
        // AI INTERACTIVE
        // ========================================================

        function setAIInteractive(
            enabled
        ) {

            aiButtons.forEach(
                (button) => {

                    button.disabled = false;

                    button.classList.remove(
                        "disabled"
                    );

                    button.setAttribute(
                        "aria-disabled",
                        "false"
                    );
                }
            );


            if (aiChatQuestion) {

                aiChatQuestion.disabled =
                    false;
            }


            if (aiChatSend) {

                aiChatSend.disabled =
                    false;
            }
        }


        function setButtonBusy(
            button,
            busy,
            label
        ) {

            if (!button) {
                return;
            }


            button.disabled =
                busy;


            button.classList.toggle(
                "loading",
                busy
            );


            if (label) {

                if (
                    !button.dataset.originalLabel
                ) {

                    button.dataset.originalLabel =
                        button.textContent;
                }


                button.textContent =
                    label;
            }


            if (!busy) {

                if (
                    button.dataset.originalLabel
                ) {

                    button.textContent =
                        button.dataset.originalLabel;

                    delete button.dataset
                        .originalLabel;
                }
            }
        }


        function setChatBusy(
            busy
        ) {

            if (aiChatQuestion) {

                aiChatQuestion.disabled =
                    busy;
            }


            if (aiChatSend) {

                aiChatSend.disabled =
                    busy;


                aiChatSend.textContent =
                    busy
                        ? "Thinking..."
                        : "Ask ResuMatch →";
            }
        }


        function showAIReadyMessage() {

            if (!aiChatMessages) {
                return;
            }


            const placeholder =
                aiChatMessages.querySelector(
                    ".chat-message.assistant"
                );


            if (!placeholder) {
                return;
            }


            const bubble =
                placeholder.querySelector(
                    ".chat-bubble"
                );


            if (
                bubble &&
                bubble.textContent.includes(
                    "Run the resume analysis"
                )
            ) {

                bubble.textContent =
                    "Analysis complete. Ask me anything about your resume, job description or ResuMatch result.";
            }
        }


        function showAIOutput(
            html
        ) {

            if (
                !aiOutput ||
                !aiOutputContent
            ) {

                return;
            }


            aiOutputContent.innerHTML =
                html;


            aiOutput.classList.add(
                "visible"
            );


            aiOutput.scrollIntoView({
                behavior: "smooth",
                block: "center"
            });
        }


        // ========================================================
        // BACKEND HEALTH
        // ========================================================

        async function checkBackend() {

            try {

                const response =
                    await fetch(
                        "/api/health",
                        {
                            method: "GET",
                            cache: "no-store"
                        }
                    );


                const data =
                    await parseResponse(
                        response
                    );


                console.log(
                    "ResuMatch health:",
                    data
                );


                if (
                    !data.genai_package
                ) {

                    console.warn(
                        "google-genai is not installed."
                    );
                }


                if (
                    !data.genai_configured
                ) {

                    console.warn(
                        "GEMINI_API_KEY is not configured."
                    );
                }


            } catch (error) {

                console.error(
                    "Backend health check failed:",
                    error
                );
            }
        }


        // ========================================================
        // LOADING
        // ========================================================

        function setLoading(
            active
        ) {

            if (loading) {

                loading.classList.toggle(
                    "active",
                    active
                );
            }


            if (analyzeButton) {

                analyzeButton.disabled =
                    active;
            }


            if (active) {

                const messages = [

                    "Reading your resume...",

                    "Extracting skills...",

                    "Comparing your profile...",

                    "Running the ResuMatch model...",

                    "Preparing your result..."

                ];


                let index = 0;


                if (loadingText) {

                    loadingText.textContent =
                        messages[0];
                }


                loadingTimer =
                    setInterval(
                        () => {

                            index =
                                (
                                    index + 1
                                ) %
                                messages.length;


                            if (loadingText) {

                                loadingText.textContent =
                                    messages[index];
                            }

                        },
                        900
                    );


            } else {

                if (loadingTimer) {

                    clearInterval(
                        loadingTimer
                    );

                    loadingTimer = null;
                }
            }
        }


        // ========================================================
        // RESPONSE PARSER
        // ========================================================

        async function parseResponse(
            response
        ) {

            const raw =
                await response.text();


            let data = {};


            try {

                data =
                    raw
                        ? JSON.parse(raw)
                        : {};

            } catch {

                throw new Error(
                    `Flask returned an invalid response (${response.status}).`
                );
            }


            if (!response.ok) {

                throw new Error(
                    data.message ||
                    data.error ||
                    `Request failed with status ${response.status}.`
                );
            }


            return data;
        }


        // ========================================================
        // SET TEXT
        // ========================================================

        function setText(
            element,
            value
        ) {

            if (!element) {
                return;
            }


            element.textContent =
                value === null ||
                value === undefined ||
                value === ""
                    ? "—"
                    : String(value);
        }


        // ========================================================
        // ERROR
        // ========================================================

        function showError(
            message
        ) {

            console.error(
                message
            );


            if (errorMessage) {

                errorMessage.textContent =
                    message;


                errorMessage.classList.add(
                    "active"
                );


                errorMessage.scrollIntoView({
                    behavior: "smooth",
                    block: "center"
                });

            } else {

                alert(message);
            }
        }


        function hideError() {

            if (!errorMessage) {
                return;
            }


            errorMessage.textContent =
                "";


            errorMessage.classList.remove(
                "active"
            );
        }


        // ========================================================
        // ESCAPE HTML
        // ========================================================

        function escapeHTML(
            value
        ) {

            const div =
                document.createElement(
                    "div"
                );


            div.textContent =
                value == null
                    ? ""
                    : String(value);


            return div.innerHTML;
        }


        // ========================================================
        // FORMAT AI RESPONSE
        // ========================================================

        function formatAIResponse(
            value
        ) {

            let text =
                String(
                    value || ""
                ).trim();


            if (!text) {

                return `
                    <p>
                        No response was returned.
                    </p>
                `;
            }


            let html =
                escapeHTML(text);


            // Bold

            html =
                html.replace(
                    /\*\*(.+?)\*\*/g,
                    "<strong>$1</strong>"
                );


            // Headings

            html =
                html.replace(
                    /^###\s+(.+)$/gm,
                    "<h4>$1</h4>"
                );


            html =
                html.replace(
                    /^##\s+(.+)$/gm,
                    "<h4>$1</h4>"
                );


            html =
                html.replace(
                    /^#\s+(.+)$/gm,
                    "<h3>$1</h3>"
                );


            // Bullets

            html =
                html.replace(
                    /^[-*]\s+(.+)$/gm,
                    "<li>$1</li>"
                );


            html =
                html.replace(
                    /(<li>.*<\/li>(?:\s*<br>)?)+/g,
                    (list) =>
                        `<ul>${list}</ul>`
                );


            // Paragraphs

            html =
                html.replace(
                    /\n\n+/g,
                    "</p><p>"
                );


            // Line breaks

            html =
                html.replace(
                    /\n/g,
                    "<br>"
                );


            return `<p>${html}</p>`;
        }
    }

})();