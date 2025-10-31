// Variáveis globais
let currentFileName = null;
let audioContext = null;
let timeChart = null;
let freqChart = null;
let originalAudioBuffer = null;
let filteredAudioBuffer = null;
let audioSource = null;
let currentAudio = null;

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Upload area
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    
    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('drop', handleDrop);
    fileInput.addEventListener('change', handleFileSelect);
    
    // Sliders
    const highpassSlider = document.getElementById('highpassSlider');
    const lowpassSlider = document.getElementById('lowpassSlider');
    
    highpassSlider.addEventListener('input', (e) => {
        updateSliderValue('highpassValue', e.target.value);
        updateSliderMax('highpass', 'lowpass');
    });
    
    lowpassSlider.addEventListener('input', (e) => {
        updateSliderValue('lowpassValue', e.target.value);
        updateSliderMax('lowpass', 'highpass');
    });
    
    // Toggle buttons
    document.getElementById('highpassToggle').addEventListener('click', toggleFilter);
    document.getElementById('lowpassToggle').addEventListener('click', toggleFilter);
    
    // Process button
    document.getElementById('processBtn').addEventListener('click', processAudio);
    
    // Play buttons
    document.getElementById('playOriginalBtn').addEventListener('click', () => playAudio('original'));
    document.getElementById('playFilteredBtn').addEventListener('click', () => playAudio('filtered'));
    document.getElementById('stopBtn').addEventListener('click', stopAudio);
    
    // Download button
    document.getElementById('downloadBtn').addEventListener('click', downloadAudio);
    
    // Inicializar gráficos
    initializeCharts();
}

// Drag and Drop
function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.style.background = '#eff0ff';
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.style.background = '#f8f9ff';
    
    const files = e.dataTransfer.files;
    if (files.length > 0 && files[0].name.endsWith('.wav')) {
        handleFileUpload(files[0]);
    }
}

function handleFileSelect(e) {
    if (e.target.files.length > 0) {
        handleFileUpload(e.target.files[0]);
    }
}

// Upload de arquivo
async function handleFileUpload(file) {
    showLoading(true);
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentFileName = data.filename;
            displayAudioInfo(data);
            await loadAudioAnalysis();
            document.getElementById('processBtn').disabled = false;
        } else {
            alert('Erro ao carregar arquivo: ' + data.error);
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao fazer upload do arquivo');
    } finally {
        showLoading(false);
    }
}

// Exibir informações do áudio
function displayAudioInfo(data) {
    document.getElementById('audioInfo').style.display = 'block';
    document.getElementById('fileName').textContent = data.filename;
    document.getElementById('sampleRate').textContent = data.sample_rate.toLocaleString();
    document.getElementById('duration').textContent = data.duration.toFixed(2);
    document.getElementById('fileInfo').textContent = `Arquivo carregado: ${data.filename}`;
    
    // Atualizar max dos sliders baseado na sample rate
    const maxFreq = Math.min(data.sample_rate / 2, 20000);
    document.getElementById('highpassSlider').max = maxFreq;
    document.getElementById('lowpassSlider').max = maxFreq;
}

// Carregar análise do áudio original
async function loadAudioAnalysis() {
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ filename: currentFileName })
        });
        
        const data = await response.json();
        
        if (data.success) {
            updateTimeChart(data.time_data, null);
            updateFreqChart(data.freq_data, null);
        }
    } catch (error) {
        console.error('Erro ao analisar áudio:', error);
    }
}

// Processar áudio
async function processAudio() {
    if (!currentFileName) {
        alert('Por favor, carregue um arquivo primeiro');
        return;
    }
    
    showLoading(true);
    
    const highpassFreq = document.getElementById('highpassToggle').classList.contains('active') 
        ? parseFloat(document.getElementById('highpassSlider').value) 
        : null;
    
    const lowpassFreq = document.getElementById('lowpassToggle').classList.contains('active')
        ? parseFloat(document.getElementById('lowpassSlider').value)
        : null;
    
    if (highpassFreq === null && lowpassFreq === null) {
        alert('Por favor, habilite pelo menos um filtro');
        showLoading(false);
        return;
    }
    
    try {
        const response = await fetch('/api/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                filename: currentFileName,
                highpass_freq: highpassFreq,
                lowpass_freq: lowpassFreq
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            updateTimeChart(data.time_data, 'both');
            updateFreqChart(data.freq_data, 'both');
            
            // Habilitar botões de preview e download
            document.getElementById('playFilteredBtn').disabled = false;
            document.getElementById('downloadBtn').disabled = false;
            
            // Salvar nome do arquivo processado
            window.processedFileName = data.processed_filename;
        } else {
            alert('Erro ao processar áudio: ' + data.error);
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao processar áudio');
    } finally {
        showLoading(false);
    }
}

// Inicializar gráficos
function initializeCharts() {
    const timeCtx = document.getElementById('timeChart').getContext('2d');
    const freqCtx = document.getElementById('freqChart').getContext('2d');
    
    timeChart = new Chart(timeCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: []
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                title: {
                    display: false
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Tempo (s)'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Amplitude'
                    }
                }
            }
        }
    });
    
    freqChart = new Chart(freqCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: []
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                title: {
                    display: false
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Frequência (Hz)'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Magnitude',
                        type: 'logarithmic'
                    }
                }
            }
        }
    });
}

// Atualizar gráfico de tempo
function updateTimeChart(timeData, mode) {
    const datasets = [];
    
    if (mode === null || mode === 'both') {
        datasets.push({
            label: 'Original',
            data: timeData.time.map((t, i) => ({ x: t, y: timeData.original[i] })),
            borderColor: 'rgb(102, 126, 234)',
            backgroundColor: 'rgba(102, 126, 234, 0.1)',
            borderWidth: 1.5,
            pointRadius: 0
        });
    }
    
    if (mode === 'both' && timeData.filtered) {
        datasets.push({
            label: 'Filtrado',
            data: timeData.time.map((t, i) => ({ x: t, y: timeData.filtered[i] })),
            borderColor: 'rgb(76, 175, 80)',
            backgroundColor: 'rgba(76, 175, 80, 0.1)',
            borderWidth: 1.5,
            pointRadius: 0
        });
    }
    
    timeChart.data.labels = timeData.time;
    timeChart.data.datasets = datasets;
    timeChart.update();
}

// Atualizar gráfico de frequência
function updateFreqChart(freqData, mode) {
    const datasets = [];
    
    if (mode === null || mode === 'both') {
        datasets.push({
            label: 'Original',
            data: freqData.frequency.map((f, i) => ({ x: f, y: freqData.original[i] })),
            borderColor: 'rgb(102, 126, 234)',
            backgroundColor: 'rgba(102, 126, 234, 0.1)',
            borderWidth: 1.5,
            pointRadius: 0
        });
    }
    
    if (mode === 'both' && freqData.filtered) {
        datasets.push({
            label: 'Filtrado',
            data: freqData.frequency.map((f, i) => ({ x: f, y: freqData.filtered[i] })),
            borderColor: 'rgb(76, 175, 80)',
            backgroundColor: 'rgba(76, 175, 80, 0.1)',
            borderWidth: 1.5,
            pointRadius: 0
        });
    }
    
    freqChart.data.labels = freqData.frequency;
    freqChart.data.datasets = datasets;
    freqChart.update();
}

// Atualizar valor do slider
function updateSliderValue(elementId, value) {
    document.getElementById(elementId).textContent = parseInt(value).toLocaleString();
}

// Atualizar max do slider baseado no outro filtro
function updateSliderMax(currentFilter, otherFilter) {
    const currentSlider = document.getElementById(currentFilter + 'Slider');
    const otherSlider = document.getElementById(otherFilter + 'Slider');
    const currentToggle = document.getElementById(currentFilter + 'Toggle');
    const otherToggle = document.getElementById(otherFilter + 'Toggle');
    
    if (currentToggle.classList.contains('active') && otherToggle.classList.contains('active')) {
        const currentValue = parseFloat(currentSlider.value);
        const otherValue = parseFloat(otherSlider.value);
        
        if (currentFilter === 'highpass') {
            if (currentValue >= otherValue) {
                currentSlider.value = Math.max(0, otherValue - 10);
                updateSliderValue('highpassValue', currentSlider.value);
            }
        } else {
            if (currentValue <= otherValue) {
                currentSlider.value = Math.min(parseFloat(currentSlider.max), otherValue + 10);
                updateSliderValue('lowpassValue', currentSlider.value);
            }
        }
    }
}

// Toggle filtro
function toggleFilter(e) {
    const button = e.target;
    const filter = button.dataset.filter;
    const slider = document.getElementById(filter + 'Slider');
    
    if (button.classList.contains('active')) {
        button.classList.remove('active');
        button.textContent = 'Desabilitado';
        slider.disabled = true;
        slider.value = 0;
        updateSliderValue(filter + 'Value', 0);
    } else {
        button.classList.add('active');
        button.textContent = 'Habilitado';
        slider.disabled = false;
    }
}

// Reproduzir áudio
async function playAudio(type) {
    stopAudio();
    
    let audioUrl;
    if (type === 'original') {
        audioUrl = `/api/audio/${currentFileName}`;
    } else {
        if (!window.processedFileName) {
            alert('Por favor, processe o áudio primeiro');
            return;
        }
        audioUrl = `/api/audio/${window.processedFileName}`;
    }
    
    const audioPlayer = document.getElementById('audioPlayer');
    audioPlayer.src = audioUrl;
    audioPlayer.style.display = 'block';
    audioPlayer.play();
    
    document.getElementById('playOriginalBtn').disabled = true;
    document.getElementById('playFilteredBtn').disabled = true;
    document.getElementById('stopBtn').disabled = false;
    
    audioPlayer.onended = () => {
        stopAudio();
    };
}

// Parar áudio
function stopAudio() {
    const audioPlayer = document.getElementById('audioPlayer');
    audioPlayer.pause();
    audioPlayer.src = '';
    audioPlayer.style.display = 'none';
    
    document.getElementById('playOriginalBtn').disabled = false;
    document.getElementById('playFilteredBtn').disabled = !window.processedFileName;
    document.getElementById('stopBtn').disabled = true;
}

// Download áudio processado
function downloadAudio() {
    if (!window.processedFileName) {
        alert('Por favor, processe o áudio primeiro');
        return;
    }
    
    window.location.href = `/api/download/${window.processedFileName}`;
}

// Mostrar/ocultar loading
function showLoading(show) {
    document.getElementById('loadingOverlay').style.display = show ? 'flex' : 'none';
}

