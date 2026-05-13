const container = d3.select("#flowersContainer");
const flowers = window.FLOWERS || [];

// =====================================================
// PETAL SHAPES
// =====================================================

const PETAL_SHAPES = [
    "M27.3586 35.3483C20.9413 40.9133 18.4456 48.1015 18 51C17.5543 48.1015 15.0587 40.9133 8.64139 35.3483C0.619713 28.392 -0.0487633 13.6098 1.95666 5.7839C3.96208 -2.04196 11.3153 2.09001 18 2.09001C24.6847 2.09001 32.0379 -2.04196 34.0433 5.7839C36.0488 13.6098 35.3803 28.392 27.3586 35.3483Z",

    "M31.7483 2.60029C23.3636 -4.43533 18.2396 13.6899 17.7737 19.0199C17.3079 13.6899 12.69 -4.43533 4.30531 2.60029C-7.2488 12.2954 14.9788 51 17.7737 51C20.5686 51 43.3024 12.2954 31.7483 2.60029Z",

    "M20.0212 1C48.0786 24.6 30.3757 44.1667 18.0171 51C5.6585 44.1667 -12.0964 24.6 15.961 1L17.5267 7.09165C17.6558 7.59395 18.3699 7.59177 18.4959 7.08869L20.0212 1Z"
];

// =====================================================
// FUNCTIONS
// =====================================================

function chooseShape(score = 0) {
    if (score < 8) return PETAL_SHAPES[0];
    if (score < 16) return PETAL_SHAPES[1];
    return PETAL_SHAPES[2];
}

function chooseColor(score = 0) {
    if (score < 8) return "#7B68EE";
    if (score < 16) return "#FFA500";
    return "#DC143C";
}

function petalCount(score = 0) {
    return Math.max(4, Math.min(12, Math.round(score / 2)));
}

function flowerScale(score = 0) {
    return 0.7 + (score / 24);
}

// =====================================================
// RENDER ALL FLOWERS
// =====================================================

flowers.forEach((flower) => {

    const svg = container.append("svg")
        .attr("width", 220)
        .attr("height", 260);

    const g = svg.append("g")
        .attr("transform", "translate(110,120)");

    const shape = chooseShape(flower.petal_shape_score);
    const color = chooseColor(flower.petal_color_score);
    const petals = petalCount(flower.petal_count_score);
    const scale = flowerScale(flower.flower_size_score);

    // scale применяется к группе
    g.attr("transform", `translate(110,120) scale(${scale})`);

    const angleStep = 360 / petals;

    // petals
    for (let i = 0; i < petals; i++) {
        g.append("path")
            .attr("d", shape)
            .attr("fill", color)
            .attr("fill-opacity", 0.75)
            .attr("stroke", "#333")
            .attr("stroke-width", 1)
            .attr("transform", `
                rotate(${i * angleStep})
                translate(0,-60)
                scale(2)
            `);
    }

    // center
    g.append("circle")
        .attr("r", 16)
        .attr("fill", "#FFD54F")
        .attr("stroke", "#333");

    // stem
    g.append("line")
        .attr("x1", 0)
        .attr("y1", 20)
        .attr("x2", 0)
        .attr("y2", 140)
        .attr("stroke", "#2E8B57")
        .attr("stroke-width", 6);

    // label
    svg.append("text")
        .attr("x", 110)
        .attr("y", 245)
        .attr("text-anchor", "middle")
        .style("font-size", "12px")
        .text(flower.name || "no name");
});