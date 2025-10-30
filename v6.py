# Rafael de Freitas Moraes - RM:563210
import os
import csv
import oracledb
import pandas as pd
from datetime import datetime

# Mapeamento de colunas do DB para exibição
COLUNAS_MAP = {
    "NOME_LIVRO": "Nome",
    "AUTOR": "Autor",
    "GENERO": "Gênero",
    "PRECO": "Preço",
    "PAGINAS": "Páginas",
    "DATA_PUBLICACAO": "Data Publicação",
    "DESCRICAO": "Descrição"
}
COLUNAS_DB_TODAS = list(COLUNAS_MAP.keys())
COLUNAS_EXIBICAO_TODAS = list(COLUNAS_MAP.values())

def limpar_terminal() -> None:
    os.system("cls" if os.name == "nt" else "clear")
limpar_terminal()

try:
    con = oracledb.connect(user = "rm563210", password = "140706", dsn = 'oracle.fiap.com.br:1521/ORCL')
    conexao = True
except Exception as e:
    print("Erro: ", e)
    conexao = False
    con = None
cur = con.cursor() if conexao else None

def cadastrar_livro() -> None:
    limpar_terminal()
    print("Iniciando cadastro de livro...")
    nome = input("Nome do livro: ")
    cur.execute("SELECT 1 FROM livros WHERE nome_livro = :n", {"n": nome})
    if cur.fetchone():
        print("Livro já cadastrado!\n"); return
    autor = input("Autor: ")
    genero = input("Gênero: ")
    try:
        preco = float(input("Preço: "))
        paginas = int(input("Páginas: "))
        data_pub = input("Data de publicação (dd/mm/aaaa): ")
        data_formatada = datetime.strptime(data_pub, "%d/%m/%Y")
    except ValueError:
        print("Erro de formato em Preço, Páginas ou Data. Cadastro cancelado.\n"); return
        
    descricao = input("Descrição: ")
    cur.execute("""
        INSERT INTO livros (nome_livro, autor, genero, preco, paginas, data_publicacao, descricao)
        VALUES (:1, :2, :3, :4, :5, :6, :7)
    """, (nome, autor, genero, preco, paginas, data_formatada, descricao))
    con.commit()
    print("Livro cadastrado!\n")

def formatar_registro(r) -> str:
    if not r:
        return "Livro não encontrado."
    nome, autor, genero, preco, paginas, data_pub, descricao = r
    data_pub_str = data_pub.strftime("%d/%m/%Y") if isinstance(data_pub, datetime) else str(data_pub)
    return (f"Nome: {nome} | Autor: {autor} | Gênero: {genero} | "
            f"Preço: R$ {preco:.2f} | Páginas: {paginas} | "
            f"Data Pub: {data_pub_str} | Descrição: {descricao}")

def pesquisar_livro() -> None:
    limpar_terminal(); print("Iniciando pesquisa de livro...")
    nome = input("Nome do livro: ")
    cur.execute("SELECT * FROM livros WHERE nome_livro = :n", {"n": nome})
    r = cur.fetchone()
    if r:
        print(f"\nLivro encontrado:\n{formatar_registro(r)}\n")
    else:
        print("Livro não encontrado.\n")

def formatar_registro_dinamico(registro: tuple, colunas_db: list[str]) -> str:
    partes = []
    for i, nome_db in enumerate(colunas_db):
        valor = registro[i]
        nome_amigavel = COLUNAS_MAP.get(nome_db, nome_db)
        
        valor_formatado = str(valor)
        if nome_db == "PRECO" and isinstance(valor, (int, float)):
            valor_formatado = f"R$ {valor:.2f}"
        elif nome_db == "DATA_PUBLICACAO" and isinstance(valor, datetime):
            valor_formatado = valor.strftime("%d/%m/%Y")
            
        partes.append(f"{nome_amigavel}: {valor_formatado}")
        
    return " | ".join(partes)

def obter_colunas_selecionadas() -> tuple[list[str], list[str]]:
    print("\nSeleção de Colunas. Use vírgulas (ex: 1,3,5) ou [ENTER] para todas.")
    colunas_db = COLUNAS_DB_TODAS
    colunas_exibicao = COLUNAS_EXIBICAO_TODAS
    
    for i, nome_amigavel in enumerate(colunas_exibicao, 1):
        print(f" {i} - {nome_amigavel}")
        
    escolha = input("Sua escolha: ").strip()
    if not escolha:
        return colunas_db, colunas_exibicao
    
    try:
        indices_escolhidos = [int(idx.strip()) - 1 for idx in escolha.split(',') if idx.strip().isdigit()]
        indices_validos = [i for i in indices_escolhidos if 0 <= i < len(colunas_db)]
        
        if not indices_validos:
            return colunas_db, colunas_exibicao

        colunas_db_selecionadas = [colunas_db[i] for i in indices_validos]
        colunas_exibicao_selecionadas = [colunas_exibicao[i] for i in indices_validos]
        
        return colunas_db_selecionadas, colunas_exibicao_selecionadas

    except Exception:
        return colunas_db, colunas_exibicao

def oferecer_exportacao_simplificada(dados: list[tuple], colunas_db: list[str], colunas_exibicao: list[str]):
    if not dados:
        return
    opcao_e = input("\nGerar arquivo [E]xcel, [C]sv ? Ou [ENTER] para retornar ao menu: ").strip().upper()
    
    if opcao_e in ['E', 'C']:
        nome_arquivo = input("Digite o nome do arquivo: ").strip()
        if not nome_arquivo:
            print("Nome do arquivo não pode ser vazio!")
            return
        
        dados_export = []
        for registro in dados:
            linha = []
            for i, nome_db in enumerate(colunas_db):
                valor = registro[i]
                if nome_db == "DATA_PUBLICACAO" and isinstance(valor, datetime):
                    linha.append(valor.strftime("%d/%m/%Y"))
                else:
                    linha.append(valor)
            dados_export.append(linha)
            
        try:
            if opcao_e == 'E':
                nome_arquivo = nome_arquivo if nome_arquivo.endswith('.xlsx') else nome_arquivo + '.xlsx'
                df = pd.DataFrame(dados_export, columns=colunas_exibicao) 
                df.to_excel(nome_arquivo, index=False)
                print(f"Arquivo Excel '{nome_arquivo}' gerado com sucesso!")
                
            elif opcao_e == 'C':
                nome_arquivo = nome_arquivo if nome_arquivo.endswith('.csv') else nome_arquivo + '.csv'
                with open(nome_arquivo, 'w', newline='', encoding='utf-8') as arquivo_csv:
                    writer = csv.writer(arquivo_csv, delimiter=';')
                    writer.writerow(colunas_exibicao) 
                    writer.writerows(dados_export)
                print(f"Arquivo CSV '{nome_arquivo}' gerado com sucesso!")
        except Exception as e:
            print(f"Erro ao gerar arquivo: {e}")

def listar_livros_generico(filtro_sql: str, params: dict = None) -> None: 
    colunas_db, colunas_exibicao = obter_colunas_selecionadas()
    colunas_sql = ", ".join(colunas_db) 
    
    sql = f"SELECT {colunas_sql} FROM livros {filtro_sql} ORDER BY nome_livro"
    
    try:
        cur.execute(sql, params if params else {})
        r = cur.fetchall()
        
        if not r:
            print("Nenhum registro encontrado.\n")
            return
            
        print(f"\nTotal de registros: {len(r)}")
        print()
        
        for l in r: 
            print(formatar_registro_dinamico(l, colunas_db))
        print()
        
        oferecer_exportacao_simplificada(r, colunas_db, colunas_exibicao)
        
    except oracledb.Error as e:
        print(f"Erro ao pesquisar: {e}\n")


def listar_livros_todos() -> None:
    limpar_terminal()
    print("3 - a. Listar todos os Livros")
    listar_livros_generico(filtro_sql="")


def listar_livros_string() -> None:
    limpar_terminal()
    print("3 - b. Pesquisar Livros por parte da String")
    campos_string = {"1": "NOME_LIVRO", "2": "AUTOR", "3": "GENERO", "4": "DESCRICAO"}
    print("Escolha o campo para pesquisa: "); [print(f"{k} - {v}") for k, v in campos_string.items()]
        
    escolha_campo = input("Escolha ( 1 - 4 ): ").strip()
    campo_db = campos_string.get(escolha_campo)
    if not campo_db: print("Escolha de campo inválida.\n"); return
        
    parte_string = input(f"Digite a parte da string para pesquisar em '{campo_db}': ").strip()
    if not parte_string: print("A string de pesquisa não pode ser vazia.\n"); return

    filtro = f"WHERE UPPER({campo_db}) LIKE UPPER(:s)"
    listar_livros_generico(filtro_sql=filtro, params={"s": f"%{parte_string}%"})


def listar_livros_numerico() -> None:
    limpar_terminal()
    print("3 - c. Pesquisar por um campo numérico e listar")
    campos_numericos = {"1": "PRECO", "2": "PAGINAS"}
    operadores_validos = [ ">", ">=", "<", "<=", "=", "!=" ]

    print("Escolha o campo numérico para pesquisa: "); [print(f"{k} - {v}") for k, v in campos_numericos.items()]
    escolha_campo = input("Escolha ( 1 - 2 ): ").strip()
    campo_db = campos_numericos.get(escolha_campo)
    if not campo_db: print("Escolha de campo inválida.\n"); return
    
    operador = input(f"Digite o operador relacional ({', '.join(operadores_validos)}): ").strip().replace("==", "=")
    if operador not in operadores_validos: print("Operador inválido.\n"); return

    try:
        valor = float(input(f"Digite o valor numérico para comparação em '{campo_db}': "))
        if campo_db == "PAGINAS": valor = int(valor)
    except ValueError: print("Valor numérico inválido.\n"); return

    filtro = f"WHERE {campo_db} {operador} :v"
    listar_livros_generico(filtro_sql=filtro, params={"v": valor})


def pesquisa_generica() -> None:
    limpar_terminal()
    print("3 - d. Pesquisa genérica")
    texto_pesquisa = input("Digite o texto para pesquisa genérica: ").strip()
    if not texto_pesquisa: print("O texto de pesquisa não pode ser vazio.\n"); return 

    filtro = """
        WHERE UPPER(nome_livro) LIKE UPPER(:s) 
           OR UPPER(autor) LIKE UPPER(:s) 
           OR UPPER(genero) LIKE UPPER(:s) 
           OR UPPER(descricao) LIKE UPPER(:s)
    """
    listar_livros_generico(filtro_sql=filtro, params={"s": f"%{texto_pesquisa}%"})


def editar_livro() -> None:
    limpar_terminal()
    nome = input("\nDigite o nome do livro que deseja editar: ").strip()
    cur.execute("SELECT * FROM livros WHERE nome_livro = :n", {"n": nome})
    r = cur.fetchone()
    if not r:
         print("Livro não encontrado.\n"); return

    print(f"\nLivro encontrado:\n{formatar_registro(r)}\n")
    confirmar = input("Deseja editar este livro? (s/n): ").lower()
    if confirmar != "s": print("Operação cancelada.\n"); return

    try:
        novo_preco = input(f"Novo preço (atual: R$ {r[3]:.2f}, enter para manter): ").replace(",", ".")
        novo_preco = float(novo_preco) if novo_preco else r[3]

        novas_paginas = input(f"Novas páginas (atual: {r[4]}, enter para manter): ")
        novas_paginas = int(novas_paginas) if novas_paginas else r[4]

        nova_descricao = input(f"Nova descrição (atual: {r[6]}, enter para manter): ") or r[6] 
    except ValueError:
         print("\nValor numérico inválido! Operação cancelada."); return

    cur.execute("""
        UPDATE livros SET preco = :p, paginas = :pg, descricao = :d WHERE nome_livro = :n
    """, {"p": novo_preco, "pg": novas_paginas, "d": nova_descricao, "n": nome})
    con.commit()
    print("Livro atualizado!\n")

def apagar_livro() -> None:
    limpar_terminal()
    nome = input("\nDigite o nome do livro a apagar: ").strip()
    cur.execute("SELECT * FROM livros WHERE nome_livro = :n", {"n": nome})
    r = cur.fetchone()
    if not r:
         print("Livro não encontrado.\n"); return

    print(f"\nLivro encontrado:\n{formatar_registro(r)}\n")
    confirmar = input("Deseja realmente apagar este livro? (s/n): ").lower()
    if confirmar == "s":
        cur.execute("DELETE FROM livros WHERE nome_livro = :n", {"n": nome})
        con.commit()
        print("Livro apagado com sucesso!\n")
    else:
        print("Operação cancelada.\n")

def menu_listar_livros() -> None:
    while True:
        limpar_terminal()
        print("3 - Listar Registros")
        print('''
             0 - Voltar ao menu Principal
             a - Todos
             b - Pesquisar por parte da String e listar
             c - Pesquisar por um campo numérico e listar
             d - Pesquisa genérica
        ''')
        
        escolha = input("Escolha: ").lower().strip() 
        match escolha:
            case "a":
                listar_livros_todos()
            case "b":
                listar_livros_string()
            case "c":
                listar_livros_numerico()
            case "d":
                pesquisa_generica()
            case "0":
                break
            case _:
                print("Opção inválida. Tente novamente.") 
        if escolha != "0":
            input("Pressione ENTER para continuar...")

while True:
    limpar_terminal()
    print("Sistema de Gerenciamento de Livros")
    print('''
        0 - Sair
        1 - Cadastrar Livro
        2 - Pesquisar Livro por nome
        3 - Listar/Filtrar Livros
        4 - Editar registro do Livro
        5 - Apagar registro do Livro
    ''')
    opcao = input("Opção: ")
    match opcao:
        case "0":
            break
        case "1":
            cadastrar_livro()
        case "2":
            pesquisar_livro()
        case "3":
            menu_listar_livros()
        case "4":
            editar_livro()
        case "5":
            apagar_livro()
        case _:
            print("Inválido!\n")
    
    if opcao != "0":
        input("Pressione ENTER para retornar ao menu principal...")

if conexao:
    cur.close()
    con.close()
print("Encerrando.")
