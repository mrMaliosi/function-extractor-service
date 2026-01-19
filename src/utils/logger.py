import logging

class SimpleLogger:
    def __init__(self, name, log_file="errors.log"):
        # Создаем логгер
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Формат сообщений
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

        # 1. Обработчик для записи в файл
        file_handler = logging.FileHandler(name + "_" + log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        # 2. Обработчик для вывода в консоль
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO) # В консоль только важные сообщения
        console_handler.setFormatter(formatter)

        # Добавляем обработчики к логгеру
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger