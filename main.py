import json
import os
from typing import List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


DATA_FILE = "library_data.json"

@dataclass
class Book:
    id: int
    title: str
    author: str
    genre: str
    year: int
    description: str
    is_read: bool = False
    is_favorite: bool = False
    added_date: str = None

    def __post_init__(self):
        if self.added_date is None:
            self.added_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class Library:

    def __init__(self):
        self.books: List[Book] = []
        self.next_id = 1
        self.load_from_file()

    def add_book(self, title: str, author: str, genre: str, year: int, description: str) -> Book:
        book = Book(
            id=self.next_id,
            title=title,
            author=author,
            genre=genre,
            year=year,
            description=description
        )
        self.books.append(book)
        self.next_id += 1
        self.save_to_file()
        return book

    def get_all_books(self) -> List[Book]:
        return self.books

    def get_book_by_id(self, book_id: int) -> Optional[Book]:
        for book in self.books:
            if book.id == book_id:
                return book
        return None

    def delete_book(self, book_id: int) -> bool:
        for i, book in enumerate(self.books):
            if book.id == book_id:
                del self.books[i]
                self.save_to_file()
                return True
        return False

    def toggle_read_status(self, book_id: int) -> bool:
        book = self.get_book_by_id(book_id)
        if book:
            book.is_read = not book.is_read
            self.save_to_file()
            return True
        return False

    def toggle_favorite(self, book_id: int) -> bool:
        book = self.get_book_by_id(book_id)
        if book:
            book.is_favorite = not book.is_favorite
            self.save_to_file()
            return True
        return False

    def get_favorites(self) -> List[Book]:
        return [book for book in self.books if book.is_favorite]

    def search_books(self, query: str) -> List[Book]:
        query = query.lower()
        results = []
        for book in self.books:
            if (query in book.title.lower() or
                    query in book.author.lower() or
                    query in book.description.lower()):
                results.append(book)
        return results

    def sort_books(self, key: str, reverse: bool = False) -> List[Book]:
        sort_keys = {
            'title': lambda b: b.title.lower(),
            'author': lambda b: b.author.lower(),
            'year': lambda b: b.year,
            'genre': lambda b: b.genre.lower()
        }

        if key in sort_keys:
            return sorted(self.books, key=sort_keys[key], reverse=reverse)
        return self.books

    def filter_books(self, genre: Optional[str] = None, is_read: Optional[bool] = None) -> List[Book]:
        filtered = self.books

        if genre:
            filtered = [b for b in filtered if b.genre.lower() == genre.lower()]

        if is_read is not None:
            filtered = [b for b in filtered if b.is_read == is_read]

        return filtered

    def save_to_file(self):
        data = {
            'next_id': self.next_id,
            'books': [asdict(book) for book in self.books]
        }

        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_from_file(self):
        if not os.path.exists(DATA_FILE):
            return

        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.next_id = data.get('next_id', 1)
            self.books = []

            for book_data in data.get('books', []):
                self.books.append(Book(**book_data))
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Ошибка при загрузке данных: {e}")
            self.books = []
            self.next_id = 1


class ConsoleUI:

    def __init__(self):
        self.library = Library()

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self, title: str):
        print("=" * 60)
        print(f"{title:^60}")
        print("=" * 60)

    def print_book(self, book: Book):
        status_read = "✓" if book.is_read else "✗"
        status_fav = "★" if book.is_favorite else "☆"

        print(f"\nID: {book.id}")
        print(f"Название: {book.title}")
        print(f"Автор: {book.author}")
        print(f"Жанр: {book.genre}")
        print(f"Год: {book.year}")
        print(f"Описание: {book.description}")
        print(f"Прочитана: {status_read} | Избранное: {status_fav}")
        print(f"Дата добавления: {book.added_date}")
        print("-" * 40)

    def print_books(self, books: List[Book], title: str = "Список книг"):
        self.print_header(title)

        if not books:
            print("\nБиблиотека пуста!")
            return

        for book in books:
            self.print_book(book)

        print(f"\nВсего книг: {len(books)}")

    def get_input(self, prompt: str, required: bool = True) -> str:
        while True:
            value = input(prompt).strip()
            if not required or value:
                return value
            print("Это поле обязательно для заполнения!")

    def get_int_input(self, prompt: str, min_val: int = None, max_val: int = None) -> Optional[int]:
        while True:
            try:
                value = input(prompt).strip()
                if not value:
                    return None

                num = int(value)

                if min_val is not None and num < min_val:
                    print(f"Значение должно быть не меньше {min_val}")
                    continue

                if max_val is not None and num > max_val:
                    print(f"Значение должно быть не больше {max_val}")
                    continue

                return num
            except ValueError:
                print("Пожалуйста, введите число!")

    def add_book_menu(self):
        self.clear_screen()
        self.print_header("ДОБАВЛЕНИЕ НОВОЙ КНИГИ")

        title = self.get_input("Название книги: ")
        author = self.get_input("Автор: ")
        genre = self.get_input("Жанр: ")

        year = self.get_int_input("Год издания: ", min_val=1000, max_val=datetime.now().year)
        if year is None:
            year = datetime.now().year

        description = self.get_input("Краткое описание: ")

        book = self.library.add_book(title, author, genre, year, description)
        print(f"\nКнига успешно добавлена с ID: {book.id}")
        input("\nНажмите Enter для продолжения...")

    def view_books_menu(self):
        self.clear_screen()
        self.print_header("ПРОСМОТР КНИГ")

        print("\n1. Показать все книги")
        print("2. Сортировать книги")
        print("3. Фильтровать книги")
        print("4. Вернуться в главное меню")

        choice = input("\nВыберите действие (1-4): ")

        if choice == '1':
            self.print_books(self.library.get_all_books())
            input("\nНажмите Enter для продолжения...")

        elif choice == '2':
            self.sort_books_menu()

        elif choice == '3':
            self.filter_books_menu()

    def sort_books_menu(self):
        self.clear_screen()
        self.print_header("СОРТИРОВКА КНИГ")

        print("\nСортировать по:")
        print("1. Названию")
        print("2. Автору")
        print("3. Году издания")
        print("4. Жанру")

        choice = input("\nВыберите критерий (1-4): ")

        sort_keys = {
            '1': 'title',
            '2': 'author',
            '3': 'year',
            '4': 'genre'
        }

        if choice in sort_keys:
            order = input("Порядок (1 - по возрастанию, 2 - по убыванию): ")
            reverse = (order == '2')

            books = self.library.sort_books(sort_keys[choice], reverse)
            self.print_books(books, "ОТСОРТИРОВАННЫЙ СПИСОК КНИГ")
            input("\nНажмите Enter для продолжения...")

    def filter_books_menu(self):
        self.clear_screen()
        self.print_header("ФИЛЬТРАЦИЯ КНИГ")

        genre = input("Жанр (оставьте пустым для пропуска): ").strip()
        if not genre:
            genre = None

        print("\nСтатус прочтения:")
        print("1. Только прочитанные")
        print("2. Только непрочитанные")
        print("3. Все книги")

        status_choice = input("Выберите (1-3): ")

        is_read = None
        if status_choice == '1':
            is_read = True
        elif status_choice == '2':
            is_read = False

        books = self.library.filter_books(genre, is_read)
        self.print_books(books, "ОТФИЛЬТРОВАННЫЙ СПИСОК КНИГ")
        input("\nНажмите Enter для продолжения...")

    def manage_book_menu(self):
        self.clear_screen()
        self.print_header("УПРАВЛЕНИЕ КНИГОЙ")

        book_id = self.get_int_input("Введите ID книги: ")
        if book_id is None:
            return

        book = self.library.get_book_by_id(book_id)
        if not book:
            print("Книга с таким ID не найдена!")
            input("\nНажмите Enter для продолжения...")
            return

        self.print_book(book)

        print("\n1. Изменить статус прочтения")
        print("2. Добавить/удалить из избранного")
        print("3. Удалить книгу")
        print("4. Вернуться")

        choice = input("\nВыберите действие (1-4): ")

        if choice == '1':
            self.library.toggle_read_status(book_id)
            print("Статус прочтения изменен!")

        elif choice == '2':
            self.library.toggle_favorite(book_id)
            print("Статус избранного изменен!")

        elif choice == '3':
            confirm = input("Вы уверены, что хотите удалить книгу? (да/нет): ")
            if confirm.lower() in ['да', 'yes', 'y']:
                self.library.delete_book(book_id)
                print("Книга удалена!")

        input("\nНажмите Enter для продолжения...")

    def favorites_menu(self):
        self.clear_screen()
        favorites = self.library.get_favorites()
        self.print_books(favorites, "ИЗБРАННЫЕ КНИГИ")
        input("\nНажмите Enter для продолжения...")

    def search_menu(self):
        self.clear_screen()
        self.print_header("ПОИСК КНИГ")

        query = self.get_input("Введите ключевое слово для поиска: ")
        results = self.library.search_books(query)

        self.print_books(results, f"РЕЗУЛЬТАТЫ ПОИСКА: '{query}'")
        input("\nНажмите Enter для продолжения...")

    def run(self):
        while True:
            self.clear_screen()
            self.print_header("T-БИБЛИОТЕКА")

            print("\n1. Добавить книгу")
            print("2. Просмотреть книги")
            print("3. Управление книгой")
            print("4. Избранные книги")
            print("5. Поиск книг")
            print("6. Выход")

            choice = input("\nВыберите действие (1-6): ")

            if choice == '1':
                self.add_book_menu()
            elif choice == '2':
                self.view_books_menu()
            elif choice == '3':
                self.manage_book_menu()
            elif choice == '4':
                self.favorites_menu()
            elif choice == '5':
                self.search_menu()
            elif choice == '6':
                print("\nСпасибо за использование T-Библиотеки!")
                break
            else:
                print("\nНеверный выбор!")
                input("Нажмите Enter для продолжения...")


def main():
    ui = ConsoleUI()
    ui.run()

if __name__ == "__main__":
    main()