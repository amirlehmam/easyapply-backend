import subprocess
import threading
import os
import time
import logging

class BotRunner:
    def __init__(self, script_path, log_path):
        self.script_path = script_path
        self.log_path = log_path
        self.process = None
        self.thread = None
        self.running = False

    def start(self):
        if self.running:
            print("BotRunner: already running")
            logging.info("BotRunner: already running")
            return False
        print(f"BotRunner: starting bot with script {self.script_path}")
        logging.info(f"BotRunner: starting bot with script {self.script_path}")
        self.running = True
        self.thread = threading.Thread(target=self._run_bot)
        self.thread.start()
        return True

    def _run_bot(self):
        try:
            print(f"BotRunner: running subprocess in {os.path.dirname(self.script_path)}")
            logging.info(f"BotRunner: running subprocess in {os.path.dirname(self.script_path)}")
            with open(self.log_path, 'a', encoding='utf-8') as log_file:
                self.process = subprocess.Popen([
                    'python', self.script_path
                ], stdout=log_file, stderr=log_file, cwd=os.path.dirname(self.script_path))
                self.process.wait()
        except Exception as e:
            print(f"BotRunner: Exception in _run_bot: {e}")
            logging.error(f"BotRunner: Exception in _run_bot: {e}")
        self.running = False

    def stop(self):
        if self.process and self.running:
            self.process.terminate()
            self.running = False
            return True
        return False

    def is_running(self):
        return self.running 