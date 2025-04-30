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

    # 組合 datetime 字串格式
    start_dt_str = f"{query_date} {start_time}"
    end_dt_str = f"{query_date} {end_time}"

    # 解析為 datetime 物件
    try:
        start_dt = datetime.strptime(start_dt_str, "%Y-%m-%d %H:%M:%S")
        end_dt = datetime.strptime(end_dt_str, "%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        return (
            make_response(
                ReturnCode.PARAM_ERROR, errorMessage="Invalid date/time format."
            ),
            400,
        )

    # 補上微秒部分並轉換為 ISO 格式
    start_dt_iso = start_dt.replace(microsecond=0).isoformat()
    end_dt_iso = end_dt.replace(microsecond=0).isoformat()

    # 使用 with_entities 來選擇需要的欄位
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

    # 將查詢結果轉換為字典
    result_list = [
        {
            "dbid": r.dbid,
            "capture_datetime": datetime.fromisoformat(r.capture_datetime).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "img_path": img_path_combiner(r.img_path),
            "predict_probability": r.predict_probability,
            "class_label": r.class_label,
        }
        for r in results
    ]

    return make_response(ReturnCode.SUCCESS, resultList=result_list), 200


def img_path_combiner(file_name):
    prefix_date = file_name.split("_")[0]  # 取出日期部分
    return f"{Config.WS_NGINX_HOST}/{prefix_date}/{file_name}"
