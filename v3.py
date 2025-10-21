import os
import oracledb
from datetime import datetime

def limpar_terminal() -> None:
    print("Limpando terminal...")
    os.system("cls" if os.name == "nt" else "clear")
limpar_terminal()

try:
    con = oracledb.connect(user = "rm563210", password = "140706", dsn = 'oracle.fiap.com.br:1521/ORCL')
    inst_cadastro = con.cursor()
    inst_consulta = con.cursor()
    inst_alteracao = con.cursor()
    inst_exclusao = con.cursor()
except Exception as e:
    print("Erro: ", e)
    conexao = False
else:
    conexao = True
cur = con.cursor()

def formatar_registro(r) -> str:
    if not r:
        return "Livro não encontrado."
    nome, autor, genero, preco, paginas, data_pub, descricao = r
    data_pub_str = data_pub.strftime("%d/%m/%Y") if isinstance(data_pub, datetime) else data_pub 
    return (f"Nome: {nome} | Autor: {autor} | Gênero: {genero} | "
            f"Preço: R$ {preco:.2f} | Páginas: {paginas} | "
            f"Data Pub: {data_pub_str} | Descrição: {descricao}")

def cadastrar_livro() -> None:
    limpar_terminal() 
    print("Iniciando cadastro de livro...")
    nome = input("Nome do livro: ")
    cur.execute("SELECT 1 FROM livros WHERE nome_livro = :n", {"n": nome})
    if cur.fetchone():
        print("Livro já cadastrado!\n")
        return
    autor = input("Autor: ")
    genero = input("Gênero: ")
    preco = float(input("Preço: "))
    paginas = int(input("Páginas: "))
    data_pub = input("Data de publicação (dd/mm/aaaa): ")
    data_formatada = datetime.strptime(data_pub, "%d/%m/%Y")
    descricao = input("Descrição: ")
    cur.execute("""
        INSERT INTO livros (nome_livro, autor, genero, preco, paginas, data_publicacao, descricao)
        VALUES (:1, :2, :3, :4, :5, :6, :7)
    """, (nome, autor, genero, preco, paginas, data_formatada, descricao))
    con.commit()
    print("Livro cadastrado!\n")

def pesquisar_livro() -> None:
    limpar_terminal()
    print("Iniciando pesquisa de livro...")
    nome = input("Nome do livro: ")
    cur.execute("SELECT * FROM livros WHERE nome_livro = :n", {"n": nome})
    r = cur.fetchone()
    print(f"\nLivro encontrado:\nNome: {r[0]} | Autor: {r[1]} | Gênero: {r[2]} | Preço: {r[3]} | Páginas: {r[4]} | Descrição: {r[5]}\n" if r else "Livro não encontrado.\n")

def listar_livros_todos() -> None:
    limpar_terminal()
    print("3 - a. Listar todos os Livros")
    cur.execute("SELECT * FROM livros ORDER BY nome_livro")
    r = cur.fetchall()
    if not r:
        print("Nenhum livro cadastrado.\n")
        return
    
    print(f"Total de registros: {len(r)}\n")
    for l in r: 
        print(formatar_registro(l))
    print()


def listar_livros_string() -> None:
    limpar_terminal()
    print("3 - b. Pesquisar Livros por parte da String")
    
    campos_string = {
        "1": "NOME_LIVRO",
        "2": "AUTOR",
        "3": "GENERO",
        "4": "DESCRICAO"
    }
    
    print("Escolha o campo para pesquisa: ")
    for k, v in campos_string.items():
        print(f"{k} - {v}")
        
    escolha_campo = input("Escolha ( 1 - 4 ): ").strip()
    campo_db = campos_string.get(escolha_campo)
    
    if not campo_db:
        print("Escolha de campo inválida.\n")
        return
        
    parte_string = input(f"Digite a parte da string para pesquisar em '{campo_db}': ").strip()
    
    if not parte_string:
        print("A string de pesquisa não pode ser vazia.\n")
        return

    sql = f"SELECT * FROM livros WHERE ({campo_db}) LIKE UPPER(:s) ORDER BY nome_livro"
    
    try:
        cur.execute(sql, {"s": f"%{parte_string}%"})
        r = cur.fetchall()
        
        if not r:
            print("Nenhum registro encontrado com a parte da string informada.\n")
            return
            
        print(f"\nRegistros encontrados ({len(r)}):")
        for l in r:
            print(formatar_registro(l))
        print()
        
    except oracledb.Error as e:
        print(f"Erro ao pesquisar: {e}\n")


def listar_livros_numerico() -> None:
    limpar_terminal()
    print("3 - c. Pesquisar por um campo numérico e listar")
    
    campos_numericos = {
        "1": "PRECO",
        "2": "PAGINAS"
    }
    operadores_validos = [ ">", ">=", "<", "<=", "==", "!=" ]

    print("Escolha o campo numérico para pesquisa: ")
    for k, v in campos_numericos.items():
        print(f"{k} - {v}")
        
    escolha_campo = input("Escolha ( 1 - 2 ): ").strip()
    campo_db = campos_numericos.get(escolha_campo)
    if not campo_db:
        print("Escolha de campo inválida.\n")
        return
    
    operador = input(f"Digite o operador relacional ({', '.join(operadores_validos)}): ").strip()
    if operador == "==":
        operador = "=" # Oracle
    elif operador not in operadores_validos:
        print("Operador inválido.\n")
        return

    try:
        valor = float(input(f"Digite o valor numérico para comparação em '{campo_db}': "))
        if campo_db == "PAGINAS":
            valor = int(valor) 
    except ValueError:
        print("Valor numérico inválido.\n")
        return
    sql = f"SELECT * FROM livros WHERE {campo_db} {operador} :v ORDER BY nome_livro"
    
    try:
        cur.execute(sql, {"v": valor})
        r = cur.fetchall()
        if not r:
            print("Nenhum registro encontrado com os critérios informados.\n")
            return
        print(f"\nRegistros encontrados ({len(r)}):")
        for l in r:
            print(formatar_registro(l))
        print()      
    except oracledb.Error as e:
        print(f"Erro ao pesquisar: {e}\n")

def editar_livro() -> None:
    limpar_terminal()
    nome = input("\nDigite o nome do livro que deseja editar: ").strip()
    cur.execute("SELECT * FROM livros WHERE nome_livro = :n", {"n": nome})
    r = cur.fetchone()
    if not r:
        print("Livro não encontrado.\n")
        return

    print(f"\nLivro encontrado:\nNome: {r[0]} | Autor: {r[1]} | Gênero: {r[2]} | Preço: R$ {r[3]:.2f} | Páginas: {r[4]} | Descrição: {r[6]}\n")
    confirmar = input("Deseja editar este livro? (s/n): ").lower()
    if confirmar != "s":
        print("Operação cancelada.\n")
        return

    novo_preco = input("Novo preço (enter para manter): ")
    novo_preco = float(novo_preco.replace(",", ".")) if novo_preco else r[3]

    novas_paginas = input("Novas páginas (enter para manter): ")
    novas_paginas = int(novas_paginas) if novas_paginas else r[4]

    nova_descricao = input("Nova descrição (enter para manter): ") or r[6]

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
        print("Livro não encontrado.\n")
        return

    print(f"\nLivro encontrado:\nNome: {r[0]} | Autor: {r[1]} | Gênero: {r[2]} | Preço: R$ {r[3]:.2f} | Páginas: {r[4]} | Descrição: {r[6]}\n")
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
        print("a - Todos")
        print("b - Pesquisar por parte da String e listar")
        print("c - Pesquisar por um campo numérico e listar")
        print("0 - Voltar ao Menu Principal")
        
        escolha = input("Escolha: ").lower().strip()
        
        match escolha:
            case "a":
                listar_livros_todos()
            case "b":
                listar_livros_string()
            case "c":
                listar_livros_numerico()
            case "0":
                break
            case _:
                print("Opção inválida. Tente novamente.")
        
        if escolha != "0":
            input("Pressione ENTER para continuar...")

while True:
    print("Livro")
    print("\n0 - Sair\n1 - Cadastrar os livros\n2 - Pesquisar os livros\n3 - Listar todos os livros\n4 - Editar registro do livro\n5 - Apagar registro do livro")
    opcao = input("Opção: ")
    match opcao:
        case "0":
            break
        case  "1":
            cadastrar_livro()
        case  "2":
            pesquisar_livro()
        case  "3":
            menu_listar_livros()
        case "4":
            editar_livro()
        case "5":
            apagar_livro()
        case _:
            print("Inválido!\n")

cur.close()
con.close()
limpar_terminal()
print("Encerrando...")
