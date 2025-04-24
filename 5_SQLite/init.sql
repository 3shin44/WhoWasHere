CREATE TABLE IF NOT EXISTS capture_log (
    dbid INTEGER PRIMARY KEY AUTOINCREMENT,  -- 流水號
    capture_datetime TEXT NOT NULL,          -- 紀錄日期時間 (YYYY-MM-DD HH:MM:SS)
    img_base64 TEXT,                         -- base64 編碼圖片
    img_path TEXT,                           -- 儲存的圖片路徑（如 /images/xxx.jpg）
    predict_probability REAL,                -- 預測機率百分比 (例如 10.5 表示 10.5%)
    class_label TEXT                         -- 分類說明
);