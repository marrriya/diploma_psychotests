const chartDataElement = document.getElementById('chart-data')

if (!chartDataElement) {
    console.error("Нет chart-data")
} else {

    const parsed = JSON.parse(chartDataElement.textContent)

    const labels = parsed.labels || []
    const data = parsed.values || []
    const type = parsed.type || 'bar'

    console.log(parsed) // 🔥 для проверки

    let chartConfig = {
        type: type,
        data: {
            labels: labels,
            datasets: [{
                label: 'Результаты',
                data: data,
            }]
        }
    }

    if (type === 'horizontal_bar') {
        chartConfig.type = 'bar'
        chartConfig.options = { indexAxis: 'y' }
    }

    if (type === 'radar') {
        chartConfig.type = 'radar'
    }

    if (type === 'line') {
        chartConfig.type = 'line'
    }

    new Chart(document.getElementById('chart'), chartConfig)
}