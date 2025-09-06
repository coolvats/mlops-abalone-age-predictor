import sys
from abaloneage.logging import logger


class PipelineException(Exception):
    def __init__(self, error_message, error_details: sys = None):
        super().__init__(str(error_message))
        self.error_message = error_message
        if error_details:
            _, _, exc_tb = error_details.exc_info()
            self.lineno = exc_tb.tb_lineno
            self.file_name = exc_tb.tb_frame.f_code.co_filename
        else:
            self.lineno = None
            self.file_name = None

    def __str__(self):
        return f"Error in script [{self.file_name}] line [{self.lineno}] message [{self.error_message}]"
        
if __name__=='__main__':
    try:
        logger.logging.info("Enter the try block")
        a=1/0
        print("This will not be printed",a)
    except Exception as e:
           raise PipelineException(e,sys)