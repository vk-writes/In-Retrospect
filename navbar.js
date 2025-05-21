document.addEventListener("DOMContentLoaded", function () {
  const nav = document.createElement("nav");
  nav.innerHTML = `
    <a href="https://vk-writes.github.io/In-Retrospect/index.html" class="home-button">Home</a>
  `;
  document.body.insertBefore(nav, document.body.firstChild);
});
