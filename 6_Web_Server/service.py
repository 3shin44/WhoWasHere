from datetime import datetime

from env_config import Config
from logger import setup_logger
from models import CaptureLog
from response_helper import ReturnCode, make_response

logger = setup_logger()


def service_query_capture_log(resquest):

    data = resquest.get_json()
    query_date = data.get("queryDate")
    start_time = data.get("startTime")
    end_time = data.get("endTime")

    if not (query_date and start_time and end_time):
        return make_response(ReturnCode.PARAM_ERROR), 400

    # 組合查詢時間字串
    start_dt_str = f"{query_date} {start_time}:00"
    end_dt_str = f"{query_date} {end_time}:00"

    # 嘗試轉換成 datetime 並轉為 ISO 格式 (符合 DB 格式)
    try:
        start_dt_iso = datetime.strptime(start_dt_str, "%Y-%m-%d %H:%M:%S").replace(microsecond=0).isoformat()
        end_dt_iso = datetime.strptime(end_dt_str, "%Y-%m-%d %H:%M:%S").replace(microsecond=0).isoformat()
    except ValueError:
        return make_response(ReturnCode.PARAM_ERROR, errorMessage="Invalid date/time format."), 400

    # 查詢符合時間區間的資料
    results = (
        CaptureLog.query.with_entities(
            CaptureLog.dbid,
            CaptureLog.capture_datetime,
            CaptureLog.img_path,
            CaptureLog.predict_probability,
            CaptureLog.class_label,
        )
        .filter(
            CaptureLog.capture_datetime >= start_dt_iso,
            CaptureLog.capture_datetime <= end_dt_iso,
        )
        .order_by(CaptureLog.capture_datetime)
        .all()
    )

    # 組合回應結果，解析 capture_datetime 為標準格式
    result_list = []
    for r in results:
        try:
            dt_obj = datetime.fromisoformat(r.capture_datetime)
            dt_formatted = dt_obj.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            logger.warning(f"無法轉換時間格式：{r.capture_datetime} | 錯誤: {e}")
            dt_formatted = r.capture_datetime  # 保留原字串

        result_list.append({
            "dbid": r.dbid,
            "capture_datetime": dt_formatted,
            "img_path": img_path_combiner(r.img_path),
            "predict_probability": r.predict_probability,
            "class_label": r.class_label,
        })

    return make_response(ReturnCode.SUCCESS, resultList=result_list), 200


def img_path_combiner(file_name):
    prefix_date = file_name.split("_")[0]  # 取出日期部分
    return f"{Config.WS_NGINX_HOST}/{prefix_date}/{file_name}"
