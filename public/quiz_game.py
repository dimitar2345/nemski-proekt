import tkinter as tk
from tkinter import messagebox, ttk
import json
import random
from pathlib import Path

class MillionaireGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Wer wird Millionär?")
        self.root.geometry("900x700")
        self.root.configure(bg="#1a1a1a")
        
        # Награди
        self.prizes = [
            100, 150, 200, 250, 300, 500, 750, 1000, 1500, 2500, 
            5000, 10000, 20000, 50000, 100000
        ]
        
        # Жокери
        self.jokers = {
            '50:50': True,
            'public_help_1': True,
            'public_help_2': True
        }
        
        # Активен жокер за 50:50
        self.fifty_fifty_active = False
        self.disabled_answers = set()
        
        # Текущо състояние на играта
        self.current_question = 0
        self.questions = []
        self.current_answers = {}
        
        self.load_questions()
        self.setup_ui()
        self.show_question()
    
    def load_questions(self):
        """Зарежда въпросите от JSON файл"""
        questions_file = Path(__file__).parent / 'questions.json'
        
        try:
            with open(questions_file, 'r', encoding='utf-8') as f:
                self.questions = json.load(f)
            
            if len(self.questions) < 15:
                messagebox.showerror("Fehler", "Es werden mindestens 15 Fragen in questions.json benötigt!")
                self.root.quit()
            
            # Shuffle questions
            random.shuffle(self.questions)
            self.questions = self.questions[:15]
        
        except FileNotFoundError:
            messagebox.showerror("Fehler", "Die Datei questions.json wurde nicht gefunden!")
            self.root.quit()
        except json.JSONDecodeError:
            messagebox.showerror("Fehler", "Die Datei questions.json ist ungültig!")
            self.root.quit()
    
    def setup_ui(self):
        """Настройка на интерфейса"""
        # Горна лента с награди
        prize_frame = tk.Frame(self.root, bg="#1a1a1a")
        prize_frame.pack(pady=10)
        
        tk.Label(prize_frame, text="PREISE", font=("Arial", 12, "bold"), 
            fg="#FFD700", bg="#1a1a1a").pack()
        
        self.prize_labels = {}
        for i, prize in enumerate(self.prizes):
            fg_color = "#FFD700" if i == 0 else "#FFFFFF"
            self.prize_labels[i] = tk.Label(
                prize_frame, 
                text=f"{i+1}. {prize} €",
                font=("Arial", 9),
                fg=fg_color,
                bg="#1a1a1a"
            )
            self.prize_labels[i].pack()
        
        # Главна площ със въпроса и отговорите
        main_frame = tk.Frame(self.root, bg="#1a1a1a")
        main_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        
        # Въпрос
        self.question_label = tk.Label(
            main_frame,
            text="",
            font=("Arial", 14, "bold"),
            fg="#FFFFFF",
            bg="#1a1a1a",
            wraplength=700,
            justify=tk.LEFT
        )
        self.question_label.pack(pady=20)
        
        # Отговори
        self.answer_buttons = {}
        answers_frame = tk.Frame(main_frame, bg="#1a1a1a")
        answers_frame.pack(pady=20)
        
        for i, letter in enumerate(['А', 'Б', 'В', 'Г']):
            btn = tk.Button(
                answers_frame,
                text="",
                font=("Arial", 11),
                width=50,
                height=2,
                bg="#2a5a8a",
                fg="#FFFFFF",
                activebackground="#3a7aba",
                command=lambda l=letter: self.check_answer(l)
            )
            btn.pack(pady=5)
            self.answer_buttons[letter] = btn
        
        # Жокери
        joker_frame = tk.Frame(self.root, bg="#1a1a1a")
        joker_frame.pack(pady=10)
        
        tk.Label(joker_frame, text="JOKER:", font=("Arial", 11, "bold"), 
            fg="#FFD700", bg="#1a1a1a").pack()
        
        buttons_frame = tk.Frame(joker_frame, bg="#1a1a1a")
        buttons_frame.pack()
        
        self.joker_50_btn = tk.Button(
            buttons_frame,
            text="50:50",
            font=("Arial", 9),
            command=self.use_fifty_fifty,
            width=15,
            bg="#2a5a2a"
        )
        self.joker_50_btn.pack(side=tk.LEFT, padx=5)
        
        self.joker_public_1_btn = tk.Button(
            buttons_frame,
            text="Publikumsjoker 1",
            font=("Arial", 9),
            command=self.use_public_help_1,
            width=15,
            bg="#2a5a2a"
        )
        self.joker_public_1_btn.pack(side=tk.LEFT, padx=5)
        
        self.joker_public_2_btn = tk.Button(
            buttons_frame,
            text="Publikumsjoker 2",
            font=("Arial", 9),
            command=self.use_public_help_2,
            width=15,
            bg="#2a5a2a"
        )
        self.joker_public_2_btn.pack(side=tk.LEFT, padx=5)
        
        # Статус бар
        self.status_label = tk.Label(
            self.root,
            text="",
            font=("Arial", 10),
            fg="#FFFFFF",
            bg="#1a1a1a"
        )
        self.status_label.pack(pady=5)
    
    def show_question(self):
        """Показва текущия въпрос"""
        if self.current_question >= len(self.questions):
            messagebox.showinfo("Herzlichen Glückwunsch!", f"Du hast 100.000 € gewonnen! 🎉")
            self.root.quit()
            return
        
        # Актуализирай награди
        for i in range(15):
            if i < self.current_question:
                self.prize_labels[i].config(fg="#888888")
            elif i == self.current_question:
                self.prize_labels[i].config(fg="#FFD700")
            else:
                self.prize_labels[i].config(fg="#FFFFFF")
        
        question_data = self.questions[self.current_question]
        self.question_label.config(text=question_data['question'])
        
        # Разбъркай отговорите
        answers = list(question_data['answers'].items())
        random.shuffle(answers)
        self.current_answers = dict(answers)
        
        # Актуализирай напомощ при 50:50
        self.disabled_answers = set()
        self.fifty_fifty_active = False
        
        # Покажи отговорите
        for letter in ['А', 'Б', 'В', 'Г']:
            self.answer_buttons[letter].config(
                text=f"{letter}: {self.current_answers[letter]}",
                state=tk.NORMAL,
                bg="#2a5a8a"
            )
        
        # Актуализирай статус
        prize = self.prizes[self.current_question]
        self.status_label.config(text=f"Frage {self.current_question + 1}/15 | Gewinn: {prize} €")
        
        # Отключи жокерите ако са налични
        self.joker_50_btn.config(state=tk.NORMAL if self.jokers['50:50'] else tk.DISABLED)
        self.joker_public_1_btn.config(state=tk.NORMAL if self.jokers['public_help_1'] else tk.DISABLED)
        self.joker_public_2_btn.config(state=tk.NORMAL if self.jokers['public_help_2'] else tk.DISABLED)
    
    def check_answer(self, answer):
        """Проверява отговора"""
        if answer in self.disabled_answers:
            return
        
        correct = self.questions[self.current_question]['correct_answer']
        
        # Намери верния отговор в текущите отговори
        correct_letter = None
        for letter, text in self.current_answers.items():
            if text == self.questions[self.current_question]['answers'][correct]:
                correct_letter = letter
                break
        
        # Покажи отговор
        for letter in ['А', 'Б', 'В', 'Г']:
            if letter == correct_letter:
                self.answer_buttons[letter].config(bg="#2a8a2a")
            elif letter == answer:
                self.answer_buttons[letter].config(bg="#8a2a2a")
        
        if answer == correct_letter:
            messagebox.showinfo("Richtig!", f"Die richtige Antwort ist {correct_letter}!\nGewinn: {self.prizes[self.current_question]} €")
            self.current_question += 1
            self.show_question()
        else:
            messagebox.showerror(
                "Falsch!",
                f"Leider falsche Antwort.\nDie richtige Antwort ist {correct_letter}!\n\nDein Gewinn: {self.prizes[self.current_question - 1] if self.current_question > 0 else 0} €"
            )
            self.root.quit()
    
    def use_fifty_fifty(self):
        """50:50 жокер - премахва два грешни отговора"""
        if not self.jokers['50:50']:
            messagebox.showwarning("Joker", "Diesen Joker hast du bereits verwendet!")
            return
        
        if self.fifty_fifty_active:
            messagebox.showwarning("Joker", "50:50 ist bereits für diese Frage aktiv!")
            return
        
        correct = self.questions[self.current_question]['correct_answer']
        
        # Намери верния отговор в текущите отговори
        correct_letter = None
        wrong_letters = []
        
        for letter, text in self.current_answers.items():
            if text == self.questions[self.current_question]['answers'][correct]:
                correct_letter = letter
            else:
                wrong_letters.append(letter)
        
        # Избери два случайни грешни отговора за отключване
        random.shuffle(wrong_letters)
        to_disable = wrong_letters[:2]
        self.disabled_answers = set(to_disable)
        self.fifty_fifty_active = True
        
        # Деактивирай бутоните
        for letter in to_disable:
            self.answer_buttons[letter].config(state=tk.DISABLED, bg="#555555")
        
        self.jokers['50:50'] = False
        self.joker_50_btn.config(state=tk.DISABLED)
        messagebox.showinfo("50:50", "Zwei falsche Antworten wurden entfernt!")
    
    def use_public_help_1(self):
        """Помощ от публика 1 - съобщение с предположение"""
        if not self.jokers['public_help_1']:
            messagebox.showwarning("Joker", "Diesen Joker hast du bereits verwendet!")
            return
        
        correct = self.questions[self.current_question]['correct_answer']
        
        # Намери верния отговор
        correct_letter = None
        for letter, text in self.current_answers.items():
            if text == self.questions[self.current_question]['answers'][correct]:
                correct_letter = letter
                break
        
        messagebox.showinfo(
            "Publikumsmeinung",
            f"Ich denke, die richtige Antwort ist {correct_letter}"
        )
        
        self.jokers['public_help_1'] = False
        self.joker_public_1_btn.config(state=tk.DISABLED)
    
    def use_public_help_2(self):
        """Помощ от публика 2 - диаграма с проценти"""
        if not self.jokers['public_help_2']:
            messagebox.showwarning("Joker", "Diesen Joker hast du bereits verwendet!")
            return
        
        correct = self.questions[self.current_question]['correct_answer']
        
        # Намери верния отговор
        correct_letter = None
        for letter, text in self.current_answers.items():
            if text == self.questions[self.current_question]['answers'][correct]:
                correct_letter = letter
                break
        
        # Генерирай случайни проценти, правилния отговор е с най-голям процент
        percentages = {}
        remaining = 100
        letters = ['А', 'Б', 'В', 'Г']
        
        for letter in letters:
            if letter == correct_letter:
                percentages[letter] = 0
            else:
                percentages[letter] = random.randint(5, 25)
        
        percentages[correct_letter] = 100 - sum(percentages.values())
        
        message = "Publikumsdiagramm:\n\n"
        sorted_answers = sorted(percentages.items(), key=lambda x: x[1], reverse=True)
        for letter, percent in sorted_answers:
            bar = "█" * (percent // 5)
            message += f"{letter}: {bar} {percent}%\n"
        
        messagebox.showinfo("Publikumsdiagramm", message)
        
        self.jokers['public_help_2'] = False
        self.joker_public_2_btn.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    game = MillionaireGame(root)
    root.mainloop()
