// line.js

export function renderLine(canvas, config) {

    const ctx = canvas.getContext('2d');

    if (!config.points.length) {
        return;
    }

    // =========================================
    // GROUP MODE
    // =========================================

    if (config.points[0].values) {

        const labels = Object.keys(config.points[0].values);

        const datasets = config.points.map(student => ({

            label: student.username,

            data: Object.values(student.values),

            backgroundColor:
                config.settings.backgroundColor ||
                'rgba(75,192,192,0.2)',

            borderColor:
                config.settings.borderColor ||
                'rgba(75,192,192,1)',

            fill:
                config.settings.fill === 'true'

        }));

        new Chart(ctx, {

            type: 'line',

            data: {
                labels,
                datasets
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

        return;
    }

    // =========================================
    // INDIVIDUAL MODE
    // =========================================

    const point = config.points[0];

    const labels = Object.keys(point);
    const values = Object.values(point);

    new Chart(ctx, {

        type: 'line',

        data: {

            labels,

            datasets: [{

                label: config.title,

                data: values,

                backgroundColor:
                    config.settings.backgroundColor ||
                    'rgba(75,192,192,0.2)',

                borderColor:
                    config.settings.borderColor ||
                    'rgba(75,192,192,1)',

                fill:
                    config.settings.fill === 'true'
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