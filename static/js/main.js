/**
 * COURSECART - Main JavaScript
 * Core functionality for the platform
 */

(function() {
    'use strict';

    // DOM Ready
    document.addEventListener('DOMContentLoaded', function() {
        initAlerts();
        initNavbarScroll();
        initSmoothScroll();
    });

    /**
     * Initialize alert/dismissible messages
     */
    function initAlerts() {
        const alerts = document.querySelectorAll('.alert');
        
        alerts.forEach(alert => {
            // Auto-add close button if not exists
            if (!alert.querySelector('.alert-close')) {
                const closeBtn = document.createElement('button');
                closeBtn.className = 'alert-close';
                closeBtn.innerHTML = '&times;';
                closeBtn.setAttribute('aria-label', 'Close');
                
                closeBtn.addEventListener('click', function() {
                    alert.style.opacity = '0';
                    alert.style.transform = 'translateY(-10px)';
                    alert.style.transition = 'all 0.3s ease';
                    
                    setTimeout(() => {
                        alert.remove();
                    }, 300);
                });
                
                alert.appendChild(closeBtn);
            }
            
            // Auto-dismiss after 5 seconds for success/info
            if (alert.classList.contains('alert-success') || 
                alert.classList.contains('alert-info')) {
                setTimeout(() => {
                    if (alert.parentNode) {
                        alert.style.opacity = '0';
                        alert.style.transform = 'translateY(-10px)';
                        alert.style.transition = 'all 0.3s ease';
                        setTimeout(() => alert.remove(), 300);
                    }
                }, 5000);
            }
        });
    }

    /**
     * Navbar scroll effect
     */
    function initNavbarScroll() {
        const navbar = document.querySelector('.navbar');
        
        if (navbar) {
            window.addEventListener('scroll', function() {
                if (window.scrollY > 10) {
                    navbar.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)';
                } else {
                    navbar.style.boxShadow = 'none';
                }
            });
        }
    }

    /**
     * Smooth scroll for anchor links
     */
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const targetId = this.getAttribute('href');
                
                if (targetId === '#') return;
                
                const target = document.querySelector(targetId);
                
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    /**
     * Export utility functions globally
     */
    window.CourseCart = window.CourseCart || {};
    
    window.CourseCart.showToast = function(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `alert alert-${type}`;
        toast.style.position = 'fixed';
        toast.style.top = '20px';
        toast.style.right = '20px';
        toast.style.zIndex = '9999';
        toast.style.minWidth = '300px';
        toast.innerHTML = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    };

})();