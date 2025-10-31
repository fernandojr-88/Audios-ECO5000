from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import numpy as np
import soundfile as sf
from scipy import signal
import librosa
import io
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Configurações
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
ALLOWED_EXTENSIONS = {'wav'}

# Criar pastas se não existirem
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def apply_filters(audio_data, sample_rate, highpass_freq=None, lowpass_freq=None):
    """
    Aplica filtros highpass e/ou lowpass no áudio
    
    Args:
        audio_data: array numpy com os dados do áudio
        sample_rate: taxa de amostragem
        highpass_freq: frequência de corte para highpass (Hz). None para desabilitar
        lowpass_freq: frequência de corte para lowpass (Hz). None para desabilitar
    
    Returns:
        audio_filtrado: array numpy com o áudio filtrado
    """
    filtered_audio = audio_data.copy()
    
    # Nyquist frequency
    nyquist = sample_rate / 2.0
    
    # Aplicar filtro highpass
    if highpass_freq is not None and highpass_freq > 0:
        # Normalizar frequência
        highpass_norm = highpass_freq / nyquist
        if highpass_norm < 1.0:
            # Criar filtro Butterworth highpass
            b, a = signal.butter(4, highpass_norm, btype='high')
            if len(filtered_audio.shape) > 1:
                # Áudio estéreo
                filtered_audio = signal.filtfilt(b, a, filtered_audio, axis=0)
            else:
                # Áudio mono
                filtered_audio = signal.filtfilt(b, a, filtered_audio)
    
    # Aplicar filtro lowpass
    if lowpass_freq is not None and lowpass_freq > 0:
        # Normalizar frequência
        lowpass_norm = lowpass_freq / nyquist
        if lowpass_norm < 1.0:
            # Criar filtro Butterworth lowpass
            b, a = signal.butter(4, lowpass_norm, btype='low')
            if len(filtered_audio.shape) > 1:
                # Áudio estéreo
                filtered_audio = signal.filtfilt(b, a, filtered_audio, axis=0)
            else:
                # Áudio mono
                filtered_audio = signal.filtfilt(b, a, filtered_audio)
    
    return filtered_audio


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Endpoint para upload de arquivo de áudio"""
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nome de arquivo vazio'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Carregar áudio para obter informações
        try:
            audio_data, sample_rate = librosa.load(filepath, sr=None)
            duration = len(audio_data) / sample_rate
            
            return jsonify({
                'success': True,
                'filename': filename,
                'sample_rate': int(sample_rate),
                'duration': float(duration),
                'channels': 1 if len(audio_data.shape) == 1 else audio_data.shape[1],
                'samples': int(len(audio_data))
            })
        except Exception as e:
            return jsonify({'error': f'Erro ao processar áudio: {str(e)}'}), 500
    
    return jsonify({'error': 'Formato de arquivo não permitido'}), 400


@app.route('/api/analyze', methods=['POST'])
def analyze_audio():
    """Endpoint para obter dados do áudio original (para gráficos)"""
    data = request.json
    filename = data.get('filename')
    
    if not filename:
        return jsonify({'error': 'Nome de arquivo não fornecido'}), 400
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'Arquivo não encontrado'}), 404
    
    try:
        # Carregar áudio
        audio_data, sample_rate = librosa.load(filepath, sr=None)
        
        # Converter para mono se necessário
        if len(audio_data.shape) > 1:
            audio_data = np.mean(audio_data, axis=1)
        
        # Limitar número de amostras para o gráfico (downsample para performance)
        max_samples = 50000
        if len(audio_data) > max_samples:
            step = len(audio_data) // max_samples
            audio_data_display = audio_data[::step]
            time_axis = np.arange(len(audio_data_display)) * step / sample_rate
        else:
            audio_data_display = audio_data
            time_axis = np.arange(len(audio_data)) / sample_rate
        
        # Calcular FFT para espectro de frequência
        fft = np.fft.rfft(audio_data)
        fft_magnitude = np.abs(fft)
        freq_axis = np.fft.rfftfreq(len(audio_data), 1/sample_rate)
        
        # Limitar frequências para visualização (até 20000 Hz)
        max_freq_idx = np.where(freq_axis <= 20000)[0]
        if len(max_freq_idx) > 0:
            freq_axis = freq_axis[:max_freq_idx[-1]+1]
            fft_magnitude = fft_magnitude[:max_freq_idx[-1]+1]
        
        # Downsample FFT para visualização
        if len(freq_axis) > 10000:
            step = len(freq_axis) // 10000
            freq_axis = freq_axis[::step]
            fft_magnitude = fft_magnitude[::step]
        
        return jsonify({
            'success': True,
            'time_data': {
                'time': time_axis.tolist(),
                'amplitude': audio_data_display.tolist()
            },
            'freq_data': {
                'frequency': freq_axis.tolist(),
                'magnitude': fft_magnitude.tolist()
            },
            'sample_rate': int(sample_rate)
        })
    except Exception as e:
        return jsonify({'error': f'Erro ao analisar áudio: {str(e)}'}), 500


@app.route('/api/process', methods=['POST'])
def process_audio():
    """Endpoint para processar áudio com filtros"""
    data = request.json
    filename = data.get('filename')
    highpass_freq = data.get('highpass_freq')
    lowpass_freq = data.get('lowpass_freq')
    
    if not filename:
        return jsonify({'error': 'Nome de arquivo não fornecido'}), 400
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'Arquivo não encontrado'}), 404
    
    try:
        # Carregar áudio original
        audio_data, sample_rate = librosa.load(filepath, sr=None)
        
        # Aplicar filtros
        filtered_audio = apply_filters(audio_data, sample_rate, highpass_freq, lowpass_freq)
        
        # Converter para mono se necessário para análise
        if len(filtered_audio.shape) > 1:
            filtered_audio_mono = np.mean(filtered_audio, axis=1)
            original_mono = np.mean(audio_data, axis=1)
        else:
            filtered_audio_mono = filtered_audio
            original_mono = audio_data
        
        # Preparar dados para gráfico de tempo (downsample)
        max_samples = 50000
        if len(original_mono) > max_samples:
            step = len(original_mono) // max_samples
            original_display = original_mono[::step]
            filtered_display = filtered_audio_mono[::step]
            time_axis = np.arange(len(original_display)) * step / sample_rate
        else:
            original_display = original_mono
            filtered_display = filtered_audio_mono
            time_axis = np.arange(len(original_mono)) / sample_rate
        
        # Calcular FFT para espectro de frequência original
        fft_original = np.fft.rfft(original_mono)
        fft_mag_original = np.abs(fft_original)
        freq_axis = np.fft.rfftfreq(len(original_mono), 1/sample_rate)
        
        # Calcular FFT para espectro de frequência filtrado
        fft_filtered = np.fft.rfft(filtered_audio_mono)
        fft_mag_filtered = np.abs(fft_filtered)
        
        # Limitar frequências para visualização
        max_freq_idx = np.where(freq_axis <= 20000)[0]
        if len(max_freq_idx) > 0:
            freq_axis = freq_axis[:max_freq_idx[-1]+1]
            fft_mag_original = fft_mag_original[:max_freq_idx[-1]+1]
            fft_mag_filtered = fft_mag_filtered[:max_freq_idx[-1]+1]
        
        # Downsample FFT
        if len(freq_axis) > 10000:
            step = len(freq_axis) // 10000
            freq_axis = freq_axis[::step]
            fft_mag_original = fft_mag_original[::step]
            fft_mag_filtered = fft_mag_filtered[::step]
        
        # Salvar áudio processado
        output_filename = f"processed_{filename}"
        output_path = os.path.join(app.config['PROCESSED_FOLDER'], output_filename)
        
        # Garantir que o áudio está no formato correto para soundfile
        if len(filtered_audio.shape) > 1:
            # Estéreo
            sf.write(output_path, filtered_audio, sample_rate)
        else:
            # Mono - adicionar dimensão para soundfile
            sf.write(output_path, filtered_audio, sample_rate)
        
        return jsonify({
            'success': True,
            'processed_filename': output_filename,
            'time_data': {
                'time': time_axis.tolist(),
                'original': original_display.tolist(),
                'filtered': filtered_display.tolist()
            },
            'freq_data': {
                'frequency': freq_axis.tolist(),
                'original': fft_mag_original.tolist(),
                'filtered': fft_mag_filtered.tolist()
            },
            'sample_rate': int(sample_rate)
        })
    except Exception as e:
        return jsonify({'error': f'Erro ao processar áudio: {str(e)}'}), 500


@app.route('/api/audio/<filename>')
def serve_audio(filename):
    """Endpoint para servir áudio para reprodução (sem forçar download)"""
    # Verificar se é arquivo processado
    processed_path = os.path.join(app.config['PROCESSED_FOLDER'], filename)
    if os.path.exists(processed_path):
        return send_file(processed_path, mimetype='audio/wav')
    
    # Verificar se é arquivo original
    original_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(original_path):
        return send_file(original_path, mimetype='audio/wav')
    
    return jsonify({'error': 'Arquivo não encontrado'}), 404


@app.route('/api/download/<filename>')
def download_file(filename):
    """Endpoint para download do áudio (processado ou original)"""
    # Verificar se é arquivo processado
    processed_path = os.path.join(app.config['PROCESSED_FOLDER'], filename)
    if os.path.exists(processed_path):
        return send_file(processed_path, as_attachment=True, download_name=filename.replace('processed_', ''))
    
    # Verificar se é arquivo original
    original_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(original_path):
        return send_file(original_path, as_attachment=True, download_name=filename)
    
    return jsonify({'error': 'Arquivo não encontrado'}), 404


if __name__ == '__main__':
    app.run(debug=True, port=5000)

