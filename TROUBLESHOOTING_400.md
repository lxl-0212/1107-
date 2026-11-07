# 400 錯誤排查與修正

本版本加入上游 API 錯誤記錄、依 baseURL 選擇 API Key、無 MCP 工具時不送 tools、改善前端錯誤提示。

## Render 環境變數
- `GEMINI_API_KEY`：有效的 Gemini API 金鑰（請勿提交到 GitHub）。
- `OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/`
- `OPENAI_MODEL=gemini-2.5-flash`：示例，請以帳號實際支援模型為準。
- 使用 Gemini 時，建議移除非必要的 `OPENAI_API_KEY`，避免混淆。

## 驗證
1. 開啟 `https://你的網域/healthz`，確認 `ok:true`、`mcpReady:true`。
2. 提問「今天星期幾」：只測試 Node.js 路由。
3. 提問一般知識：測試 LLM API。
4. 提問校務規定：測試 MCP 與 LLM 整合。
5. 如仍有 400，查看 Render Logs 中 `[CHAT ERROR]` 的 `status`、`code`、`upstream`。

注意：本修補未在真實 Render 或 Gemini 金鑰環境執行端到端測試。
