# 使用 Gemma-3-12B-it API 建立對話式訓練資料集（Colab 實作）

透過 **Twinkle AI 社群** 提供的 **原生 Gemma-3-12B-it 免費 API**，  
學員將完整體驗：API 呼叫 → 資料生成 → 品質檢查 → 格式化 → 上傳到 Hugging Face Hub 的流程。

---

## 🚀 快速開始
點擊下方 Colab badge，在雲端直接開啟並運行：  

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/<YOUR_ORG>/<YOUR_REPO>/blob/main/courses/2025-08-llm-dialogue-dataset/00_setup_and_api_call.ipynb)

> ⚠️ 請將 `<YOUR_ORG>/<YOUR_REPO>` 替換成你實際的 GitHub 路徑  
> （例如 `ai-twinkle/twinkle-llm-labs`）。

---

## 📘 課程流程
請依序完成以下 notebooks：

1. **00_setup_and_api_call.ipynb**  
   - 安裝依賴、設定 API key、測試最小 Gemma-3-12B-it 呼叫  

2. **01_generate_dialogs.ipynb**  
   - 設定主題池與風格，批次生成對話資料 → 輸出 `raw.jsonl`  

3. **02_quality_checks.ipynb**  
   - 檢查敏感詞、長度、結構 → 輸出 `clean.jsonl`  

4. **03_format_for_training.ipynb**  
   - 轉換為常見訓練格式（SFT JSONL / Chat messages）  
   - JSON Schema 驗證 → 輸出 `sft.jsonl`  

5. **04_export_and_license.ipynb**  
   - 匿名化檢查、授權說明  
   - 使用 `huggingface_hub` 上傳資料集到 Hugging Face Hub  

---

## 🎯 學習目標
- 瞭解如何使用 LLM API（Gemma-3-12B-it）自動生成對話資料  
- 學會檢查並清理資料品質  
- 掌握常見訓練資料格式轉換方法  
- 學習如何將資料集正確授權並上傳到 Hugging Face Hub  

---

## 🛡️ 注意事項
- 請勿生成或上傳包含個資、敏感資訊的資料  
- 建議使用 **CC BY 4.0** 或 **CC BY-SA 4.0** 作為資料集授權  
- 上傳 Hugging Face Hub 前，請再次檢查內容  

---

## 📖 延伸閱讀
- [Hugging Face Hub: Datasets](https://huggingface.co/docs/datasets)  
- [Hugging Face Hub Python Library](https://huggingface.co/docs/huggingface_hub)  
- [Gemma Models (Google DeepMind)](https://ai.google.dev/gemma)  