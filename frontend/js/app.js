const API_BASE = 'http://localhost:8000';

const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const selectBtn = document.getElementById('selectBtn');
const clearBtn = document.getElementById('clearBtn');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');
const functionsList = document.getElementById('functionsList');

// Обработчики загрузки файла
uploadArea.addEventListener('click', () => fileInput.click());
selectBtn.addEventListener('click', () => fileInput.click());

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('drag-over');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    handleFiles(e.dataTransfer.files);
});

fileInput.addEventListener('change', (e) => {
    handleFiles(e.target.files);
});

clearBtn.addEventListener('click', () => {
    fileInput.value = '';
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';
    functionsList.innerHTML = '';
});

async function handleFiles(files) {
    if (files.length === 0) return;

    const file = files;
    const formData = new FormData();
    formData.append('file', file);

    try {
        updateStatus('Обработка...', 'processing');
        
        const response = await fetch(`${API_BASE}/extract`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Ошибка: ${response.statusText}`);
        }

        const data = await response.json();
        displayResults(data);
        updateStatus('Завершено', 'success');
    } catch (error) {
        showError(error.message);
        updateStatus('Ошибка', 'error');
    }
}

function displayResults(data) {
    document.getElementById('fileName').textContent = data.file;
    document.getElementById('languageTag').textContent = data.language.toUpperCase();
    document.getElementById('functionCount').textContent = `${data.functions.length} функций`;

    functionsList.innerHTML = data.functions.map(fn => `
        <div class="function-item">
            <strong>${fn.name}</strong>(${fn.parameters.join(', ')})
            ${fn.return_type ? `→ ${fn.return_type}` : ''}
            <div style="font-size: 0.8em; color: #666; margin-top: 4px;">Строка ${fn.line_number}</div>
        </div>
    `).join('');

    resultsSection.style.display = 'block';
    errorSection.style.display = 'none';
}

function showError(message) {
    document.getElementById('errorMessage').textContent = message;
    errorSection.style.display = 'block';
    resultsSection.style.display = 'none';
}

function updateStatus(text, status) {
    document.getElementById('statusText').textContent = text;
    const indicator = document.getElementById('statusIndicator');
    indicator.style.color = status === 'success' ? '#10b981' : 
                           status === 'error' ? '#ef4444' : '#3b82f6';
}