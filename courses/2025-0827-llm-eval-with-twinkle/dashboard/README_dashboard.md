# Twinkle Eval Analyzer Dashboard

這是一個基於 Streamlit 的互動式儀表板，用於分析 Twinkle Eval 評測結果。

## 功能特色

- 📁 **檔案上傳**：支援 `.json` 和 `.jsonl` 格式（最大 200MB）
- 📊 **視覺化分析**：準確率圖表、多輪評測比較
- 🔍 **詳細檢視**：個別題目結果檢視與分析
- ⚙️ **靈活控制**：分數過濾、排序、分頁功能
- 🎨 **美觀介面**：現代化的使用者介面設計

## 安裝與執行

### 1. 安裝依賴套件

```bash
# 啟用虛擬環境
source twinkle-labs/bin/activate

# 安裝 dashboard 所需套件
pip install -r requirements_dashboard.txt
```

### 2. 啟動儀表板

```bash
streamlit run twinkle_eval_analyzer.py
```

### 3. 開啟瀏覽器

預設會在 `http://localhost:8501` 啟動儀表板

## 使用方法

### 檔案格式支援

1. **完整評測結果檔案** (`results_*.json`)
   - 包含完整的評測配置和結果統計
   - 支援多資料集結果顯示
   - 提供準確率分析圖表

2. **個別題目結果檔案** (`eval_results_*_run*.jsonl`)
   - 包含每題的詳細回答記錄
   - 支援題目逐一檢視
   - 提供錯誤分析功能

### 主要功能

#### 📊 結果總覽
- 評測基本資訊（時間、模型、執行時長）
- 準確率統計圖表
- 多輪評測結果比較

#### 📋 詳細分析
- 各資料集表現對比
- 個別題目答題情況
- Token 使用量統計

#### ⚙️ 互動控制
- **分數過濾**：選擇顯示特定分數範圍的題目
- **排序選項**：按準確率或題目 ID 排序
- **分頁控制**：可調整每頁顯示項目數量

## 檔案結構

```
twinkle_eval_analyzer.py    # 主要儀表板程式
requirements_dashboard.txt  # Python 依賴套件
README_dashboard.md        # 說明文件
```

## 技術實現

- **Streamlit**：互動式網頁應用框架
- **Plotly**：視覺化圖表庫
- **Pandas**：資料處理與分析

## 注意事項

- 確保上傳的檔案為有效的 JSON/JSONL 格式
- 大型檔案可能需要較長的載入時間
- 建議在良好的網路環境下使用