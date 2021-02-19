import logging


def setup_logger(logger_name, log_file, level):
    logger = logging.getLogger(logger_name)
    formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
    file_handler = logging.FileHandler(filename=log_file, encoding="utf-8", mode="w")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(level)

    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


def discord_logger():
    logger = logging.getLogger("discord")
    logger.setLevel(logging.ERROR)
    handler = logging.FileHandler(filename="errors.log", encoding="utf-8", mode="w")
    handler.setFormatter(
        logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
    )
    logger.addHandler(handler)


errorLogger = setup_logger("errorLog", "errors.log", logging.ERROR)
infoLogger = setup_logger("discord", "info.log", logging.INFO)
