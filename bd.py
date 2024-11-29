import mysql.connector
from mysql.connector import Error
from datetime import date

def conectar():
    """Estabelece a conexão com o banco de dados"""
    try:
        conexao = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="root",
            database="trabalhojonas"
        )
        if conexao.is_connected():
            print("Conexão estabelecida com sucesso!")
        return conexao
    except Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None


def criar_tabelas():
    """Cria todas as tabelas necessárias no banco de dados"""
    try:
        conexao = conectar()
        if conexao is None:
            return

        cursor = conexao.cursor()

        # Tabela Item
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Item (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            categoria VARCHAR(50),
            preco DECIMAL(10, 2),
            quantidade INT,
            desconto FLOAT DEFAULT 0.0
        );
        """)

        # Tabela Venda
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Venda (
            id INT AUTO_INCREMENT PRIMARY KEY,
            data DATE NOT NULL,
            total DECIMAL(10, 2) NOT NULL
        );
        """)

        # Tabela Venda_Item
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Venda_Item (
            id INT AUTO_INCREMENT PRIMARY KEY,
            venda_id INT,
            item_id INT,
            quantidade INT,
            preco_unitario DECIMAL(10, 2),
            FOREIGN KEY (venda_id) REFERENCES Venda(id),
            FOREIGN KEY (item_id) REFERENCES Item(id)
        );
        """)

        print("Tabelas criadas com sucesso!")
        cursor.close()
        conexao.close()
    except Error as e:
        print(f"Erro ao criar tabelas: {e}")


def adicionar_item(nome, categoria, preco, quantidade):
    """Adiciona um item ao estoque"""
    try:
        conexao = conectar()
        if conexao is None:
            return
        cursor = conexao.cursor()
        comando = "INSERT INTO Item (nome, categoria, preco, quantidade) VALUES (%s, %s, %s, %s)"
        valores = (nome, categoria, preco, quantidade)
        cursor.execute(comando, valores)
        conexao.commit()
        print(f"Item '{nome}' adicionado com sucesso!")
        cursor.close()
        conexao.close()
    except Error as e:
        print(f"Erro ao adicionar item: {e}")


def atualizar_item(item_id, novo_nome=None, nova_categoria=None, novo_preco=None, nova_quantidade=None):
    """Atualiza os detalhes de um item"""
    try:
        conexao = conectar()
        if conexao is None:
            return
        cursor = conexao.cursor()

        if novo_nome:
            cursor.execute("UPDATE Item SET nome = %s WHERE id = %s", (novo_nome, item_id))
        if nova_categoria:
            cursor.execute("UPDATE Item SET categoria = %s WHERE id = %s", (nova_categoria, item_id))
        if novo_preco:
            cursor.execute("UPDATE Item SET preco = %s WHERE id = %s", (novo_preco, item_id))
        if nova_quantidade:
            cursor.execute("UPDATE Item SET quantidade = %s WHERE id = %s", (nova_quantidade, item_id))

        conexao.commit()
        print(f"Item '{item_id}' atualizado com sucesso!")
        cursor.close()
        conexao.close()
    except Error as e:
        print(f"Erro ao atualizar item: {e}")


def remover_item(item_id):
    """Remove um item do estoque"""
    try:
        conexao = conectar()
        if conexao is None:
            return
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM Item WHERE id = %s", (item_id,))
        conexao.commit()
        print(f"Item '{item_id}' removido com sucesso!")
        cursor.close()
        conexao.close()
    except Error as e:
        print(f"Erro ao remover item: {e}")


def listar_itens():
    """Lista todos os itens disponíveis no cardápio"""
    try:
        conexao = conectar()
        if conexao is None:
            return
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM Item")
        resultados = cursor.fetchall()
        print("Itens Disponíveis no Cardápio:")
        for item in resultados:
            print(item)
        cursor.close()
        conexao.close()
    except Error as e:
        print(f"Erro ao listar itens: {e}")


def atualizar_estoque(item_id, nova_quantidade):
    """Atualiza o estoque de um item manualmente"""
    try:
        conexao = conectar()
        if conexao is None:
            return
        cursor = conexao.cursor()
        cursor.execute("UPDATE Item SET quantidade = %s WHERE id = %s", (nova_quantidade, item_id))
        conexao.commit()
        print(f"Estoque do item com ID {item_id} atualizado para {nova_quantidade} unidades.")
        cursor.close()
        conexao.close()
    except Error as e:
        print(f"Erro ao atualizar estoque: {e}")


def registrar_venda(itens_vendidos):
    """Registra uma venda"""
    try:
        conexao = conectar()
        if conexao is None:
            return
        cursor = conexao.cursor()

        total = 0
        for item_id, quantidade in itens_vendidos:
            cursor.execute("SELECT preco FROM Item WHERE id = %s", (item_id,))
            resultado = cursor.fetchone()
            if resultado is None:
                print(f"Item com ID {item_id} não encontrado.")
                continue
            preco_unitario = resultado[0]
            total += preco_unitario * quantidade

        hoje = date.today()
        cursor.execute("INSERT INTO Venda (data, total) VALUES (%s, %s)", (hoje, total))
        venda_id = cursor.lastrowid

        for item_id, quantidade in itens_vendidos:
            cursor.execute("SELECT preco FROM Item WHERE id = %s", (item_id,))
            resultado = cursor.fetchone()
            if resultado is None:
                continue
            preco_unitario = resultado[0]
            cursor.execute("""
            INSERT INTO Venda_Item (venda_id, item_id, quantidade, preco_unitario)
            VALUES (%s, %s, %s, %s)
            """, (venda_id, item_id, quantidade, preco_unitario))

            cursor.execute("UPDATE Item SET quantidade = quantidade - %s WHERE id = %s", (quantidade, item_id))

        conexao.commit()
        print(f"Venda registrada com sucesso! ID da venda: {venda_id}")
        cursor.close()
        conexao.close()
    except Error as e:
        print(f"Erro ao registrar venda: {e}")


def aplicar_desconto(item_id, desconto_percentual=None, desconto_valor_fixo=None):
    """Aplica um desconto a um item, atualizando o preço no banco de dados."""
    try:
        conexao = conectar()
        if conexao is None:
            return
        
        cursor = conexao.cursor()

        # Obtém o preço atual do item
        cursor.execute("SELECT preco FROM Item WHERE id = %s", (item_id,))
        resultado = cursor.fetchone()
        
        if resultado is None:
            print(f"Item com ID {item_id} não encontrado.")
            return
        
        # Converte o preço atual para float
        preco_atual = float(resultado[0])
        novo_preco = preco_atual

        # Aplica o desconto percentual, se fornecido
        if desconto_percentual:
            desconto = preco_atual * (desconto_percentual / 100)
            novo_preco -= desconto

        # Aplica o desconto fixo, se fornecido
        if desconto_valor_fixo:
            novo_preco -= desconto_valor_fixo

        # Garante que o preço não fique negativo
        if novo_preco < 0:
            print("Erro: O desconto resultaria em um preço negativo.")
            return

        # Atualiza o preço no banco de dados
        cursor.execute("UPDATE Item SET preco = %s WHERE id = %s", (novo_preco, item_id))
        conexao.commit()

        print(f"Desconto aplicado com sucesso! Novo preço do item com ID {item_id}: R${novo_preco:.2f}")
        cursor.close()
        conexao.close()
    except Error as e:
        print(f"Erro ao aplicar desconto: {e}")


def gerar_relatorio_vendas():
    """Gera relatório de vendas"""
    try:
        conexao = conectar()
        if conexao is None:
            return
        cursor = conexao.cursor()
        cursor.execute("""
        SELECT Venda.id, Venda.data, SUM(Venda_Item.quantidade), Venda.total
        FROM Venda
        INNER JOIN Venda_Item ON Venda.id = Venda_Item.venda_id
        GROUP BY Venda.id
        """)
        resultados = cursor.fetchall()
        print("Relatório de Vendas:")
        for venda_id, data, total_itens, total in resultados:
            print(f"Venda {venda_id} | Data: {data} | Itens: {total_itens} | Total: R${total:.2f}")
        cursor.close()
        conexao.close()
    except Error as e:
        print(f"Erro ao gerar relatório de vendas: {e}")


def gerar_relatorio_pedidos():
    """Gera relatório detalhado de pedidos"""
    try:
        conexao = conectar()
        if conexao is None:
            return
        cursor = conexao.cursor()
        cursor.execute("""
        SELECT Venda.id, Venda.data, Item.nome, Venda_Item.quantidade, Venda_Item.preco_unitario
        FROM Venda
        INNER JOIN Venda_Item ON Venda.id = Venda_Item.venda_id
        INNER JOIN Item ON Venda_Item.item_id = Item.id
        ORDER BY Venda.id
        """)
        resultados = cursor.fetchall()
        print("Relatório de Pedidos:")
        for venda_id, data, item, quantidade, preco_unitario in resultados:
            print(f"Venda {venda_id} | Data: {data} | Item: {item} | Qtd: {quantidade} | Preço: R${preco_unitario:.2f}")
        cursor.close()
        conexao.close()
    except Error as e:
        print(f"Erro ao gerar relatório de pedidos: {e}")


def menu():
    """Menu de interação"""
    while True:
        print("\n" + "=" * 40)
        print("MENU DA CANTINA")
        print("=" * 40)
        print("1. Adicionar item")
        print("2. Atualizar item")
        print("3. Remover item")
        print("4. Listar itens")
        print("5. Atualizar estoque")
        print("6. Registrar venda")
        print("7. Gerar relatório de vendas")
        print("8. Gerar relatório de pedidos")
        print("9. Aplicar desconto")
        print("0. Sair")
        opcao = input("Escolha uma opção: ")
        
        if opcao == "1":
            nome = input("Nome: ")
            categoria = input("Categoria: ")
            preco = float(input("Preço: "))
            quantidade = int(input("Quantidade: "))
            adicionar_item(nome, categoria, preco, quantidade)
        elif opcao == "2":
            item_id = int(input("ID do item: "))
            novo_nome = input("Novo nome (vazio para não alterar): ") or None
            nova_categoria = input("Nova categoria (vazio para não alterar): ") or None
            novo_preco = input("Novo preço (vazio para não alterar): ")
            nova_quantidade = input("Nova quantidade (vazio para não alterar): ")
            atualizar_item(
                item_id,
                novo_nome,
                nova_categoria,
                float(novo_preco) if novo_preco else None,
                int(nova_quantidade) if nova_quantidade else None
            )
        elif opcao == "3":
            item_id = int(input("ID do item: "))
            remover_item(item_id)
        elif opcao == "4":
            listar_itens()
        elif opcao == "5":
            item_id = int(input("ID do item: "))
            nova_quantidade = int(input("Nova quantidade: "))
            atualizar_estoque(item_id, nova_quantidade)
        elif opcao == "6":
            itens_vendidos = []
            while True:
                item_id = int(input("ID do item vendido (0 para sair): "))
                if item_id == 0:
                    break
                quantidade = int(input(f"Quantidade vendida do item {item_id}: "))
                itens_vendidos.append((item_id, quantidade))
            registrar_venda(itens_vendidos)
        elif opcao == "7":
            gerar_relatorio_vendas()
        elif opcao == "8":
            gerar_relatorio_pedidos()
        elif opcao == "9":
            item_id = int(input("ID do item: "))
            print("1. Desconto percentual")
            print("2. Desconto fixo")
            tipo_desconto = input("Escolha o tipo de desconto: ")
            if tipo_desconto == "1":
                desconto_percentual = float(input("Percentual de desconto: "))
                aplicar_desconto(item_id, desconto_percentual=desconto_percentual)
            elif tipo_desconto == "2":
                desconto_valor_fixo = float(input("Valor fixo de desconto: "))
                aplicar_desconto(item_id, desconto_valor_fixo=desconto_valor_fixo)
            else:
                print("Tipo de desconto inválido.")
        elif opcao == "0":
            print("Saindo...")
            break
        else:
            print("Opção inválida!")

# Executa o menu
if __name__ == "__main__":
    criar_tabelas()
    menu()
