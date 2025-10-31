"""
Script para processar em lote os arquivos de áudio das pastas Leak-NonMetal e NoLeak-NonMetal
Aplica filtros: Highpass 50 Hz e Lowpass 460 Hz
Gera novas pastas com os arquivos filtrados
"""

import os
import numpy as np
import soundfile as sf
from scipy import signal
import librosa
from tqdm import tqdm


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


def process_audio_file(input_path, output_path, highpass_freq=40, lowpass_freq=460):
    """
    Processa um único arquivo de áudio
    
    Args:
        input_path: caminho do arquivo de entrada
        output_path: caminho do arquivo de saída
        highpass_freq: frequência de corte do highpass (Hz)
        lowpass_freq: frequência de corte do lowpass (Hz)
    
    Returns:
        True se sucesso, False caso contrário
    """
    try:
        # Carregar áudio
        audio_data, sample_rate = librosa.load(input_path, sr=None)
        
        # Aplicar filtros
        filtered_audio = apply_filters(audio_data, sample_rate, highpass_freq, lowpass_freq)
        
        # Salvar arquivo processado
        sf.write(output_path, filtered_audio, sample_rate)
        
        return True
    except Exception as e:
        print(f"  Erro ao processar {os.path.basename(input_path)}: {str(e)}")
        return False


def process_folder(input_folder, output_folder, highpass_freq=40, lowpass_freq=460):
    """
    Processa todos os arquivos .wav de uma pasta
    
    Args:
        input_folder: pasta de entrada
        output_folder: pasta de saída
        highpass_freq: frequência de corte do highpass (Hz)
        lowpass_freq: frequência de corte do lowpass (Hz)
    
    Returns:
        tupla (sucessos, falhas)
    """
    # Criar pasta de saída se não existir
    os.makedirs(output_folder, exist_ok=True)
    
    # Listar arquivos .wav
    audio_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.wav')]
    
    if not audio_files:
        print(f"  Nenhum arquivo .wav encontrado em {input_folder}")
        return 0, 0
    
    success_count = 0
    fail_count = 0
    
    print(f"  Processando {len(audio_files)} arquivos...")
    
    # Processar cada arquivo
    for audio_file in tqdm(audio_files, desc=f"  {os.path.basename(input_folder)}"):
        input_path = os.path.join(input_folder, audio_file)
        
        # Criar nome do arquivo de saída com sufixo '_filted'
        name, ext = os.path.splitext(audio_file)
        output_filename = f"{name}_filted{ext}"
        output_path = os.path.join(output_folder, output_filename)
        
        # Processar arquivo
        if process_audio_file(input_path, output_path, highpass_freq, lowpass_freq):
            success_count += 1
        else:
            fail_count += 1
    
    return success_count, fail_count


def main():
    """
    Função principal: processa as pastas Leak-NonMetal e NoLeak-NonMetal
    """
    # Configurações
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))
    AUDIO_DIR = os.path.join(BASE_PATH, 'Audios para Treinamento')
    
    # Filtros configurados
    HIGHPASS_FREQ = 50  # Hz
    LOWPASS_FREQ = 460  # Hz
    
    print("=" * 60)
    print("Processador em Lote de Áudios - ECO5000")
    print("=" * 60)
    print(f"\nConfigurações:")
    print(f"  Filtro Highpass: {HIGHPASS_FREQ} Hz")
    print(f"  Filtro Lowpass: {LOWPASS_FREQ} Hz")
    print(f"\nPasta base: {AUDIO_DIR}\n")
    
    # Verificar se a pasta existe
    if not os.path.exists(AUDIO_DIR):
        print(f"ERRO: Pasta '{AUDIO_DIR}' não encontrada!")
        print("Certifique-se de que o script está na pasta correta.")
        return
    
    # Pastas de entrada e saída
    folders_to_process = [
        {
            'input': os.path.join(AUDIO_DIR, 'Leak-NonMetal'),
            'output': os.path.join(AUDIO_DIR, 'Leak-NonMetal-Filtred')
        },
        {
            'input': os.path.join(AUDIO_DIR, 'NoLeak-NonMetal'),
            'output': os.path.join(AUDIO_DIR, 'NoLeak-NonMetal-Filtred')
        }
    ]
    
    total_success = 0
    total_fail = 0
    
    # Processar cada pasta
    for folder_info in folders_to_process:
        input_folder = folder_info['input']
        output_folder = folder_info['output']
        
        print(f"\n{'=' * 60}")
        print(f"Processando: {os.path.basename(input_folder)}")
        print(f"{'=' * 60}")
        
        # Verificar se a pasta de entrada existe
        if not os.path.exists(input_folder):
            print(f"  AVISO: Pasta '{input_folder}' não encontrada. Pulando...")
            continue
        
        # Processar pasta
        success, fail = process_folder(
            input_folder, 
            output_folder, 
            HIGHPASS_FREQ, 
            LOWPASS_FREQ
        )
        
        total_success += success
        total_fail += fail
        
        print(f"  [OK] Sucessos: {success}")
        if fail > 0:
            print(f"  [ERRO] Falhas: {fail}")
        print(f"  Pasta de saida: {output_folder}")
    
    # Resumo final
    print(f"\n{'=' * 60}")
    print("RESUMO FINAL")
    print(f"{'=' * 60}")
    print(f"Total de arquivos processados com sucesso: {total_success}")
    if total_fail > 0:
        print(f"Total de falhas: {total_fail}")
    print(f"\nProcessamento concluído!")
    print("=" * 60)


if __name__ == '__main__':
    main()

