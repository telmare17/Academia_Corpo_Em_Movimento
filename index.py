import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
from PIL import Image, ImageTk, ImageDraw

# Configuração de cores e estilos
COR_PRIMARIA = "#3498db"  # Azul
COR_SECUNDARIA = "#2ecc71"  # Verde
COR_FUNDO = "#f5f5f5"  # Cinza claro
COR_TEXTO = "#333333"  # Cinza escuro quase preto
COR_BOTAO = "#3498db"  # Azul
COR_BOTAO_HOVER = "#2980b9"  # Azul mais escuro
COR_DESTAQUE = "#e74c3c"  # Vermelho

class TooltipManager:
    """Gerencia tooltips para widgets"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = tk.Label(self.tooltip, text=self.text,
                         background="#FFFFaa", relief="solid", borderwidth=1,
                         font=("Arial", 10, "normal"))
        label.pack(ipadx=5, ipady=5)

    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class CustomButton(tk.Canvas):
    """Botão personalizado com efeitos hover"""
    def __init__(self, parent, text, command, icon=None, **kwargs):
        self.width = kwargs.pop('width', 200)
        self.height = kwargs.pop('height', 40)
        super().__init__(parent, width=self.width, height=self.height, 
                         highlightthickness=0, bg=COR_FUNDO, **kwargs)
        self.command = command
        self.text = text
        self.icon = icon
        self.font = ("Segoe UI", 11)
        self.active = False
        
        # Estado normal
        self.normal_bg = COR_BOTAO
        # Estado hover
        self.hover_bg = COR_BOTAO_HOVER
        
        self.draw_button()
        
        # Bind events
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)
        
    def draw_button(self):
        self.delete("all")
        
        # Fundo do botão
        bg_color = self.hover_bg if self.active else self.normal_bg
        self.create_rectangle(0, 0, self.width, self.height, 
                              fill=bg_color, outline="", tags="bg")
        
        # Arredondamento das bordas
        radius = 8
        self.create_arc(0, 0, radius*2, radius*2, start=90, extent=90, 
                        fill=bg_color, outline="")
        self.create_arc(self.width-radius*2, 0, self.width, radius*2, 
                        start=0, extent=90, fill=bg_color, outline="")
        self.create_arc(0, self.height-radius*2, radius*2, self.height, 
                        start=180, extent=90, fill=bg_color, outline="")
        self.create_arc(self.width-radius*2, self.height-radius*2, 
                        self.width, self.height, start=270, extent=90, 
                        fill=bg_color, outline="")
        
        # Texto centralizado
        text_x = self.width // 2
        if self.icon:
            # Se houver ícone, ajustar a posição do texto
            text_x = self.width // 2 + 15  # Desloca o texto um pouco para dar espaço ao ícone
            self.create_text(text_x, self.height // 2, text=self.text,
                             fill="white", font=self.font, tags="text")
            # Desenhar ou carregar ícone
            icon_x = text_x - 30
            self.create_text(icon_x, self.height // 2, text=self.icon,
                          fill="white", font=("Segoe UI Symbol", 12), tags="icon")
        else:
            self.create_text(text_x, self.height // 2, text=self.text,
                             fill="white", font=self.font, tags="text")
    
    def on_enter(self, event):
        self.active = True
        self.draw_button()
        
    def on_leave(self, event):
        self.active = False
        self.draw_button()
        
    def on_click(self, event):
        # Efeito de click
        self.move("text", 1, 1)
        if self.icon:
            self.move("icon", 1, 1)
        
    def on_release(self, event):
        # Retornar ao normal e executar comando
        self.move("text", -1, -1)
        if self.icon:
            self.move("icon", -1, -1)
        if self.command:
            self.command()

class SistemaAcademia:
    def __init__(self, root):
        self.root = root
        self.root.title("Academia Corpo em Movimento")
        self.root.geometry("900x600")
        self.root.resizable(True, True)
        self.root.configure(bg=COR_FUNDO)
        self.root.minsize(800, 600)
        
        # Carregar dados
        self.fichas_treino = []

        # Configurar o ícone da janela
        try:
            # Tente usar o ícone se disponível
            self.root.iconbitmap("gym_icon.ico")
        except:
            # Não faz nada se o ícone não estiver disponível
            pass
            
        # Fonte personalizada
        self.titulo_font = ("Segoe UI", 24, "bold")
        self.subtitulo_font = ("Segoe UI", 14)
        self.texto_font = ("Segoe UI", 12)
        
        # Criar frame principal
        self.main_frame = tk.Frame(self.root, bg=COR_FUNDO)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Criar barra de status primeiro
        self.criar_barra_status()
        
        # Depois criar os outros componentes
        self.criar_cabecalho()
        self.criar_barra_lateral()
        self.criar_area_conteudo()
        
        # Criar notebook para abas de conteúdo
        self.criar_abas()
        
        # Agora podemos carregar os dados com segurança
        self.carregar_dados()
        
        # Configurar protocolo de fechamento
        self.root.protocol("WM_DELETE_WINDOW", self.sair)
        
    def criar_cabecalho(self):
        """Criar o cabeçalho com título e logotipo"""
        header_frame = tk.Frame(self.main_frame, bg=COR_FUNDO)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Título
        titulo = tk.Label(header_frame, text="Sistema de Gerenciamento", 
                         font=self.titulo_font, bg=COR_FUNDO, fg=COR_TEXTO)
        titulo.pack(side=tk.LEFT, padx=(10, 0))
        
        subtitulo = tk.Label(header_frame, text="Academia Corpo em Movimento", 
                            font=self.subtitulo_font, bg=COR_FUNDO, fg=COR_PRIMARIA)
        subtitulo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Informações da data/hora atual
        self.data_label = tk.Label(header_frame, font=self.texto_font, 
                                  bg=COR_FUNDO, fg=COR_TEXTO)
        self.data_label.pack(side=tk.RIGHT, padx=10)
        self.atualizar_data()
    
    def atualizar_data(self):
        """Atualizar a data e hora no cabeçalho"""
        agora = datetime.now()
        data_formatada = agora.strftime("%d/%m/%Y %H:%M:%S")
        self.data_label.config(text=data_formatada)
        self.root.after(1000, self.atualizar_data)  # Atualizar a cada segundo
    
    def criar_barra_lateral(self):
        """Criar barra lateral com menu de navegação"""
        # Frame da barra lateral
        self.sidebar_frame = tk.Frame(self.main_frame, bg=COR_FUNDO, width=220)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Garantir que o frame mantenha sua largura
        self.sidebar_frame.pack_propagate(False)
        
        # Título da barra lateral
        sidebar_title = tk.Label(self.sidebar_frame, text="Menu Principal", 
                                font=self.subtitulo_font, bg=COR_FUNDO, fg=COR_PRIMARIA)
        sidebar_title.pack(pady=(0, 20), anchor="w")
        
        # Botões do menu
        btn_cadastrar = CustomButton(self.sidebar_frame, text="Cadastrar Ficha", 
                                    command=self.mostrar_cadastro, icon="✏️", width=200)
        btn_cadastrar.pack(pady=5)
        TooltipManager(btn_cadastrar, "Cadastrar uma nova ficha de treino")
        
        btn_consultar = CustomButton(self.sidebar_frame, text="Consultar Ficha", 
                                    command=self.mostrar_consulta, icon="🔍", width=200)
        btn_consultar.pack(pady=5)
        TooltipManager(btn_consultar, "Buscar ficha de treino por nome do aluno")
        
        btn_listar = CustomButton(self.sidebar_frame, text="Treinos em Andamento", 
                                 command=self.mostrar_listagem, icon="📋", width=200)
        btn_listar.pack(pady=5)
        TooltipManager(btn_listar, "Visualizar todos os treinos cadastrados")
        
        btn_salvar = CustomButton(self.sidebar_frame, text="Salvar Dados", 
                                 command=self.salvar_dados, icon="💾", width=200)
        btn_salvar.pack(pady=5)
        TooltipManager(btn_salvar, "Salvar todas as fichas em arquivo")
        
        btn_sair = CustomButton(self.sidebar_frame, text="Sair", 
                               command=self.sair, icon="🚪", width=200)
        btn_sair.pack(pady=5)
        TooltipManager(btn_sair, "Salvar e fechar o programa")
        
        # Contador de fichas
        self.contador_frame = tk.Frame(self.sidebar_frame, bg="#e6e6e6",
                                     highlightbackground=COR_PRIMARIA,
                                     highlightthickness=1)
        self.contador_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)
        
        lbl_contador = tk.Label(self.contador_frame, text="Fichas Cadastradas:", 
                               font=self.texto_font, bg="#e6e6e6")
        lbl_contador.pack(pady=(10, 0))
        
        self.contador_valor = tk.Label(self.contador_frame, text=str(len(self.fichas_treino)), 
                                     font=("Segoe UI", 24, "bold"), fg=COR_PRIMARIA, bg="#e6e6e6")
        self.contador_valor.pack(pady=(0, 10))
    
    def criar_area_conteudo(self):
        """Criar área principal de conteúdo"""
        self.content_frame = tk.Frame(self.main_frame, bg=COR_FUNDO)
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def criar_barra_status(self):
        """Criar barra de status na parte inferior"""
        self.status_frame = tk.Frame(self.root, bg=COR_PRIMARIA, height=25)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = tk.Label(self.status_frame, text="Pronto", 
                                   bg=COR_PRIMARIA, fg="white", anchor="w", padx=10)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Versão
        versao_label = tk.Label(self.status_frame, text="v1.0.0", 
                               bg=COR_PRIMARIA, fg="white", padx=10)
        versao_label.pack(side=tk.RIGHT)
    
    def criar_abas(self):
        """Criar abas para diferentes funcionalidades"""
        self.notebook = ttk.Notebook(self.content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Estilo para as abas
        style = ttk.Style()
        style.configure("TNotebook", background=COR_FUNDO, borderwidth=0)
        style.configure("TNotebook.Tab", background="#d9d9d9", padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", COR_PRIMARIA)], 
                 foreground=[("selected", "white")])
        
        # Aba de Cadastro
        self.aba_cadastro = tk.Frame(self.notebook, bg=COR_FUNDO)
        self.notebook.add(self.aba_cadastro, text="  Cadastro  ")
        self.criar_form_cadastro()
        
        # Aba de Consulta
        self.aba_consulta = tk.Frame(self.notebook, bg=COR_FUNDO)
        self.notebook.add(self.aba_consulta, text="  Consulta  ")
        self.criar_area_consulta()
        
        # Aba de Listagem
        self.aba_listagem = tk.Frame(self.notebook, bg=COR_FUNDO)
        self.notebook.add(self.aba_listagem, text="  Listagem  ")
        self.criar_area_listagem()
    
    def criar_form_cadastro(self):
        """Criar formulário de cadastro de fichas"""
        form_frame = tk.Frame(self.aba_cadastro, bg=COR_FUNDO)
        form_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        
        # Título
        titulo = tk.Label(form_frame, text="Cadastro de Ficha de Treino", 
                         font=self.subtitulo_font, bg=COR_FUNDO, fg=COR_PRIMARIA)
        titulo.pack(pady=(0, 20))
        
        # Campo: Nome do aluno
        frame_nome = tk.Frame(form_frame, bg=COR_FUNDO)
        frame_nome.pack(fill=tk.X, pady=5)
        
        lbl_nome = tk.Label(frame_nome, text="Nome do Aluno:", 
                           width=15, anchor="e", font=self.texto_font, bg=COR_FUNDO)
        lbl_nome.pack(side=tk.LEFT, padx=(0, 10))
        
        self.entry_nome = ttk.Entry(frame_nome, font=self.texto_font, width=40)
        self.entry_nome.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Campo: Objetivo
        frame_objetivo = tk.Frame(form_frame, bg=COR_FUNDO)
        frame_objetivo.pack(fill=tk.X, pady=5)
        
        lbl_objetivo = tk.Label(frame_objetivo, text="Objetivo:", 
                               width=15, anchor="e", font=self.texto_font, bg=COR_FUNDO)
        lbl_objetivo.pack(side=tk.LEFT, padx=(0, 10))
        
        self.entry_objetivo = ttk.Entry(frame_objetivo, font=self.texto_font, width=40)
        self.entry_objetivo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Campo: Exercícios
        frame_exercicios = tk.Frame(form_frame, bg=COR_FUNDO)
        frame_exercicios.pack(fill=tk.BOTH, pady=5, expand=True)
        
        lbl_exercicios = tk.Label(frame_exercicios, text="Exercícios:", 
                                 width=15, anchor="e", font=self.texto_font, bg=COR_FUNDO)
        lbl_exercicios.pack(side=tk.LEFT, padx=(0, 10), anchor="n")
        
        exercicios_frame = tk.Frame(frame_exercicios, bg=COR_FUNDO)
        exercicios_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.txt_exercicios = scrolledtext.ScrolledText(exercicios_frame, 
                                                      width=40, height=10,
                                                      font=self.texto_font)
        self.txt_exercicios.pack(fill=tk.BOTH, expand=True)
        
        tip_exercicios = tk.Label(exercicios_frame, text="Insira um exercício por linha", 
                                 font=("Segoe UI", 10, "italic"), fg="gray", bg=COR_FUNDO)
        tip_exercicios.pack(anchor="w")
        
        # Botão de cadastro
        btn_frame = tk.Frame(form_frame, bg=COR_FUNDO)
        btn_frame.pack(pady=20)
        
        btn_limpar = ttk.Button(btn_frame, text="Limpar", 
                               command=self.limpar_form_cadastro, width=15)
        btn_limpar.pack(side=tk.LEFT, padx=10)
        
        btn_cadastrar = ttk.Button(btn_frame, text="Cadastrar", 
                                  command=self.cadastrar_ficha, width=15)
        btn_cadastrar.pack(side=tk.LEFT, padx=10)
        
        # Configurar estilo dos botões
        style = ttk.Style()
        style.configure("TButton", font=self.texto_font, background=COR_BOTAO)
    
    def criar_area_consulta(self):
        """Criar área de consulta de fichas"""
        consulta_frame = tk.Frame(self.aba_consulta, bg=COR_FUNDO)
        consulta_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        
        # Título
        titulo = tk.Label(consulta_frame, text="Consulta de Ficha de Treino", 
                         font=self.subtitulo_font, bg=COR_FUNDO, fg=COR_PRIMARIA)
        titulo.pack(pady=(0, 20))
        
        # Campo de busca
        busca_frame = tk.Frame(consulta_frame, bg=COR_FUNDO)
        busca_frame.pack(fill=tk.X, pady=10)
        
        lbl_busca = tk.Label(busca_frame, text="Nome do Aluno:", 
                            font=self.texto_font, bg=COR_FUNDO)
        lbl_busca.pack(side=tk.LEFT, padx=(0, 10))
        
        self.entry_busca = ttk.Entry(busca_frame, font=self.texto_font, width=30)
        self.entry_busca.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        btn_buscar = ttk.Button(busca_frame, text="Buscar", 
                               command=self.consultar_ficha, width=15)
        btn_buscar.pack(side=tk.LEFT)
        
        # Área de resultado
        result_frame = tk.Frame(consulta_frame, bg=COR_FUNDO)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        lbl_resultado = tk.Label(result_frame, text="Resultado da Consulta:", 
                                font=self.texto_font, bg=COR_FUNDO)
        lbl_resultado.pack(anchor="w", pady=(0, 5))
        
        # Frame para o resultado com borda
        self.resultado_frame = tk.Frame(result_frame, bg="white", 
                                      highlightbackground=COR_PRIMARIA,
                                      highlightthickness=1)
        self.resultado_frame.pack(fill=tk.BOTH, expand=True)
        
        self.resultado_text = scrolledtext.ScrolledText(self.resultado_frame, 
                                                      width=40, height=12,
                                                      font=self.texto_font)
        self.resultado_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.resultado_text.config(state=tk.DISABLED)
    
    def criar_area_listagem(self):
        """Criar área de listagem de todos os treinos"""
        listagem_frame = tk.Frame(self.aba_listagem, bg=COR_FUNDO)
        listagem_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        
        # Título
        titulo = tk.Label(listagem_frame, text="Treinos em Andamento", 
                         font=self.subtitulo_font, bg=COR_FUNDO, fg=COR_PRIMARIA)
        titulo.pack(pady=(0, 20))
        
        # Botão de atualizar
        btn_frame = tk.Frame(listagem_frame, bg=COR_FUNDO)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        btn_atualizar = ttk.Button(btn_frame, text="Atualizar Lista", 
                                  command=self.atualizar_lista_treinos, width=15)
        btn_atualizar.pack(side=tk.RIGHT)
        
        # Treeview para exibir os treinos
        colunas = ("nome", "objetivo", "data")
        
        self.treinos_tree = ttk.Treeview(listagem_frame, columns=colunas, show="headings")
        
        # Configurar cabeçalhos
        self.treinos_tree.heading("nome", text="Nome do Aluno")
        self.treinos_tree.heading("objetivo", text="Objetivo")
        self.treinos_tree.heading("data", text="Data de Início")
        
        # Configurar larguras das colunas
        self.treinos_tree.column("nome", width=150, minwidth=100)
        self.treinos_tree.column("objetivo", width=250, minwidth=150)
        self.treinos_tree.column("data", width=150, minwidth=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(listagem_frame, orient=tk.VERTICAL, 
                                 command=self.treinos_tree.yview)
        self.treinos_tree.configure(yscroll=scrollbar.set)
        
        # Layout
        self.treinos_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind para exibir detalhes ao clicar
        self.treinos_tree.bind("<Double-1>", self.exibir_detalhes_treino)
        
        # Inicialmente, preencher a lista
        self.atualizar_lista_treinos()
    
    def atualizar_contador(self):
        """Atualizar o contador de fichas cadastradas"""
        self.contador_valor.config(text=str(len(self.fichas_treino)))
    
    def limpar_form_cadastro(self):
        """Limpar o formulário de cadastro"""
        self.entry_nome.delete(0, tk.END)
        self.entry_objetivo.delete(0, tk.END)
        self.txt_exercicios.delete(1.0, tk.END)
    
    def cadastrar_ficha(self):
        """Cadastrar uma nova ficha de treino"""
        nome = self.entry_nome.get().strip()
        objetivo = self.entry_objetivo.get().strip()
        exercicios_text = self.txt_exercicios.get(1.0, tk.END)
        
        if not nome:
            messagebox.showwarning("Aviso", "O nome do aluno é obrigatório!")
            return
        
        # Processar exercícios
        lista_exercicios = [e.strip() for e in exercicios_text.split('\n') if e.strip()]
        
        data_inicio = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        ficha = {
            'nome': nome,
            'objetivo': objetivo,
            'exercicios': lista_exercicios,
            'data_inicio': data_inicio
        }
        
        self.fichas_treino.append(ficha)
        self.salvar_dados()
        self.atualizar_contador()
        self.atualizar_lista_treinos()
        self.limpar_form_cadastro()
        
        messagebox.showinfo("Sucesso", f"Ficha de treino para {nome} cadastrada com sucesso!")
        self.status_label.config(text=f"Ficha cadastrada para {nome}")
    
    def consultar_ficha(self):
        """Consultar ficha por nome de aluno"""
        nome = self.entry_busca.get().strip().lower()
        
        if not nome:
            messagebox.showwarning("Aviso", "Digite um nome para buscar!")
            return
        
        ficha_encontrada = None
        for ficha in self.fichas_treino:
            if ficha['nome'].lower() == nome:
                ficha_encontrada = ficha
                break
        
        self.resultado_text.config(state=tk.NORMAL)
        self.resultado_text.delete(1.0, tk.END)
        
        if ficha_encontrada:
            # Formatar resultado
            resultado = f"Nome: {ficha_encontrada['nome']}\n"
            resultado += f"Objetivo: {ficha_encontrada['objetivo']}\n"
            resultado += f"Data início: {ficha_encontrada['data_inicio']}\n\n"
            resultado += "Exercícios:\n"
            
            for i, exercicio in enumerate(ficha_encontrada['exercicios'], 1):
                resultado += f"{i}. {exercicio}\n"
            
            self.resultado_text.insert(tk.END, resultado)
            self.status_label.config(text=f"Ficha de {ficha_encontrada['nome']} encontrada")
        else:
            self.resultado_text.insert(tk.END, "Nenhuma ficha encontrada para este aluno.")
            self.status_label.config(text="Ficha não encontrada")
        
        self.resultado_text.config(state=tk.DISABLED)
    
    def atualizar_lista_treinos(self):
        """Atualizar a lista de treinos na treeview"""
        # Limpar itens existentes
        for item in self.treinos_tree.get_children():
            self.treinos_tree.delete(item)
        
        # Adicionar fichas à treeview
        for ficha in self.fichas_treino:
            self.treinos_tree.insert("", tk.END, values=(
                ficha['nome'],
                ficha['objetivo'],
                ficha['data_inicio']
            ))
        
        self.status_label.config(text=f"Lista atualizada: {len(self.fichas_treino)} treinos encontrados")
    
    def exibir_detalhes_treino(self, event):
        """Exibir detalhes do treino selecionado na treeview"""
        item = self.treinos_tree.focus()
        if not item:
            return
        
        values = self.treinos_tree.item(item, "values")
        nome_aluno = values[0]
        
        # Buscar ficha completa
        for ficha in self.fichas_treino:
            if ficha['nome'] == nome_aluno:
                self.mostrar_detalhes_ficha(ficha)
                break
    
    def mostrar_detalhes_ficha(self, ficha):
        """Exibir janela com detalhes completos da ficha"""
        detalhes_window = tk.Toplevel(self.root)
        detalhes_window.title(f"Detalhes do Treino - {ficha['nome']}")
        detalhes_window.geometry("500x400")
        detalhes_window.configure(bg=COR_FUNDO)
        
        # Frame principal
        main_frame = tk.Frame(detalhes_window, bg=COR_FUNDO, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Cabeçalho
        header_frame = tk.Frame(main_frame, bg=COR_PRIMARIA)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        lbl_titulo = tk.Label(header_frame, text=f"Ficha de Treino - {ficha['nome']}", 
                             font=("Segoe UI", 14, "bold"), fg="white", bg=COR_PRIMARIA,
                             padx=10, pady=5)
        lbl_titulo.pack(fill=tk.X)
        
        # Conteúdo
        content = tk.Frame(main_frame, bg=COR_FUNDO)
        content.pack(fill=tk.BOTH, expand=True)
        
        # Informações básicas
        info_frame = tk.Frame(content, bg=COR_FUNDO)
        info_frame.pack(fill=tk.X, pady=5)
        
        # Nome
        lbl_nome = tk.Label(info_frame, text="Nome:", font=("Segoe UI", 11, "bold"), 
                           bg=COR_FUNDO, fg=COR_TEXTO, width=10, anchor="w")
        lbl_nome.grid(row=0, column=0, sticky="w", pady=2)
        
        lbl_nome_valor = tk.Label(info_frame, text=ficha['nome'], font=self.texto_font, 
                                 bg=COR_FUNDO, fg=COR_TEXTO)
        lbl_nome_valor.grid(row=0, column=1, sticky="w", pady=2)
        
        # Objetivo
        lbl_objetivo = tk.Label(info_frame, text="Objetivo:", font=("Segoe UI", 11, "bold"), 
                               bg=COR_FUNDO, fg=COR_TEXTO, width=10, anchor="w")
        lbl_objetivo.grid(row=1, column=0, sticky="w", pady=2)
        
        lbl_obj_valor = tk.Label(info_frame, text=ficha['objetivo'], font=self.texto_font, 
                                bg=COR_FUNDO, fg=COR_TEXTO)
        lbl_obj_valor.grid(row=1, column=1, sticky="w", pady=2)
        
        # Data
        lbl_data = tk.Label(info_frame, text="Início:", font=("Segoe UI", 11, "bold"), 
                           bg=COR_FUNDO, fg=COR_TEXTO, width=10, anchor="w")
        lbl_data.grid(row=2, column=0, sticky="w", pady=2)
        
        lbl_data_valor = tk.Label(info_frame, text=ficha['data_inicio'], font=self.texto_font, 
                                 bg=COR_FUNDO, fg=COR_TEXTO)
        lbl_data_valor.grid(row=2, column=1, sticky="w", pady=2)
        
        # Linha separadora
        separator = ttk.Separator(content, orient="horizontal")
        separator.pack(fill=tk.X, pady=10)
        
        # Exercícios
        exercicios_frame = tk.Frame(content, bg=COR_FUNDO)
        exercicios_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        lbl_exercicios = tk.Label(exercicios_frame, text="Exercícios:", 
                                 font=("Segoe UI", 12, "bold"), bg=COR_FUNDO, fg=COR_PRIMARIA)
        lbl_exercicios.pack(anchor="w", pady=(0, 5))
        
        # Lista de exercícios
        exercicios_list = tk.Frame(exercicios_frame, bg="white", 
                                  highlightbackground=COR_PRIMARIA,
                                  highlightthickness=1)
        exercicios_list.pack(fill=tk.BOTH, expand=True)
        
        # Criar canvas para scrolling
        canvas = tk.Canvas(exercicios_list, bg="white")
        scrollbar = ttk.Scrollbar(exercicios_list, orient="vertical", command=canvas.yview)
        
        # Frame dentro do canvas
        exercises_interior = tk.Frame(canvas, bg="white")
        
        # Configurar canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Criar janela no canvas
        canvas.create_window((0, 0), window=exercises_interior, anchor="nw")
        
        # Adicionar exercícios ao frame interior
        for i, exercicio in enumerate(ficha['exercicios'], 1):
            ex_frame = tk.Frame(exercises_interior, bg="white")
            ex_frame.pack(fill=tk.X, padx=5, pady=2)
            
            lbl_num = tk.Label(ex_frame, text=f"{i}.", font=self.texto_font, 
                              bg="white", fg=COR_PRIMARIA, width=3)
            lbl_num.pack(side=tk.LEFT)
            
            lbl_ex = tk.Label(ex_frame, text=exercicio, font=self.texto_font, 
                             bg="white", fg=COR_TEXTO, anchor="w", padx=5)
            lbl_ex.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Atualizar scrollregion após adicionar itens
        exercises_interior.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
        
        # Botão de fechar
        btn_frame = tk.Frame(main_frame, bg=COR_FUNDO)
        btn_frame.pack(fill=tk.X, pady=(15, 0))
        
        btn_fechar = ttk.Button(btn_frame, text="Fechar", 
                               command=detalhes_window.destroy, width=15)
        btn_fechar.pack(side=tk.RIGHT)
    
    def carregar_dados(self):
        """Carregar dados de fichas do arquivo"""
        try:
            with open('fichas_treino.json', 'r') as file:
                self.fichas_treino = json.load(file)
            
            # Atualizar contador e status
            if hasattr(self, 'contador_valor'):
                self.contador_valor.config(text=str(len(self.fichas_treino)))
            
            self.status_label.config(text=f"Dados carregados: {len(self.fichas_treino)} fichas")
        except (FileNotFoundError, json.JSONDecodeError):
            self.fichas_treino = []
            self.status_label.config(text="Nenhum dado encontrado. Iniciando novo arquivo.")
    
    def salvar_dados(self):
        """Salvar dados das fichas em arquivo"""
        with open('fichas_treino.json', 'w') as file:
            json.dump(self.fichas_treino, file, indent=4)
        self.status_label.config(text=f"Dados salvos: {len(self.fichas_treino)} fichas")
        messagebox.showinfo("Sucesso", "Dados salvos com sucesso!")
    
    def mostrar_cadastro(self):
        """Mostrar aba de cadastro"""
        self.notebook.select(0)
    
    def mostrar_consulta(self):
        """Mostrar aba de consulta"""
        self.notebook.select(1)
    
    def mostrar_listagem(self):
        """Mostrar aba de listagem"""
        self.notebook.select(2)
        self.atualizar_lista_treinos()
    
    def sair(self):
        """Salvar dados e fechar o programa"""
        resposta = messagebox.askyesno("Sair", "Deseja salvar os dados antes de sair?")
        if resposta:
            self.salvar_dados()
        self.root.destroy()

def main():
    """Função principal para iniciar o programa"""
    root = tk.Tk()
    app = SistemaAcademia(root)
    root.mainloop()

if __name__ == "__main__":
    main()