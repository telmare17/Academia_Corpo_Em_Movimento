import json
from datetime import datetime

# Lista para armazenar as fichas de treino
fichas_treino = []

def cadastrar_ficha():
    nome_aluno = input("Nome do aluno: ")
    objetivo = input("Objetivo (emagrecimento, hipertrofia, resistência, condicionamento físico): ")
    lista_exercicios = input("Lista de exercícios (separados por vírgula): ").split(',')
    data_inicio = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    ficha = {
        'nome': nome_aluno,
        'objetivo': objetivo,
        'exercicios': [exercicio.strip() for exercicio in lista_exercicios],
        'data_inicio': data_inicio
    }
    
    fichas_treino.append(ficha)
    print("Ficha cadastrada com sucesso!")

def consultar_ficha():
    nome_aluno = input("Digite o nome do aluno para consulta: ")
    for ficha in fichas_treino:
        if ficha['nome'].lower() == nome_aluno.lower():
            print(ficha)
            return
    print("Ficha não encontrada.")

def listar_treinos():
    print("Treinos em andamento:")
    for ficha in fichas_treino:
        print(f"Nome: {ficha['nome']}, Objetivo: {ficha['objetivo']}, Data de Início: {ficha['data_inicio']}")

def salvar_dados():
    with open('fichas_treino.json', 'w') as file:
        json.dump(fichas_treino, file)
    print("Dados salvos com sucesso!")

def carregar_dados():
    global fichas_treino
    try:
        with open('fichas_treino.json', 'r') as file:
            fichas_treino = json.load(file)
        print("Dados carregados com sucesso!")
    except FileNotFoundError:
        print("Arquivo não encontrado. Inicie com fichas vazias.")

def menu():
    carregar_dados()
    while True:
        print("\nMenu:")
        print("1. Cadastrar Ficha de Treino")
        print("2. Consultar Ficha de Treino")
        print("3. Listar Treinos em Andamento")
        print("4. Salvar Dados")
        print("5. Sair")
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == '1':
            cadastrar_ficha()
        elif opcao == '2':
            consultar_ficha()
        elif opcao == '3':
            listar_treinos()
        elif opcao == '4':
            salvar_dados()
        elif opcao == '5':
            salvar_dados()
            print("Saindo do sistema.")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    menu()
