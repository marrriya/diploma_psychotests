const flowers = window.FLOWERS || [];

const container = d3.select("#flowersContainer");

// =====================================================
// PETAL SHAPES
// =====================================================

const PETAL_SHAPES = [

"M27.3586 35.3483C20.9413 40.9133 18.4456 48.1015 18 51C17.5543 48.1015 15.0587 40.9133 8.64139 35.3483C0.619713 28.392 -0.0487633 13.6098 1.95666 5.7839C3.96208 -2.04196 11.3153 2.09001 18 2.09001C24.6847 2.09001 32.0379 -2.04196 34.0433 5.7839C36.0488 13.6098 35.3803 28.392 27.3586 35.3483Z",

"M31.7483 2.60029C23.3636 -4.43533 18.2396 13.6899 17.7737 19.0199C17.3079 13.6899 12.69 -4.43533 4.30531 2.60029C-7.2488 12.2954 14.9788 51 17.7737 51C20.5686 51 43.3024 12.2954 31.7483 2.60029Z",

"M20.0212 1C48.0786 24.6 30.3757 44.1667 18.0171 51C5.6585 44.1667 -12.0964 24.6 15.961 1L17.5267 7.09165C17.6558 7.59395 18.3699 7.59177 18.4959 7.08869L20.0212 1Z"
];

// =====================================================
// LOGIC
// =====================================================

// function sincerityColor(score) {

//     if (score <= 3) return "#F2C66D";

//     if (score <= 6) return "#E8A96B";

//     return "#D98973";
// }

// function neuroticismPetals(score) {

//     if (score <= 2) return 6;

//     if (score <= 10) return 10;

//     return 14;
// }

// function extraversionScale(score) {

//     if (score <= 6) return 0.8;

//     if (score <= 14) return 1.0;

//     return 1.2;
// }

// function chooseShape(score) {

//     if (score <= 2) return PETAL_SHAPES[0];

//     if (score <= 10) return PETAL_SHAPES[1];

//     return PETAL_SHAPES[2];
// }


// =====================================================
// LOGIC
// =====================================================

// ИСКРЕННОСТЬ → ЦВЕТ

function sincerityColor(score) {

    // Откровенный
    if (score <= 3) {
        return "#F2C66D";
    }

    // Ситуативный
    if (score <= 6) {
        return "#E8A96B";
    }

    // Лживый
    return "#D98973";
}


// НЕВРОТИЗМ → КОЛИЧЕСТВО ЛЕПЕСТКОВ

function neuroticismPetals(score) {

    // Сверхконкордант
    if (score <= 2) return 5;

    // Конкордант
    if (score <= 6) return 7;

    // Потенциальный конкордант
    if (score <= 10) return 9;

    // Нормостеник
    if (score <= 14) return 11;

    // Потенциальный дискордант
    if (score <= 18) return 13;

    // Дискордант
    if (score <= 22) return 15;

    // Сверхдискордант
    return 17;
}


// ЭКСТРАВЕРТИРОВАННОСТЬ → РАЗМЕР

function extraversionScale(score) {

    // Сверхинтроверт
    if (score <= 2) return 0.7;

    // Интроверт
    if (score <= 6) return 0.85;

    // Потенциальный интроверт
    if (score <= 10) return 1.0;

    // Амбиверт
    if (score <= 14) return 1.12;

    // Потенциальный экстраверт
    if (score <= 18) return 1.22;

    // Экстраверт
    if (score <= 22) return 1.32;

    // Сверхэкстраверт
    return 1.45;
}
// =====================================================
// RENDER
// =====================================================

flowers.forEach((flower) => {

    const item = container
        .append("div")
        .attr("class", "flower-item");

    // TOOLTIP

    item.append("div")
        .attr("class", "tooltip")
        .html(`
            <div class="tooltip-title">${flower.name}</div>

            <div class="tooltip-row">
                Искренность: ${flower.sincerity}
            </div>

            <div class="tooltip-row">
                Невротизм: ${flower.neuroticism}
            </div>

            <div class="tooltip-row">
                Экстравертированность: ${flower.extraversion}
            </div>
        `);

    // CIRCLE

    const circle = item
        .append("div")
        .attr("class", "flower-circle");

    const svg = circle
        .append("svg")
        .attr("width", 220)
        .attr("height", 220)
        .attr("viewBox", "0 0 260 260");

    const g = svg.append("g")
        .attr("transform", "translate(130,120)");

    const color = sincerityColor(flower.sincerity);

    const petals = neuroticismPetals(flower.neuroticism);

    const scale = extraversionScale(flower.extraversion);

    // const shape = chooseShape(flower.neuroticism);
    const shape = PETAL_SHAPES[1];

    g.attr(
        "transform",
        `translate(130,120) scale(${scale})`
    );

    const angleStep = 360 / petals;

    // petals

    for (let i = 0; i < petals; i++) {

        g.append("path")
            .attr("d", shape)
            .attr("fill", color)
            .attr("fill-opacity", 0.82)
            .attr("stroke", "#C07D63")
            .attr("stroke-width", 1)
            .attr(
                "transform",
                `
                rotate(${i * angleStep})
                translate(0,-50)
                scale(1.7)
                `
            );
    }

    // center

    g.append("circle")
        .attr("r", 16)
        .attr("fill", "#F4D58D")
        .attr("stroke", "#D4B06A")
        .attr("stroke-width", 2);

    // stem

    g.append("line")
        .attr("x1", 0)
        .attr("y1", 18)
        .attr("x2", 0)
        .attr("y2", 90)
        .attr("stroke", "#7FA37A")
        .attr("stroke-width", 6)
        .attr("stroke-linecap", "round");

    // leaves

    g.append("ellipse")
        .attr("cx", -18)
        .attr("cy", 55)
        .attr("rx", 14)
        .attr("ry", 7)
        .attr("fill", "#98B692")
        .attr("transform", "rotate(-30)");

    g.append("ellipse")
        .attr("cx", 18)
        .attr("cy", 72)
        .attr("rx", 14)
        .attr("ry", 7)
        .attr("fill", "#98B692")
        .attr("transform", "rotate(30)");

    // NAME

    item.append("div")
        .attr("class", "student-name")
        .text(flower.name);
});