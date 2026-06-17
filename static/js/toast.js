/**
 * CourseCart Toast Notification System
 * Auto-dismiss, smooth animations, accessibility
 */
(function() {
    'use strict';
    
    document.addEventListener('DOMContentLoaded', function() {
        const toasts = document.querySelectorAll('.toast');
        
        toasts.forEach(function(toast) {
            // Get delay from data attribute or default 5 seconds
            const delay = parseInt(toast.getAttribute('data-delay')) || 5000;
            
            // Auto dismiss
            if (delay > 0) {
                setTimeout(function() {
                    dismissToast(toast);
                }, delay);
            }
            
            // Pause auto-dismiss on hover
            toast.addEventListener('mouseenter', function() {
                toast.setAttribute('data-paused', 'true');
            });
            
            toast.addEventListener('mouseleave', function() {
                toast.removeAttribute('data-paused');
                // Resume with shorter delay
                setTimeout(function() {
                    if (!toast.hasAttribute('data-paused')) {
                        dismissToast(toast);
                    }
                }, 2000);
            });
        });
    });
    
    function dismissToast(toast) {
        if (toast.classList.contains('removing')) return;
        
        toast.classList.add('removing');
        
        // Remove from DOM after animation
        setTimeout(function() {
            toast.remove();
            
            // Remove container if empty
            const container = document.getElementById('toastContainer');
            if (container && container.children.length === 0) {
                container.remove();
            }
        }, 300);
    }
    
    // Expose dismiss function globally
    window.dismissToast = dismissToast;
    
})();