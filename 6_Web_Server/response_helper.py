from enum import Enum

from flask import Flask, jsonify
from logger import setup_logger

logger = setup_logger()

app = Flask(__name__)


class ReturnCode(Enum):
    SUCCESS = ("0000", "Success")
    PARAM_ERROR = ("L500", "Parameters error")
    SERVER_ERROR = ("S500", "Server error")

    def code(self):
        return self.value[0]

    def msg(self):
        return self.value[1]


def make_response(code_enum: ReturnCode, **kwargs):
    # **kwargs 代表「**keyword arguments（關鍵字參數）」的縮寫
    response = {"returnCode": code_enum.code(), "returnMsg": code_enum.msg()}
    response.update(kwargs)
    return jsonify(response)


# 全局異常處理
@app.errorhandler(Exception)
def handle_exception(e):
    # 你可以選擇在此記錄錯誤訊息或日誌
    logger.error(f"API error occurred: {str(e)}")
    # 回傳預期格式的錯誤訊息
    return make_response(ReturnCode.SERVER_ERROR, errorMessage=str(e)), 500
