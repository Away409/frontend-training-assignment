import { readFile } from "node:fs/promises";

const html = await readFile(new URL("../index.html", import.meta.url), "utf8");
const css = await readFile(new URL("../styles.css", import.meta.url), "utf8");
const js = await readFile(new URL("../app.js", import.meta.url), "utf8");

const failures = [];
const requiredHtml = [
  '<html lang="zh-CN">',
  '<meta charset="UTF-8"',
  '<link rel="icon" href="favicon.svg" type="image/svg+xml"',
  'id="main-content"',
  'id="history"',
  'id="skeleton"',
  'id="tags"',
  'id="containers"',
  'id="tables"',
  'id="table-anatomy-title"',
  '<table class="course-plan-table">',
  '<caption id="demo-table-caption">',
  '<thead>',
  '<tbody>',
  '<tr>',
  '<th scope="col">',
  '<th scope="row">',
  '<td>',
  'role="region" aria-labelledby="demo-table-caption" tabindex="0"',
  'id="semantic-compare-title"',
  'data-semantic="strong"',
  'data-semantic="em"',
  'data-semantic="b"',
  'data-semantic="i"',
  'data-semantic="u"',
  'data-semantic="del"',
  'data-semantic="mark"',
  '&lt;del datetime=',
  '&lt;mark&gt;',
  'id="global-attributes-title"',
  'id="attribute-demo-card"',
  'id="toggle-attribute-level"',
  'id="toggle-hidden-content"',
  'data-level="important"',
  'Reference/Global_attributes',
  'id="file-paths"',
  'contact.html',
  'images/lesson.svg',
  '../index.html',
  '/assets/site.css',
  'id="html-comments"',
  '&lt;!-- 页面主导航 --&gt;',
  '<!-- 这条注释保留在 HTML 源码中',
  'id="character-entities"',
  '&amp;lt;h1&amp;gt;',
  '<code>&amp;lt;</code>',
  '&amp;nbsp;',
  'id="figures"',
  '<figure class="lesson-figure">',
  '<figcaption>',
  '&lt;figure&gt;',
  '&lt;figcaption&gt;',
  'id="quotes"',
  '<blockquote cite=',
  '<q>',
  '<cite>',
  '&lt;blockquote cite=',
  'id="code-text"',
  '<kbd>⌘</kbd>',
  '<samp>内容检查通过</samp>',
  '<var>viewportWidth</var>',
  '&lt;kbd&gt;',
  '&lt;samp&gt;',
  '&lt;var&gt;',
  'id="time-text"',
  '<time datetime="2026-08-15T09:00+08:00">',
  '<time datetime="PT45M">',
  '&lt;time datetime=',
  'id="forms"',
  'id="learning-form"',
  'id="registration-case"',
  'id="registration-form"',
  'id="registration-payload"',
  'id="save-registration-draft"',
  '&lt;form action="/register" method="post"&gt;',
  '&lt;fieldset&gt;',
  '&lt;legend&gt;',
  'type="radio" name="mode"',
  'name="skills"',
  'type="date"',
  '&lt;textarea',
  'type="submit"',
  'type="reset"',
  'type="button"',
  'id="responsive"',
  'id="responsive-title"',
  'id="responsive-device"',
  'id="modern"',
  'id="compatibility-title"',
  'id="practice"',
  'id="next"',
  'HTML Living Standard',
  '&lt;h1&gt;',
  '&lt;img',
  '&lt;a href=',
  '&lt;ul&gt;',
  '&lt;ol',
  '&lt;dl&gt;',
  'popovertarget="html-tip"',
  '<dialog',
  'loading="lazy"',
  'HarmonyOS · ArkTS',
  'Nu HTML Checker',
  'https://validator.w3.org/nu/',
  'https://caniuse.com/',
  'arkui-overview',
  'id="vscode-tools"',
  'id="emmet-input"',
  'id="emmet-output"',
  'id="vscode-settings"',
  'data-shortcut-os="windows"',
  'ritwickdey.LiveServer',
  'esbenp.prettier-vscode',
  'HTMLHint.vscode-htmlhint',
  'Snippets: Configure Snippets',
  '<textarea id="project-code"',
  '<iframe id="project-frame"',
  'sandbox="allow-scripts"',
  'id="project-progress-count"',
  'id="show-project-hint"',
  'id="project-result"',
  'id="stretch-challenges"',
  'data-project-device="mobile"',
  'aria-live="polite"',
  'https://html.spec.whatwg.org/',
];

for (const fragment of requiredHtml) {
  if (!html.includes(fragment)) failures.push(`缺少课程内容：${fragment}`);
}

if (!css.includes("prefers-reduced-motion")) failures.push("缺少减少动态效果的系统偏好适配");
if (!css.includes("@media (max-width: 620px)")) failures.push("缺少手机端响应式布局");

for (const behavior of ["runHeroCode", "renderPreview", "highlightStructure", "inspectProject", "showModal", "learningForm", "registrationForm", "readRegistrationData", "registrationDraftKey", "deviceLabels", "attributeDemoCard", "updateAttributeStatus", "expandEmmetExample", "shortcutOs"]) {
  if (!js.includes(behavior)) failures.push(`缺少交互逻辑：${behavior}`);
}

const previewFrames = [...html.matchAll(/<iframe\b[^>]*id="(?:hero-preview|project-frame)"[^>]*>/g)].map((match) => match[0]);
if (previewFrames.length !== 2 || previewFrames.some((frame) => !/\bsandbox="allow-scripts"/.test(frame))) {
  failures.push("代码预览 iframe 应在保留隔离的同时允许示例脚本执行：sandbox=\"allow-scripts\"");
}

const lessonIndexes = [...html.matchAll(/class="lesson-index">([^<]+)/g)].map((match) => match[1]);
const expectedLessonIndexes = ["3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7", "3.8", "3.9", "3.10", "3.11", "3.12", "3.13", "3.14", "3.15", "3.16", "4.1"];
if (lessonIndexes.join(",") !== expectedLessonIndexes.join(",")) {
  failures.push(`常用标签与布局小节编号错误：${lessonIndexes.join(", ")}`);
}

const projectChecks = [...html.matchAll(/data-check="([^"]+)"/g)].map((match) => match[1]);
const expectedProjectChecks = ["main", "h1", "img", "list", "link", "viewport"];
if (projectChecks.join(",") !== expectedProjectChecks.join(",")) {
  failures.push(`综合实践检查项不完整：${projectChecks.join(", ")}`);
}

const tagsStart = html.indexOf('<section class="tags lesson-section"');
const layoutStart = html.indexOf('<section class="layout lesson-section"');
const modernStart = html.indexOf('<section class="modern lesson-section"');
if (!(tagsStart < layoutStart && layoutStart < modernStart)) {
  failures.push("章节顺序错误：常用标签、布局与设备适配、现代 HTML 应依次独立出现");
}
const tagsMarkup = html.slice(tagsStart, layoutStart);
if (tagsMarkup.includes('id="responsive"') || tagsMarkup.includes("device-toolbar")) {
  failures.push("响应式布局仍嵌套在常用标签章节中");
}

// Teaching samples repeat realistic ids inside raw text. Exclude code blocks and editors
// before checking ids belonging to the actual course interface.
const documentMarkup = html
  .replace(/<pre\b[\s\S]*?<\/pre>/gi, "")
  .replace(/<textarea\b[\s\S]*?<\/textarea>/gi, "");
const ids = [...documentMarkup.matchAll(/\sid="([^"]+)"/g)].map((match) => match[1]);
const duplicateIds = ids.filter((id, index) => ids.indexOf(id) !== index);
if (duplicateIds.length) failures.push(`存在重复 id：${[...new Set(duplicateIds)].join(", ")}`);

const localTargets = [...documentMarkup.matchAll(/href="#([^"]+)"/g)].map((match) => match[1]);
const missingTargets = localTargets.filter((target) => !ids.includes(target));
if (missingTargets.length) failures.push(`存在无效页内链接：${[...new Set(missingTargets)].join(", ")}`);

if (failures.length) {
  console.error(failures.join("\n"));
  process.exitCode = 1;
} else {
  console.log(`内容检查通过：${ids.length} 个唯一 id，${localTargets.length} 个有效页内链接，7 个完整章节。`);
}
