# 使用 Gemma-3-12B-it API 建立對話式訓練資料集（Colab 實作）
<div align="left" style="line-height: 1;">
  <a href="https://discord.gg/Cx737yw4ed" target="_blank" style="margin: 2px;">
    <img alt="Discord" src="https://img.shields.io/badge/Discord-Twinkle%20AI-7289da?logo=discord&logoColor=white&color=7289da" style="display: inline-block; vertical-align: middle;"/>
  </a>
  <a href="https://huggingface.co/twinkle-ai" target="_blank" style="margin: 2px;">
    <img alt="Hugging Face" src="https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Twinkle%20AI-ffc107?color=ffc107&logoColor=white" style="display: inline-block; vertical-align: middle;"/>
  </a>
</div>

透過 **Twinkle AI 社群** 提供的 **原生 Gemma-3-12B-it 免費 API**，  
學員將完整體驗：**API 呼叫 → 資料生成 → 品質檢查 → 格式化 → 上傳到 Hugging Face Hub** 的完整流程。

---

## 📘 課程流程
請依序完成以下 Notebooks：

1. **00_setup_and_api_call.ipynb**  
   - 安裝依賴、設定 API key  
   - 測試最小化 Gemma-3-12B-it 呼叫  

2. **01_generate_dialogs.ipynb**  
   - 設定主題池與對話風格  
   - 批次生成對話資料 → 輸出 `raw.jsonl`  

3. **02_quality_checks.ipynb**  
   - 檢查敏感詞、長度、格式與結構  
   - 清理後輸出 `clean.jsonl`  

4. **03_format_dataset.ipynb**  
   - 轉換為常見訓練格式（SFT JSONL / Chat messages）  
   - JSON Schema 驗證 → 輸出 `sft.jsonl`  

5. **04_upload_to_hfhub.ipynb**  
   - 匿名化檢查、授權說明  
   - 使用 `huggingface_hub` 上傳資料集到 Hugging Face Hub  

---

## 🎯 學習目標
- 瞭解如何使用 **Gemma-3-12B-it API** 自動生成對話資料  
- 學會檢查並清理資料品質  
- 掌握訓練資料格式轉換與驗證方法  
- 學會設定授權並將資料集上傳至 Hugging Face Hub  

---

## 🛡️ 注意事項
- 請勿生成或上傳包含 **個資、敏感資訊** 的資料  
- 建議使用 **CC BY 4.0** 或 **CC BY-SA 4.0** 作為資料集授權  
- 上傳 Hugging Face Hub 前，請務必再次檢查資料內容  

---

## 📖 延伸閱讀
- [Hugging Face Hub: Datasets](https://huggingface.co/docs/datasets)  
- [Hugging Face Hub Python Library](https://huggingface.co/docs/huggingface_hub)  
- [Gemma Models (Google DeepMind)](https://ai.google.dev/gemma)  