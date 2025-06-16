function showField(fieldId) {
    const button = document.querySelector(`#${fieldId}_group button`);
    const textInput = document.getElementById(fieldId);
    const fontSizeInput = document.querySelector(`#${fieldId}_group input[name='${fieldId}_font_size']`);

    button.style.display = 'none';
    textInput.style.display = 'block';
    if (fontSizeInput) fontSizeInput.closest('.col-md-3').style.display = 'block';
    textInput.focus();

    // Update preview when text input changes
    textInput.addEventListener('input', function() {
        updatePreview(fieldId);
    });

    // Update preview when font size input changes
    if (fontSizeInput) {
        fontSizeInput.addEventListener('input', function() {
            updatePreview(fieldId);
        });
    }

    // Initial preview update if field is shown on load
    if (textInput.style.display !== 'none') {
        updatePreview(fieldId);
    }
}

function updatePreview(fieldId) {
    const textElement = document.getElementById(fieldId);
    const fontSizeElement = document.querySelector(`#${fieldId}_group input[name='${fieldId}_font_size']`);
    const previewElement = document.getElementById(`preview_${fieldId}`);

    if (previewElement) {
        previewElement.textContent = textElement.value;
        if (fontSizeElement && fontSizeElement.value) {
            previewElement.style.fontSize = `${fontSizeElement.value}rem`;
        }
    }
    // Handle site_name which is <h3>
    if (fieldId === 'site_name') {
        const siteNamePreview = document.getElementById('preview_site_name');
        if(siteNamePreview) {
            siteNamePreview.textContent = textElement.value;
            if (fontSizeElement && fontSizeElement.value) {
                siteNamePreview.style.fontSize = `${fontSizeElement.value}rem`;
            }
        }
    }
}

function attachInputListeners(fieldRow) {
    const keyInput = fieldRow.querySelector('.extra-field-key');
    const textInput = fieldRow.querySelector('.extra-field-value');
    const fontSizeInput = fieldRow.querySelector('.extra-field-font-size');

    // Add input listeners to update preview
    keyInput.addEventListener('input', function() { updateExtraFieldPreview(fieldRow); });
    textInput.addEventListener('input', function() { updateExtraFieldPreview(fieldRow); });
    fontSizeInput.addEventListener('input', function() { updateExtraFieldPreview(fieldRow); });

    // Initial preview update for existing fields
    updateExtraFieldPreview(fieldRow);
}

function updateExtraFieldPreview(fieldRow) {
    const keyInput = fieldRow.querySelector('.extra-field-key');
    const valueInput = fieldRow.querySelector('.extra-field-value');
    const fontSizeInput = fieldRow.querySelector('.extra-field-font-size');
    const index = fieldRow.querySelector('.extra-field-key').name.replace('extra_field_key_', '');
    const previewElement = document.querySelector(`#extra-fields-preview p[data-index='${index}']`);

    if (previewElement) {
        // Update key and value spans
        const previewKeySpan = previewElement.querySelector('.extra-field-preview-key');
        const previewValueSpan = previewElement.querySelector('.extra-field-preview-value');

        if (previewKeySpan) previewKeySpan.textContent = keyInput.value;
        if (previewValueSpan) previewValueSpan.textContent = valueInput.value;

        // Update font size
        if (fontSizeInput && fontSizeInput.value) {
            previewElement.style.fontSize = `${fontSizeInput.value}rem`;
        }

        // Show/hide preview element based on content
        if (keyInput.value || valueInput.value) {
            previewElement.style.display = '';
        } else {
            previewElement.style.display = 'none';
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Add input listeners for standard fields to update preview
    document.getElementById('site_name').addEventListener('input', function() { updatePreview('site_name'); });
    document.getElementById('site_name_font_size').addEventListener('input', function() { updatePreview('site_name'); });

    document.getElementById('copyright_text').addEventListener('input', function() { updatePreview('copyright_text'); });
    document.getElementById('copyright_text_font_size').addEventListener('input', function() { updatePreview('copyright_text'); });

    // Optional fields - listeners attached when shown
    // Initial preview update if optional fields are shown on load
    if (document.getElementById('registration_info').style.display !== 'none'){
        updatePreview('registration_info');
    }
    if (document.getElementById('editor_info').style.display !== 'none'){
        updatePreview('editor_info');
    }

    const extraFieldsContainer = document.getElementById('extra-fields-container');
    const addExtraFieldButton = document.getElementById('add-extra-field');

    function updateRemoveButtons() {
        const removeButtons = extraFieldsContainer.querySelectorAll('.remove-extra-field');
        if (extraFieldsContainer.querySelectorAll('.extra-field-row').length === 1) {
            removeButtons.forEach(btn => btn.style.display = 'none');
        } else {
            removeButtons.forEach(btn => btn.style.display = 'inline-block');
        }
    }

    // Attach listeners to all extra fields on load
    extraFieldsContainer.querySelectorAll('.extra-field-row').forEach(attachInputListeners);

    function addExtraField(key = '', text = '', font_size = '0.9') {
        const index = extraFieldsContainer.querySelectorAll('.extra-field-row').length;
        const newFieldRow = document.createElement('div');
        newFieldRow.classList.add('row', 'mb-3', 'extra-field-row');
        newFieldRow.innerHTML = `
            <div class="col">
                <input type="text" class="form-control extra-field-key" name="extra_field_key_${index}" value="${key}" placeholder="Название поля">
            </div>
            <div class="col-md-6">
                <input type="text" class="form-control extra-field-value" name="extra_field_value_${index}" value="${text}" placeholder="Значение">
            </div>
            <div class="col-md-3">
                <input type="number" class="form-control font-size-input extra-field-font-size" name="extra_field_font_size_${index}" value="${font_size}" step="0.1" min="0.1" max="5" placeholder="${font_size}">
            </div>
            <div class="col-auto">
                <button type="button" class="btn btn-danger remove-extra-field"><i class="bi bi-x-circle"></i></button>
            </div>
        `;
        extraFieldsContainer.appendChild(newFieldRow);
        updateRemoveButtons();
        attachInputListeners(newFieldRow);
    }

    addExtraFieldButton.addEventListener('click', function() {
        addExtraField();
    });

    extraFieldsContainer.addEventListener('click', function(event) {
        if (event.target.classList.contains('remove-extra-field') || event.target.closest('.remove-field')) {
            const row = event.target.closest('.extra-field-row');
            if (extraFieldsContainer.querySelectorAll('.extra-field-row').length > 1) {
                row.remove();
                // Reindex fields after removal
                extraFieldsContainer.querySelectorAll('.extra-field-row').forEach((currentRow, idx) => {
                    currentRow.querySelector('.extra-field-key').name = `extra_field_key_${idx}`;
                    currentRow.querySelector('.extra-field-value').name = `extra_field_value_${idx}`;
                    currentRow.querySelector('.extra-field-font-size').name = `extra_field_font_size_${idx}`;
                });
                updateRemoveButtons();
            } else {
                // If only one field remains, clear it instead of removing
                row.querySelector('.extra-field-key').value = '';
                row.querySelector('.extra-field-value').value = '';
                row.querySelector('.extra-field-font-size').value = '0.9';
                updateRemoveButtons();
            }
        }
    });
}); 