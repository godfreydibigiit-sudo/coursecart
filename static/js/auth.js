/**
 * COURSECART - Authentication JavaScript
 * Handles forms, validation, and role selection
 */

(function() {
    'use strict';

    document.addEventListener('DOMContentLoaded', function() {
        initRoleSelection();
        initPasswordToggle();
        initFormValidation();
    });

    /**
     * Role selection cards (Registration page)
     */
    function initRoleSelection() {
        const roleCards = document.querySelectorAll('.role-card');
        const roleInput = document.getElementById('id_role');
        
        if (!roleCards.length) return;
        
        roleCards.forEach(card => {
            card.addEventListener('click', function() {
                // Remove selected class from all cards
                roleCards.forEach(c => c.classList.remove('selected'));
                
                // Add selected class to clicked card
                this.classList.add('selected');
                
                // Update hidden/radio input
                const radio = this.querySelector('input[type="radio"]');
                if (radio) {
                    radio.checked = true;
                }
                
                // Update Django form field if exists
                if (roleInput) {
                    roleInput.value = radio ? radio.value : '';
                }
            });
        });
    }

    /**
     * Password visibility toggle
     */
    function initPasswordToggle() {
        const toggleButtons = document.querySelectorAll('.password-toggle');
        
        toggleButtons.forEach(button => {
            button.addEventListener('click', function() {
                const input = this.parentElement.querySelector('input');
                const icon = this.querySelector('i, svg, img');
                
                if (input.type === 'password') {
                    input.type = 'text';
                    if (icon) {
                        icon.textContent = '🙈';
                    }
                    this.setAttribute('aria-label', 'Hide password');
                } else {
                    input.type = 'password';
                    if (icon) {
                        icon.textContent = '👁️';
                    }
                    this.setAttribute('aria-label', 'Show password');
                }
            });
        });
    }

    /**
     * Client-side form validation
     */
    function initFormValidation() {
        const authForms = document.querySelectorAll('.auth-card form');
        
        authForms.forEach(form => {
            form.addEventListener('submit', function(e) {
                let hasErrors = false;
                
                // Required field check
                const requiredFields = form.querySelectorAll('[required]');
                requiredFields.forEach(field => {
                    if (!field.value.trim()) {
                        field.classList.add('is-invalid');
                        hasErrors = true;
                        
                        // Add error message if not exists
                        let errorMsg = field.parentElement.querySelector('.form-error');
                        if (!errorMsg) {
                            errorMsg = document.createElement('div');
                            errorMsg.className = 'form-error';
                            errorMsg.textContent = 'This field is required';
                            field.parentElement.appendChild(errorMsg);
                        }
                    } else {
                        field.classList.remove('is-invalid');
                        const errorMsg = field.parentElement.querySelector('.form-error');
                        if (errorMsg) errorMsg.remove();
                    }
                });
                
                // Email validation
                const emailFields = form.querySelectorAll('input[type="email"]');
                emailFields.forEach(field => {
                    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                    if (field.value && !emailRegex.test(field.value)) {
                        field.classList.add('is-invalid');
                        hasErrors = true;
                        
                        let errorMsg = field.parentElement.querySelector('.form-error');
                        if (!errorMsg) {
                            errorMsg = document.createElement('div');
                            errorMsg.className = 'form-error';
                            errorMsg.textContent = 'Please enter a valid email address';
                            field.parentElement.appendChild(errorMsg);
                        }
                    }
                });
                
                // Password match validation
                const password1 = form.querySelector('[name="password1"]');
                const password2 = form.querySelector('[name="password2"]');
                
                if (password1 && password2) {
                    if (password1.value !== password2.value) {
                        password2.classList.add('is-invalid');
                        hasErrors = true;
                        
                        let errorMsg = password2.parentElement.querySelector('.form-error');
                        if (!errorMsg) {
                            errorMsg = document.createElement('div');
                            errorMsg.className = 'form-error';
                            errorMsg.textContent = 'Passwords do not match';
                            password2.parentElement.appendChild(errorMsg);
                        }
                    }
                }
                
                // Password strength (minimum 8 characters)
                if (password1 && password1.value.length > 0 && password1.value.length < 8) {
                    password1.classList.add('is-invalid');
                    hasErrors = true;
                    
                    let errorMsg = password1.parentElement.querySelector('.form-error');
                    if (!errorMsg) {
                        errorMsg = document.createElement('div');
                        errorMsg.className = 'form-error';
                        errorMsg.textContent = 'Password must be at least 8 characters';
                        password1.parentElement.appendChild(errorMsg);
                    }
                }
                
                if (hasErrors) {
                    e.preventDefault();
                    
                    // Scroll to first error
                    const firstError = form.querySelector('.is-invalid');
                    if (firstError) {
                        firstError.focus();
                        firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                }
            });
            
            // Real-time validation (remove error on input)
            form.querySelectorAll('input').forEach(input => {
                input.addEventListener('input', function() {
                    this.classList.remove('is-invalid');
                    const errorMsg = this.parentElement.querySelector('.form-error');
                    if (errorMsg) errorMsg.remove();
                });
            });
        });
    }

})();