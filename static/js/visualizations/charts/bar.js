// bar.js

export function renderBar(canvas, config) {

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
                'rgba(59,130,246,0.7)',

            borderColor:
                config.settings.borderColor ||
                'rgba(59,130,246,1)',

            borderWidth: 2

        }));

        new Chart(ctx, {

            type: 'bar',

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

        type: 'bar',

        data: {

            labels,

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