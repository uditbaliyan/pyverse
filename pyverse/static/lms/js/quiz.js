// static/lms/js/quiz.js
(function () {
  const STORAGE_KEY = "pyverse_quiz_results";

  function loadResults() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {};
    } catch {
      return {};
    }
  }

  function saveResult(slug, result) {
    const all = loadResults();
    all[slug] = result;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(all));
  }

  function grade(quiz, responses) {
    let earned = 0;
    let possible = 0;
    const perQuestion = [];

    for (const q of quiz.questions) {
      possible += q.points;
      let correct = false;

      if (q.type === "true_false") {
        correct = responses[q.id] === q.correct_bool;
      } else {
        const selected = new Set(responses[q.id] || []);
        const correctIds = new Set(q.choices.filter((c) => c.is_correct).map((c) => c.id));
        correct =
          selected.size === correctIds.size && [...selected].every((id) => correctIds.has(id));
      }

      if (correct) earned += q.points;
      perQuestion.push({ id: q.id, correct, explanation: q.explanation });
    }

    const score = possible ? Math.round((earned / possible) * 100) : 0;
    return { score, passed: score >= quiz.pass_percentage, perQuestion };
  }

  function renderQuiz(container) {
    const quiz = JSON.parse(container.dataset.quiz);

    const form = document.createElement("form");
    form.className = "quiz-form";

    quiz.questions.forEach((q) => {
      const fieldset = document.createElement("fieldset");
      fieldset.dataset.qid = q.id;
      const legend = document.createElement("legend");
      legend.textContent = q.text;
      fieldset.appendChild(legend);

      if (q.code_snippet) {
        const pre = document.createElement("pre");
        pre.textContent = q.code_snippet;
        fieldset.appendChild(pre);
      }

      if (q.type === "true_false") {
        ["True", "False"].forEach((label) => {
          const val = label === "True";
          fieldset.insertAdjacentHTML(
            "beforeend",
            `<label><input type="radio" name="q_${q.id}" value="${val}"> ${label}</label>`,
          );
        });
      } else {
        q.choices.forEach((c) => {
          fieldset.insertAdjacentHTML(
            "beforeend",
            `<label><input type="checkbox" name="q_${q.id}" value="${c.id}"> ${c.text}</label>`,
          );
        });
      }

      form.appendChild(fieldset);
    });

    const submitBtn = document.createElement("button");
    submitBtn.type = "submit";
    submitBtn.textContent = "Submit Quiz";
    form.appendChild(submitBtn);

    const resultBox = document.createElement("div");
    resultBox.className = "quiz-result";
    resultBox.hidden = true;

    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const responses = {};

      quiz.questions.forEach((q) => {
        const inputs = form.querySelectorAll(`[name="q_${q.id}"]`);
        if (q.type === "true_false") {
          const checked = [...inputs].find((i) => i.checked);
          responses[q.id] = checked ? checked.value === "true" : null;
        } else {
          responses[q.id] = [...inputs].filter((i) => i.checked).map((i) => parseInt(i.value, 10));
        }
      });

      const result = grade(quiz, responses);
      saveResult(quiz.slug, { ...result, completedAt: Date.now() });

      resultBox.hidden = false;
      resultBox.innerHTML = `
        <p><strong>${result.score}%</strong> — ${result.passed ? "Passed ✅" : "Not yet — try again"}</p>
      `;
    });

    container.appendChild(form);
    container.appendChild(resultBox);
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-quiz]").forEach(renderQuiz);
  });
})();
