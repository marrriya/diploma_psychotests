export function renderRadar(canvas, config) {

    new Chart(canvas, {
        type: 'radar',

        data: {
            labels: config.labels,

            datasets: [{
                label: config.title,
                data: config.values
            }]
        }
    });
}