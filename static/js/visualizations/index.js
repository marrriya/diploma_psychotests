import { renderBar } from './charts/bar.js';
import { renderRadar } from './charts/radar.js';
import { renderLine } from './charts/line.js';
import { renderScatter } from './charts/scatter.js';

const registry = {
    bar: renderBar,
    radar: renderRadar,
    line: renderLine,
    scatter: renderScatter
};


if (!chartConfig || !chartConfig.type) {
    console.error("chartConfig пустой");
} else {

    const renderer = registry[chartConfig.type];

    if (!renderer) {
        console.error("Не найден renderer:", chartConfig.type);
    } else {

        // renderer(
        //     document.getElementById('chart'),
        //     chartConfig
        // );
        renderer(
            document.getElementById('chart'),
            chartConfig
        );
    }
}


