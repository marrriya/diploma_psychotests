let currentStep = 1;

/* ===== HELPERS ===== */
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => Array.from(el.querySelectorAll(s));

/* ===== STEPS ===== */
function showStep(n) {
    const next = document.getElementById("step" + n);
    if (!next) return;

    $$(".step-block").forEach(b => b.classList.remove("active"));
    next.classList.add("active");

    $$(".step").forEach((s, i) => {
        s.classList.toggle("active", i < n);
    });

    currentStep = n;
}

/* ===== SAFE REMOVE ===== */
// function removeItem(btn) {
//     const el = btn?.closest(".scale-item, .question-item");
//     if (el) el.remove();

//     updateScaleSelects();
// }
function removeItem(btn) {
    const el = btn?.closest(".scale-item, .question-item");
    if (el) el.remove();

    updateScaleSelects();

    // 🔥 ДОБАВЬ ЭТО
    rebuildInterpretationsSafe();
}
function rebuildInterpretationsSafe() {
    const scales = getScalesFromDOM();
    buildInterpretations(scales);
}

function removeAnswer(btn) {
    btn?.closest(".answer-item")?.remove();
}

/* ===== STEP 1 ===== */
function next1() {
    let ok = true;

    const title = $("#title")?.value?.trim() || "";
    const topic = $("#topic")?.value?.trim() || "";
    const desc = $("#description")?.value?.trim() || "";

    setError("error_title", "");
    setError("error_topic", "");
    setError("error_description", "");

    if (!title) { setError("error_title"); ok = false; }
    if (!topic) { setError("error_topic"); ok = false; }
    if (!desc) { setError("error_description"); ok = false; }

    if (!ok) return;

    showStep(2);
}

/* ===== SCALES ===== */
function addScale() {
    const div = document.createElement("div");
    div.className = "scale-item";

    div.innerHTML = `
        <button type="button" class="remove-btn">−</button>
        <div class="scale-fields">
            <input class="scale-name" placeholder="Название шкалы *">
            <input class="scale-max" type="number" placeholder="Макс. балл *">
            <div class="error"></div>
        </div>
    `;

    div.querySelector(".remove-btn").onclick = () => removeItem(div.querySelector("button"));

    $("#scales").appendChild(div);
}
function next2() {

    let ok = true;

    $$(".scale-item").forEach(s => {

        const name = $(".scale-name", s)?.value?.trim();
        const max = $(".scale-max", s)?.value?.trim();
        const err = $(".error", s);

        if (err) err.innerText = "";

        if (!name || !max) {
            if (err) err.innerText = "Заполните поля";
            ok = false;
        }
    });

    if (!ok) return;

    updateScaleSelects();
    showStep(3);
}

/* ===== QUESTIONS ===== */
function addQuestion() {

    const div = document.createElement("div");
    div.className = "question-item";

    div.innerHTML = `
        <button type="button" class="remove-btn">−</button>
        <div class="question-fields">
            <input class="question-text" placeholder="Вопрос *">
            <select class="question-scale"></select>
            <div class="answers"></div>
            <button type="button" class="add-answer-btn">+ ответ</button>
            <div class="error"></div>
        </div>
    `;

    div.querySelector(".remove-btn").onclick = () => removeItem(div.querySelector("button"));
    div.querySelector(".add-answer-btn").onclick = () => addAnswer(div);

    $("#questions").appendChild(div);

    updateScaleSelects();
    // addAnswer(div);
    // addAnswer(div);
}

function addAnswer(block) {
    const container = $(".answers", block);
    if (!container) return;

    const div = document.createElement("div");
    div.className = "answer-item";

    div.innerHTML = `
        <input class="answer-text" placeholder="Ответ *">
        <input type="number" class="answer-score" placeholder="Баллы *">
        <button type="button">×</button>
    `;

    div.querySelector("button").onclick = () => removeAnswer(div.querySelector("button"));

    container.appendChild(div);
}

/* ===== SCALE UPDATE (FIX SAFE) ===== */
function updateScaleSelects() {

    const scales = $$(".scale-item")
        .map(s => $(".scale-name", s)?.value?.trim())
        .filter(Boolean);

    $$(".question-scale").forEach(select => {

        const current = select.value;
        select.innerHTML = "";

        if (!scales.length) {
            const opt = document.createElement("option");
            opt.textContent = "Нет шкал";
            opt.disabled = true;
            select.appendChild(opt);
            return;
        }

        scales.forEach((name, i) => {
            const opt = document.createElement("option");
            opt.value = i;
            opt.textContent = name;
            select.appendChild(opt);
        });

        select.value = current || "0";
    });
}

/* ===== STEP 3 ===== */
// function next3() {

//     let ok = true;

//     $$(".question-item").forEach(q => {

//         const text = $(".question-text", q)?.value?.trim();
//         const answers = $$(".answer-item", q);

//         if (!text || answers.length < 1) ok = false;

//         answers.forEach(a => {
//             const t = $(".answer-text", a)?.value?.trim();
//             const s = $(".answer-score", a)?.value;

//             if (!t || s === "") ok = false;
//         });
//     });

//     if (!ok) {
//         alert("Заполните вопросы, ответы и баллы");
//         return;
//     }

//     buildInterpretations();
//     showStep(4);
// }
function next3() {

    let ok = true;

    $$(".question-item").forEach(q => {

        const text = $(".question-text", q)?.value?.trim();
        const answers = $$(".answer-item", q);

        if (!text || answers.length < 1) ok = false;

        answers.forEach(a => {
            const t = $(".answer-text", a)?.value?.trim();
            const s = $(".answer-score", a)?.value;

            if (!t || s === "") ok = false;
        });
    });

    if (!ok) {
        alert("Заполните вопросы, ответы и баллы");
        return;
    }

    // 🔥 ВАЖНО
    buildInterpretations(getScalesFromDOM());

    showStep(4);
}
function getScalesFromDOM() {
    return $$(".scale-item").map((s, i) => ({
        id: i, // временный id для create
        name: $(".scale-name", s)?.value || "",
        max_score: Number($(".scale-max", s)?.value || 0)
    }));
}

/* ===== INTERPRETATIONS ===== */
// function buildInterpretations() {

//     const container = $("#interpretations");
//     if (!container) return;

//     container.innerHTML = "";

//     $$(".scale-item").forEach((s, i) => {

//         const name = $(".scale-name", s)?.value || "";
//         const max = Number($(".scale-max", s)?.value || 0);

//         const block = document.createElement("div");
//         block.className = "interp-block";

//         block.innerHTML = `
//             <h3>${name}</h3>
//             <div class="ranges" data-scale="${window.SCALES?.[i]?.id ?? i}" data-max="${max}"></div>
//             <button type="button">+ добавить</button>
//         `;

//         const btn = block.querySelector("button");
//         const ranges = $(".ranges", block);

//         btn.onclick = () => addRange(ranges);

//         container.appendChild(block);

//         addRangeRow(ranges, 0, "", true, false);
//         addRangeRow(ranges, "", max, false, true, true);
//     });
// }
// function buildInterpretations() {

//     const container = $("#interpretations");
//     if (!container) return;

//     container.innerHTML = "";

//     SCALES.forEach(scale => {

//         const block = document.createElement("div");
//         block.className = "interp-block";

//         block.innerHTML = `
//             <h3>${scale.name}</h3>
//             <div class="ranges" data-scale-id="${scale.id}" data-max="${scale.max_score}"></div>
//             <button type="button">+ добавить</button>
//         `;

//         const ranges = block.querySelector(".ranges");

//         block.querySelector("button").onclick = () => addRange(ranges);

//         container.appendChild(block);

//         // минимально 1 строка
//         addRangeRow(ranges, 0, "", true, false);
//         addRangeRow(ranges, "", scale.max_score, false, true, true);
//     });
// }
// function buildInterpretationsFromData(scales, interpretations) {

//     const container = $("#interpretations");
//     container.innerHTML = "";

//     const grouped = {};

//     interpretations.forEach(i => {
//         const key = String(i.scale_id);
//         if (!grouped[key]) grouped[key] = [];
//         grouped[key].push(i);
//     });

//     scales.forEach(scale => {

//         const block = document.createElement("div");
//         block.className = "interp-block";

//         block.innerHTML = `
//             <h3>${scale.name}</h3>
//             <div class="ranges" data-scale-id="${scale.id}"></div>
//             <button type="button">+ добавить</button>
//         `;

//         const ranges = block.querySelector(".ranges");

//         block.querySelector("button").onclick = () => addRange(ranges);

//         container.appendChild(block);

//         const items = grouped[String(scale.id)] || [];

//         if (!items.length) {
//             addRangeRow(ranges, 0, "", true, false);
//             addRangeRow(ranges, "", scale.max_score, false, true, true);
//             return;
//         }

//         items.forEach(it => {
//             addRangeRow(
//                 ranges,
//                 it.min_score,
//                 it.max_score,
//                 false,
//                 false
//             );

//             const row = ranges.lastElementChild;

//             $(".title", row).value = it.title || "";
//             $(".desc", row).value = it.description || "";
//         });
//     });
// }

function buildInterpretations(scales, interpretations = null) {

    const container = $("#interpretations");
    container.innerHTML = "";

    const grouped = {};

    if (interpretations) {
        interpretations.forEach(i => {
            const key = String(i.scale_id);
            if (!grouped[key]) grouped[key] = [];
            grouped[key].push(i);
        });
    }

    scales.forEach(scale => {

        const block = document.createElement("div");
        block.className = "interp-block";

        block.innerHTML = `
            <h3>${scale.name}</h3>
            <div class="ranges" data-scale-id="${scale.id}"></div>
            <button type="button">+ добавить</button>
        `;

        const ranges = block.querySelector(".ranges");

        block.querySelector("button").onclick = () => addRange(ranges);

        container.appendChild(block);

        const items = grouped[String(scale.id)] || [];

        if (!items.length) {
            addRangeRow(ranges, 0, "", true, false);
            addRangeRow(ranges, "", scale.max_score, false, true, true);
            return;
        }

        items.forEach(it => {

            addRangeRow(ranges, it.min_score, it.max_score);

            const row = ranges.lastElementChild;

            $(".title", row).value = it.title || "";
            $(".desc", row).value = it.description || "";
        });
    });
}
function addRange(container) {
    addRangeRow(container, "", "", false, false);
}

function addRangeRow(container, min, max, lockMin, lockMax, isLast = false) {

    const row = document.createElement("div");
    row.className = "interp-row";

    row.innerHTML = `
        <input type="number" class="min" value="${min}" ${lockMin ? "disabled" : ""}>
        <input type="number" class="max" value="${max}" ${lockMax ? "disabled" : ""}>
        <input class="title" placeholder="Название">
        <input class="desc" placeholder="Описание">
    `;

    if (isLast) container.appendChild(row);
    else container.insertBefore(row, container.lastElementChild);
}

/* ===== VALIDATION ===== */
function validateRanges() {

    for (const r of $$(".ranges")) {

        const rows = $$(".interp-row", r);

        for (let i = 0; i < rows.length - 1; i++) {

            const max = Number($(".max", rows[i])?.value);
            const next = Number($(".min", rows[i + 1])?.value);

            if (max >= next) {
                alert("Ошибка диапазонов");
                return false;
            }
        }
    }

    return true;
}

/* ===== STEP 4 ===== */
function next4() {
    if (!validateRanges()) return;
    showStep(5);
}

/* ===== STEP 5 ===== */
function next5() {
    renderPreview();
    showStep(6);
}

/* ===== PREVIEW (FIXED + SCORES) ===== */
// function renderPreview() {

//     const preview = $("#preview");
//     if (!preview) return;

//     const title = $("#title")?.value || "";
//     const desc = $("#description")?.value || "";
//     const instruction = $("#instruction")?.value || "";

//     let html = `
//         <h2>${title}</h2>
//         <p>${desc}</p>
//         <p>${instruction}</p>

//         <h3>Вопросы</h3>
//     `;

//     $$(".question-item").forEach((q, i) => {

//         html += `<div><h4>${i + 1}. ${$(".question-text", q)?.value || ""}</h4>`;

//         $$(".answer-item", q).forEach(a => {
//             html += `
//                 <div>
//                     ${$(".answer-text", a)?.value || ""}
//                     — <b>${$(".answer-score", a)?.value || 0}</b>
//                 </div>
//             `;
//         });

//         html += `</div>`;
//     });

//     preview.innerHTML = html;
// }
function renderPreview() {

    const preview = $("#preview");
    if (!preview) return;

    const title = $("#title")?.value || "";
    const topic = $("#topic")?.value || "";
    const desc = $("#description")?.value || "";
    const instruction = $("#instruction")?.value || "";

    /* ===== SCALES ===== */
    let scalesHTML = "";

    $$(".scale-item").forEach((s, i) => {
        const name = $(".scale-name", s)?.value || "";
        const max = $(".scale-max", s)?.value || "";

        scalesHTML += `
            <div>
                <b>${name}</b> — max: ${max}
            </div>
        `;
    });

    /* ===== QUESTIONS ===== */
    let questionsHTML = "";

    $$(".question-item").forEach((q, i) => {

        const text = $(".question-text", q)?.value || "";

        const scaleSelect = $(".question-scale", q);
        const scaleName = scaleSelect?.options?.[scaleSelect.selectedIndex]?.text || "—";

        let answersHTML = "";

        $$(".answer-item", q).forEach(a => {
            const at = $(".answer-text", a)?.value || "";
            const sc = $(".answer-score", a)?.value || 0;

            answersHTML += `
                <li>${at} — <b>${sc}</b> баллов</li>
            `;
        });

        questionsHTML += `
            <div class="preview-question">
                <h4>${i + 1}. ${text}</h4>
                <div><b>Шкала:</b> ${scaleName}</div>
                <ul>${answersHTML}</ul>
            </div>
        `;
    });

    /* ===== INTERPRETATIONS ===== */
    let interpHTML = "";

    // $$(".ranges").forEach(r => {

        // const scaleIndex = r.dataset.scale;
    $$(".ranges").forEach((r, i) => {

        const scaleName = $$(".scale-item")[i]
        ?.querySelector(".scale-name")?.value || "";


        // const scaleId = r.getAttribute("data-scale-id");
        // const scale = SCALES.find(s => String(s.id) === String(scaleId));
        // const scaleName = scale?.name || "";


        // const scaleName = $$(".scale-item")[scaleIndex]
        //     ?.querySelector(".scale-name")?.value || "";

        let rowsHTML = "";

        $$(".interp-row", r).forEach(row => {

            const min = $(".min", row)?.value || "";
            const max = $(".max", row)?.value || "";
            const title = $(".title", row)?.value || "";
            const desc = $(".desc", row)?.value || "";

            rowsHTML += `
                <div>
                    <b>${min} - ${max}</b> — ${title}
                    <div style="opacity:0.7">${desc}</div>
                </div>
            `;
        });

        interpHTML += `
            <div class="preview-question">
                <h4>${scaleName}</h4>
                ${rowsHTML}
            </div>
        `;
    });

    /* ===== FINAL ===== */
    preview.innerHTML = `
        <h2>${title}</h2>
        <p><b>Тема:</b> ${topic}</p>
        <p>${desc}</p>
        <p>${instruction}</p>

        <h3>Шкалы</h3>
        ${scalesHTML}

        <h3>Вопросы</h3>
        ${questionsHTML}

        <h3>Интерпретации</h3>
        ${interpHTML}
    `;
}

/* ===== SUBMIT (SAFE) ===== */
async function submitTest() {

    try {

        const payload = {
            title: $("#title")?.value || "",
            topic: $("#topic")?.value || "",
            description: $("#description")?.value || "",
            instruction: $("#instruction")?.value || "",

            scales: $$(".scale-item").map(s => ({
                name: $(".scale-name", s)?.value || "",
                max: Number($(".scale-max", s)?.value || 0)
            })),

            questions: $$(".question-item").map(q => ({
                text: $(".question-text", q)?.value || "",
                scale: Number($(".question-scale", q)?.value || 0),

                answers: $$(".answer-item", q).map(a => ({
                    text: $(".answer-text", a)?.value || "",
                    score: Number($(".answer-score", a)?.value || 0)
                }))
            })),

            // interpretations: $$(".ranges").map(r => ({
            //     // scale_index: Number(r.dataset.scale),
            //     scale_id: Number(r.dataset.scaleId) || null,
            interpretations: $$(".ranges").map((r, i) => ({
                scale_index: i,
                ranges: $$(".interp-row", r).map(row => ({
                    min: Number($(".min", row)?.value),
                    max: Number($(".max", row)?.value),
                    title: $(".title", row)?.value || "",
                    desc: $(".desc", row)?.value || ""
                }))
            }))
        };
        const url = window.MODE === "edit"
            ? `/teacher/update_test/${window.TEST_ID}`
            : "/teacher/create_test_full";

        const res = await fetch(url, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(payload)
        });

        // const res = await fetch("/teacher/create_test_full", {
        //     method: "POST",
        //     headers: {"Content-Type": "application/json"},
        //     body: JSON.stringify(payload)
        // });

        const data = await res.json();
        console.log(data);

        if (data.success) {
            alert("Тест создан!");

            // ВАЖНО — возврат на старт
            window.location.href = "/teacher/teach";
        } else {
            alert("Ошибка создания: " + (data.error || "unknown"));
        }

    } catch (e) {
        console.error(e);
        alert("Ошибка запроса");
    }
}

/* ===== ERRORS ===== */
function setError(id, text = "Обязательное поле") {
    const el = document.getElementById(id);
    if (el) el.innerText = text;
}
function initEdit(data) {

    const { test, scales, questions, answers, interpretations } = data;

    /* ===== STEP 1 ===== */
    $("#title").value = test.title || "";
    $("#description").value = test.description || "";
    $("#instruction").value = test.instruction || "";
    $("#topic").value = test.topic || "";

    /* ===== STEP 2 ===== */
    $("#scales").innerHTML = "";

    scales.forEach(s => {
        addScale();

        const last = $$(".scale-item").slice(-1)[0];

        $(".scale-name", last).value = s.name || "";
        $(".scale-max", last).value = s.max_score || "";
    });

    updateScaleSelects();

    /* ===== STEP 3 ===== */
    $("#questions").innerHTML = "";

    questions.forEach(q => {

        addQuestion();
        const lastQ = $$(".question-item").slice(-1)[0];

        $(".question-text", lastQ).value = q.question;

        const scaleIndex = scales.findIndex(s => s.id == q.scale_id);
        $(".question-scale", lastQ).value = scaleIndex;

        answers
            .filter(a => a.question_id == q.id)
            .forEach(a => {

                addAnswer(lastQ);

                const lastA = $$(".answer-item", lastQ).slice(-1)[0];

                $(".answer-text", lastA).value = a.answer_text;
                $(".answer-score", lastA).value = a.score;
            });
    });

    /* ===== STEP 4 ===== */
    // buildInterpretationsFromData(scales, interpretations);
    const normalizedScales = scales.map((s, i) => ({
        ...s,
        id: i
    }));

    buildInterpretations(normalizedScales, interpretations);
    // buildInterpretations(scales, interpretations);
}
window.onload = function () {

    if (window.MODE !== "edit") return;

    const dataEl = document.getElementById("data");
    if (!dataEl) return;

    const data = JSON.parse(dataEl.textContent);

    initEdit(data);
};