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
    return (f"{config['app']['name']} v{config['app']['version']}")

# 查詢時間範圍內訪客
@bp.route('/api/queryVistor', methods=['POST'])
def query_capture_log():
    response = service_query_capture_log(request)
    return response