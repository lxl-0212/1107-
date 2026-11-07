# Mini AI Campus Assistant V3 — Render 部署

1. 將本 ZIP **解壓縮後的所有檔案及資料夾**放在 GitHub repository 根目錄，不要只上傳 ZIP。
2. GitHub 必須存在 `public/index.html`、`server.js`、`Dockerfile`、`agent.js`、`hello_tool.py`、`data/` 與 `evaluation/`。
3. Render 使用 Docker runtime，部署最新 commit。Docker build 會驗證首頁檔案確實存在。
4. Render Environment 設定 `OPENAI_API_KEY` (使用新金鑰) 與 `OPENAI_MODEL=gpt-4.1-mini`。不要把金鑰寫進 GitHub。
5. 測試 `/healthz`，再開啟 `/`，最後從首頁測試 `/chat`。
6. 執行 70 題評測前，閱讀 `evaluation/README.md`；離線命中率不等於正式正確率。

若看到 `ENOENT /app/public/index.html`，表示 GitHub commit 或 Docker build context 沒有包含 `public/index.html`，不是 OpenAI 的問題。

注意：此前在聊天中公開的 API 金鑰應撤銷並換新。
