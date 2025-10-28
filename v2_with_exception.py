# Rafael de Freitas Moraes - RM:563210

import os
import oracledb
from datetime import datetime

def limpar_terminal() -> None:
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

def cadastrar_livro() -> None:
    if not conexao or not con or not cur:
        print("Erro: Sem conexão com o banco de dados. Operação cancelada.")
        return
    limpar_terminal()
    print("Iniciando cadastro de livro...")
    while True:
        nome = input("Nome do livro: ").strip()
        if not nome:
            print("O nome do livro não pode estar vazio. Tente novamente.")
            continue
        try:
            cur.execute("SELECT 1 FROM livros WHERE nome_livro = :n", {"n": nome})
            if cur.fetchone():
                print("Livro já cadastrado! Voltando ao menu principal.\n")
                return
            break
        except Exception as e:
            print(f"Erro ao verificar o livro: {e}. Tente novamente.")

    while True:
        autor = input("Autor: ").strip()
        if not autor:
            print("O nome do autor não pode estar vazio. Tente novamente.")
            continue
        break

    while True:
        genero = input("Gênero: ").strip()
        if not genero:
            print("O gênero não pode estar vazio. Tente novamente.")
            continue
        break

    while True:
        preco_input = input("Preço: ")
        try:
            preco = float(preco_input.replace(',', '.'))
            if preco < 0:
                 print("O preço não pode ser negativo. Tente novamente.")
                 continue
            break
        except ValueError:
            print("Preço inválido. Digite um número válido (ex: 45.90).")

    while True:
        paginas_input = input("Páginas: ")
        try:
            paginas = int(paginas_input)
            if paginas <= 0:
                 print("O número de páginas deve ser um inteiro positivo. Tente novamente.")
                 continue
            break
        except ValueError:
            print("Páginas inválidas. Digite um número inteiro.")

    data_formatada = None
    while True:
        data_pub = input("Data de publicação (dd/mm/aaaa): ")
        try:
            data_formatada = datetime.strptime(data_pub, "%d/%m/%Y")
            if data_formatada > datetime.now():
                print("A data de publicação não pode ser futura. Tente novamente.")
                continue
            break
        except ValueError:
            print("Formato de data inválido. Use o padrão dd/mm/aaaa (ex: 25/12/2023).")
            
    descricao = input("Descrição: ").strip()

    try:
        sql = "INSERT INTO livros (nome_livro, autor, genero, preco, paginas, data_publicacao, descricao) VALUES (:1, :2, :3, :4, :5, :6, :7)"
        cur.execute(sql, (nome, autor, genero, preco, paginas, data_formatada, descricao)) 
        con.commit()
        print("Livro Cadastrado!\n")
    except Exception as e:
        con.rollback()
        print(f"Erro ao inserir no banco de dados: {e}")
        print("Operação de cadastro falhou.\n")

def pesquisar_livro() -> None:
    if not conexao or not con or not cur:
        print("Erro: Sem conexão com o banco de dados. Operação cancelada.")
        return
        
    limpar_terminal()
    print("Pesquisa...")
    nome = input("Nome do livro: ").strip()
    
    try:
        cur.execute("SELECT nome_livro, autor, genero, preco, paginas, data_publicacao, descricao FROM livros WHERE nome_livro = :n", {"n": nome})
        r = cur.fetchone()
    except Exception as e:
        print(f"Erro ao consultar o banco de dados: {e}")
        return
        
    if r:
        data_publicacao = r[5]
        data_formatada = data_publicacao.strftime('%d/%m/%Y') if data_publicacao else 'N/A'
        
        print(f"\nLivro encontrado:")
        print(f"  Nome: {r[0]}")
        print(f"  Autor: {r[1]}")
        print(f"  Gênero: {r[2]}")
        print(f"  Preço: R$ {r[3]:.2f}")
        print(f"  Páginas: {r[4]}")
        print(f"  Data Publicação: {data_formatada}")
        print(f"  Descrição: {r[6]}\n")
    else:
        print("Livro não encontrado.\n")

def listar_todos() -> None:
    if not conexao or not con or not cur:
        print("Erro: Sem conexão com o banco de dados. Operação cancelada.")
        return
        
    limpar_terminal()
    print("Listando todos os livros...")
    
    try:
        cur.execute("SELECT nome_livro, autor, genero, preco, paginas, data_publicacao, descricao FROM livros ORDER BY nome_livro")
        livros = cur.fetchall()
    except Exception as e:
        print(f"Erro ao consultar o banco de dados: {e}")
        return
    
    if not livros:
        print("Nenhum livro cadastrado.\n")
        return
    
    print("-" * 40)
    for livro in livros:
        nome, autor, genero, preco, paginas, data_pub, descricao = livro

        preco_formatado = f"R$ {preco:.2f}"

        data_formatada = data_pub.strftime('%d/%m/%Y') if isinstance(data_pub, datetime) else 'N/A'
        
        print(f"Nome do livro: {nome}")
        print(f"Autor: {autor}")
        print(f"Gênero: {genero}")
        print(f"Preço: {preco_formatado}")
        print(f"Páginas: {paginas}")
        print(f"Data Publicação: {data_formatada}")
        print(f"Descrição: {descricao}")
        print("-" * 40)
    
    print(f"Total de livros encontrados: {len(livros)}\n")

def editar_livro() -> None:
    if not conexao or not con or not cur:
        print("Erro: Sem conexão com o banco de dados. Operação cancelada.")
        return
        
    limpar_terminal()
    nome = input("\nDigite o nome do livro que deseja editar: ").strip()
    
    try:
        cur.execute("SELECT nome_livro, autor, genero, preco, paginas, data_publicacao, descricao FROM livros WHERE nome_livro = :n", {"n": nome})
        r = cur.fetchone()
    except Exception as e:
        print(f"Erro ao consultar o banco de dados: {e}")
        return
        
    if not r:
        print("Livro não encontrado.\n")
        return

    print(f"\nLivro encontrado:\nNome: {r[0]} | Autor: {r[1]} | Gênero: {r[2]} | Preço: R$ {r[3]:.2f} | Páginas: {r[4]} | Descrição: {r[6]}\n")
    confirmar = input("Deseja editar este livro? (s/n): ").lower()
    
    if confirmar != "s":
        print("Operação cancelada.\n")
        return

    while True:
        novo_p = input(f"Novo preço (atual R$ {r[3]:.2f}) (enter para manter): ").strip()
        if not novo_p:
            novo_preco = r[3]
            break
        try:
            novo_preco = float(novo_p.replace(",", "."))
            if novo_preco < 0:
                print("O preço não pode ser negativo. Tente novamente.")
                continue
            break
        except ValueError:
            print("Preço inválido. Digite um número válido (ex: 45.90).")

    while True:
        novas_p = input(f"Novas páginas (atual {r[4]}) (enter para manter): ").strip()
        if not novas_p:
            novas_paginas = r[4]
            break
        try:
            novas_paginas = int(novas_p)
            if novas_paginas <= 0:
                print("O número de páginas deve ser um inteiro positivo. Tente novamente.")
                continue
            break
        except ValueError:
            print("Páginas inválidas. Digite um número inteiro.")

    nova_descricao = input(f"Nova descrição (atual {r[6]}) (enter para manter): ").strip() or r[6]

    try:
        cur.execute("""
            UPDATE livros SET preco = :p, paginas = :pg, descricao = :d WHERE nome_livro = :n
        """, {"p": novo_preco, "pg": novas_paginas, "d": nova_descricao, "n": nome})
        con.commit()
        print("Livro atualizado!\n")
    except Exception as e:
        con.rollback()
        print(f"Erro ao atualizar no banco de dados: {e}")
        print("Operação de edição falhou.\n")

def apagar_livro() -> None:
    if not conexao or not con or not cur:
        print("Erro: Sem conexão com o banco de dados. Operação cancelada.")
        return
        
    limpar_terminal()
    nome = input("\nDigite o nome do livro a apagar: ").strip()
    
    try:
        cur.execute("SELECT nome_livro, autor, genero, preco, paginas, data_publicacao, descricao FROM livros WHERE nome_livro = :n", {"n": nome})
        r = cur.fetchone()
    except Exception as e:
        print(f"Erro ao consultar o banco de dados: {e}")
        return
        
    if not r:
        print("Livro não encontrado.\n")
        return
        
    print(f"\nLivro encontrado:\nNome: {r[0]} | Autor: {r[1]} | Gênero: {r[2]} | Preço: R$ {r[3]:.2f} | Páginas: {r[4]} | Descrição: {r[6]}\n")
    confirmar = input("Deseja realmente apagar este livro? (s/n): ").lower()
    
    if confirmar == "s":
        try:
            cur.execute("DELETE FROM livros WHERE nome_livro = :n", {"n": nome})
            con.commit()
            print("Livro apagado com sucesso!\n")
        except Exception as e:
            con.rollback()
            print(f"Erro ao apagar no banco de dados: {e}")
            print("Operação de exclusão falhou.\n")
    else:
        print("Operação cancelada.\n")

if conexao:
    while True:
        print("Livro - Menu Principal")
        print("\n0 - Sair")
        print("1 - Cadastrar novo livro")
        print("2 - Pesquisar livro por nome")
        print("3 - Listar todos os livros")
        print("4 - Editar registro do livro (Preço, Páginas, Descrição)")
        print("5 - Apagar registro do livro")
        
        opcao = input("Opção: ").strip()
        
        match opcao:
            case "0":
                break
            case "1":
                cadastrar_livro()
            case "2":
                pesquisar_livro()
            case "3":
                listar_todos()
            case "4":
                editar_livro()
            case "5":
                apagar_livro()
            case _:
                print("Opção inválida! Tente novamente.\n")
else:
    print("\nNão foi possível iniciar o menu devido ao erro de conexão.")


cur.close()
con.close()
limpar_terminal()
print("Encerrando a aplicação e fechando a conexão com o banco de dados...")