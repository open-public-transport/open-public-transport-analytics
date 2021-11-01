import os


class FileLogger:

    def log_line(self, results_path, message):
        # Make results path
        os.makedirs(results_path, exist_ok=True)

        with open(results_path + "/receipt.txt", "a") as log_file:
            log_file.write(message + "\n")
            log_file.close()
