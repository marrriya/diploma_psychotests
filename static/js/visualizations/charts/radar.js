export function renderRadar(canvas, config) {

    const ctx = canvas.getContext('2d');

    const point = config.points[0];

    const labels = Object.keys(point);
    const values = Object.values(point);

    new Chart(ctx, {

        type: 'radar',

        data: {

            labels: labels,

            datasets: [{

                label: config.title,

                data: values,

                backgroundColor:
                    config.settings.backgroundColor ||
                    'rgba(54,162,235,0.2)',

                borderColor:
                    config.settings.borderColor ||
                    'rgba(54,162,235,1)',

                pointBackgroundColor:
                    config.settings.pointBackgroundColor ||
                    'rgba(54,162,235,1)',

                borderWidth: 2
            }]
        },

        options: {
            responsive: true,
            scales: {
                r: {
                    beginAtZero: true
                }
            }
        }

    });

}