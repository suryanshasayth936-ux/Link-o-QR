/**
 * Link'o'QR — Production Frontend Application Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const qrForm = document.getElementById('qr-form');
    const urlInput = document.getElementById('url-input');
    const pasteBtn = document.getElementById('paste-btn');
    const urlFeedback = document.getElementById('url-feedback');
    const generateBtn = document.getElementById('generate-btn');
    const btnText = generateBtn.querySelector('.btn-text');
    const spinner = generateBtn.querySelector('.spinner');

    const toggleOptionsBtn = document.getElementById('toggle-options-btn');
    const optionsPanel = document.getElementById('options-panel');

    const boxSizeSlider = document.getElementById('box-size-slider');
    const boxSizeVal = document.getElementById('box-size-val');
    const borderSlider = document.getElementById('border-slider');
    const borderVal = document.getElementById('border-val');

    const fillColorPicker = document.getElementById('fill-color-picker');
    const fillColorHex = document.getElementById('fill-color-hex');
    const backColorPicker = document.getElementById('back-color-picker');
    const backColorHex = document.getElementById('back-color-hex');
    const formatSelect = document.getElementById('format-select');
    const ecSelect = document.getElementById('ec-select');

    const previewPlaceholder = document.getElementById('preview-placeholder');
    const previewDisplay = document.getElementById('preview-display');
    const qrImage = document.getElementById('qr-image');
    const targetLink = document.getElementById('target-link');
    const outputMeta = document.getElementById('output-meta');
    const actionToolbar = document.getElementById('action-toolbar');

    const downloadBtn = document.getElementById('download-btn');
    const copyBtn = document.getElementById('copy-btn');
    const visitBtn = document.getElementById('visit-btn');
    const toast = document.getElementById('toast');

    let currentQRData = null;

    // Toggle Advanced Customization Accordion
    toggleOptionsBtn.addEventListener('click', () => {
        const isExpanded = toggleOptionsBtn.getAttribute('aria-expanded') === 'true';
        toggleOptionsBtn.setAttribute('aria-expanded', String(!isExpanded));
        optionsPanel.hidden = isExpanded;
    });

    // Sync Slider Numerical Labels
    boxSizeSlider.addEventListener('input', (e) => {
        boxSizeVal.textContent = `${e.target.value}px`;
    });

    borderSlider.addEventListener('input', (e) => {
        borderVal.textContent = `${e.target.value} modules`;
    });

    // Color Pickers & Hex Inputs Sync
    function syncColor(picker, textInput) {
        picker.addEventListener('input', (e) => {
            textInput.value = e.target.value;
        });
        textInput.addEventListener('input', (e) => {
            const val = e.target.value.trim();
            if (/^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$/.test(val)) {
                picker.value = val;
            }
        });
    }

    syncColor(fillColorPicker, fillColorHex);
    syncColor(backColorPicker, backColorHex);

    // Color Presets
    document.querySelectorAll('.preset-btn').forEach((btn) => {
        btn.addEventListener('click', () => {
            const fill = btn.dataset.fill;
            const back = btn.dataset.back;
            fillColorPicker.value = fill;
            fillColorHex.value = fill;
            backColorPicker.value = back;
            backColorHex.value = back;
        });
    });

    // Paste from Clipboard
    pasteBtn.addEventListener('click', async () => {
        try {
            const text = await navigator.clipboard.readText();
            if (text) {
                urlInput.value = text.trim();
                validateUrlInput();
            }
        } catch {
            showToast('Unable to read from clipboard. Please paste manually.', 'error');
        }
    });

    // Real-time URL Input Validation
    function validateUrlInput() {
        const raw = urlInput.value.trim();
        urlFeedback.textContent = '';
        urlFeedback.className = 'feedback-msg';
        urlInput.classList.remove('is-invalid');

        if (!raw) {
            return false;
        }

        try {
            const parsed = new URL(raw);
            if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
                showInputError("URL protocol must be 'http://' or 'https://'");
                return false;
            }
            if (!parsed.hostname || (!parsed.hostname.includes('.') && parsed.hostname !== 'localhost')) {
                showInputError('URL domain host must be valid.');
                return false;
            }
            return true;
        } catch {
            showInputError('Please enter a valid URL (e.g. https://example.com)');
            return false;
        }
    }

    function showInputError(msg) {
        urlInput.classList.add('is-invalid');
        urlFeedback.textContent = msg;
        urlFeedback.classList.add('error');
    }

    urlInput.addEventListener('input', validateUrlInput);

    // Form Submission & QR Code Generation
    qrForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (!validateUrlInput()) {
            if (!urlInput.value.trim()) {
                showInputError('Destination URL is required.');
            }
            urlInput.focus();
            return;
        }

        setLoading(true);

        const payload = {
            url: urlInput.value.trim(),
            box_size: parseInt(boxSizeSlider.value, 10),
            border: parseInt(borderSlider.value, 10),
            error_correction: ecSelect.value,
            fill_color: fillColorHex.value.trim(),
            back_color: backColorHex.value.trim(),
            format: formatSelect.value,
        };

        try {
            const response = await fetch('/api/v1/qr/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            const data = await response.json();

            if (!response.ok) {
                const message = data.message || 'Generation failed. Please check your inputs.';
                throw new Error(message);
            }

            currentQRData = data;
            renderPreview(data);
            showToast('QR Code generated successfully!', 'success');
        } catch (err) {
            showToast(err.message || 'Error communicating with server.', 'error');
        } finally {
            setLoading(false);
        }
    });

    function setLoading(isLoading) {
        generateBtn.disabled = isLoading;
        spinner.hidden = !isLoading;
        btnText.textContent = isLoading ? 'Generating...' : 'Generate QR Code';
    }

    function renderPreview(data) {
        qrImage.src = data.data_uri;
        qrImage.alt = `QR Code pointing directly to ${data.url}`;

        targetLink.href = data.url;
        targetLink.textContent = data.url;

        outputMeta.textContent = `${data.format.toUpperCase()} (${data.box_size * 29}x${data.box_size * 29}px est.)`;
        outputMeta.hidden = false;

        previewPlaceholder.hidden = true;
        previewDisplay.hidden = false;
        actionToolbar.hidden = false;
    }

    // Action: Direct Download
    downloadBtn.addEventListener('click', () => {
        if (!currentQRData) return;

        const downloadUrl = `/api/v1/qr/download?${new URLSearchParams({
            url: currentQRData.url,
            box_size: currentQRData.box_size,
            border: currentQRData.border,
            error_correction: currentQRData.error_correction,
            fill_color: currentQRData.fill_color,
            back_color: currentQRData.back_color,
            format: currentQRData.format,
            filename: 'linkoqr',
        }).toString()}`;

        const anchor = document.createElement('a');
        anchor.href = downloadUrl;
        anchor.setAttribute('download', `linkoqr.${currentQRData.format}`);
        document.body.appendChild(anchor);
        anchor.click();
        document.body.removeChild(anchor);
        showToast(`Downloaded as ${currentQRData.format.toUpperCase()}`, 'success');
    });

    // Action: Copy to Clipboard
    copyBtn.addEventListener('click', async () => {
        if (!currentQRData) return;

        try {
            if (currentQRData.format === 'png') {
                // Fetch blob from data URI and write image to clipboard
                const res = await fetch(currentQRData.data_uri);
                const blob = await res.blob();
                await navigator.clipboard.write([
                    new ClipboardItem({ 'image/png': blob })
                ]);
                showToast('Image copied to clipboard!', 'success');
            } else {
                // For SVG or fallbacks, copy the data URI / SVG markup
                await navigator.clipboard.writeText(currentQRData.data_uri);
                showToast('SVG Data URI copied to clipboard!', 'success');
            }
        } catch {
            // Fallback: copy destination URL if image clipboard write is blocked by browser permissions
            try {
                await navigator.clipboard.writeText(currentQRData.url);
                showToast('Copied URL to clipboard (image permissions restricted).', 'success');
            } catch {
                showToast('Failed to copy to clipboard.', 'error');
            }
        }
    });

    // Action: Visit Link
    visitBtn.addEventListener('click', () => {
        if (!currentQRData) return;
        window.open(currentQRData.url, '_blank', 'noopener,noreferrer');
    });

    // Toast Notification System
    let toastTimeout = null;
    function showToast(message, type = 'success') {
        if (toastTimeout) clearTimeout(toastTimeout);

        toast.textContent = message;
        toast.className = `toast toast-${type}`;
        toast.hidden = false;

        toastTimeout = setTimeout(() => {
            toast.hidden = true;
        }, 4000);
    }
});
