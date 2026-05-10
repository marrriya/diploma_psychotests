window.onload = function () {
    if (window.MODE === "edit") {
        loadEditData();
    }
};

function loadEditData() {

    if (!window.TEST) return;

    /* ===== STEP 1 ===== */
    $("#title").value = TEST.title || "";
    $("#description").value = TEST.description || "";
    $("#instruction").value = TEST.instruction || "";
    $("#topic").value = TEST.topic || "";

    /* ===== STEP 2 (SCALES) ===== */
    $("#scales").innerHTML = "";

    SCALES.forEach(scale => {

        addScale();

        const last = $$(".scale-item").slice(-1)[0];

        $(".scale-name", last).value = scale.name || "";
        $(".scale-max", last).value = scale.max_score || "";
    });

    updateScaleSelects();

    /* ===== STEP 3 (QUESTIONS + ANSWERS) */
    $("#questions").innerHTML = "";

    QUESTIONS.forEach(q => {

        addQuestion();

        const lastQ = $$(".question-item").slice(-1)[0];

        $(".question-text", lastQ).value = q.question || "";

        const scaleIndex = SCALES.findIndex(s => s.id == q.scale_id);
        if (scaleIndex >= 0) {
            $(".question-scale", lastQ).value = scaleIndex;
        }

        ANSWERS
            .filter(a => a.question_id == q.id)
            .forEach(a => {

                addAnswer(lastQ);

                const lastA = $$(".answer-item", lastQ).slice(-1)[0];

                $(".answer-text", lastA).value = a.answer_text || "";
                $(".answer-score", lastA).value = a.score || 0;
            });
    });


    buildInterpretations(); // создаём структуру ОДИН РАЗ

    const grouped = {};

    INTERPRETATIONS.forEach(i => {
        const key = String(i.scale_id);
        if (!grouped[key]) grouped[key] = [];
        grouped[key].push(i);
    });

    const ranges = document.querySelectorAll(".ranges");

    ranges.forEach(r => {

        const scaleId = r.getAttribute("data-scale-id");
        const items = grouped[String(scaleId)] || [];

        console.log("fill:", scaleId, items);

        // ❗ ВСЕГДА чистим и пересоздаём (самый стабильный вариант)
        const btn = r.parentElement.querySelector("button");
        r.innerHTML = "";
        if (btn) r.appendChild(btn);

        if (items.length === 0) {
            addRangeRow(r, 0, "", true, false);
            addRangeRow(r, "", "", false, true, true);
            return;
        }

        items.forEach(it => {

            const row = document.createElement("div");
            row.className = "interp-row";

            row.innerHTML = `
                <input type="number" class="min" value="${it.min_score ?? ''}">
                <input type="number" class="max" value="${it.max_score ?? ''}">
                <input class="title" value="${it.title ?? ''}">
                <input class="desc" value="${it.description ?? ''}">
            `;

            r.appendChild(row);
        });
    });
    console.log("EDIT MODE FULLY LOADED");
}