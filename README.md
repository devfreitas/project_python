# Sistema de Gerenciamento de Livros

Este projeto é um **Sistema de Gerenciamento de Livros** desenvolvido em Python, com foco na manipulação de dados em um banco de dados **Oracle**. Ele implementa todas as operações CRUD (Create, Read, Update, Delete) de forma interativa via console (CLI).
O principal destaque do sistema é sua flexibilidade na **visualização e filtragem de dados**, permitindo buscas por texto, por valores numéricos com operadores relacionais e até mesmo a **exportação dos resultados** para arquivos **CSV** ou **Excel**.

### Desenvolvedor 
* **Nome:** Rafael de Freitas Moraes
* **GitHub:** <a href="https://github.com/devfreitas" target="_blank">DevFreitas</a>

---

## Tecnologias Utilizadas

* **Linguagem:** Python
* **Banco de Dados:** Oracle (via `oracledb`)
* **Bibliotecas Principais:**
    * `oracledb`: Para conectar e interagir com o banco de dados Oracle.
    * `pandas`: Utilizada para a criação e exportação dos dados para o formato Excel (`.xlsx`).
    * `csv`: Utilizada para a exportação dos dados para o formato CSV.
    * `datetime`: Para manipulação e formatação das datas de publicação.

---

## Instalação e Configuração

### 1. Pré-requisitos

Certifique-se de ter o Python instalado e acesso a um banco de dados Oracle.

### 2. Instalação das Dependências

Instale as bibliotecas necessárias usando `pip`:

**pandas**
```bash
pip install pandas
```
**oracledb**
```bash
pip install oracledb
```
**openpyxl**
```bash
pip install openpyxl
```
