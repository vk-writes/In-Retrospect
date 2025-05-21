// navbar.js

document.addEventListener("DOMContentLoaded", () => {
  // Create sidebar HTML
  const sidebarHTML = `
    <div class="sidebar" id="sidebar" aria-hidden="true">
      <button class="close-btn" id="closeSidebar" aria-label="Close menu">&times;</button>
      <nav>
        <a href="index.html" class="nav-link">Home</a>
        <a href="about.html" class="nav-link">About</a>
        <a href="contact.html" class="nav-link">Contact</a>
        <a href="articles.html" class="nav-link">Articles</a>
      </nav>
      <button id="darkModeToggle" class="dark-toggle" aria-label="Toggle dark mode">🌓 Dark Mode</button>
    </div>
    <div id="overlay"></div>
    <button class="hamburger" id="openSidebar" aria-label="Open menu">&#9776;</button>
  `;

  // Insert sidebar and hamburger at the top of body
  document.body.insertAdjacentHTML("afterbegin", sidebarHTML);

  // Elements
  const sidebar = document.getElementById("sidebar");
  const openBtn = document.getElementById("openSidebar");
  const closeBtn = document.getElementById("closeSidebar");
  const overlay = document.getElementById("overlay");
  const darkToggleBtn = document.getElementById("darkModeToggle");
  const navLinks = document.querySelectorAll(".nav-link");

  // Functions to open/close sidebar
  function openSidebar() {
    sidebar.setAttribute("aria-hidden", "false");
    sidebar.classList.add("open");
    overlay.style.display = "block";
  }
  function closeSidebar() {
    sidebar.setAttribute("aria-hidden", "true");
    sidebar.classList.remove("open");
    overlay.style.display = "none";
  }

  openBtn.addEventListener("click", openSidebar);
  closeBtn.addEventListener("click", closeSidebar);
  overlay.addEventListener("click", closeSidebar);

  // Highlight active nav link based on current URL
  const currentPath = window.location.pathname.split("/").pop(); // get current file name
  navLinks.forEach(link => {
    if (link.getAttribute("href") === currentPath || 
       (link.getAttribute("href") === "index.html" && currentPath === "")) {
      link.classList.add("active");
    }
  });

  // Dark mode toggle
  function toggleDarkMode() {
    document.body.classList.toggle("dark-mode");
    if (document.body.classList.contains("dark-mode")) {
      localStorage.setItem("darkMode", "enabled");
      darkToggleBtn.textContent = "🌞 Light Mode";
    } else {
      localStorage.setItem("darkMode", "disabled");
      darkToggleBtn.textContent = "🌓 Dark Mode";
    }
  }

  // Initialize dark mode state from localStorage
  if (localStorage.getItem("darkMode") === "enabled") {
    document.body.classList.add("dark-mode");
    darkToggleBtn.textContent = "🌞 Light Mode";
  } else {
    darkToggleBtn.textContent = "🌓 Dark Mode";
  }

  darkToggleBtn.addEventListener("click", toggleDarkMode);

  // Auto-hide hamburger and sidebar on wider screens (>768px)
  function checkScreenSize() {
    if (window.innerWidth >= 768) {
      openBtn.style.display = "none";
      sidebar.classList.remove("open");
      sidebar.setAttribute("aria-hidden", "true");
      overlay.style.display = "none";
    } else {
      openBtn.style.display = "block";
    }
  }
  checkScreenSize();
  window.addEventListener("resize", checkScreenSize);
});
