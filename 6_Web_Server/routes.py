from flask import Blueprint, request
from service import service_query_capture_log
from config_loader import load_config
from logger import setup_logger

bp = Blueprint('api', __name__)

logger = setup_logger()

# 查詢版本號
@bp.route('/api/version', methods=['GET'])
def get_version():
    config = load_config()
    logger.info(f"/api/version: {request}")
    return (f"{config['app']['name']} v{config['app']['version']}")

# 查詢時間範圍內訪客
@bp.route('/api/queryVisitor', methods=['POST'])
def query_capture_log():
    try:
        req_json = request.get_json(silent=True) or {}
        logger.info(f"/api/queryVisitor: {req_json}")
    except Exception as e:
        logger.error(f"Error parsing JSON: {e}")
        req_json = {}
    response = service_query_capture_log(request)
    return response