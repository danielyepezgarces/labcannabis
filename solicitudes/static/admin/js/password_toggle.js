// Password visibility toggle functionality
(function() {
    'use strict';
    
    function initPasswordToggles() {
        // Find all password input fields
        const passwordFields = document.querySelectorAll('input[type="password"].password-input-toggle');
        
        passwordFields.forEach(function(field) {
            // Check if toggle button already exists
            if (field.parentElement.querySelector('.password-toggle-btn')) {
                return;
            }
            
            // Create wrapper if needed
            let wrapper = field.parentElement;
            if (!wrapper.classList.contains('password-field-wrapper')) {
                wrapper = document.createElement('div');
                wrapper.className = 'password-field-wrapper';
                field.parentNode.insertBefore(wrapper, field);
                wrapper.appendChild(field);
            }
            
            // Create toggle button
            const toggleBtn = document.createElement('button');
            toggleBtn.type = 'button';
            toggleBtn.className = 'password-toggle-btn';
            toggleBtn.innerHTML = '👁️';
            toggleBtn.setAttribute('aria-label', 'Mostrar contraseña');
            toggleBtn.title = 'Mostrar/Ocultar contraseña';
            
            // Add click handler
            toggleBtn.addEventListener('click', function(e) {
                e.preventDefault();
                
                if (field.type === 'password') {
                    field.type = 'text';
                    toggleBtn.innerHTML = '🔒';
                    toggleBtn.setAttribute('aria-label', 'Ocultar contraseña');
                } else {
                    field.type = 'password';
                    toggleBtn.innerHTML = '👁️';
                    toggleBtn.setAttribute('aria-label', 'Mostrar contraseña');
                }
            });
            
            // Insert toggle button after input field
            wrapper.appendChild(toggleBtn);
        });
    }
    
    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initPasswordToggles);
    } else {
        initPasswordToggles();
    }
    
    // Re-initialize when dynamic content is loaded (for inline forms, etc.)
    if (typeof django !== 'undefined' && django.jQuery) {
        django.jQuery(document).on('formset:added', function() {
            setTimeout(initPasswordToggles, 100);
        });
    }
})();
