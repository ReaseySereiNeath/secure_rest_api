import json
import logging

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "time": self.formatTime(record, "%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
            "message": record.getMessage(),
        }

        # Add extra context if present
        if hasattr(record, "user"):
            log_entry["user"] = record.user
        if hasattr(record, "path"):
            log_entry["path"] = record.path
        if hasattr(record, "method"):
            log_entry["method"] = record.method
        if hasattr(record, "status_code"):
            log_entry["status_code"] = record.status_code
        if hasattr(record, "process_time"):
            log_entry["process_time"] = getattr(record, "process_time")
        if hasattr(record, "exception"):
            log_entry["exception"] = record.exception

        return json.dumps(log_entry)
