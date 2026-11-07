# Mini AI Campus Assistant V4 — 全部檔案放同一層

本專案 ZIP 內 **沒有子資料夾**。解壓縮後將全部檔案上傳 GitHub 儲存庫根目錄。

## Render Docker
- `Dockerfile` 與 `index.html`、`server.js` 位於同一層。
- `/` 直接回傳 `index.html`，不再使用 `public/`。
- `/healthz` 檢查服務與 MCP 工具。
- `/chat` 執行 Agent 查詢。
- `hello_tool.py` 從同層讀取 JSON、Markdown。

## Render 環境變數
- `OPENAI_API_KEY`：請使用新金鑰，**不可上傳到 GitHub**。
- `OPENAI_MODEL=gpt-4.1-mini`
- `PYTHON_BIN=python3`
- `MAX_AGENT_STEPS=4`

## 評測
- `cases_70.json`：70題測試案例（仍需官方人工核對）。
- `official_sources.json`：來源清單，非所有項目均為文件直連。
- `demo_mcp_traces.json`：先前 MCP 執行紀錄，非 OpenAI 端到端完成證據。
- `node run_online_eval.mjs`：對本地服務執行70題測試；設定 `AGENT_URL` 可指定 Render URL。

## 注意
這個版本只調整檔案佈局與路徑，沒有宣稱完成端到端70題評測或場域驗證。
