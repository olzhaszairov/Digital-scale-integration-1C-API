import serial
import tkinter as tk
from tkinter import messagebox
import threading
import time
import serial.tools.list_ports
import qrcode
from PIL import Image, ImageTk

# Глобальные переменные
running = False
selected_port = None
latest_weight = None

def get_com_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def read_weight(label):
    global running, selected_port, latest_weight
    try:
        with serial.Serial(selected_port, 9600, timeout=1) as ser:
            while running:
                if ser.in_waiting > 0:
                    raw_data = ser.read(ser.in_waiting)
                    decoded_data = raw_data.decode('ascii', errors='ignore')
                    cleaned_data = ''.join(char for char in decoded_data if char.isprintable() or char in ['.', 'k', 'g', 'c'])

                    weight_start_index = cleaned_data.find('kg')
                    if weight_start_index != -1:
                        weight_end_index = weight_start_index - 1
                        while weight_end_index >= 0 and (cleaned_data[weight_end_index].isdigit() or cleaned_data[weight_end_index] == '.'):
                            weight_end_index -= 1
                        weight_end_index += 1

                        weight_string = cleaned_data[weight_end_index:weight_start_index].strip()

                        try:
                            latest_weight = float(weight_string)
                        except ValueError:
                            latest_weight = None
                    else:
                        latest_weight = None

                    # Отображение и запись в файл
                    show_current_weight(label)
                    write_weight_to_file()

                time.sleep(5)
    except serial.SerialException as e:
        messagebox.showerror("Ошибка", f"Не удалось открыть порт {selected_port}: {e}")

def toggle_reading(label, button):
    global running, selected_port
    if running:
        # Остановить чтение данных
        running = False
        button.config(text="Старт")
    else:
        if selected_port:
            # Начать чтение данных
            running = True
            button.config(text="Стоп")
            thread = threading.Thread(target=read_weight, args=(label,))
            thread.start()
        else:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите COM порт")

def update_port(port):
    global selected_port
    selected_port = port

def show_current_weight(label):
    if latest_weight is not None:
        weight_text = f"Вес: {latest_weight} кг"
        label.config(text=weight_text)
        update_qr_code(weight_text)
    else:
        label.config(text="Ошибка: Невозможно получить вес")

def update_qr_code(weight_text):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(weight_text)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')

    qr_image = ImageTk.PhotoImage(img)
    qr_label.config(image=qr_image)
    qr_label.image = qr_image

def write_weight_to_file():
    if latest_weight is not None:
        with open("weights.txt", "a") as file:
            file.write(f"Вес: {latest_weight} кг\n")

def create_window():
    global window, qr_label, selected_port
    window = tk.Tk()
    window.title("Чтение веса с весов")

    # Метка для отображения веса
    label = tk.Label(window, text="Вес: -- кг", font=("Arial", 24))
    label.pack(pady=20)

    # Метка для отображения QR-кода
    qr_label = tk.Label(window)
    qr_label.pack(pady=20)

    # Получение списка COM портов
    com_ports = get_com_ports()

    if not com_ports:
        messagebox.showerror("Ошибка", "Не найдено доступных COM портов")
        window.destroy()
        return
    elif len(com_ports) == 1:
        # Если найден только один COM порт, выбираем его автоматически
        selected_port = com_ports[0]
    else:
        # Если найдено несколько COM портов, создаем выпадающее меню для выбора
        selected_port_var = tk.StringVar(window)
        selected_port_var.set(com_ports[0])  # Устанавливаем первый порт по умолчанию
        selected_port = com_ports[0]

        port_menu = tk.OptionMenu(window, selected_port_var, *com_ports, command=update_port)
        port_menu.pack(pady=10)

    # Кнопка "Старт/Стоп"
    start_stop_button = tk.Button(window, text="Старт", command=lambda: toggle_reading(label, start_stop_button), font=("Arial", 14))
    start_stop_button.pack(pady=10)

    window.protocol("WM_DELETE_WINDOW", on_closing)
    window.mainloop()

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
