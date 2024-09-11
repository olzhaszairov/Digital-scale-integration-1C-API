import serial

# Настройки порта
COM_PORT = 'COM7'  # Укажите свой COM порт
BAUD_RATE = 9600   # Скорость передачи данных (должна совпадать с настройками устройства)

def main():
    # Открытие порта
    with serial.Serial(COM_PORT, BAUD_RATE, timeout=1) as ser:
        print(f"Порт {COM_PORT} успешно открыт.")

        while True:
            if ser.in_waiting > 0:
                # Чтение данных
                raw_data = ser.read(ser.in_waiting)

                # Декодирование данных в строку ASCII
                decoded_data = raw_data.decode('ascii', errors='ignore')

                # Печать необработанных данных для отладки
                print(f"Полученные данные (необработанные): {decoded_data}")

                # Очистка данных от управляющих символов и пробелов
                cleaned_data = ''.join(char for char in decoded_data if char.isprintable() or char in ['.', 'k', 'g', 'c'])

                # Печать очищенных данных для отладки
                print(f"Очищенные данные: {cleaned_data}")

                # Поиск веса в данных
                weight_start_index = cleaned_data.find('kg')
                if weight_start_index != -1:
                    weight_end_index = weight_start_index - 1
                    while weight_end_index >= 0 and (cleaned_data[weight_end_index].isdigit() or cleaned_data[weight_end_index] == '.'):
                        weight_end_index -= 1
                    weight_end_index += 1

                    weight_string = cleaned_data[weight_end_index:weight_start_index].strip()

                    try:
                        weight_value = float(weight_string)
                        print(f"Извлеченный вес: {weight_value} кг")
                    except ValueError:
                        print("Не удалось преобразовать строку веса в число.")
                else:
                    print("Не найдено значения веса в данных.")

if __name__ == "__main__":
    main()
