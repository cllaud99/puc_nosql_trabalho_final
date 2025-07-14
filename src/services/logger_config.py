from loguru import logger
import os

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../logs')
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "puc_trabalho.log")

def configure_logger():
    """
    Configura o logger com saída colorida no console e arquivo com rotação diária.
    """
    logger.remove()  # Remove configuração padrão

    # Console colorido
    logger.add(
        sink=lambda msg: print(msg, end=''),  # print para suportar cores no terminal
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{module}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

    # Arquivo com rotação diária e compressão
    logger.add(
        LOG_FILE,
        rotation="00:00",  # rotaciona à meia-noite
        retention="7 days",  # mantém logs por 7 dias
        compression="zip",
        encoding="utf-8",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {module}:{line} - {message}"
    )

if __name__ == "__main__":
    configure_logger()
    logger.info("Logger configurado com loguru! Colorido no terminal e arquivo rotacionado.")
