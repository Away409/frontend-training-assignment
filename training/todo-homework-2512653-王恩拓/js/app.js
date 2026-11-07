"use strict";

const form = document.querySelector("#todo-form");
const titleInput = document.querySelector("#title");
const inputError = document.querySelector("#input-error");
const storageError = document.querySelector("#storage-error");
const tasks = document.querySelector("#tasks");
const filters = document.querySelector("#filters");
const remaining = document.querySelector("#remaining");
const empty = document.querySelector("#empty");
const storageKey = "todos";

let todos = loadTodos();
let filter = "all";

function loadTodos() {
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey) ?? "[]");
    const valid = Array.isArray(saved) && saved.every(todo =>
      todo && typeof todo.id === "string" &&
      typeof todo.title === "string" && todo.title.trim() &&
      typeof todo.done === "boolean"
    );
    return valid && new Set(saved.map(todo => todo.id)).size === saved.length ? saved : [];
  } catch {
    return [];
  }
}

function updateTodos(nextTodos) {
  todos = nextTodos;
  try {
    localStorage.setItem(storageKey, JSON.stringify(todos));
    storageError.hidden = true;
  } catch {
    storageError.textContent = "浏览器无法保存任务。本次更改可能在刷新后丢失。";
    storageError.hidden = false;
  }
  render();
}

function createTaskRow(todo) {
  const row = document.createElement("li");
  row.className = todo.done ? "task done" : "task";

  const toggle = document.createElement("input");
  toggle.type = "checkbox";
  toggle.checked = todo.done;
  toggle.dataset.action = "toggle";
  toggle.dataset.id = todo.id;
  toggle.setAttribute("aria-label", "完成任务：" + todo.title);

  const title = document.createElement("span");
  title.textContent = todo.title;

  const remove = document.createElement("button");
  remove.type = "button";
  remove.className = "delete";
  remove.dataset.action = "delete";
  remove.dataset.id = todo.id;
  remove.textContent = "删除";
  remove.setAttribute("aria-label", "删除任务：" + todo.title);

  row.append(toggle, title, remove);
  return row;
}

function render() {
  const visible = todos.filter(todo =>
    filter === "all" || todo.done === (filter === "done")
  );
  tasks.replaceChildren(...visible.map(createTaskRow));
  remaining.textContent = "剩余 " + todos.filter(todo => !todo.done).length + " 项";
  empty.hidden = visible.length > 0;
  empty.textContent = {
    all: "清单还是空的，添加一项任务吧。",
    active: "没有未完成的任务。",
    done: "还没有已完成的任务。"
  }[filter];

  for (const button of filters.querySelectorAll("button")) {
    button.setAttribute("aria-pressed", String(button.dataset.filter === filter));
  }
}

function showInputError(message) {
  inputError.textContent = message;
  titleInput.setAttribute("aria-invalid", String(Boolean(message)));
}

form.addEventListener("submit", event => {
  event.preventDefault();
  const title = titleInput.value.trim();
  if (!title) {
    showInputError("请输入任务标题。");
    titleInput.focus();
    return;
  }

  const id = Array.from(crypto.getRandomValues(new Uint32Array(4)), value =>
    value.toString(16).padStart(8, "0")
  ).join("");
  updateTodos([...todos, { id, title, done: false }]);
  showInputError("");
  form.reset();
  titleInput.focus();
});

titleInput.addEventListener("input", () => showInputError(""));

tasks.addEventListener("click", event => {
  const control = event.target.closest("[data-action]");
  if (!control) return;

  const { action, id } = control.dataset;
  const rowIndex = Array.from(tasks.children).indexOf(control.closest("li"));

  if (action === "toggle") {
    updateTodos(todos.map(todo => todo.id === id ? { ...todo, done: control.checked } : todo));
  } else if (action === "delete") {
    updateTodos(todos.filter(todo => todo.id !== id));
  }

  const nextRow = tasks.children[Math.min(rowIndex, tasks.children.length - 1)];
  (nextRow?.querySelector('[data-action="' + action + '"]') ?? titleInput).focus();
});

filters.addEventListener("click", event => {
  const button = event.target.closest("button[data-filter]");
  if (!button) return;
  filter = button.dataset.filter;
  render();
});

render();

