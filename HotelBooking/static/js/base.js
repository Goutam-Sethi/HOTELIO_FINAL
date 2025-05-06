// Function to open the sidebar
function openNav() {
    document.getElementById("mySidebar").classList.add('open');
    document.body.classList.add('sidebar-open');
  }
  
  // Function to close the sidebar
  function closeNav() {
    document.getElementById("mySidebar").classList.remove('open');
    document.body.classList.remove('sidebar-open');
  }


  function checkLogin() {
    const isLoggedIn = {{ request.session.is_authenticated|yesno:"true,false" }};
    if (!isLoggedIn) {
      alert("⚠️ Please log in first to access taxi booking.");
      return false; // block navigation
    }
    return true; // allow normal link
  }
  