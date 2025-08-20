import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image
import os
import zipfile
import shutil
import math

class SpritesheetCreator(TkinterDnD.Tk):
    """
    A simple Python application with a GUI to create a spritesheet from images.
    It supports drag-and-drop of individual files, folders, or ZIP archives.
    """
    def __init__(self):
        super().__init__()
        self.title("Створення спрайт-листів")
        self.geometry("600x400")
        self.config(bg="#f0f0f0")
        self.resizable(False, False) # Заборонити зміну розміру вікна

        # Set up drag and drop
        self.dnd_bind("<<Drop>>", self.handle_drop)

        # UI elements
        self.create_widgets()

    def create_widgets(self):
        """
        Creates all the widgets for the application's GUI.
        """
        main_frame = ttk.Frame(self, padding="20", style='TFrame')
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Drop area
        # NOTE: tkinter does not support "dashed" relief. Changed to "solid".
        drop_area = tk.Label(main_frame, text="Перетягніть сюди файли, теку або ZIP-архів",
                             font=("Arial", 14), bg="#e0e0e0", fg="#555",
                             relief="solid", bd=4, justify="center")
        drop_area.pack(expand=True, fill="both", pady=20)
        drop_area.drop_target_register(DND_FILES)
        drop_area.dnd_bind("<<Drop>>", self.handle_drop)

        # Export format selection
        format_frame = ttk.Frame(main_frame)
        format_frame.pack(pady=10)

        format_label = ttk.Label(format_frame, text="Формат експорту:", font=("Arial", 12))
        format_label.pack(side=tk.LEFT, padx=(0, 10))

        self.export_format = tk.StringVar(value="PNG")
        
        png_radio = ttk.Radiobutton(format_frame, text="PNG", variable=self.export_format, value="PNG")
        png_radio.pack(side=tk.LEFT, padx=5)
        
        webp_radio = ttk.Radiobutton(format_frame, text="WEBP", variable=self.export_format, value="WEBP")
        webp_radio.pack(side=tk.LEFT, padx=5)

        # Status label
        self.status_label = ttk.Label(main_frame, text="Очікую на файли...",
                                      font=("Arial", 12), foreground="blue")
        self.status_label.pack(pady=10)

        # Create a style for the frame
        style = ttk.Style(self)
        style.configure('TFrame', background='#f0f0f0')

    def handle_drop(self, event):
        """
        Handles the file/folder drop event.
        It identifies if a file, directory, or zip archive was dropped and
        initiates the spritesheet creation process.
        """
        path = event.data.strip('{}').replace('\\', '/')
        self.status_label.config(text="Обробка...", foreground="orange")
        self.update_idletasks()

        if os.path.isdir(path):
            base_name = os.path.basename(path)
            self.process_directory(path, base_name)
        elif os.path.isfile(path):
            if path.lower().endswith('.zip'):
                base_name = os.path.splitext(os.path.basename(path))[0]
                self.process_zip(path, base_name)
            elif path.lower().endswith(('.png', '.webp')):
                base_name = os.path.splitext(os.path.basename(path))[0]
                self.process_files([path], os.path.dirname(path), base_name)
            else:
                self.status_label.config(text="Непідтримуваний формат файлу.", foreground="red")
        else:
            self.status_label.config(text="Невірний шлях.", foreground="red")

    def process_directory(self, dir_path, base_name):
        """
        Processes a dropped directory to find valid image files.
        """
        try:
            image_files = []
            # Use os.walk to find all files recursively in subdirectories
            for root, _, files in os.walk(dir_path):
                for filename in sorted(files):
                    if filename.lower().endswith(('.png', '.webp')):
                        image_files.append(os.path.join(root, filename))
            
            if not image_files:
                self.status_label.config(text="У вибраній теці не знайдено спрайтів.", foreground="red")
                return

            # Call process_files with the correct output directory
            self.process_files(image_files, dir_path, base_name=base_name)

        except Exception as e:
            self.status_label.config(text=f"Помилка при обробці теки: {e}", foreground="red")

    def process_zip(self, zip_path, base_name):
        """
        Extracts a zip archive to a temporary directory and processes the images.
        """
        temp_dir_base = os.path.join(os.path.dirname(zip_path), "temp_sprites")
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir_base)
            
            # Find the actual directory with extracted files
            extracted_contents = os.listdir(temp_dir_base)
            if len(extracted_contents) == 1 and os.path.isdir(os.path.join(temp_dir_base, extracted_contents[0])):
                # If there's a single subdirectory, use it
                temp_dir = os.path.join(temp_dir_base, extracted_contents[0])
            else:
                # Otherwise, use the base directory
                temp_dir = temp_dir_base
            
            # Use the directory of the original zip file for the final spritesheet output
            output_dir = os.path.dirname(zip_path)
            self.process_files(self.get_files_from_dir(temp_dir), default_output_dir=output_dir, output_dir=output_dir, base_name=base_name)

        except Exception as e:
            self.status_label.config(text=f"Помилка при розпакуванні ZIP-архіву: {e}", foreground="red")
        finally:
            if os.path.exists(temp_dir_base):
                shutil.rmtree(temp_dir_base)

    def get_files_from_dir(self, dir_path):
        """
        Helper function to get all image files from a directory recursively.
        """
        image_files = []
        for root, _, files in os.walk(dir_path):
            for filename in sorted(files):
                if filename.lower().endswith(('.png', '.webp')):
                    image_files.append(os.path.join(root, filename))
        return image_files

    # Added an optional output_dir parameter to handle zip file case
    def process_files(self, file_paths, default_output_dir, output_dir=None, base_name="spritesheet"):
        """
        Creates the spritesheet from a list of image file paths.
        The images are sorted by name before being processed.
        The layout is now a grid instead of a single row.
        """
        if output_dir is None:
            output_dir = default_output_dir

        try:
            if not file_paths:
                self.status_label.config(text="Не знайдено файлів для обробки.", foreground="red")
                return

            images = []
            for path in sorted(file_paths):
                try:
                    img = Image.open(path).convert("RGBA")
                    images.append(img)
                except Exception:
                    print(f"Помилка при відкритті файлу: {path}") # For debugging
            
            if not images:
                self.status_label.config(text="Жодного валідного спрайта не знайдено.", foreground="red")
                return

            # Determine the maximum width and height for a single sprite
            max_sprite_width = max(img.width for img in images)
            max_sprite_height = max(img.height for img in images)
            
            # --- New grid logic ---
            num_sprites = len(images)
            # Calculate the number of columns to make the sheet as square as possible.
            cols = math.ceil(math.sqrt(num_sprites))
            # Calculate the number of rows needed.
            rows = math.ceil(num_sprites / cols)

            # Calculate the total dimensions of the new spritesheet.
            total_width = cols * max_sprite_width
            total_height = rows * max_sprite_height

            spritesheet = Image.new('RGBA', (total_width, total_height))

            for i, img in enumerate(images):
                # Calculate the column and row index for the current image.
                col = i % cols
                row = i // cols
                
                # Calculate the x and y offsets.
                x_offset = col * max_sprite_width
                y_offset = row * max_sprite_height
                
                # Paste the image onto the spritesheet.
                spritesheet.paste(img, (x_offset, y_offset))

            # Get the selected export format
            export_format = self.export_format.get()
            output_filename = f"{base_name}_sh_{rows}x{cols}.{export_format.lower()}"
            output_path = os.path.join(output_dir, output_filename)
            spritesheet.save(output_path, export_format)

            # Update the status label with the new information
            self.status_label.config(text=f"Готово! Спрайт-лист збережено як {output_path}. Рядків: {rows}, Стовпчиків: {cols}",
                                     foreground="green")
            
            # Update the success message box
            messagebox.showinfo("Готово!", f"Спрайт-лист успішно створено:\nРядків: {rows}\nСтовпчиків: {cols}\n\nШлях: {output_path}")

        except Exception as e:
            self.status_label.config(text=f"Помилка: {e}", foreground="red")
            messagebox.showerror("Помилка", f"Сталася помилка:\n{e}")

if __name__ == "__main__":
    # Check for required libraries
    try:
        from tkinterdnd2 import TkinterDnD
    except ImportError:
        messagebox.showerror("Відсутня бібліотека",
                             "Для перетягування файлів потрібно встановити 'tkinterdnd2'.\n"
                             "Виконайте: pip install tkinterdnd2")
        exit()

    try:
        from PIL import Image
    except ImportError:
        messagebox.showerror("Відсутня бібліотека",
                             "Для обробки зображень потрібно встановити 'Pillow'.\n"
                             "Виконайте: pip install Pillow")
        exit()

    app = SpritesheetCreator()
    app.mainloop()
