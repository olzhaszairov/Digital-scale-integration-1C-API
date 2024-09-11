import serial
import tkinter as tk
from tkinter import messagebox, simpledialog
import threading
import time
import serial.tools.list_ports
from bluetooth_module import scan_bluetooth_devices, connect_bluetooth_device, send_weight_via_bluetooth, close_bluetooth_connection

# Глобальные переменные
running = False
selected_port = None

def get_com_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def read_weight(label):
    global running, selected_port
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
                            weight_value = float(weight_string)
                            label.config(text=f"Вес: {weight_value} кг")
                            send_weight_via_bluetooth(weight_value)  # Отправляем вес по Bluetooth
                        except ValueError:
                            label.config(text="Ошибка: Невозможно преобразовать вес")
                    else:
                        label.config(text="Вес не найден")
                time.sleep(0.5)
    except serial.SerialException as e:
        messagebox.showerror("Ошибка", f"Не удалось открыть порт {selected_port}: {e}")

def start_reading(label):
    global running, selected_port
    if selected_port:
        running = True
        thread = threading.Thread(target=read_weight, args=(label,))
        thread.start()
    else:
        messagebox.showerror("Ошибка", "Пожалуйста, выберите COM порт")

def stop_reading():
    global running
    running = False

def update_port(port):
    global selected_port
    selected_port = port

def scan_and_select_bluetooth_device():
    devices = scan_bluetooth_devices()
    if not devices:
        messagebox.showinfo("Нет устройств", "Не обнаружено Bluetooth-устройств.")
        return

    # Создаем окно для выбора устройства
    device_list = [f"{name} ({addr})" for addr, name in devices]
    selected_device = simpledialog.askstring("Выбор устройства", "Выберите устройство:\n" + "\n".join(device_list))

    if selected_device:
        # Извлекаем адрес устройства
        address = selected_device.split(' (')[1].strip(')')
        connect_bluetooth_device(address)

def create_window():
    global window
    window = tk.Tk()
    window.title("Чтение веса с весов")

    # Метка для отображения веса
    label = tk.Label(window, text="Вес: -- кг", font=("Arial", 24))
    label.pack(pady=20)

    # Получение списка COM портов
    com_ports = get_com_ports()

    if not com_ports:
        messagebox.showerror("Ошибка", "Не найдено доступных COM портов")
        window.destroy()
        return

    selected_port_var = tk.StringVar(window)
    selected_port_var.set(com_ports[0])
    selected_port = com_ports[0]

    port_menu = tk.OptionMenu(window, selected_port_var, *com_ports, command=update_port)
    port_menu.pack(pady=10)

    # Кнопка "Старт"
    start_button = tk.Button(window, text="Старт", command=lambda: start_reading(label), font=("Arial", 14))
    start_button.pack(pady=10)

    # Кнопка "Стоп"
    stop_button = tk.Button(window, text="Стоп", command=stop_reading, font=("Arial", 14))
    stop_button.pack(pady=10)

    # Кнопка для подключения к Bluetooth
    bt_scan_button = tk.Button(window, text="Сканировать Bluetooth", command=scan_and_select_bluetooth_device, font=("Arial", 14))
    bt_scan_button.pack(pady=10)

    # Кнопка для закрытия Bluetooth соединения
    bt_disconnect_button = tk.Button(window, text="Отключить Bluetooth", command=close_bluetooth_connection, font=("Arial", 14))
    bt_disconnect_button.pack(pady=10)

    window.protocol("WM_DELETE_WINDOW", on_closing)
    window.mainloop()

def on_closing():
    global running
    if running:
        if messagebox.askokcancel("Выход", "Программа все еще работает, хотите выйти?"):
            running = False
            close_bluetooth_connection()
            window.destroy()
    else:
        close_bluetooth_connection()
        window.destroy()

if __name__ == "__main__":
    create_window()