# Audio Leak Detection Model

Este projeto treina um modelo de classificação de áudio para detectar vazamentos em sistemas, categorizando os áudios em:
- **Leak-Metal**: Vazamento em material metálico
- **Leak-NonMetal**: Vazamento em material não-metálico
- **NoLeak-Metal**: Sem vazamento em material metálico
- **NoLeak-NonMetal**: Sem vazamento em material não-metálico

## Estrutura do Projeto

```
ECO5000 - Modelos IA/
├── Audios para Treinamento/
│   ├── Leak-Metal/
│   ├── Leak-NonMetal/
│   ├── NoLeak-Metal/
│   └── NoLeak-NonMetal/
├── requirements.txt
├── train_model_colab.ipynb
└── README.md
```

## Configuração no Google Colab

### Opção 1: Upload dos arquivos diretamente no Colab

1. Abra o Google Colab: https://colab.research.google.com/
2. Faça upload do notebook `train_model_colab.ipynb`
3. Faça upload do arquivo `requirements.txt`
4. Crie uma pasta chamada `Audios para Treinamento` e faça upload de todos os arquivos de áudio
5. Execute as células do notebook

### Opção 2: Usando Google Drive

1. Faça upload de todo o projeto para o Google Drive
2. Abra o Google Colab
3. Monte o Google Drive:
   ```python
   from google.colab import drive
   drive.mount('/content/drive')
   ```
4. Ajuste o `BASE_PATH` no notebook para:
   ```python
   BASE_PATH = '/content/drive/MyDrive/ECO5000 - Modelos IA'
   ```
5. Execute as células do notebook

### Opção 3: Usando GitHub

1. Faça commit do projeto no GitHub
2. No Colab, clone o repositório:
   ```python
   !git clone https://github.com/seu-usuario/seu-repositorio.git
   ```
3. Ajuste o `BASE_PATH` no notebook conforme necessário

## Dependências

Todas as dependências estão listadas no arquivo `requirements.txt`. O notebook instala automaticamente ao executar a primeira célula.

### Principais bibliotecas:
- **librosa**: Processamento de áudio e extração de features
- **tensorflow**: Framework de deep learning
- **scikit-learn**: Utilidades de machine learning
- **numpy, pandas**: Manipulação de dados
- **matplotlib, seaborn**: Visualização

## Características do Modelo

O modelo utiliza:
- **Features extraídas**: MFCCs, Mel Spectrogram e Chroma
- **Arquitetura**: Rede Neural com camadas densas (Dense)
- **Regularização**: Dropout para prevenir overfitting
- **Callbacks**: Early Stopping, Model Checkpoint e Reduce Learning Rate

## Uso

1. Execute todas as células do notebook `train_model_colab.ipynb` em ordem
2. O modelo será treinado e avaliado automaticamente
3. O modelo treinado será salvo como `audio_leak_classifier.h5`

## Notas

- O modelo divide os dados em: 64% treino, 16% validação, 20% teste
- As features são normalizadas usando StandardScaler
- O treinamento usa early stopping para evitar overfitting
- O melhor modelo durante o treinamento é automaticamente salvo

## Customização

Você pode ajustar os seguintes parâmetros no notebook:
- `n_mfcc`, `n_mels`: Número de features MFCC e Mel
- Arquitetura da rede neural (camadas, neurônios, dropout)
- Número de épocas e batch size
- Taxa de divisão dos dados (train/val/test)

