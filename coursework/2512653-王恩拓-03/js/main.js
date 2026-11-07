// 本地演示：不联网、不保存留言，不把输入内容插入 HTML。
const form = document.querySelector('form');
const status = document.querySelector('#form-status');
form.addEventListener('submit', (event) => {
  event.preventDefault();
  const nickname = form.elements.nickname.value.trim();
  if (!nickname) {
    form.elements.nickname.setCustomValidity('请输入称呼，不能只填写空格。');
    form.elements.nickname.reportValidity();
    return;
  }
  status.textContent = `谢谢你，${nickname}！已完成本地表单演示，留言未发送或保存。`;
});
form.elements.nickname.addEventListener('input', () => {
  form.elements.nickname.setCustomValidity('');
  status.textContent = '';
});
