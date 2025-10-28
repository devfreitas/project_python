import os
import oracledb
from datetime import datetime

def limpar_terminal() -> None:
    print("Limpando terminal...")
    os.system("cls" if os.name == "nt" else "clear")
limpar_terminal()

con = oracledb.connect(user="rm563210", password="140706", dsn="oracle.fiap.com.br/orcl")
cur = con.cursor()

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

def listar_todos() -> None:
    print("Listando todos os livros...")
    cur.execute("SELECT * FROM livros ORDER BY nome_livro")
    r = cur.fetchall()
    if not r:
         print("Nenhum livro cadastrado.\n")
         return
    for l in r: print(l)
    print()

# ----- v2 -----

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
            listar_todos()
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