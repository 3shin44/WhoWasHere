# Who Was Here 誰來過

## 說明

提供用戶查詢曾來訪住家的訪客。  
透過影像監控與人形偵測，產生截圖並記錄時間，使用者可於 Android 裝置中快速查詢，不需要一格格翻閱監控錄影。

## 功能特色

- 自動分析監控影像，偵測「人形物體」
- 擷取訪客出現時的畫面截圖與時間
- 使用 Redis 緩衝處理，降低系統負載
- 提供 Android APP 查詢，使用時間條件過濾

## 系統架構

### SERVER 端

1. **影像處理接口**  
   將攝影機串流轉為可程式處理的格式（如 RTSP → OpenCV），作為後續偵測之輸入。

2. **人形物體監測**  
   使用影像辨識技術（YOLO）偵測畫面中是否有人形出現，若有，擷取截圖並記錄時間。

3. **Redis 暫存區**  
   所有偵測到的紀錄會暫時寫入 Redis（包含圖檔位置、時間等資訊），避免主程式阻塞。

4. **資料入庫監聽器**  
   背景服務持續監聽 Redis，當有新資料時，將其批次寫入 SQLite 資料庫，永久儲存。

5. **SQLite 資料庫**  
   儲存所有訪客出現時間與截圖資訊，供查詢使用。

6. **Web API 服務**  
   提供 HTTP 查詢介面，支援條件查詢（如日期、時間區間），回傳結果。
   
7. **Web 靜態資源**  
  提供HTTP存取圖片資源，使用Ngnix提供服務。

---

### Android Client (APP)

1. **查詢 UI**  
   使用者可於 APP 中輸入查詢條件（日期、時間等），按下查詢後呼叫後端 API。

2. **資料呈現**  
   APP 解析回傳 JSON 結果，並以圖文列表呈現當時的訪客截圖與時間。

---

## 使用技術

| 類別         | 技術/工具                |
| ------------ | ------------------------ |
| 人形偵測     | YOLO                     |
| 資料傳遞緩衝 | Redis                    |
| 資料庫       | SQLite                   |
| Web API      | Flask/SQLAlchemy         |
| Client APP   | Android Studio (React Native) |
| 主機         | Raspberry Pi 5 (Rpi OS)  |
| 容器化       | Docker                   |

---

## 佈署說明

### SERVER 端

1. **影像處理接口: Cam Server**  

  - 切換至目錄下
  - 修改 .env 參數, 影像來源與暴露PORT號
  - 執行 `docker compose up`
  - 服務位址`http://{server}:{port}/video`

2. **人形物體監測: Human Dectecor**  
   
   - 切換至目錄下
   - 建立虛擬環境 `python -m vevn vevn`
   - 切換 `source venv/bin/activate`
   - 安裝 `pip install -r requirements.txt`
   - 註冊systemd
```
# 註冊系統服務
sudo nano /etc/systemd/system/wwh-human-detector.service


# 編輯內容
[Unit]
Description=WhoWasHere Human Detector
After=network.target

[Service]
User={USERNAME}
Group={USERGROUP}
WorkingDirectory=/{PATH}/WhoWasHere/2_Human_Detector
ExecStart=/{PATH}/WhoWasHere/2_Human_Detector/venv/bin/python main.py
Restart=always
RestartSec=5
StandardOutput=append:/{PATH}/WhoWasHere/2_Human_Detector/logs/human-detector.log
StandardError=append:/{PATH}/WhoWasHere/2_Human_Detector/logs/human-detector.err.log
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target

```
   - 啟動/停止指令
```
# 初次設定載入
sudo systemctl daemon-reexec

# 重啟
sudo systemctl daemon-reload

# 啟動
sudo systemctl enable wwh-human-detector

# 停止
sudo systemctl start wwh-human-detector
```
   - (備註)因Rpi5硬體性能，使用容器容易卡住，使用YOLO4-tiny


1. **Redis 暫存區** 

  - 切換至目錄下
  - 修改 .env 參數，使用PORT號與密碼
  - 執行 `docker compose up`

4. **資料入庫監聽器**  

  - (Optional) 本機允許 REDIS PORT (若有防火牆UFW，或其他方式需設定DOCKER NETWORK)
  - 切換至目錄下
  - 修改 .env 參數，使用PORT號與密碼
  - 執行 `docker compose up`

5. **SQLite 資料庫**  

  - SQLite使用預設檔案或init.sql建立初始化資料庫
  - 紀錄資料夾路徑與檔案名稱，供其他服務掛載

6. **Web API 服務**  

  - 切換至目錄下
  - 修改 .env 參數，SQLITE資料夾路徑與DB檔案名稱、WEB API服務PORT號、Nginx HOST位址
  - 執行 `docker compose up`
   
7. **Web 靜態資源**  

  - 切換至目錄下
  - 修改 .env 參數，以WEB方式提供圖片資源，設定服務PORT號與圖片資料夾路徑
  - 執行 `docker compose up`

---

## 專案結構

```aiignore
├─0_Rpi_Script              # 樹梅派快捷指令
│
├─1_Cam_Server              # 影像處理接口
│  └─configs                  # 微服務設定檔
│
├─2_Human_Detector          # 人形物體監測
│  ├─configs                  # 微服務設定檔
│  └─yolo                     # YOLO 模型, 參數, 類別清單...
│
├─3_Redis                   # Redis 暫存區
│
├─4_DB_Writer               # 資料入庫監聽器
│  └─configs                  # 微服務設定檔
│
├─5_SQLite                  # SQLite 資料庫
│  
├─6_Web_Server              # Web API 服務
│  └─configs                  # 微服務設定檔
│
└─7_Img_Server              # Web 靜態資源
   └─nginx                    # nginx設定檔

```

## 討論

- 遠端存取  
可能方案: 申請DOMAIN & 套用Cloudflare Tunnel服務 (網路安全性)

- 共用函式庫  
應建立本地/私有函式庫，避免同樣功能重工，例如：封裝後的logger工具

- 容器化與虛擬環境  
最終需要以容器佈署, 開發階段要改為容器化啟動, 避免使用VENV

- DOCKER網路  
DOCKER提供容器互相通訊, 可能是本機防火牆規則導致連接異常, 此處仍以本機PORT連接

- 服務占用PORT號  
應盡量避免暴露過多PORT號，最外層可能統一使用反向代理或類似服務，外部存取皆使用單一PORT號，透過路徑映對內部服務

- YOLO 模型佈署  
在樹梅派(硬體資源有限)的環境，再套上容器可能導致調用硬體資源不足(或是底層IMAGE未針對特定環境最佳化)，故最後改用VENV啟動，在容器跑不動

-  DOCKER IMAGE  
python-slim可能缺乏預設套件, 執行異常記得檢查

- HTTPS連線  
掛載自簽憑證或對外接口走公有服務(如: Cloudflare)

## ChatGPT估算工時 (2025.04.22)

| 工作項目                       | 子項目                             | 預估工時 (h) |
| ------------------------------ | ---------------------------------- | ------------ |
| 規劃與設計                     | 需求釐清、架構設計、技術選型       | 24           |
| Docker 容器化環境與 CI/CD 設定 |                                    | 16           |
| Server：影像處理接口           | RTSP → OpenCV 影像串流讀取         | 24           |
| Server：人形偵測 (YOLO)        | 模型整合、推論流程開發與調校       | 40           |
|                                | 偵測成功擷取截圖與時間戳註記       | 16           |
| Server：Redis 暫存區           | Redis 安裝、Schema 設計、寫入邏輯  | 16           |
| Server：資料入庫監聽器         | 監聽 Redis、批次寫入 SQLite        | 24           |
| Server：SQLite 資料庫          | 資料庫設計、SQLAlchemy ORM 設定    | 16           |
| Server：Web API 服務           | Flask 架構／路由、條件查詢 API     | 32           |
| Android Client：UI 設計        | Wireframe、畫面切版、Material 實作 | 16           |
| Android Client：API 整合       | Retrofit / OkHttp 呼叫與序列化     | 24           |
| Android Client：資料呈現       | RecyclerView、Base64 圖片顯示      | 24           |
| Android Client：時間篩選控件   | 日期與時間區間選取元件             | 16           |
| 測試與除錯                     | 單元測試、整合測試 (Server + App)  | 48           |
| 部署、文件與驗收               | Server & App 打包、部署腳本        | 16           |
|                                | 開發文件、使用手冊、最終驗收       | 16           |
| 小計（開發+測試+部署）         |                                    | 368          |
| ＋20% 預留（專案管理／Buffer） |                                    | 74           |
| 總計                           |                                    | 442          |