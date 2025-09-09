import uuid, os, json
from concurrent.futures import ThreadPoolExecutor
from .utils import ocr_from_image, ocr_from_pdf, parse_invoice_text
from . import db
from .models import ScanResult

_executor = ThreadPoolExecutor(max_workers=2)
_task_status = {}

class TaskStatusStore:
    @staticmethod
    def create(task_id):
        _task_status[task_id] = {"status":"pending", "processed":0, "total":0, "results": []}
        return _task_status[task_id]
    @staticmethod
    def update(task_id, **kwargs):
        _task_status[task_id].update(kwargs)
    @staticmethod
    def get_status(task_id):
        return _task_status.get(task_id, {"status":"not_found"})

def _process_file(file_storage, user_id):
    filename = file_storage.filename
    tmp_path = os.path.join("uploads", f"{uuid.uuid4().hex}_{filename}")
    file_storage.save(tmp_path)
    if filename.lower().endswith(".pdf"):
        text = ocr_from_pdf(tmp_path)
    else:
        text = ocr_from_image(tmp_path)
    parsed = parse_invoice_text(text)
    sr = ScanResult(user_id=user_id, filename=filename, raw_text=text, parsed=json.dumps(parsed))
    db.session.add(sr)
    db.session.commit()
    return {"filename": filename, "parsed": parsed, "id": sr.id}

def submit_background_task(file_list, user_id):
    task_id = uuid.uuid4().hex
    TaskStatusStore.create(task_id)
    TaskStatusStore.update(task_id, total=len(file_list))
    def runner(files, uid, tid):
        TaskStatusStore.update(tid, status="running")
        processed = 0
        for f in files:
            try:
                res = _process_file(f, uid)
                TaskStatusStore.get_status(tid)["results"].append(res)
            except Exception as e:
                TaskStatusStore.get_status(tid)["results"].append({"error": str(e)})
            processed += 1
            TaskStatusStore.update(tid, processed=processed)
        TaskStatusStore.update(tid, status="done")
    _executor.submit(runner, file_list, user_id, task_id)
    return task_id
