/**
 * CourseCart Admin - Mobile Enhancements
 */
(function() {
    'use strict';
    
    // Mobile sidebar toggle
    document.addEventListener('DOMContentLoaded', function() {
        // Add hamburger button for mobile
        var navbar = document.querySelector('.main-header .navbar-nav');
        if (navbar && window.innerWidth <= 768) {
            var toggleBtn = document.createElement('button');
            toggleBtn.className = 'btn btn-link nav-link d-md-none';
            toggleBtn.innerHTML = '<i class="fas fa-bars"></i>';
            toggleBtn.style.cssText = 'font-size:20px;color:#475569;padding:8px;';
            toggleBtn.onclick = function() {
                document.body.classList.toggle('sidebar-open');
            };
            
            var navItem = document.createElement('li');
            navItem.className = 'nav-item';
            navItem.appendChild(toggleBtn);
            navbar.insertBefore(navItem, navbar.firstChild);
        }
        
        // Close sidebar when clicking overlay
        document.addEventListener('click', function(e) {
            if (document.body.classList.contains('sidebar-open') && 
                !e.target.closest('.main-sidebar') && 
                !e.target.closest('.btn-link')) {
                document.body.classList.remove('sidebar-open');
            }
        });
        
        // Close sidebar on escape
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                document.body.classList.remove('sidebar-open');
            }
        });
    });
    
})();