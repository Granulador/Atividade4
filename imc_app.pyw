import tkinter
import tkinter.messagebox
import customtkinter
import sqlite3
from datetime import datetime
import os  # NOVO: para abrir o PDF depois de gerar

# NOVO: imports para PDF
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # controle do tema
        self.modo_escuro = (customtkinter.get_appearance_mode() == "Dark")

        # Window
        self.title("Cálculo do IMC - Índice de Massa Corporal")
        self.geometry("780x420")
        self.resizable(False, False)

        # Grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Banco de dados
        self.conexao = sqlite3.connect("imc.db")
        self.criar_tabela()

        # Sidebar
        self.sidebar_frame = customtkinter.CTkFrame(self, width=160, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=6, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1)

        self.logo_label = customtkinter.CTkLabel(
            self.sidebar_frame,
            text="IMC",
            font=customtkinter.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Campos
        self.label_nome = customtkinter.CTkLabel(self, text="Nome do Paciente:")
        self.label_nome.grid(row=0, column=1, padx=20, pady=(20, 5), sticky="w")
        self.entry_nome = customtkinter.CTkEntry(self, placeholder_text="Digite o nome")
        self.entry_nome.grid(row=0, column=2, padx=20, pady=(20, 5), sticky="ew")

        self.label_idade = customtkinter.CTkLabel(self, text="Idade Completa:")
        self.label_idade.grid(row=1, column=1, padx=20, pady=5, sticky="w")
        self.entry_idade = customtkinter.CTkEntry(self, placeholder_text="Digite a Idade")
        self.entry_idade.grid(row=1, column=2, padx=20, pady=5, sticky="ew")

        self.label_altura = customtkinter.CTkLabel(self, text="Altura (cm):")
        self.label_altura.grid(row=2, column=1, padx=20, pady=5, sticky="w")
        self.entry_altura = customtkinter.CTkEntry(self, placeholder_text="Ex: 170")
        self.entry_altura.grid(row=2, column=1, padx=(150, 20), pady=5, sticky="w")

        self.label_peso = customtkinter.CTkLabel(self, text="Peso (kg):")
        self.label_peso.grid(row=3, column=1, padx=20, pady=5, sticky="w")
        self.entry_peso = customtkinter.CTkEntry(self, placeholder_text="Ex: 70")
        self.entry_peso.grid(row=3, column=1, padx=(150, 20), pady=5, sticky="w")

        # Resultado
        self.resultado_box = customtkinter.CTkTextbox(self, width=320, height=170)
        self.resultado_box.grid(row=2, column=2, rowspan=2, padx=20, pady=10, sticky="nsew")
        self.resultado_box.insert("0.0", "Resultado")

        # Botões principais
        self.btn_calcular = customtkinter.CTkButton(self, text="Calcular", command=self.calcular_imc)
        self.btn_calcular.grid(row=4, column=1, padx=10, pady=10, sticky="e")

        self.btn_reiniciar = customtkinter.CTkButton(self, text="Reiniciar", command=self.reiniciar)
        self.btn_reiniciar.grid(row=4, column=2, padx=10, pady=10, sticky="w")

        self.btn_sair = customtkinter.CTkButton(self, text="Sair", command=self.on_close)
        self.btn_sair.grid(row=4, column=2, padx=10, pady=10, sticky="e")

        # Botões na sidebar
        self.btn_historico = customtkinter.CTkButton(
            self.sidebar_frame, text="Histórico", command=self.mostrar_historico
        )
        self.btn_historico.grid(row=2, column=0, padx=20, pady=(20, 10))

        # PDF do último
        self.btn_pdf = customtkinter.CTkButton(
            self.sidebar_frame, text="Gerar PDF (último)", command=self.gerar_pdf_ultimo
        )
        self.btn_pdf.grid(row=3, column=0, padx=20, pady=10)

        # PDF com todos
        self.btn_pdf_todos = customtkinter.CTkButton(
            self.sidebar_frame, text="Gerar PDF (todos)", command=self.gerar_pdf_todos
        )
        self.btn_pdf_todos.grid(row=4, column=0, padx=20, pady=10)

        # Botão de tema
        tema_emoji = "🌚" if self.modo_escuro else "🌞"
        self.btn_tema = customtkinter.CTkButton(
            self.sidebar_frame,
            text=tema_emoji,
            width=40,
            command=self.alternar_tema,
            font=("Segoe UI Emoji", 28)
        )
        self.btn_tema.grid(row=5, column=0, pady=10)

        # Evento de fechar
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # ================== BANCO DE DADOS ================== #

    def criar_tabela(self):
        cursor = self.conexao.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS imc_registros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                idade INTEGER,
                altura_cm REAL NOT NULL,
                peso_kg REAL NOT NULL,
                imc REAL NOT NULL,
                classificacao TEXT NOT NULL,
                data_hora TEXT NOT NULL
            )
        """)
        self.conexao.commit()

    def salvar_registro(self, nome, idade, altura_cm, peso_kg, imc, classificacao):
        cursor = self.conexao.cursor()
        data_hora = datetime.now().strftime("%Y-%m-%d %Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO imc_registros (nome, idade, altura_cm, peso_kg, imc, classificacao, data_hora)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (nome, idade, altura_cm, peso_kg, imc, classificacao, data_hora))
        self.conexao.commit()

    def buscar_ultimos_registros(self, limite=10):
        cursor = self.conexao.cursor()
        cursor.execute("""
            SELECT nome, idade, altura_cm, peso_kg, imc, classificacao, data_hora
            FROM imc_registros
            ORDER BY id DESC
            LIMIT ?
        """, (limite,))
        return cursor.fetchall()

    def buscar_ultimo_registro(self):
        cursor = self.conexao.cursor()
        cursor.execute("""
            SELECT nome, idade, altura_cm, peso_kg, imc, classificacao, data_hora
            FROM imc_registros
            ORDER BY id DESC
            LIMIT 1
        """)
        return cursor.fetchone()

    def buscar_todos_registros(self):
        cursor = self.conexao.cursor()
        cursor.execute("""
            SELECT nome, idade, altura_cm, peso_kg, imc, classificacao, data_hora
            FROM imc_registros
            ORDER BY id ASC
        """)
        return cursor.fetchall()

    # ================== LÓGICA / INTERFACE ================== #

    def calcular_imc(self):
        try:
            nome = self.entry_nome.get().strip()
            idade_texto = self.entry_idade.get().strip()
            altura_cm_texto = self.entry_altura.get().strip()
            peso_texto = self.entry_peso.get().strip()

            if not nome or not idade_texto or not altura_cm_texto or not peso_texto:
                tkinter.messagebox.showerror("Erro", "Preencha todos os campos!")
                return

            idade = int(idade_texto)
            altura_cm = float(altura_cm_texto.replace(",", "."))
            peso = float(peso_texto.replace(",", "."))

            altura_m = altura_cm / 100
            imc = peso / (altura_m * altura_m)

            if imc < 18.5:
                estado = "Abaixo do peso"
            elif imc < 25:
                estado = "Peso normal"
            elif imc < 30:
                estado = "Sobrepeso"
            elif imc < 35:
                estado = "Obesidade grau I"
            elif imc < 40:
                estado = "Obesidade grau II"
            else:
                estado = "Obesidade grau III"

            texto = (
                f"Paciente: {nome}\n"
                f"Idade: {idade} anos\n"
                f"Altura: {altura_cm:.1f} cm\n"
                f"Peso: {peso:.1f} kg\n\n"
                f"IMC calculado: {imc:.2f}\n"
                f"Classificação: {estado}"
            )

            self.resultado_box.delete("0.0", "end")
            self.resultado_box.insert("0.0", texto)

            # Salvar no banco
            self.salvar_registro(nome, idade, altura_cm, peso, imc, estado)

            tkinter.messagebox.showinfo("Sucesso", "Cálculo salvo no banco de dados!")

        except ValueError:
            tkinter.messagebox.showerror("Erro", "Digite valores numéricos válidos para idade, altura e peso!")
        except Exception as e:
            tkinter.messagebox.showerror("Erro", f"Ocorreu um erro: {e}")

    def reiniciar(self):
        self.entry_nome.delete(0, "end")
        self.entry_idade.delete(0, "end")
        self.entry_altura.delete(0, "end")
        self.entry_peso.delete(0, "end")
        self.resultado_box.delete("0.0", "end")
        self.resultado_box.insert("0.0", "Resultado")

    def alternar_tema(self):
        if self.modo_escuro:
            customtkinter.set_appearance_mode("Light")
            self.modo_escuro = False
            self.btn_tema.configure(text="🌞")
        else:
            customtkinter.set_appearance_mode("Dark")
            self.modo_escuro = True
            self.btn_tema.configure(text="🌚")

    def mostrar_historico(self):
        registros = self.buscar_ultimos_registros()

        if not registros:
            tkinter.messagebox.showinfo("Histórico", "Nenhum registro encontrado no banco de dados.")
            return

        self.resultado_box.delete("0.0", "end")
        self.resultado_box.insert("0.0", "=== ÚLTIMOS REGISTROS DE IMC ===\n\n")

        for nome, idade, altura_cm, peso_kg, imc, classificacao, data_hora in registros:
            linha = (
                f"Data/Hora: {data_hora}\n"
                f"Paciente: {nome} | Idade: {idade}\n"
                f"Altura: {altura_cm:.1f} cm | Peso: {peso_kg:.1f} kg\n"
                f"IMC: {imc:.2f} | Classificação: {classificacao}\n"
                f"{'-'*40}\n"
            )
            self.resultado_box.insert("end", linha)

    # ================== PDF (ÚLTIMO) ================== #

    def gerar_pdf_ultimo(self):
        registro = self.buscar_ultimo_registro()
        if not registro:
            tkinter.messagebox.showinfo("PDF", "Nenhum registro no banco para gerar PDF.")
            return

        nome, idade, altura_cm, peso_kg, imc, classificacao, data_hora = registro

        nome_arquivo = "relatorio_imc_ULTIMO.pdf"
        c = canvas.Canvas(nome_arquivo, pagesize=A4)
        largura, altura_pagina = A4

        # Margens
        x_inicial = 50
        y = altura_pagina - 80

        # Título
        c.setFont("Helvetica-Bold", 18)
        c.drawString(x_inicial, y, "Relatório de IMC")
        y -= 30

        # Linha
        c.setLineWidth(1)
        c.line(x_inicial, y, largura - 50, y)
        y -= 30

        # Dados do paciente
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x_inicial, y, "Dados do Paciente:")
        y -= 20

        c.setFont("Helvetica", 12)
        c.drawString(x_inicial, y, f"Nome: {nome}")
        y -= 20
        c.drawString(x_inicial, y, f"Idade: {idade} anos")
        y -= 20
        c.drawString(x_inicial, y, f"Altura: {altura_cm:.1f} cm")
        y -= 20
        c.drawString(x_inicial, y, f"Peso: {peso_kg:.1f} kg")
        y -= 30

        # Resultado IMC
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x_inicial, y, "Resultado do IMC:")
        y -= 20

        c.setFont("Helvetica", 12)
        c.drawString(x_inicial, y, f"IMC: {imc:.2f}")
        y -= 20
        c.drawString(x_inicial, y, f"Classificação: {classificacao}")
        y -= 30

        # Data
        c.setFont("Helvetica", 10)
        c.drawString(x_inicial, y, f"Data/Hora do cálculo: {data_hora}")
        y -= 20
        c.drawString(x_inicial, y, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

        c.showPage()
        c.save()

        # Abrir o PDF automaticamente
        try:
            os.startfile(nome_arquivo)
        except Exception:
            pass

    # ================== PDF (TODOS) ================== #

    def gerar_pdf_todos(self):
        registros = self.buscar_todos_registros()
        if not registros:
            tkinter.messagebox.showinfo("PDF", "Nenhum registro no banco para gerar PDF.")
            return

        nome_arquivo = "relatorio_imc_TODOS.pdf"
        c = canvas.Canvas(nome_arquivo, pagesize=A4)
        largura, altura_pagina = A4

        x_inicial = 40
        y = altura_pagina - 60

        def cabecalho_pagina():
            nonlocal y
            c.setFont("Helvetica-Bold", 16)
            c.drawString(x_inicial, y, "Relatório de IMC - Todos os Pacientes")
            y -= 25
            c.setLineWidth(1)
            c.line(x_inicial, y, largura - 40, y)
            y -= 25

        cabecalho_pagina()

        c.setFont("Helvetica", 11)

        for nome, idade, altura_cm, peso_kg, imc, classificacao, data_hora in registros:
            if y < 80:
                c.showPage()
                y = altura_pagina - 60
                cabecalho_pagina()
                c.setFont("Helvetica", 11)

            c.drawString(x_inicial, y, f"Data/Hora: {data_hora}")
            y -= 15
            c.drawString(x_inicial, y, f"Nome: {nome}")
            y -= 15
            c.drawString(x_inicial, y, f"Idade: {idade} anos")
            y -= 15
            c.drawString(x_inicial, y, f"Altura: {altura_cm:.1f} cm | Peso: {peso_kg:.1f} kg")
            y -= 15
            c.drawString(x_inicial, y, f"IMC: {imc:.2f} | Classificação: {classificacao}")
            y -= 15
            c.drawString(x_inicial, y, "-" * 80)
            y -= 20

        c.save()

        # Abrir o PDF automaticamente
        try:
            os.startfile(nome_arquivo)
        except Exception:
            pass

    def on_close(self):
        try:
            self.conexao.close()
        except:
            pass
        self.quit()


if __name__ == "__main__":
    app = App()
    app.mainloop()
