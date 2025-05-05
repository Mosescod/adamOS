from apscheduler.schedulers.background import BackgroundScheduler
from knowledge.document_manager import DocumentManager
import atexit
import datetime

class KnowledgeUpdater:
    def __init__(self):
        self.docs = DocumentManager()
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(
            func=self.docs.build_knowledge_base,
            trigger="interval",
            weeks=1,  # Full scan weekly
            next_run_time=datetime.now()
        )
        self.scheduler.start()
        atexit.register(self.scheduler.shutdown)