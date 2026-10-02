/* =========================================================
   MOBILE MENU
========================================================= */

const menuButton =
    document.getElementById("menuButton");

const mobileMenu =
    document.getElementById("mobileMenu");


menuButton.addEventListener(
    "click",
    () => {

        mobileMenu.classList.toggle(
            "active"
        );

    }
);


document
    .querySelectorAll(".mobile-menu a")
    .forEach(link => {

        link.addEventListener(
            "click",
            () => {

                mobileMenu.classList.remove(
                    "active"
                );

            }
        );

    });



/* =========================================================
   RECOMMENDATION
========================================================= */

const recommendButton =
    document.getElementById(
        "recommendButton"
    );

const foodInput =
    document.getElementById(
        "foodInput"
    );

const recommendations =
    document.getElementById(
        "recommendations"
    );

const recommendMessage =
    document.getElementById(
        "recommendMessage"
    );


async function getRecommendations() {

    const item =
        foodInput.value.trim();


    if (!item) {

        recommendMessage.textContent =
            "Please enter a food item.";

        recommendations.innerHTML =
            "";

        return;

    }


    recommendMessage.textContent =
        "Analyzing food relationships...";

    recommendations.innerHTML =
        "";


    try {

        const response =
            await fetch(
                `/api/recommend?item=${encodeURIComponent(item)}`
            );


        const data =
            await response.json();


        if (
            !data.success
        ) {

            recommendMessage.textContent =
                data.message ||
                "Something went wrong.";

            return;

        }


        if (
            !data.recommendations ||
            data.recommendations.length === 0
        ) {

            recommendMessage.textContent =
                `No strong association found for "${item}".`;

            return;

        }


        recommendMessage.textContent =
            `Recommendations related to "${item}"`;


        data.recommendations
            .forEach(
                recommendation => {

                    const div =
                        document.createElement(
                            "div"
                        );

                    div.className =
                        "recommend-item";


                    div.innerHTML = `

                        <div class="food-name">
                            ${recommendation.FoodItem}
                        </div>

                        <div class="metric">
                            Confidence:
                            ${recommendation.Confidence}%
                        </div>

                        <div class="lift">
                            Lift:
                            ${recommendation.Lift}
                        </div>

                    `;


                    recommendations.appendChild(
                        div
                    );

                }
            );


    } catch (error) {

        console.error(error);

        recommendMessage.textContent =
            "Unable to connect to the recommendation API.";

    }

}


recommendButton.addEventListener(
    "click",
    getRecommendations
);


foodInput.addEventListener(
    "keydown",
    event => {

        if (
            event.key === "Enter"
        ) {

            getRecommendations();

        }

    }
);



/* =========================================================
   FORECAST
========================================================= */

let forecastChart = null;


async function loadForecast() {

    try {

        const response =
            await fetch(
                "/api/forecast"
            );


        const data =
            await response.json();


        if (
            !data.success
        ) {

            return;

        }


        createForecastChart(
            data.forecast
        );


        createForecastCards(
            data.forecast
        );


    } catch (error) {

        console.error(
            "Forecast error:",
            error
        );

    }

}



/* =========================================================
   CHART
========================================================= */

function createForecastChart(
    forecast
) {

    const canvas =
        document.getElementById(
            "forecastChart"
        );


    if (!canvas) {

        return;

    }


    const labels =
        forecast.map(
            item => item.month
        );


    const orders =
        forecast.map(
            item => item.orders
        );


    const sales =
        forecast.map(
            item => item.sales
        );


    if (forecastChart) {

        forecastChart.destroy();

    }


    forecastChart =
        new Chart(
            canvas,
            {

                type: "line",

                data: {

                    labels: labels,

                    datasets: [

                        {

                            label:
                                "Forecasted Orders",

                            data:
                                orders,

                            borderColor:
                                "#e11d2e",

                            backgroundColor:
                                "rgba(225,29,46,0.08)",

                            tension:
                                0.35,

                            fill:
                                true,

                            yAxisID:
                                "orders"

                        },

                        {

                            label:
                                "Forecasted Sales",

                            data:
                                sales,

                            borderColor:
                                "#111111",

                            backgroundColor:
                                "rgba(17,17,17,0.04)",

                            tension:
                                0.35,

                            fill:
                                false,

                            yAxisID:
                                "sales"

                        }

                    ]

                },


                options: {

                    responsive:
                        true,

                    interaction: {

                        mode:
                            "index",

                        intersect:
                            false

                    },


                    plugins: {

                        legend: {

                            position:
                                "bottom"

                        }

                    },


                    scales: {

                        orders: {

                            type:
                                "linear",

                            position:
                                "left",

                            beginAtZero:
                                true

                        },


                        sales: {

                            type:
                                "linear",

                            position:
                                "right",

                            beginAtZero:
                                true,

                            grid: {

                                drawOnChartArea:
                                    false

                            }

                        }

                    }

                }

            }
        );

}



/* =========================================================
   FORECAST CARDS
========================================================= */

function createForecastCards(
    forecast
) {

    const container =
        document.getElementById(
            "forecastCards"
        );


    container.innerHTML =
        "";


    forecast.forEach(
        item => {

            const card =
                document.createElement(
                    "div"
                );


            card.className =
                "forecast-card";


            card.innerHTML = `

                <h3>
                    ${item.month}
                </h3>

                <div class="forecast-orders">
                    ${Number(
                        item.orders
                    ).toLocaleString()}
                </div>

                <div class="forecast-sales">
                    ₹${Number(
                        item.sales
                    ).toLocaleString(
                        "en-IN",
                        {
                            maximumFractionDigits: 2
                        }
                    )}
                </div>

                <p
                    style="
                        margin-top:10px;
                        color:#777;
                        font-size:11px;
                    "
                >
                    FORECASTED ORDERS / SALES
                </p>

            `;


            container.appendChild(
                card
            );

        }
    );

}



/* =========================================================
   INITIALIZE
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        loadForecast();

    }
);