export function renderLine(canvas, config) {

    const ctx = canvas.getContext('2d');

    if (!config || !config.series) {
        console.error("Line chart: нет данных");
        return;
    }

    // превращаем series → labels + values
    const labels = config.series.map((item, i) =>
        item.label ?? `Point ${i + 1}`
    );

    const values = config.series.map(item =>
        item.value ?? 0
    );

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: config.title || 'Line chart',
                data: values,

                fill: false,
                tension: 0.3,
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,

            plugins: {
                legend: {
                    display: true
                }
            },

            scales: {
                x: {
                    display: true
                },
                y: {
                    display: true,
                    beginAtZero: true
                }
            }
        }
    });
}