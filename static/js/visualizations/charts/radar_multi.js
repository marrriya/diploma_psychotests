export function renderRadarMulti(canvas, config) {

    const ctx = canvas.getContext('2d');

    const points = config.points || [];

    if (!points.length) return;

    // =========================
    // STUDENTS
    // =========================

    const students = points.map(p => p.username);

    // =========================
    // SCALES
    // =========================

    const scales = Object.keys(points[0].values || {});

    // =========================
    // LABELS
    // Экстраверсия · student1
    // Экстраверсия · student2
    // =========================

    const labels = [];

    scales.forEach(scale => {

        students.forEach(student => {

            labels.push(`${scale} · ${student}`);

        });

    });

    // =========================
    // COLORS PER SCALE
    // =========================

    const scaleColors = {};

    scales.forEach((scale, idx) => {

        scaleColors[scale] =
            `hsl(${idx * 360 / scales.length}, 80%, 55%)`;

    });

    // =========================
    // DATASETS
    // =========================

    const datasets = scales.map((scale, scaleIndex) => {

        const data = [];

        scales.forEach(currentScale => {

            students.forEach(student => {

                const row = points.find(
                    p => p.username === student
                );

                // показываем значения
                // ТОЛЬКО для своей шкалы
                if (currentScale === scale) {

                    data.push(
                        row?.values?.[scale] ?? 0
                    );

                } else {

                    data.push(null);

                }

            });

        });

        return {

            label: scale,

            data,

            borderColor: scaleColors[scale],
            backgroundColor:
                scaleColors[scale].replace("55%)", "55%, 0.15)"),

            pointRadius: 5,
            borderWidth: 2,
            spanGaps: false
        };
    });
    const allValues = [];

    points.forEach(p => {

        Object.entries(p.values || {}).forEach(([_, value]) => {
            allValues.push(value);
        });

    });

    const maxValue = Math.max(...allValues, 10);

    // небольшой запас сверху
    const chartMax = Math.ceil(maxValue * 1.15);
    // =========================
    // CHART
    // =========================
    new Chart(ctx, {

        type: 'radar',

        data: {
            labels,
            datasets
        },

        options: {

            responsive: true,

            scales: {
                r: {

                    beginAtZero: true,

                    min: 0,

                    max: chartMax,

                    ticks: {
                        stepSize: Math.ceil(chartMax / 5)
                    }
                }
            },

            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });

    // new Chart(ctx, {

    //     type: 'radar',

    //     data: {
    //         labels,
    //         datasets
    //     },

    //     options: {

    //         responsive: true,

    //         scales: {
    //             r: {
    //                 beginAtZero: true,
    //                 suggestedMax: 100
    //             }
    //         },

    //         plugins: {
    //             legend: {
    //                 position: 'bottom'
    //             }
    //         }
    //     }
    // });
}