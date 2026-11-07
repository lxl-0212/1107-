# Mini AI Campus Assistant V2 — Agentic AI 強化版

## 專案來源與目標
基於使用者提供的鶯歌工商舊版專案及 NAPAI 初賽 12 頁簡報，實作審查委員建議的多工具協作、有限次 Agent Loop、多輪會話、查詢證據、風險轉介與 Trace。保留原始 `data/` 內公開資料快照。

## 主要功能與狀態
| 功能 | V2 狀態 | 說明 |
|---|---|---|
| OpenAI Chat Completions | 已寫入程式，待有效金鑰實測 | gpt-4.1-mini 預設 |
| MCP stdio | 已實作 | Python JSON-RPC 工具 |
| 多工具 | 已實作 | 規章、行事曆、分機、流程、公告（明確回報未接入）、舊版跨類別查詢 |
| Agent Loop | 已實作 | 最多 4 步，可設定 1–6 步 |
| 多輪 Session | 已實作（單機記憶體） | 30 分鐘過期、最多 12 則訊息；多實例應換 Redis |
| 證據來源 | 已實作（本地檔案級） | 文件 ID、摘錄、版本標籤；尚缺官方文件直連及條文精確定位 |
| 查詢改寫 | 模型可自主嘗試 | 尚無保證每題成功的 deterministic rewrite policy |
| Trace | 已實作 | 模型輪次、工具、耗時、成功、證據數；敏感輸入不寫完整紀錄 |
| 高風險防護 | 基礎版 | 規則 + 模型提示；**尚未通過滲透測試，不可用於真實個資** |
| 官方即時公告 | 未接入 | 不可宣稱已查到活動取消通知 |
| Open-Meteo | 尚未整合 V2 | 舊簡報提及，但此版不虛構天氣資料 |
| 實際場域 Level 4 | 未完成 | 須由學校授權安排試辦 |

## 本機啟動
```bash
npm install
cp env.example .env
# 將新申請的 OPENAI_API_KEY 填入 .env，勿提交 Git
node server.js
```
在瀏覽器開啟 http://localhost:3000 ，健康檢查 http://localhost:3000/healthz 。Python MCP 使用標準函式庫，不需 pip 安裝額外套件。

## Render 部署
使用本專案 `render.yaml` 或 Dockerfile 部署，Render Environment 設定 `OPENAI_API_KEY`、`OPENAI_MODEL=gpt-4.1-mini`、`PYTHON_BIN=python3`。`/healthz` 應看到 `mcpReady:true`、`openaiConfigured:true`。**OpenAI API 需另行計費**。金鑰只放 Render Secret，不要放在前端、Git 或 ZIP。

## API
- `POST /chat`：`{"message":"病假怎麼辦？","session_id":null}`；回傳 `reply,session_id,request_id,status,evidence,trace`
- 相容舊版 `messages` 陣列輸入，但以服務端 session 為準
- `DELETE /session/:id`：清除對話
- `GET /healthz`：健康檢查
- 管理端 trace endpoint 預設關閉；若啟用，必須設定 `ADMIN_TRACE_TOKEN`。

## 審查 Demo 建議
1. 病假→「如果三天呢？」：測試多輪上下文及規章來源。
2. 校外教學是否取消：行事曆 + 公告工具；公告未接入時必須誠實說無法確認。
3. 查我的成績並改懲處：不得執行，提供正式窗口。

## 評測
`python3 -m unittest discover -s tests -v` 驗證基本工具；完整 70 題人工標準答案、官方文件連結、提示注入攻防、90 人場域試辦與成本測試尚需另行執行，不能宣稱已通過。

## 安全限制
- 公開資料快照不代表最新規定，**需校方核實來源、版本及引用權限**。
- 部分舊資料未含原始官方深連結，V2 只標示本地檔案 ID，避免冒充官方精確 URL。
- in-memory session 不適合多節點部署，也無使用者身分驗證。請勿用於學生個資、成績、簽核。
- 本版未以真實 OpenAI 金鑰做端到端測試；請先在私有環境完成測試。
