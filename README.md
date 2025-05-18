# Sistema - Academia Corpo Em Movimento

Este projeto simula um sistema de gerenciamento de fichas de treino de uma academia. Foi desenvolvido como parte da disciplina de Algoritmos e Programação. Abaixo estão descritos os principais fluxos do sistema, focando na lógica de cada um deles com os respectivos trechos de código.

---

## 🖼️ Imagem do Sistema

![Tela do Sistema](img/foto-sistema.png)

## ✅ Funcionalidades Atendidas

| Funcionalidade                                                                               | Status |
| -------------------------------------------------------------------------------------------- | ------ |
| Registrar fichas de treino com nome do aluno, objetivo, lista de exercícios e data de início | OK     |
| Consultar fichas cadastradas, buscando por nome do aluno;                                    | OK     |
| Listar todos os treinos em andamento;                                                        | OK     |
| Salvamento de alunos via JSON                                                                | OK     |
| Organizar os dados de forma eficiente usando listas e tuplas.                                | OK     |
| Barra de status com contador de fichas                                                       | OK     |
| Data e hora em tempo real                                                                    | OK     |

---

## 1. Registrar fichas de treino

### Lógica:

1. Captura os dados do formulário preenchido pelo usuário (nome, objetivo, exercícios, data).
2. Verifica se todos os campos foram preenchidos corretamente.
3. Valida o formato da data e estrutura dos exercícios.
4. Cria um dicionário com os dados da ficha de treino.
5. Adiciona esse dicionário à lista principal de fichas (`fichas`).
6. Atualiza o contador de fichas na interface.
7. Salva a lista no arquivo JSON.

```python
if not aluno or not objetivo or not exercicios:
    messagebox.showwarning("Atenção", "Preencha todos os campos!")
    return

ficha = {
    "aluno": aluno,
    "objetivo": objetivo,
    "exercicios": exercicios,
    "data_inicio": data_inicio
}

fichas.append(ficha)
barra_status.config(text=f"Fichas cadastradas: {len(fichas)}")
salvar_dados()
```

---

## 2. Consultar fichas por nome do aluno

### Lógica:

1. Obtém o nome digitado no campo de busca.
2. Converte o nome para minúsculas (case-insensitive).
3. Percorre todas as fichas.
4. Compara o nome do aluno na ficha com o nome digitado.
5. Se encontrar, formata os dados da ficha e exibe na interface.

```python
resultado = ""
nome_busca = entrada_nome.get().strip().lower()

for ficha in fichas:
    if ficha["aluno"].lower() == nome_busca:
        resultado += formatar_ficha(ficha)

if resultado:
    texto_resultado.delete("1.0", tk.END)
    texto_resultado.insert(tk.END, resultado)
else:
    messagebox.showinfo("Resultado", "Nenhuma ficha encontrada.")
```

---

## 3. Listar todos os treinos em andamento

### Lógica:

1. Verifica se existem fichas cadastradas.
2. Percorre todas as fichas da lista.
3. Usa a função de formatação para montar um texto com as informações de cada ficha.
4. Exibe o texto formatado na área de exibição.

```python
resultado = ""
for ficha in fichas:
    resultado += formatar_ficha(ficha)

texto_resultado.delete("1.0", tk.END)
texto_resultado.insert(tk.END, resultado)
```

---

## 4. Salvamento e carregamento automático via JSON

### Lógica:

* **Carregamento**:

  1. Ao iniciar o programa, verifica se o arquivo JSON existe.
  2. Se existir, carrega os dados e converte em lista de fichas.
  3. Atualiza o contador na interface com o número de fichas carregadas.

* **Salvamento**:

  1. Após qualquer modificação na lista de fichas (inclusão, edição ou exclusão), sobrescreve o arquivo com os novos dados.

```python
def salvar_dados():
    with open(ARQUIVO_DADOS, 'w') as f:
        json.dump(fichas, f, indent=4)

if os.path.exists(ARQUIVO_DADOS):
    with open(ARQUIVO_DADOS, 'r') as f:
        fichas = json.load(f)
    barra_status.config(text=f"Fichas cadastradas: {len(fichas)}")
```

---

## 5. Organização com listas e tuplas

### Lógica:

* O sistema armazena as fichas como uma lista de dicionários:

  ```python
  fichas = []
  ```
* Cada dicionário representa uma ficha e contém:

  * nome do aluno (string)
  * objetivo (string)
  * lista de exercícios (lista de tuplas)
  * data de início (string)

```python
exercicios = [("Agachamento", "3x10"), ("Supino", "3x12")]
```

---

## 6. Barra de status com contador de fichas

### Lógica:

* A cada ação que modifica o número de fichas (adicionar, carregar), a barra de status é atualizada com o novo total.

```python
barra_status.config(text=f"Fichas cadastradas: {len(fichas)}")
```

---

## 7. Data e hora em tempo real

### Lógica:

* O sistema usa a função `after()` do Tkinter para agendar a atualização da hora a cada segundo.
* A hora formatada é exibida em um `Label`.

```python
def atualizar_hora():
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    rotulo_hora.config(text=agora)
    root.after(1000, atualizar_hora)
```

---

## Comentários sobre a interface gráfica

A interface foi feita com o Tkinter, com as seguintes características:

* Campos de entrada para nome, objetivo, exercícios e data.
* Botões para salvar ficha, buscar por nome e listar fichas.
* Área de exibição para resultados.
* Barra de status informando a quantidade de fichas.
* Exibição da data e hora atual em tempo real.

---
