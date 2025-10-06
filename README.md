# 🕵️ DataAgent EDA: Agente de Análise de Dados com IA

[![streamlit](https://img.shields.io/badge/OPEN-Streamlit-green)](https://i2a2mao08out25.streamlit.app/) 
[![m4ntonio badge](https://img.shields.io/badge/2025-ꂵ4ꋊ꓄ꄲꋊ꒐ꄲ-blue)](https://m4ntonio.github.io/) 
[![Licença](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

> **Faça perguntas em português sobre seus dados e receba respostas com gráficos, cálculos e código gerado por IA.**

O **DataAgent EDA** é uma aplicação web construído em Streamlit que utiliza inteligência artificial generativa para responder perguntas sobre conjuntos de dados CSV, Excel ou JSON, gerando respostas, análises, gráficos, estatísticas e código Python de forma interativa e segura, tudo em português do Brasil.

## 🔍 Funcionalidades

- Upload de arquivos CSV, XLSX ou JSON diretamente pela interface web.

- Análise automatizada dos dados com respostas em linguagem natural, explicações, insights e geração de código Python em tempo real.

- Geração automática de gráficos e visualizações customizadas a partir das perguntas dos usuários.

- Histórico de análises com controle de sessões, permitindo salvar e recuperar interações anteriores com os dados (requer o arquivo adicional database.py).

- Execução segura de código Python, restringindo comandos perigosos, para proteção do ambiente do usuário.

- Respostas e interação totalmente em português do Brasil

## 🚀 Como Usar

1. Clone o repositório:
   ```bash
   git clone https://github.com/seuusuario/dataagent.git
   cd dataagent

2. Crie um ambiente virtual e instale as dependências:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
                              # ou
    venv\Scripts\activate     # Windows

    pip install -r requirements.txt

3. Configure sua chave da API do Google AI:
    
    Crie um arquivo `.streamlit/secrets.toml` e insira sua chave em GOOGLE_API_KEY.
    ```bash
    #dentro do arquivo .streamlit/secrets.toml

    GOOGLE_API_KEY = "sua-chave-aqui"

4. Como rodar:

   Execute o seguinte comando na raiz do projeto:
   ```bash
   streamlit run app.py

## 📂 Estrutura do Projeto

```
dataagent/               # pasta principal
├── app.py               # App principal com Streamlit
├── database.py          # Sistema de salvamento com SQLite
├── .streamlit/          # pasta API
│   └── secrets.toml     # Chave da API (não versionada)
├── requirements.txt     # Dependências
└── README.md            # Este arquivo
```

## ⚙️ Tecnologias Utilizadas
- Streamlit – Interface web rápida e dinâmica
- Google Generative AI – Modelo `gemini-flash-latest` para geração de código
- SQLite3 – Banco leve para salvar histórico
- pandas – Manipulação de dados
- matplotlib/seaborn – Visualização de dados

## 🌐 Hospedagem

Você pode hospedar este app gratuitamente nos seguintes plataformas:

- [Streamlit Community Cloud](https://share.streamlit.io/) – Plataforma oficial gratuita para apps Streamlit
- [Google Cloud Run](https://cloud.google.com/run) – Solução serverless da Google Cloud
- [Render](https://render.com) – Plataforma simples e amigável para deploy de aplicações

Basta conectar seu repositório e seguir as instruções.

## 📄 Licença
Este projeto está licenciado sob a MIT License - veja o arquivo LICENSE para detalhes.

## 💬 Contribuição
Contribuições, relatórios de bugs e sugestões são bem-vindos!
Abra uma issue ou um pull request no GitHub.

## 🧑‍💻 Autor

Desenvolvido por m4ntonio – v1.0.9, 2025
