import bluetooth
from tkinter import messagebox

bt_socket = None  # Глобальная переменная для хранения сокета Bluetooth

def scan_bluetooth_devices():
    try:
        devices = bluetooth.discover_devices(duration=8, lookup_names=True, flush_cache=True)
        return devices
    except bluetooth.BluetoothError as e:
        messagebox.showerror("Ошибка", f"Не удалось сканировать устройства: {e}")
        return []

def connect_bluetooth_device(device_address):
    global bt_socket
    try:
        bt_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        bt_socket.connect((device_address, 1))  # Подключаемся к устройству
        messagebox.showinfo("Успех", f"Успешно подключено к {device_address}")
    except bluetooth.BluetoothError as e:
        messagebox.showerror("Ошибка", f"Не удалось подключиться к устройству: {e}")
        bt_socket = None

def send_weight_via_bluetooth(weight_value):
    global bt_socket
    if bt_socket:
        try:
            bt_socket.send(f"Вес: {weight_value} кг\n")
        except bluetooth.BluetoothError as e:
            messagebox.showerror("Ошибка", f"Не удалось отправить данные: {e}")
            bt_socket = None
    else:
        messagebox.showwarning("Предупреждение", "Нет активного Bluetooth соединения.")

def close_bluetooth_connection():
    global bt_socket
    if bt_socket:
        try:
            bt_socket.close()
        except bluetooth.BluetoothError as e:
            messagebox.showerror("Ошибка", f"Не удалось закрыть соединение: {e}")
        finally:
            bt_socket = None
