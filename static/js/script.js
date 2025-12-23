document.addEventListener('DOMContentLoaded', () => {

    // --- Navigation (Tab Switching) ---
    const navLinks = document.querySelectorAll('.nav-links li');
    const tabContents = document.querySelectorAll('.tab-content');

    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            // Remove active class from all
            navLinks.forEach(l => l.classList.remove('active'));
            tabContents.forEach(t => t.classList.remove('active'));

            // Add active class to clicked
            link.classList.add('active');
            const tabId = link.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });

    // --- File Handling & Drag n Drop ---
    setupFileHandler('split', false);
    setupFileHandler('merge', true);
    setupFileHandler('reorder', false);
    setupFileHandler('pdf2img', false);
    setupFileHandler('img2pdf', true); // accepts multiple images
    setupFileHandler('encrypt', false);

    // --- Specific UI Logic ---

    // Split Mode Toggle
    const splitRadios = document.querySelectorAll('input[name="mode"]');
    const splitRangeGroup = document.getElementById('split-range-group');
    splitRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            splitRangeGroup.style.display = e.target.value === 'range' ? 'flex' : 'none';
        });
    });
});

// Store selected files
const fileStorage = {};

function setupFileHandler(idSuffix, multiple) {
    const dropArea = document.getElementById(`drop-area-${idSuffix}`);
    const fileInput = document.getElementById(`file-${idSuffix}`);
    const infoArea = document.getElementById(multiple ? `file-list-${idSuffix}` : `file-info-${idSuffix}`);

    // Click to open file dialog handled by transparent input
    // dropArea.addEventListener('click', () => fileInput.click());

    // File Input Change
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            handleFiles(e.target.files, idSuffix, multiple, infoArea);
        });
    }

    if (dropArea) {
        // Drag & Drop events
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        dropArea.addEventListener('dragover', () => dropArea.classList.add('dragover'));
        dropArea.addEventListener('dragleave', () => dropArea.classList.remove('dragover'));
        dropArea.addEventListener('drop', (e) => {
            dropArea.classList.remove('dragover');

            // Assign dropped files to the actual input for Form Submit
            const dataTransfer = new DataTransfer();
            Array.from(e.dataTransfer.files).forEach(file => dataTransfer.items.add(file));
            fileInput.files = dataTransfer.files;

            handleFiles(e.dataTransfer.files, idSuffix, multiple, infoArea);
        });
    }
}

function handleFiles(files, idSuffix, multiple, infoArea) {
    if (!files || !files.length) return;

    if (multiple) {
        // For multiple files (Merge, Img2PDF)
        fileStorage[idSuffix] = files; // store FileList
        infoArea.innerHTML = '';
        Array.from(files).forEach(f => {
            const div = document.createElement('div');
            div.textContent = `📄 ${f.name} (${formatBytes(f.size)})`;
            infoArea.appendChild(div);
        });
    } else {
        // For single file
        fileStorage[idSuffix] = files[0];
        infoArea.innerHTML = `<div>Selected: <strong>${files[0].name}</strong> (${formatBytes(files[0].size)})</div>`;
    }
}

// --- Form Validation ---
// Replaces the previous fetch-based handlers. Returns true to allow submit, false to stop.
function validateForm(idSuffix) {
    const fileInput = document.getElementById(`file-${idSuffix}`);

    // Check if file is selected
    if (!fileInput.files || fileInput.files.length === 0) {
        alert('ファイルを選択してください');
        return false;
    }

    // Specific validations
    if (idSuffix === 'merge' || idSuffix === 'img2pdf') {
        if (fileInput.files.length < 2) {
            alert('2つ以上のファイルを選択してください');
            return false;
        }
    }

    if (idSuffix === 'split') {
        const mode = document.querySelector('input[name="mode"]:checked').value;
        if (mode === 'range') {
            const range = document.getElementById('split-range').value;
            if (!range) {
                alert('ページ範囲を入力してください');
                return false;
            }
        }
    }

    if (idSuffix === 'reorder') {
        const order = document.getElementById('reorder-input').value;
        if (!order) {
            alert('順序を入力してください');
            return false;
        }
    }

    if (idSuffix === 'encrypt') {
        const pass = document.getElementById('encrypt-password').value;
        if (!pass) {
            alert('パスワードを入力してください');
            return false;
        }
    }

    // Show simplified loading indication (optional, as browser will handle download)
    // alert('処理を開始します。ダウンロードが開始されるまでお待ちください。');
    return true;
}

// Utils
function formatBytes(bytes, decimals = 2) {
    if (!+bytes) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
}
