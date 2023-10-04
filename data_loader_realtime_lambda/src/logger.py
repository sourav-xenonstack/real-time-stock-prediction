"""
Logger object for logging
"""
# import dependencies
import logging

def create_logger(logger_name, log_level=logging.INFO):
    """
    The function `create_logger` creates a logger object with a specified name and logging level, and
    adds a console handler with a formatter to the logger.
    
    :param logger_name: The logger_name parameter is a string that specifies the name of the logger.
    This name is used to identify the logger when logging messages
    :param log_level: The log_level parameter is used to set the logging level for the logger. It
    determines the severity of the messages that will be logged. The available logging levels are:
    :return: a logger object.
    """
    # create logger
    logger = logging.getLogger(logger_name)

    # set logging level
    logger.setLevel(log_level)

    # create console handler and set level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to console handler
    console_handler.setFormatter(formatter)

    # add console handler to logger
    logger.addHandler(console_handler)

    return logger