export function renderBar(canvas, config) {

    const ctx = canvas.getContext('2d');

    const point = config.points[0];

    const labels = Object.keys(point);
    const values = Object.values(point);

    new Chart(ctx, {

        type: 'bar',

        data: {

            labels: labels,

            datasets: [{

                label: config.title,

                data: values,

                backgroundColor:
                    config.settings.backgroundColor ||
                    'rgba(59,130,246,0.7)',

                borderColor:
                    config.settings.borderColor ||
                    'rgba(59,130,246,1)',

                borderWidth: 2
            }]
        },

        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }

    });

}