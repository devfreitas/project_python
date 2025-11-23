# Rafael de Freitas Moraes RM:563210

import os
import csv
import oracledb
import pandas as pd
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
    print("Erro na conexão: ", e)
    conexao = False
else:
    conexao = True
cur = con.cursor()

def formatar_registro(r) -> str:
    if not r:
        return "Livro não encontrado."
    if len(r) == 7:
        nome, autor, genero, preco, paginas, data_pub, descricao = r
        data_pub_str = data_pub.strftime("%d/%m/%Y") if isinstance(data_pub, datetime) else str(data_pub)
        return (f"Nome: {nome} | Autor: {autor} | Gênero: {genero} | "
                f"Preço: R$ {preco:.2f} | Páginas: {paginas} | "
                f"Data Pub: {data_pub_str} | Descrição: {descricao}")
                
    elif len(r) == 9:
        # Formato novo (9 campos)
        nome, autor, genero, preco, paginas, data_pub, descricao, data_cadastro, data_ultima_atualizacao = r
        data_pub_str = data_pub.strftime("%d/%m/%Y") if isinstance(data_pub, datetime) else str(data_pub)

        data_cadastro_str = data_cadastro.strftime("%d/%m/%Y") if isinstance(data_cadastro, datetime) else "N/A"
        data_att_str = data_ultima_atualizacao.strftime("%d/%m/%Y %H:%M:%S") if isinstance(data_ultima_atualizacao, datetime) else "N/A"
        
        return (f"Nome: {nome} | Autor: {autor} | Gênero: {genero} | "
                f"Preço: R$ {preco:.2f} | Páginas: {paginas} | "
                f"Data Pub: {data_pub_str} | Descrição: {descricao}\n"
                f"  Cadastrado em: {data_cadastro_str} | Última atualização: {data_att_str}")
    else:
        return f"Erro: Registro com formato inesperado ({len(r)} campos). Esperado: 7 ou 9 campos."

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
    
    try:
        preco = float(input("Preço: "))
        paginas = int(input("Páginas: "))
    except ValueError:
        print("Preço ou Páginas inválidos. Cadastro cancelado.\n")
        return
        
    data_pub = input("Data de publicação (dd/mm/aaaa): ")
    try:
        data_formatada = datetime.strptime(data_pub, "%d/%m/%Y")
    except ValueError:
        print("Formato de data inválido. Cadastro cancelado.\n")
        return
        
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
    cur.execute("SELECT * FROM livros WHERE nome_livro = :n", {"n": nome}) # Pega as 9 colunas agora
    r = cur.fetchone()
    if r:
        print(f"\nLivro encontrado:")
        print(formatar_registro(r))
        print()
    else:
        print("Livro não encontrado.\n")

def gerar_arquivo_exportacao(dados, tipo_arquivo, nome_arquivo):
    try:
        colunas = ['Nome', 'Autor', 'Gênero', 'Preço', 'Páginas', 'Data Publicação', 'Descrição']
        dados_formatados = []
        
        for registro in dados:
            if len(registro) == 7:
                nome, autor, genero, preco, paginas, data_pub, descricao = registro
            elif len(registro) == 9:
                nome, autor, genero, preco, paginas, data_pub, descricao = registro[:7]
            else:
                print(f"Aviso: Registro com formato inesperado ({len(registro)} campos) foi ignorado na exportação.")
                continue
            
            data_pub_str = data_pub.strftime("%d/%m/%Y") if isinstance(data_pub, datetime) else str(data_pub)
            dados_formatados.append([nome, autor, genero, preco, paginas, data_pub_str, descricao])
        
        if tipo_arquivo.upper() == 'E':
            if not nome_arquivo.endswith('.xlsx'):
                nome_arquivo += '.xlsx'
            df = pd.DataFrame(dados_formatados, columns=colunas)
            df.to_excel(nome_arquivo, index=False)
            print(f"Arquivo Excel '{nome_arquivo}' gerado com sucesso!")
            
        elif tipo_arquivo.upper() == 'C':
            if not nome_arquivo.endswith('.csv'):
                nome_arquivo += '.csv'
            with open(nome_arquivo, 'w', newline='', encoding='utf-8') as arquivo_csv:
                writer = csv.writer(arquivo_csv, delimiter=';')
                writer.writerow(colunas)
                writer.writerows(dados_formatados)
            print(f"Arquivo CSV '{nome_arquivo}' gerado com sucesso!")
            
    except Exception as e:
        print(f"Erro ao gerar arquivo: {e}")

def oferecer_exportacao(dados):
    if not dados:
        return
    opcao_e = input("\nGerar arquivo [E]xcel, [C]sv ? Ou ENTER para retornar ao menu: ").strip().upper()
    
    if opcao_e in ['E', 'C']:
        nome_arquivo = input("Digite o nome do arquivo: ").strip()
        if nome_arquivo:
            gerar_arquivo_exportacao(dados, opcao_e, nome_arquivo)
        else:
            print("Nome do arquivo não pode ser vazio!")
    elif opcao_e == '':
        return
    else:
        print("Opção inválida!")

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
        print("-" * 50)
        print(formatar_registro(l))
    print()
    
    oferecer_exportacao(r)


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

    sql = f"SELECT * FROM livros WHERE UPPER({campo_db}) LIKE UPPER(:s) ORDER BY nome_livro"
    
    try:
        cur.execute(sql, {"s": f"%{parte_string}%"})
        r = cur.fetchall()
        
        if not r:
            print("Nenhum registro encontrado com a parte da string informada.\n")
            return
            
        print(f"\nRegistros encontrados ({len(r)}):")
        for l in r:
            print("-" * 50)
            print(formatar_registro(l))
        print()
        oferecer_exportacao(r)
        
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
            print("-" * 50)
            print(formatar_registro(l))
        print()
        oferecer_exportacao(r)
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

    print(f"\nLivro encontrado:")
    print(formatar_registro(r))
    print()
    confirmar = input("Deseja editar este livro? (s/n): ").lower()
    if confirmar != "s":
        print("Operação cancelada.\n")
        return
    try:
        novo_preco = input("Novo preço (enter para manter, atual: R$ {:.2f}): ".format(r[3]))
        novo_preco = float(novo_preco.replace(",", ".")) if novo_preco else r[3]
    except ValueError:
        print("Preço inválido. Edição cancelada.\n")
        return
        
    try:
        novas_paginas = input("Novas páginas (enter para manter, atual: {}): ".format(r[4]))
        novas_paginas = int(novas_paginas) if novas_paginas else r[4]
    except ValueError:
        print("Páginas inválidas. Edição cancelada.\n")
        return
    nova_descricao = input("Nova descrição (enter para manter, atual: {}): ".format(r[6])) or r[6]

    # Atualiza a data_ultima_atualizacao com SYSTIMESTAMP do Oracle
    cur.execute("""
        UPDATE livros 
        SET preco = :p, paginas = :pg, descricao = :d, data_ultima_atualizacao = SYSTIMESTAMP
        WHERE nome_livro = :n
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

    print(f"\nLivro encontrado:")
    print(formatar_registro(r))
    print()
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
            a - Todos
            b - Pesquisar por parte da String e listar
            c - Pesquisar por um campo numérico e listar
            d - Pesquisa genérica
            0 - Voltar ao menu Principal
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

def pesquisa_generica() -> pd.DataFrame:
    limpar_terminal()
    print("3 - d. Pesquisa genérica")
    texto_pesquisa = input("Digite o texto para pesquisa genérica: ").strip()
    if not texto_pesquisa:
        print("O texto de pesquisa não pode ser vazio.\n")
        return pd.DataFrame()
 
    sql = """
        SELECT * FROM livros 
        WHERE UPPER(nome_livro) LIKE UPPER(:s) 
            OR UPPER(autor) LIKE UPPER(:s) 
            OR UPPER(genero) LIKE UPPER(:s) 
            OR UPPER(descricao) LIKE UPPER(:s)
        ORDER BY nome_livro
    """
    
    try:
        cur.execute(sql, {"s": f"%{texto_pesquisa}%"})
        r = cur.fetchall()
        if not r:
            print(f"Nenhum registro encontrado com o texto '{texto_pesquisa}'.\n")
            return pd.DataFrame()
        
        colunas = ['Nome', 'Autor', 'Gênero', 'Preço', 'Páginas', 'Data Publicação', 'Descrição'] 
        dados_formatados = []
        
        for registro in r:
            if len(registro) == 7:
                nome, autor, genero, preco, paginas, data_pub, descricao = registro
            elif len(registro) == 9:
                nome, autor, genero, preco, paginas, data_pub, descricao = registro[:7]
            else:
                print(f"Aviso: Registro com formato inesperado ({len(registro)} campos) foi ignorado.")
                continue
            
            data_pub_str = data_pub.strftime("%d/%m/%Y") if isinstance(data_pub, datetime) else str(data_pub)
            dados_formatados.append([nome, autor, genero, preco, paginas, data_pub_str, descricao])
        
        df = pd.DataFrame(dados_formatados, columns=colunas)
        
        print(f"\nPesquisa genérica por '{texto_pesquisa}' - Registros encontrados: {len(r)}")
        print("-" * 40) 
        for i, l in enumerate(r, 1):
            print(f"{i}. {formatar_registro(l)}")
            print("-" * 40)
        print()
        oferecer_exportacao(r)
        return df    

    except oracledb.Error as e:
        print(f"Erro ao pesquisar: {e}\n")
        return pd.DataFrame()
    except Exception as e:
        print(f"Erro ao criar DataFrame: {e}\n")
        return pd.DataFrame()

while True:
    limpar_terminal()
    print("Menu - Livros")
    print('''
        0 - Sair
        1 - Cadastrar os livros
        2 - Pesquisar os livros (por nome exato)
        3 - Listar Livros (várias opções)
        4 - Editar registro do livro
        5 - Apagar registro do livro
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
            print("Opção Inválida!\n")
            input("Pressione ENTER para continuar...")

cur.close()
con.close()
limpar_terminal()
print("Encerrando.")