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
    // =========================

    const labels = [];

    scales.forEach(scale => {

        students.forEach(student => {

            labels.push(`${scale} · ${student}`);

        });

    });

    // =========================
    // MODERN SOFT COLORS
    // =========================

    const palette = [
        {
            border: '#60a5fa',
            background: 'rgba(96,165,250,0.16)'
        },
        {
            border: '#38bdf8',
            background: 'rgba(56,189,248,0.16)'
        },
        {
            border: '#818cf8',
            background: 'rgba(129,140,248,0.16)'
        },
        {
            border: '#34d399',
            background: 'rgba(52,211,153,0.16)'
        },
        {
            border: '#f9a8d4',
            background: 'rgba(249,168,212,0.16)'
        },
        {
            border: '#fca5a5',
            background: 'rgba(252,165,165,0.16)'
        }
    ];

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

                if (currentScale === scale) {

                    data.push(
                        row?.values?.[scale] ?? 0
                    );

                } else {

                    data.push(null);

                }

            });

        });

        const color =
            palette[scaleIndex % palette.length];

        return {

            label: scale,

            data,

            borderColor: color.border,

            backgroundColor: color.background,

            pointBackgroundColor: color.border,

            pointBorderColor: '#ffffff',

            pointHoverBackgroundColor: '#ffffff',

            pointHoverBorderColor: color.border,

            pointRadius: 5,

            pointHoverRadius: 7,

            borderWidth: 3,

            spanGaps: false,

            tension: 0.35
        };
    });

    // =========================
    // MAX VALUE
    // =========================

    const allValues = [];

    points.forEach(p => {

        Object.entries(p.values || {}).forEach(([_, value]) => {

            allValues.push(value);

        });

    });

    const maxValue = Math.max(...allValues, 10);

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

            maintainAspectRatio: true,

            plugins: {

                legend: {

                    position: 'bottom',

                    labels: {

                        usePointStyle: true,

                        pointStyle: 'circle',

                        padding: 20,

                        font: {
                            size: 13
                        },

                        color: '#334155'
                    }
                }
            },

            scales: {

                r: {

                    beginAtZero: true,

                    min: 0,

                    max: chartMax,

                    ticks: {

                        stepSize: Math.ceil(chartMax / 5),

                        backdropColor: 'transparent',

                        color: '#64748b'
                    },

                    grid: {
                        color: 'rgba(148,163,184,0.15)'
                    },

                    angleLines: {
                        color: 'rgba(148,163,184,0.12)'
                    },

                    pointLabels: {

                        color: '#475569',

                        font: {
                            size: 11
                        }
                    }
                }
            }
        }
    });
}