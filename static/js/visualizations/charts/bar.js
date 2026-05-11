export function renderBar(canvas, config) {

    new Chart(canvas, {
        type: 'bar',

        data: {
            labels: config.labels,

            datasets: [{
                label: config.title,
                data: config.values,

                backgroundColor:
                    config.settings.backgroundColor
                    || 'rgba(54,162,235,0.5)',

                borderColor:
                    config.settings.borderColor
                    || 'rgba(54,162,235,1)',

                borderWidth: 1
            }]
        },

        options: {
            responsive: true
        }
    });
}