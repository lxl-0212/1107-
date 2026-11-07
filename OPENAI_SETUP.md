# OpenAI 官方 API 部署說明

1. 到 https://platform.openai.com/api-keys 建立新的 API key。請撤銷任何已在聊天或公開管道分享的舊 key。
2. 在 Render 服務 Environment 設定 `OPENAI_API_KEY`（新 key）與 `OPENAI_MODEL=gpt-4.1-mini`。
3. 移除舊的 `GEMINI_API_KEY`；`OPENAI_BASE_URL` 不再用來覆蓋官方 API 端點。
4. 重新部署，先檢查 `/healthz`，再測試 `/chat`。
5. 如遇 401：檢查金鑰；429：檢查 API 額度/計費或速率限制；400：查看 Render 日誌的上游錯誤。

注意：ChatGPT Plus 訂閱與 OpenAI API 計費分開。不要將 API Key 放在 GitHub、網頁前端或 ZIP 中。
