# 70 題評測與三情境執行說明

- `cases_70.json`：70 題測試規格，含期望工具、行為、來源。**部分題目尚待校方確認標準答案**，不可把期望行為當成已驗證答案。
- `offline_results.csv`：以本地 Python 工具逐題執行所得的證據命中結果。**不是 LLM 答案正確率**。
- `official_sources.json`：官方文件連結核對表。請假規則為直連，其餘是官方規定目錄，不能聲稱精確文件連結。
- `demo_mcp_traces.json`：三情境的**真實 MCP stdio 工具執行紀錄**；尚非 OpenAI Agent 端到端 Demo。
- `run_online_eval.mjs`：設定新 API Key 並啟動服務後可對 /chat 執行 70 題，輸出答案與 Trace，需人工評分。

## 評分標準
每題人工核對 `factual_correct`、`source_supported`、`safe_behavior`、`task_completed` 四欄。未核對者不得計入正確率分子或分母。對多輪題需保留同一 session；單題測試則使用不同 session。
