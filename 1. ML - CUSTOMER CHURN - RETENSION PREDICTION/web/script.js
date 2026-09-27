/* =========================================================
   PAGE LOADER
========================================================= */

window.addEventListener("load", () => {

    const loader = document.getElementById("pageLoader");

    setTimeout(() => {
        loader.classList.add("hidden");
    }, 700);

});


/* =========================================================
   PREDICTION ELEMENTS
========================================================= */

const form = document.getElementById("predictionForm");

const resultSection =
    document.getElementById("result");

const probabilityElement =
    document.getElementById("probability");

const riskElement =
    document.getElementById("risk");

const recommendationList =
    document.getElementById("recommendationList");

const probabilityBar =
    document.getElementById("probabilityBar");

const analyzeButton =
    document.getElementById("analyzeButton");


/* =========================================================
   FORM SUBMISSION
========================================================= */

form.addEventListener("submit", async (event) => {

    event.preventDefault();

    const originalButtonHTML =
        analyzeButton.innerHTML;

    analyzeButton.disabled = true;

    analyzeButton.innerHTML = `
        <span>ANALYZING...</span>
        <span class="button-arrow">↻</span>
    `;


    const data = {

        Age:
            document.getElementById("Age").value,

        Gender:
            document.getElementById("Gender").value,

        Tenure:
            document.getElementById("Tenure").value,

        "Usage Frequency":
            document.getElementById("Usage Frequency").value,

        "Support Calls":
            document.getElementById("Support Calls").value,

        "Payment Delay":
            document.getElementById("Payment Delay").value,

        "Subscription Type":
            document.getElementById("Subscription Type").value,

        "Contract Length":
            document.getElementById("Contract Length").value,

        "Total Spend":
            document.getElementById("Total Spend").value,

        "Last Interaction":
            document.getElementById("Last Interaction").value
    };


    try {

        const response = await fetch("/predict", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify(data)

        });


        const result = await response.json();


        if (!response.ok || result.error) {

            throw new Error(
                result.error ||
                "Prediction failed."
            );

        }


        displayPrediction(result);


    } catch (error) {

        console.error(
            "Prediction error:",
            error
        );

        alert(
            "Something went wrong while analyzing the customer.\n\n" +
            error.message
        );


    } finally {

        analyzeButton.disabled = false;

        analyzeButton.innerHTML =
            originalButtonHTML;

    }

});


/* =========================================================
   DISPLAY PREDICTION
========================================================= */

function displayPrediction(data) {

    const probability =
        Number(data.probability);


    resultSection.classList.remove(
        "hidden"
    );


    riskElement.classList.remove(
        "risk-high",
        "risk-medium",
        "risk-low"
    );


    if (probability >= 70) {

        riskElement.classList.add(
            "risk-high"
        );

    } else if (probability >= 40) {

        riskElement.classList.add(
            "risk-medium"
        );

    } else {

        riskElement.classList.add(
            "risk-low"
        );

    }


    riskElement.textContent =
        data.risk;


    recommendationList.innerHTML = "";


    data.recommendation.forEach(
        (recommendation) => {

            const item =
                document.createElement("li");

            item.textContent =
                recommendation;

            recommendationList.appendChild(
                item
            );

        }
    );


    setTimeout(() => {

        resultSection.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

    }, 100);


    probabilityElement.textContent =
        "0%";

    probabilityBar.style.width =
        "0%";


    animateNumber(
        probabilityElement,
        0,
        probability,
        1000
    );


    setTimeout(() => {

        probabilityBar.style.width =
            `${probability}%`;

    }, 100);


    probabilityBar.classList.remove(
        "risk-high",
        "risk-medium",
        "risk-low"
    );


    if (probability >= 70) {

        probabilityBar.classList.add(
            "risk-high"
        );

    } else if (probability >= 40) {

        probabilityBar.classList.add(
            "risk-medium"
        );

    } else {

        probabilityBar.classList.add(
            "risk-low"
        );

    }

}


/* =========================================================
   NUMBER ANIMATION
========================================================= */

function animateNumber(
    element,
    start,
    end,
    duration
) {

    const startTime =
        performance.now();


    function update(currentTime) {

        const elapsed =
            currentTime - startTime;

        const progress =
            Math.min(
                elapsed / duration,
                1
            );


        const easedProgress =
            1 -
            Math.pow(
                1 - progress,
                3
            );


        const currentValue =
            start +
            (end - start) *
            easedProgress;


        element.textContent =
            `${currentValue.toFixed(1)}%`;


        if (progress < 1) {

            requestAnimationFrame(
                update
            );

        } else {

            element.textContent =
                `${end.toFixed(2)}%`;

        }

    }


    requestAnimationFrame(update);

}


/* =========================================================
   INPUT INTERACTION
========================================================= */

const inputs =
    document.querySelectorAll(
        ".input-field input, .input-field select"
    );


inputs.forEach((input) => {

    input.addEventListener(
        "focus",
        () => {

            input.parentElement.classList.add(
                "active"
            );

        }
    );


    input.addEventListener(
        "blur",
        () => {

            input.parentElement.classList.remove(
                "active"
            );

        }
    );

});


/* =========================================================
   SCROLL REVEAL
========================================================= */

const sections =
    document.querySelectorAll(
        "section"
    );


const observer =
    new IntersectionObserver(
        (entries) => {

            entries.forEach(
                (entry) => {

                    if (
                        entry.isIntersecting
                    ) {

                        entry.target.classList.add(
                            "visible"
                        );

                    }

                }
            );

        },
        {
            threshold: 0.12
        }
    );


sections.forEach((section) => {

    section.classList.add("reveal");

    observer.observe(section);

});


/* =========================================================
   CURSOR GLOW
========================================================= */

const cursorGlow =
    document.createElement("div");

cursorGlow.className =
    "cursor-glow";

document.body.appendChild(
    cursorGlow
);


let mouseX = 0;
let mouseY = 0;

let glowX = 0;
let glowY = 0;


document.addEventListener(
    "mousemove",
    (event) => {

        mouseX = event.clientX;
        mouseY = event.clientY;

    }
);


function animateCursor() {

    glowX +=
        (mouseX - glowX) * 0.12;

    glowY +=
        (mouseY - glowY) * 0.12;


    cursorGlow.style.transform =
        `translate3d(${glowX}px, ${glowY}px, 0)`;


    requestAnimationFrame(
        animateCursor
    );

}

animateCursor();


/* =========================================================
   MAGNETIC BUTTON
========================================================= */

if (analyzeButton) {

    analyzeButton.addEventListener(
        "mousemove",
        (event) => {

            const rect =
                analyzeButton.getBoundingClientRect();

            const x =
                event.clientX -
                rect.left -
                rect.width / 2;

            const y =
                event.clientY -
                rect.top -
                rect.height / 2;


            analyzeButton.style.transform =
                `translate(${x * 0.08}px, ${y * 0.08}px)`;

        }
    );


    analyzeButton.addEventListener(
        "mouseleave",
        () => {

            analyzeButton.style.transform =
                "";

        }
    );

}


/* =========================================================
   INTERACTIVE INPUT TILT
========================================================= */

const interactiveInputs =
    document.querySelectorAll(
        ".input-field"
    );


interactiveInputs.forEach((field) => {

    field.addEventListener(
        "mousemove",
        (event) => {

            const rect =
                field.getBoundingClientRect();

            const x =
                event.clientX -
                rect.left;

            const y =
                event.clientY -
                rect.top;


            const rotateX =
                ((y / rect.height) - 0.5) *
                -2;

            const rotateY =
                ((x / rect.width) - 0.5) *
                2;


            field.style.transform =
                `perspective(500px)
                 rotateX(${rotateX}deg)
                 rotateY(${rotateY}deg)
                 translateY(-2px)`;

        }
    );


    field.addEventListener(
        "mouseleave",
        () => {

            field.style.transform =
                "";

        }
    );

});


/* =========================================================
   TECH STACK HOVER
========================================================= */

const techItems =
    document.querySelectorAll(
        ".tech-stack span"
    );


techItems.forEach((item) => {

    item.addEventListener(
        "mousemove",
        (event) => {

            const rect =
                item.getBoundingClientRect();

            const x =
                event.clientX -
                rect.left;

            const y =
                event.clientY -
                rect.top;


            const moveX =
                ((x / rect.width) - 0.5) *
                5;

            const moveY =
                ((y / rect.height) - 0.5) *
                5;


            item.style.transform =
                `translate(${moveX}px, ${moveY}px)`;

        }
    );


    item.addEventListener(
        "mouseleave",
        () => {

            item.style.transform =
                "";

        }
    );

});


/* =========================================================
   RESULT PANEL HOVER
========================================================= */

const resultPanels =
    document.querySelectorAll(
        ".probability-panel, .recommendation-panel"
    );


resultPanels.forEach((panel) => {

    panel.addEventListener(
        "mousemove",
        (event) => {

            const rect =
                panel.getBoundingClientRect();

            const x =
                event.clientX -
                rect.left;

            const y =
                event.clientY -
                rect.top;


            panel.style.setProperty(
                "--mouse-x",
                `${x}px`
            );

            panel.style.setProperty(
                "--mouse-y",
                `${y}px`
            );

        }
    );

});


/* =========================================================
   RECOMMENDATION HOVER
========================================================= */

document.addEventListener(
    "mouseover",
    (event) => {

        if (
            event.target.matches(
                ".recommendation-list li"
            )
        ) {

            event.target.style.transform =
                "translateX(6px)";

        }

    }
);


document.addEventListener(
    "mouseout",
    (event) => {

        if (
            event.target.matches(
                ".recommendation-list li"
            )
        ) {

            event.target.style.transform =
                "";

        }

    }
);

/* =========================================
   INTERACTIVE FOOTER EFFECTS
   ========================================= */

const footerBox = document.querySelector(".footer-box");

if (footerBox) {

    /* Cursor-following glow */

    footerBox.addEventListener("mousemove", (e) => {

        const rect = footerBox.getBoundingClientRect();

        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        footerBox.style.setProperty(
            "--footer-x",
            `${x}px`
        );

        footerBox.style.setProperty(
            "--footer-y",
            `${y}px`
        );
    });


    /* Footer entrance interaction */

    footerBox.addEventListener("mouseenter", () => {

        footerBox.style.setProperty(
            "--footer-glow-opacity",
            "1"
        );

    });


    footerBox.addEventListener("mouseleave", () => {

        footerBox.style.setProperty(
            "--footer-glow-opacity",
            "0"
        );

        footerBox.style.transform =
            "translateY(0)";
    });


    /* Magnetic movement for action buttons */

    const footerActions =
        footerBox.querySelectorAll(".footer-action");


    footerActions.forEach((action) => {

        action.addEventListener("mousemove", (e) => {

            const rect =
                action.getBoundingClientRect();

            const x =
                e.clientX -
                rect.left -
                rect.width / 2;

            const y =
                e.clientY -
                rect.top -
                rect.height / 2;


            action.style.transform =
                `translate(${x * 0.08}px, ${y * 0.08}px)`;
        });


        action.addEventListener("mouseleave", () => {

            action.style.transform =
                "translate(0, 0)";
        });

    });


    /* Small magnetic effect for social links */

    const footerLinks =
        footerBox.querySelectorAll(".footer-socials a");


    footerLinks.forEach((link) => {

        link.addEventListener("mousemove", (e) => {

            const rect =
                link.getBoundingClientRect();

            const x =
                e.clientX -
                rect.left -
                rect.width / 2;

            const y =
                e.clientY -
                rect.top -
                rect.height / 2;


            link.style.transform =
                `translate(${x * 0.12}px, ${y * 0.12}px)`;
        });


        link.addEventListener("mouseleave", () => {

            link.style.transform =
                "translate(0, 0)";
        });

    });
}



