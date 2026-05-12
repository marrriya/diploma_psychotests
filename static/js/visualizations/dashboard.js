import { renderBar } from './charts/bar.js';
import { renderRadar } from './charts/radar.js';
import { renderLine } from './charts/line.js';
import { renderScatter } from './charts/scatter.js';

// const registry = {
//     bar: renderBar,
//     radar: renderRadar,
//     line: renderLine,
//     scatter: renderScatter
// };
import { renderRadarMulti } from './charts/radar_multi.js';

const registry = {
    bar: renderBar,
    radar: renderRadar,
    radar_multi: renderRadarMulti,
    line: renderLine,
    scatter: renderScatter
};

const container = document.getElementById('chartsContainer');

if (!visualizations || !Array.isArray(visualizations)) {

    console.error("visualizations пустой");

} else {

    visualizations.forEach(chartConfig => {

        const renderer = registry[chartConfig.type];

        if (!renderer) {
            console.error("Не найден renderer:", chartConfig.type);
            return;
        }

        // CARD

        const card = document.createElement('div');
        card.className = 'card';

        // TITLE

        const title = document.createElement('h2');
        title.innerText = chartConfig.title;

        // CANVAS

        const canvas = document.createElement('canvas');

        // APPEND

        card.appendChild(title);
        card.appendChild(canvas);

        container.appendChild(card);

        // RENDER

        renderer(canvas, chartConfig);

    });

}