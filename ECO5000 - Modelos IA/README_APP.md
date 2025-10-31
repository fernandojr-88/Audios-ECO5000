# 🎵 Processador de Áudio ECO5000 - Aplicação Web

Aplicação web interativa para processar arquivos de áudio WAV com filtros Highpass e Lowpass, visualizar gráficos no domínio do tempo e frequência, e exportar o áudio processado.

## 📋 Funcionalidades

- ✅ **Upload de arquivos WAV** - Interface drag-and-drop para carregar áudios
- ✅ **Filtros configuráveis** - Highpass e Lowpass com controles deslizantes
- ✅ **Visualização em tempo real** - Gráficos de forma de onda e espectro de frequência (FFT)
- ✅ **Comparação antes/depois** - Visualize o áudio original e filtrado simultaneamente
- ✅ **Pré-visualização de áudio** - Ouça o áudio original e filtrado antes de baixar
- ✅ **Download do áudio processado** - Exporte o áudio filtrado como arquivo WAV

## 🚀 Instalação

### 1. Instalar Dependências

Certifique-se de ter Python 3.8+ instalado. Depois, instale as dependências:

```bash
pip install -r requirements.txt
```

### 2. Executar a Aplicação

Execute o arquivo `app.py`:

```bash
python app.py
```

Ou no Windows:

```bash
python app.py
```

A aplicação estará disponível em: **http://localhost:5000**

## 📖 Como Usar

### Passo 1: Carregar Áudio

1. Clique na área de upload ou arraste um arquivo `.wav` para a área indicada
2. Aguarde o carregamento do arquivo
3. As informações do áudio (taxa de amostragem, duração) serão exibidas

### Passo 2: Configurar Filtros

1. **Filtro Highpass**: Remove frequências abaixo do valor selecionado
   - Clique em "Desabilitado" para habilitar
   - Ajuste o slider para definir a frequência de corte (Hz)
   - Útil para remover ruído de baixa frequência

2. **Filtro Lowpass**: Remove frequências acima do valor selecionado
   - Clique em "Desabilitado" para habilitar
   - Ajuste o slider para definir a frequência de corte (Hz)
   - Útil para remover ruído de alta frequência

**Nota**: Você pode usar ambos os filtros simultaneamente para criar um filtro passa-banda.

### Passo 3: Processar Áudio

1. Clique no botão "Processar Áudio"
2. Aguarde o processamento (um indicador de carregamento será exibido)
3. Os gráficos serão atualizados mostrando o áudio original e filtrado

### Passo 4: Visualizar Resultados

- **Gráfico de Forma de Onda**: Mostra a amplitude do sinal ao longo do tempo
- **Gráfico de Espectro de Frequência**: Mostra a distribuição de frequências (FFT)

### Passo 5: Pré-visualizar e Baixar

1. Use os botões "Reproduzir Original" ou "Reproduzir Filtrado" para ouvir o áudio
2. Clique em "Baixar Áudio Processado" para salvar o arquivo filtrado

## 🗂️ Estrutura do Projeto

```
ECO5000 - Modelos IA/
├── app.py                    # Servidor Flask (backend)
├── requirements.txt          # Dependências Python
├── templates/
│   └── index.html           # Interface web
├── static/
│   ├── css/
│   │   └── style.css        # Estilos da interface
│   └── js/
│       └── app.js            # Lógica JavaScript
├── uploads/                  # Arquivos enviados (criado automaticamente)
└── processed/                # Áudios processados (criado automaticamente)
```

## 🔧 Tecnologias Utilizadas

### Backend
- **Flask**: Framework web Python
- **librosa**: Processamento de áudio
- **scipy**: Filtros digitais (Butterworth)
- **soundfile**: Leitura/escrita de arquivos WAV
- **numpy**: Manipulação de arrays

### Frontend
- **HTML5/CSS3**: Estrutura e estilização
- **JavaScript**: Lógica da interface
- **Chart.js**: Visualização de gráficos
- **Web Audio API**: Reprodução de áudio

## 📝 Notas Técnicas

### Filtros

- Os filtros utilizam a implementação **Butterworth** de ordem 4
- Aplicação bidirecional (filtfilt) para evitar deslocamento de fase
- Suporte para áudio mono e estéreo

### Limitações

- Tamanho máximo de arquivo: 100MB
- Formatos suportados: Apenas WAV
- Visualização limitada a 50.000 pontos para performance

### Performance

- Para arquivos grandes, o áudio é subamostrado para visualização
- O processamento completo é sempre aplicado ao arquivo original
- O download contém o áudio processado completo

## 🐛 Solução de Problemas

### Erro ao carregar arquivo
- Verifique se o arquivo é .wav válido
- Certifique-se de que o arquivo não está corrompido

### Gráficos não aparecem
- Verifique o console do navegador (F12) para erros
- Certifique-se de que Chart.js está carregando corretamente

### Áudio não reproduz
- Verifique se o navegador suporta Web Audio API
- Tente em outro navegador (Chrome, Firefox, Edge)

### Filtros não funcionam
- Certifique-se de que pelo menos um filtro está habilitado
- Verifique se a frequência de corte está dentro dos limites (0 a metade da taxa de amostragem)

## 📞 Suporte

Para problemas ou dúvidas, verifique:
1. Se todas as dependências estão instaladas
2. Se o Python está na versão 3.8 ou superior
3. Se a porta 5000 está disponível

## 📄 Licença

Este projeto faz parte do sistema ECO5000 para detecção de vazamentos em áudio.


