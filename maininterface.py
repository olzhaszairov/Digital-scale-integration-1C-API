import serial
import tkinter as tk
from tkinter import messagebox
import threading
import time
import serial.tools.list_ports

# Флаг для контроля потока данных
running = False
selected_port = None

# Функция для получения доступных COM портов
def get_com_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

# Функция для чтения данных с весов
def read_weight(label):
    global running, selected_port
    try:
        with serial.Serial(selected_port, 9600, timeout=1) as ser:
            while running:
                if ser.in_waiting > 0:
                    raw_data = ser.read(ser.in_waiting)
                    decoded_data = raw_data.decode('ascii', errors='ignore')
                    cleaned_data = ''.join(char for char in decoded_data if char.isprintable() or char in ['.', 'k', 'g', 'c'])

                    # Поиск значения веса перед 'kg'
                    weight_start_index = cleaned_data.find('kg')
                    if weight_start_index != -1:
                        # Находим начало числового значения веса
                        weight_end_index = weight_start_index - 1
                        while weight_end_index >= 0 and (cleaned_data[weight_end_index].isdigit() or cleaned_data[weight_end_index] == '.'):
                            weight_end_index -= 1
                        weight_end_index += 1

                        weight_string = cleaned_data[weight_end_index:weight_start_index].strip()

                        try:
                            # Преобразуем строку в число
                            weight_value = float(weight_string)
                            label.config(text=f"Вес: {weight_value} кг")
                        except ValueError:
                            label.config(text="Ошибка: Невозможно преобразовать вес")
                    else:
                        label.config(text="Вес не найден")
                time.sleep(0.5)
    except serial.SerialException as e:
        messagebox.showerror("Ошибка", f"Не удалось открыть порт {selected_port}: {e}")

# Функция для старта потока чтения данных
def start_reading(label):
    global running, selected_port
    if selected_port:
        running = True
        thread = threading.Thread(target=read_weight, args=(label,))
        thread.start()
    else:
        messagebox.showerror("Ошибка", "Пожалуйста, выберите COM порт")

# Функция для остановки чтения данных
def stop_reading():
    global running
    running = False

# Функция для обновления выбранного COM порта
def update_port(port):
    global selected_port
    selected_port = port

# Создание окна с помощью tkinter
def create_window():
    window = tk.Tk()
    window.title("Чтение веса с весов")

    # Метка для отображения веса
    label = tk.Label(window, text="Вес: -- кг", font=("Arial", 24))
    label.pack(pady=20)

    # Получение списка COM портов
    com_ports = get_com_ports()

    # Если нет доступных COM портов, выводим сообщение
    if not com_ports:
        messagebox.showerror("Ошибка", "Не найдено доступных COM портов")
        window.destroy()
        return

    # Создание выпадающего списка для выбора COM порта
    selected_port_var = tk.StringVar(window)
    selected_port_var.set(com_ports[0])  # Устанавливаем первый порт по умолчанию
    selected_port = com_ports[0]  # Присваиваем выбранный порт

    port_menu = tk.OptionMenu(window, selected_port_var, *com_ports, command=update_port)
    port_menu.pack(pady=10)

    # Кнопка "Старт"
    start_button = tk.Button(window, text="Старт", command=lambda: start_reading(label), font=("Arial", 14))
    start_button.pack(pady=10)

    # Кнопка "Стоп"
    stop_button = tk.Button(window, text="Стоп", command=stop_reading, font=("Arial", 14))
    stop_button.pack(pady=10)

    window.protocol("WM_DELETE_WINDOW", on_closing)
    window.mainloop()

# Функция для корректного закрытия окна
def on_closing():
    global running
    if running:
        if messagebox.askokcancel("Выход", "Программа все еще работает, хотите выйти?"):
            running = False
            window.destroy()
    else:
        window.destroy()

if __name__ == "__main__":
    create_window()
