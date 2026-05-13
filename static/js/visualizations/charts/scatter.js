// scatter.js

export function renderScatter(canvas, config) {

    const ctx = canvas.getContext('2d');

    if (!config?.points) {
        console.error("No data");
        return;
    }

    const points = config.points;

    // =========================================
    // COLOR SYSTEM (shared style)
    // =========================================

    function getColor(i, total) {

        if (total <= 1) {
            return "rgb(96,165,250)";
        }

        const ratio = i / (total - 1);

        const r = Math.round(103 + (129 - 103) * ratio);
        const g = Math.round(232 + (140 - 232) * ratio);
        const b = Math.round(250 + (248 - 250) * ratio);

        return `rgb(${r},${g},${b})`;
    }

    // =========================================
    // DATASETS
    // =========================================

    const datasets = points.map((p, i) => ({

        label: p.username || config.title,

        data: [{
            x: p.x ?? 0,
            y: p.y ?? 0
        }],

        pointRadius: p.point_size ?? 6,

        backgroundColor: getColor(i, points.length),

        borderColor: getColor(i, points.length),

        borderWidth: 2
    }));

    const xMax = config.scaleRanges?.x || 100;
    const yMax = config.scaleRanges?.y || 100;

    new Chart(ctx, {

        type: 'scatter',

        data: {
            datasets
        },

        options: {
            responsive: true,

            plugins: {
                legend: {
                    position: 'bottom'
                }
            },

            scales: {

                x: {
                    type: 'linear',
                    min: 0,
                    max: xMax,

                    title: {
                        display: true,
                        text: config.settings?.xAxisLabel || "X"
                    }
                },

                y: {
                    min: 0,
                    max: yMax,

                    title: {
                        display: true,
                        text: config.settings?.yAxisLabel || "Y"
                    }
                }
            }
        }
    });
}