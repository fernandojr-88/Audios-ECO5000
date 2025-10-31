# Processamento em Lote de Áudios

Script para processar automaticamente todos os arquivos de áudio das pastas **Leak-Metal** e **NoLeak-Metal** com filtros Highpass (400 Hz) e Lowpass (1000 Hz).

## 🎯 O que o script faz

1. Lê todos os arquivos `.wav` das pastas:
   - `Audios para Treinamento/Leak-Metal`
   - `Audios para Treinamento/NoLeak-Metal`

2. Aplica os filtros:
   - **Highpass**: 400 Hz (remove frequências abaixo de 400 Hz)
   - **Lowpass**: 1000 Hz (remove frequências acima de 1000 Hz)

3. Cria novas pastas com os arquivos processados:
   - `Audios para Treinamento/Leak-Metal-Filtred`
   - `Audios para Treinamento/NoLeak-Metal-Filtred`

4. Salva os arquivos com sufixo `_filted.wav`
   - Exemplo: `003_05593-20180927.wav` → `003_05593-20180927_filted.wav`

## 🚀 Como usar

### Opção 1: Executar diretamente (Python)

```bash
python batch_process_audio.py
```

### Opção 2: Usar o script batch (Windows)

```bash
batch_process.bat
```

## ⚙️ Configurações

Você pode modificar as frequências dos filtros editando o arquivo `batch_process_audio.py`:

```python
# Linha 147-148
HIGHPASS_FREQ = 400  # Hz
LOWPASS_FREQ = 1000  # Hz
```

## 📊 Resultado

- ✅ 15 arquivos processados de Leak-Metal
- ✅ 15 arquivos processados de NoLeak-Metal
- ✅ Total: 30 arquivos processados

Todos os arquivos processados estão nas pastas:
- `Leak-Metal-Filtred/`
- `NoLeak-Metal-Filtred/`

## 📝 Notas

- O script preserva a taxa de amostragem original dos áudios
- Suporta áudio mono e estéreo
- Os filtros são aplicados usando Butterworth de ordem 4 (bidirecional, sem deslocamento de fase)
- O script mostra progresso em tempo real com barra de progresso
- Erros são reportados individualmente sem interromper o processamento

## 🔧 Requisitos

As mesmas dependências do projeto principal (ver `requirements.txt`):
- librosa
- soundfile
- scipy
- numpy
- tqdm

