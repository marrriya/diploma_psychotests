// scatter.js

export function renderScatter(canvas, config) {

    const ctx = canvas.getContext('2d');

    if (!config?.points) {
        console.error("No data");
        return;
    }

    // =========================================
    // GROUP MODE
    // =========================================

    const datasets = config.points.map(p => ({

        label: p.username || config.title,

        data: [{
            x: p.x ?? 0,
            y: p.y ?? 0
        }],

        pointRadius: p.point_size ?? 5

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