from database import db


class CaptureLog(db.Model):
    __tablename__ = "capture_log"

    dbid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    capture_datetime = db.Column(
        db.String, nullable=False
    )  # 存為 TEXT 格式（YYYY-MM-DD HH:MM:SS）
    img_base64 = db.Column(db.Text)  # 用 Text 儲存 base64 長字串
    img_path = db.Column(db.String)
    predict_probability = db.Column(db.Float)  # REAL → Float
    class_label = db.Column(db.String)

    def to_dict(self):
        return {
            "dbid": self.dbid,
            "capture_datetime": self.capture_datetime,
            "img_base64": self.img_base64,
            "img_path": self.img_path,
            "predict_probability": self.predict_probability,
            "class_label": self.class_label,
        }
