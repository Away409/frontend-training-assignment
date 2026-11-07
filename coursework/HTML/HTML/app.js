const $ = (selector, scope = document) => scope.querySelector(selector);
const $$ = (selector, scope = document) => [...scope.querySelectorAll(selector)];

// Reading progress and active chapter
const progressBar = $("#reading-progress-bar");

function updateReadingProgress() {
  const scrollable = document.documentElement.scrollHeight - window.innerHeight;
  const percentage = scrollable > 0 ? (window.scrollY / scrollable) * 100 : 0;
  progressBar.style.width = `${Math.min(100, Math.max(0, percentage))}%`;
}

window.addEventListener("scroll", updateReadingProgress, { passive: true });
updateReadingProgress();

const railLinks = $$(".chapter-rail a");
const observedSections = railLinks
  .map((link) => $(link.getAttribute("href")))
  .filter(Boolean);

if ("IntersectionObserver" in window) {
  const sectionObserver = new IntersectionObserver(
    (entries) => {
      const current = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
      if (!current) return;

      railLinks.forEach((link) => {
        const active = link.getAttribute("href") === `#${current.target.id}`;
        link.classList.toggle("is-active", active);
        if (active) link.setAttribute("aria-current", "location");
        else link.removeAttribute("aria-current");
      });
    },
    { rootMargin: "-18% 0px -66%", threshold: [0, 0.15, 0.35] },
  );

  observedSections.forEach((section) => sectionObserver.observe(section));
}

// Mobile navigation
const menuButton = $("#menu-button");
const mobileNav = $("#mobile-nav");

menuButton.addEventListener("click", () => {
  const willOpen = menuButton.getAttribute("aria-expanded") !== "true";
  menuButton.setAttribute("aria-expanded", String(willOpen));
  mobileNav.hidden = !willOpen;
});

$$('a[href^="#"]', mobileNav).forEach((link) => {
  link.addEventListener("click", () => {
    menuButton.setAttribute("aria-expanded", "false");
    mobileNav.hidden = true;
  });
});

$$('[data-scroll-to]').forEach((button) => {
  button.addEventListener("click", () => {
    $(`#${button.dataset.scrollTo}`)?.scrollIntoView({ behavior: "smooth" });
  });
});

// Hero editor and preview tabs
const heroCode = $("#hero-code");
const heroPreview = $("#hero-preview");
const heroTabs = $$(".lab-tabs [role='tab']");

// Use a Blob URL for editable previews. Chrome can reject scripts injected into
// sandboxed srcdoc/about:blank documents (for example Live Server's reload
// helper), while a Blob URL renders the same HTML consistently across browsers.
const previewUrls = new WeakMap();
function renderPreview(frame, markup) {
  const previousUrl = previewUrls.get(frame);
  if (previousUrl) URL.revokeObjectURL(previousUrl);
  // Blob documents otherwise resolve relative assets against the blob: URL.
  // Keep the editor's normal page-relative behavior (e.g. lab-diagram.svg).
  let previewMarkup = markup;
  if (!/<base\b/i.test(previewMarkup)) {
    const baseHref = document.baseURI.replace(/&/g, "&amp;").replace(/"/g, "&quot;");
    const baseTag = `<base href="${baseHref}">`;
    previewMarkup = /<head\b[^>]*>/i.test(previewMarkup)
      ? previewMarkup.replace(/(<head\b[^>]*>)/i, `$1${baseTag}`)
      : `${baseTag}${previewMarkup}`;
  }
  const blob = new Blob([previewMarkup], { type: "text/html" });
  const url = URL.createObjectURL(blob);
  previewUrls.set(frame, url);
  frame.removeAttribute("srcdoc");
  frame.src = url;
}

function selectHeroTab(tab) {
  heroTabs.forEach((candidate) => {
    const active = candidate === tab;
    const panel = $(`#${candidate.getAttribute("aria-controls")}`);
    candidate.setAttribute("aria-selected", String(active));
    candidate.tabIndex = active ? 0 : -1;
    panel.hidden = !active;
  });
}

function runHeroCode() {
  renderPreview(heroPreview, heroCode.value);
  selectHeroTab($("#preview-tab"));
}

heroTabs.forEach((tab, index) => {
  tab.addEventListener("click", () => selectHeroTab(tab));
  tab.addEventListener("keydown", (event) => {
    if (!["ArrowLeft", "ArrowRight"].includes(event.key)) return;
    event.preventDefault();
    const direction = event.key === "ArrowRight" ? 1 : -1;
    const next = heroTabs[(index + direction + heroTabs.length) % heroTabs.length];
    selectHeroTab(next);
    next.focus();
  });
});

$("#hero-run").addEventListener("click", runHeroCode);
renderPreview(heroPreview, heroCode.value);

// Allow Tab characters inside code editors
[heroCode, $("#project-code")].forEach((editor) => {
  editor.addEventListener("keydown", (event) => {
    if (event.key !== "Tab") return;
    event.preventDefault();
    const start = editor.selectionStart;
    const end = editor.selectionEnd;
    editor.value = `${editor.value.slice(0, start)}  ${editor.value.slice(end)}`;
    editor.selectionStart = editor.selectionEnd = start + 2;
  });
});

// Document skeleton highlighting
const structureCards = $$(".structure-card");
const codeParts = $$("[data-code-part]");

function highlightStructure(part) {
  structureCards.forEach((card) => {
    const active = card.dataset.highlight === part;
    card.classList.toggle("is-selected", active);
    card.setAttribute("aria-pressed", String(active));
  });
  codeParts.forEach((codePart) => {
    codePart.classList.toggle("is-highlighted", codePart.dataset.codePart === part);
  });
}

structureCards.forEach((card) => {
  card.setAttribute("aria-pressed", "false");
  card.addEventListener("click", () => highlightStructure(card.dataset.highlight));
});
highlightStructure("doctype");

// Copy buttons
$$('[data-copy-target]').forEach((button) => {
  button.addEventListener("click", async () => {
    const target = $(`#${button.dataset.copyTarget}`);
    if (!target) return;
    const originalLabel = button.textContent;
    try {
      await navigator.clipboard.writeText(target.textContent);
      button.textContent = "已复制 ✓";
    } catch {
      button.textContent = "请手动选择复制";
    }
    window.setTimeout(() => {
      button.textContent = originalLabel;
    }, 1800);
  });
});

// Native dialog demo
const courseDialog = $("#course-dialog");
$("#open-dialog").addEventListener("click", () => {
  if (typeof courseDialog.showModal === "function") courseDialog.showModal();
  else courseDialog.setAttribute("open", "");
});

[$("#close-dialog"), $("#dialog-got-it")].forEach((button) => {
  button.addEventListener("click", () => {
    if (typeof courseDialog.close === "function") courseDialog.close();
    else courseDialog.removeAttribute("open");
  });
});

courseDialog.addEventListener("click", (event) => {
  if (event.target !== courseDialog) return;
  const box = courseDialog.getBoundingClientRect();
  const clickedOutside =
    event.clientX < box.left ||
    event.clientX > box.right ||
    event.clientY < box.top ||
    event.clientY > box.bottom;
  if (clickedOutside) courseDialog.close();
});

// Form validation demo
const learningForm = $("#learning-form");
const formFeedback = $("#form-feedback");

learningForm.addEventListener(
  "invalid",
  () => {
    formFeedback.textContent = "还有输入没有通过：浏览器已标出第一个需要修改的位置。";
    formFeedback.className = "form-feedback is-error";
  },
  true,
);

learningForm.addEventListener("input", () => {
  if (!learningForm.checkValidity()) {
    formFeedback.textContent = "正在填写，提交时浏览器会检查必填项和邮箱格式。";
    formFeedback.className = "form-feedback";
  }
});

learningForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const data = new FormData(learningForm);
  formFeedback.textContent = `${data.get("name")}，信息已通过原生校验，学习方向：${data.get("direction")}。`;
  formFeedback.className = "form-feedback is-success";
});

// Complete registration form: validation, FormData preview and local draft
const registrationForm = $("#registration-form");
const registrationFeedback = $("#registration-feedback");
const registrationPayload = $("#registration-payload");
const registrationDraftKey = "html-course-registration-draft-v1";

function readRegistrationData() {
  const data = new FormData(registrationForm);
  return {
    name: data.get("name") || "",
    email: data.get("email") || "",
    direction: data.get("direction") || "",
    mode: data.get("mode") || "",
    skills: data.getAll("skills"),
    startDate: data.get("startDate") || "",
    goal: data.get("goal") || "",
    agreement: data.get("agreement") === "accepted",
  };
}

function showRegistrationPayload(data) {
  registrationPayload.textContent = JSON.stringify(data, null, 2);
}

registrationForm.addEventListener(
  "invalid",
  () => {
    registrationFeedback.textContent = "报名信息尚未通过：浏览器已定位第一个无效控件，请按提示修改。";
    registrationFeedback.className = "registration-feedback is-error";
  },
  true,
);

registrationForm.addEventListener("input", () => {
  registrationFeedback.textContent = "内容已修改，提交时会检查必填项、邮箱格式和文字长度。";
  registrationFeedback.className = "registration-feedback";
});

registrationForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const data = readRegistrationData();
  showRegistrationPayload(data);
  registrationFeedback.textContent = `${data.name}，原生校验已通过。右侧数据就是浏览器准备提交的字段。`;
  registrationFeedback.className = "registration-feedback is-success";
});

$("#save-registration-draft").addEventListener("click", () => {
  const data = readRegistrationData();
  try {
    localStorage.setItem(registrationDraftKey, JSON.stringify(data));
    registrationFeedback.textContent = "草稿已保存在这台设备中，刷新页面后仍可继续填写。";
    registrationFeedback.className = "registration-feedback is-draft";
    showRegistrationPayload({ draft: true, ...data });
  } catch {
    registrationFeedback.textContent = "浏览器不允许本地存储；表单仍可继续填写和提交。";
    registrationFeedback.className = "registration-feedback is-error";
  }
});

registrationForm.addEventListener("reset", () => {
  window.setTimeout(() => {
    try {
      localStorage.removeItem(registrationDraftKey);
    } catch {
      // Resetting the visible form does not depend on storage access.
    }
    registrationPayload.textContent = JSON.stringify({ 状态: "表单已清空" }, null, 2);
    registrationFeedback.textContent = "表单和本机草稿已清空。";
    registrationFeedback.className = "registration-feedback";
  });
});

try {
  const savedDraft = JSON.parse(localStorage.getItem(registrationDraftKey) || "null");
  if (savedDraft) {
    $("#reg-name").value = savedDraft.name || "";
    $("#reg-email").value = savedDraft.email || "";
    $("#reg-direction").value = savedDraft.direction || "";
    $("#reg-date").value = savedDraft.startDate || "";
    $("#reg-goal").value = savedDraft.goal || "";
    if (savedDraft.mode) {
      const mode = registrationForm.querySelector(`input[name="mode"][value="${savedDraft.mode}"]`);
      if (mode) mode.checked = true;
    }
    registrationForm.querySelectorAll('input[name="skills"]').forEach((skill) => {
      skill.checked = Array.isArray(savedDraft.skills) && savedDraft.skills.includes(skill.value);
    });
    registrationForm.elements.agreement.checked = Boolean(savedDraft.agreement);
    registrationFeedback.textContent = "已恢复上次保存的本机草稿。";
    registrationFeedback.className = "registration-feedback is-draft";
    showRegistrationPayload({ draft: true, ...savedDraft });
  }
} catch {
  // Invalid or unavailable local storage should not block the form demo.
}

// Responsive layout preview
const deviceButtons = $$("[data-device]");
const responsiveDevice = $("#responsive-device");
const viewportOutput = $("#viewport-output");
const deviceLabels = {
  desktop: "桌面 · 720px",
  tablet: "平板 · 520px",
  mobile: "手机 · 300px",
};

deviceButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const device = button.dataset.device;
    deviceButtons.forEach((candidate) => {
      const selected = candidate === button;
      candidate.classList.toggle("is-selected", selected);
      candidate.setAttribute("aria-pressed", String(selected));
    });
    responsiveDevice.className = `responsive-device is-${device}`;
    viewportOutput.textContent = deviceLabels[device];
  });
});

// Global attributes playground
const attributeDemoCard = $("#attribute-demo-card");
const attributeBadge = $("#attribute-badge");
const attributeExtra = $("#attribute-extra");
const attributeStatus = $("#attribute-status");
const hiddenToggle = $("#toggle-hidden-content");

function updateAttributeStatus() {
  const level = attributeDemoCard.dataset.level;
  attributeStatus.textContent = `data-level="${level}" · 详细内容${attributeExtra.hidden ? "隐藏" : "显示"}`;
}

$("#toggle-attribute-level").addEventListener("click", () => {
  const important = attributeDemoCard.dataset.level === "important";
  attributeDemoCard.dataset.level = important ? "normal" : "important";
  attributeBadge.textContent = important ? "普通" : "重要";
  updateAttributeStatus();
});

hiddenToggle.addEventListener("click", () => {
  attributeExtra.hidden = !attributeExtra.hidden;
  hiddenToggle.setAttribute("aria-expanded", String(!attributeExtra.hidden));
  hiddenToggle.textContent = attributeExtra.hidden ? "显示 hidden 内容" : "隐藏详细内容";
  updateAttributeStatus();
});

// VS Code efficiency toolkit: Emmet expansion and shortcut platform switch
const emmetInput = $("#emmet-input");
const emmetOutput = $("#emmet-output");
const emmetExamples = {
  "ul.skill-list>li.item*3": `<ul class="skill-list">
  <li class="item"></li>
  <li class="item"></li>
  <li class="item"></li>
</ul>`,
  "nav>a*3": `<nav>
  <a href=""></a>
  <a href=""></a>
  <a href=""></a>
</nav>`,
  "form>label+input:email+button": `<form>
  <label for="email"></label>
  <input type="email" id="email" name="email">
  <button type="submit"></button>
</form>`,
  "!": `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Document</title>
</head>
<body>

</body>
</html>`,
};

function expandEmmetExample() {
  const abbreviation = emmetInput.value.trim();
  emmetOutput.textContent = emmetExamples[abbreviation] || "这个网页演示器只收录了上方四个示例。请在 VS Code 的 HTML 文件中按 Tab，体验完整 Emmet 语法。";
  $$("[data-emmet]").forEach((button) => {
    button.classList.toggle("is-selected", button.dataset.emmet === abbreviation);
  });
}

$("#expand-emmet").addEventListener("click", expandEmmetExample);
emmetInput.addEventListener("keydown", (event) => {
  if (event.key !== "Enter") return;
  event.preventDefault();
  expandEmmetExample();
});

$$('[data-emmet]').forEach((button) => {
  button.addEventListener("click", () => {
    emmetInput.value = button.dataset.emmet;
    expandEmmetExample();
  });
});

$$('[data-shortcut-os]').forEach((button) => {
  button.addEventListener("click", () => {
    const os = button.dataset.shortcutOs;
    $$('[data-shortcut-os]').forEach((candidate) => {
      const selected = candidate === button;
      candidate.classList.toggle("is-selected", selected);
      candidate.setAttribute("aria-pressed", String(selected));
    });
    $$('[data-mac][data-windows]').forEach((key) => {
      key.textContent = key.dataset[os];
    });
  });
});

// Fallback for browsers without the Popover API
const popoverButton = $('[popovertarget="html-tip"]');
const tipPopover = $("#html-tip");
if (!("popover" in HTMLElement.prototype)) {
  popoverButton.addEventListener("click", () => {
    const isOpen = tipPopover.hasAttribute("data-fallback-open");
    tipPopover.toggleAttribute("data-fallback-open", !isOpen);
    tipPopover.style.display = isOpen ? "none" : "block";
    tipPopover.style.position = "fixed";
    tipPopover.style.inset = "auto 24px 24px auto";
  });
}

// Capstone editor, preview and structural checks
const projectCode = $("#project-code");
const projectFrame = $("#project-frame");
const projectStatus = $("#project-status");
const projectResult = $("#project-result");
const stretchChallenges = $("#stretch-challenges");
const projectProgressCount = $("#project-progress-count");
const projectProgressBar = $("#project-progress-bar");
const projectHint = $("#project-hint");
const projectHintCopy = $("#project-hint-copy");
const initialProjectCode = projectCode.value;
const projectStorageKey = "html-course-project-code-v2";
const projectCheckOrder = ["main", "h1", "img", "list", "link", "viewport"];
const projectHints = {
  main: "当前页面使用的是通用 div。找到包住整张名片的容器，把标签名改为表示页面主体的 main，并记得同步修改结束标签。",
  h1: "页面需要一个主标题。把“你好，我是小明”对应的 h2 改为 h1；“我的技能”仍然保留为 h2。",
  img: "内容图片需要替代文字。在 img 中加入 alt 属性，用一句短话描述这张图在页面中的用途。",
  list: "技能清单目前只有两个 li。再添加一个你已经掌握或正在学习的技能。",
  link: "没有 href 的 a 不是可导航链接。为“我的学习资料”添加一个真实地址，例如 MDN HTML 页面。",
  viewport: "在 head 中添加 name 为 viewport 的 meta，并让 content 包含 width=device-width。",
};

function inspectProject(markup) {
  const parsed = new DOMParser().parseFromString(markup, "text/html");
  const viewport = parsed.querySelector('meta[name="viewport"]');
  const checks = {
    main: Boolean(parsed.querySelector("main")),
    h1: parsed.querySelectorAll("h1").length === 1,
    img: [...parsed.querySelectorAll("img")].some((image) => image.hasAttribute("alt") && image.getAttribute("alt").trim()),
    list: [...parsed.querySelectorAll("ul, ol")].some((list) => list.querySelectorAll("li").length >= 3),
    link: [...parsed.querySelectorAll("a")].some((link) => link.hasAttribute("href") && link.getAttribute("href").trim()),
    viewport: Boolean(viewport?.getAttribute("content")?.includes("width=device-width")),
  };

  Object.entries(checks).forEach(([name, passed]) => {
    $(`[data-check="${name}"]`).classList.toggle("is-complete", passed);
  });

  return { checks, passed: Object.values(checks).filter(Boolean).length };
}

function runProject() {
  const markup = projectCode.value;
  renderPreview(projectFrame, markup);
  const { passed } = inspectProject(markup);
  const total = projectCheckOrder.length;
  projectProgressCount.textContent = `${passed} / ${total}`;
  projectProgressBar.style.width = `${(passed / total) * 100}%`;

  if (passed === total) {
    projectStatus.textContent = "6 / 6 项通过，核心任务完成！";
    projectStatus.className = "is-success";
    projectResult.hidden = false;
    stretchChallenges.hidden = false;
    projectHint.hidden = true;
  } else {
    projectStatus.textContent = `${passed} / ${total} 项通过，黄色任务单显示了下一步。`;
    projectStatus.className = "is-error";
    projectResult.hidden = true;
    stretchChallenges.hidden = true;
  }

  try {
    localStorage.setItem(projectStorageKey, markup);
  } catch {
    // The playground still works when storage is disabled.
  }
}

projectCode.addEventListener("input", () => {
  projectStatus.textContent = "代码已修改，运行后更新检查结果";
  projectStatus.className = "";
  projectHint.hidden = true;
});

projectCode.addEventListener("keydown", (event) => {
  if (event.key !== "Enter" || (!event.ctrlKey && !event.metaKey)) return;
  event.preventDefault();
  runProject();
});

$("#show-project-hint").addEventListener("click", () => {
  const { checks } = inspectProject(projectCode.value);
  const firstMissing = projectCheckOrder.find((name) => !checks[name]);
  projectHintCopy.textContent = firstMissing
    ? projectHints[firstMissing]
    : "核心任务已经全部通过。运行代码解锁下方三个进阶挑战。";
  projectHint.hidden = false;
});

$$('[data-project-device]').forEach((button) => {
  button.addEventListener("click", () => {
    const device = button.dataset.projectDevice;
    $$('[data-project-device]').forEach((candidate) => {
      const selected = candidate === button;
      candidate.classList.toggle("is-selected", selected);
      candidate.setAttribute("aria-pressed", String(selected));
    });
    $("#project-frame-shell").className = `project-frame-shell is-${device}`;
  });
});

try {
  const savedProject = localStorage.getItem(projectStorageKey);
  if (savedProject) projectCode.value = savedProject;
} catch {
  // Local persistence is optional.
}

$("#run-project").addEventListener("click", runProject);
$("#reset-project").addEventListener("click", () => {
  projectCode.value = initialProjectCode;
  try {
    localStorage.removeItem(projectStorageKey);
  } catch {
    // Ignore unavailable storage.
  }
  runProject();
});

runProject();
