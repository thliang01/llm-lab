import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional
import io

# 設定頁面配置
st.set_page_config(
    page_title="✨ Twinkle Eval Analyzer (.json / .jsonl)",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定義 CSS 樣式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f2937;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .metric-card {
        background-color: #f8fafc;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3b82f6;
        margin-bottom: 1rem;
    }
    
    .dataset-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.75rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        border: 1px solid #e5e7eb;
        margin-bottom: 1rem;
    }
    
    .stFileUploader {
        border: 2px dashed #cbd5e1;
        border-radius: 0.5rem;
        padding: 2rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def load_json_data(uploaded_file) -> Optional[Dict]:
    """載入上傳的 JSON 檔案"""
    try:
        if uploaded_file.name.endswith('.json'):
            content = uploaded_file.read().decode('utf-8')
            return json.loads(content)
        elif uploaded_file.name.endswith('.jsonl'):
            content = uploaded_file.read().decode('utf-8')
            lines = content.strip().split('\n')
            return [json.loads(line) for line in lines if line.strip()]
        else:
            st.error("請上傳 .json 或 .jsonl 檔案")
            return None
    except Exception as e:
        st.error(f"檔案載入錯誤：{str(e)}")
        return None

def aggregate_multiple_jsonl_files(files_data: List[List[Dict]]) -> Dict:
    """聚合多個 JSONL 檔案的結果"""
    if not files_data:
        return {}
    
    # 合併所有題目資料，並添加來源檔案資訊
    all_questions = []
    for run_idx, file_data in enumerate(files_data):
        for question in file_data:
            question_copy = question.copy()
            question_copy['source_run'] = run_idx  # 添加來源輪次標記
            all_questions.append(question_copy)
    
    # 計算總體統計
    total_questions = len(all_questions)
    correct_questions = sum(1 for q in all_questions if q.get('is_correct', False))
    overall_accuracy = (correct_questions / total_questions) * 100 if total_questions > 0 else 0
    
    # 按題目 ID 分組以計算每題的準確率
    question_groups = {}
    for question in all_questions:
        q_id = question.get('question_id', 0)
        if q_id not in question_groups:
            question_groups[q_id] = []
        question_groups[q_id].append(question)
    
    # 計算每題的統計資訊
    aggregated_questions = []
    for q_id, questions in question_groups.items():
        correct_count = sum(1 for q in questions if q.get('is_correct', False))
        total_runs = len(questions)
        accuracy = (correct_count / total_runs) * 100 if total_runs > 0 else 0
        
        # 取第一個問題作為基礎資料
        base_question = questions[0].copy()
        base_question.update({
            'run_count': total_runs,
            'correct_count': correct_count,
            'run_accuracy': accuracy,
            'all_runs_data': questions  # 保存所有輪次的資料
        })
        aggregated_questions.append(base_question)
    
    return {
        'individual_questions': all_questions,
        'aggregated_questions': aggregated_questions,
        'total_questions': len(question_groups),
        'total_runs': len(files_data),
        'overall_accuracy': overall_accuracy,
        'total_evaluations': total_questions
    }

def parse_evaluation_results(data: Dict) -> Dict:
    """解析評測結果資料"""
    if not data:
        return {}
    
    # 處理 Twinkle Eval 結果格式
    if 'dataset_results' in data:
        results = []
        for dataset_path, dataset_info in data['dataset_results'].items():
            if 'results' in dataset_info and dataset_info['results']:
                for result in dataset_info['results']:
                    results.append({
                        'dataset_path': dataset_path,
                        'file': result.get('file', ''),
                        'accuracy_mean': result.get('accuracy_mean', 0),
                        'accuracy_std': result.get('accuracy_std', 0),
                        'individual_runs': result.get('individual_runs', {})
                    })
        return {
            'results': results,
            'config': data.get('config', {}),
            'timestamp': data.get('timestamp', ''),
            'duration_seconds': data.get('duration_seconds', 0)
        }
    
    # 處理 JSONL 格式（個別題目結果）
    if isinstance(data, list):
        return {'individual_questions': data}
    
    return data

def create_accuracy_chart(results: List[Dict]) -> go.Figure:
    """建立準確率圖表"""
    if not results:
        return go.Figure()
    
    df = pd.DataFrame(results)
    
    fig = px.bar(
        df,
        x='file',
        y='accuracy_mean',
        error_y='accuracy_std',
        title='各資料集準確率表現',
        labels={'accuracy_mean': '平均準確率', 'file': '資料集檔案'},
        color='accuracy_mean',
        color_continuous_scale='viridis'
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        height=500,
        showlegend=False
    )
    
    return fig

def create_runs_comparison_chart(result: Dict) -> go.Figure:
    """建立多輪評測比較圖表"""
    if 'individual_runs' not in result or 'accuracies' not in result['individual_runs']:
        return go.Figure()
    
    accuracies = result['individual_runs']['accuracies']
    run_numbers = list(range(1, len(accuracies) + 1))
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=run_numbers,
        y=accuracies,
        mode='lines+markers',
        name='準確率',
        line=dict(color='#3b82f6', width=3),
        marker=dict(size=8, color='#1e40af')
    ))
    
    # 添加平均線
    mean_accuracy = sum(accuracies) / len(accuracies)
    fig.add_hline(
        y=mean_accuracy,
        line_dash="dash",
        line_color="red",
        annotation_text=f"平均: {mean_accuracy:.3f}"
    )
    
    fig.update_layout(
        title=f'多輪評測結果比較 ({result["file"]})',
        xaxis_title='評測輪次',
        yaxis_title='準確率',
        height=400
    )
    
    return fig

def display_individual_questions(questions: List[Dict], score_filter: tuple, items_per_page: int, sort_by: str, is_aggregated: bool = False, section_key: str = "default"):
    """顯示個別題目結果"""
    if not questions:
        st.info("沒有個別題目資料可顯示")
        return
    
    # 過濾資料
    if is_aggregated:
        # 聚合資料使用 run_accuracy 進行過濾
        if score_filter[0] == 0 and score_filter[1] == 100:
            filtered_questions = questions
        else:
            filtered_questions = [
                q for q in questions 
                if score_filter[0] <= q.get('run_accuracy', 0) <= score_filter[1]
            ]
    else:
        # 單次結果資料使用 is_correct 進行過濾
        if 'is_correct' in questions[0]:
            if score_filter[0] == 0 and score_filter[1] == 100:
                filtered_questions = questions
            else:
                # 將 is_correct 轉換為分數 (True=100, False=0)
                filtered_questions = [
                    q for q in questions 
                    if score_filter[0] <= (100 if q.get('is_correct', False) else 0) <= score_filter[1]
                ]
        else:
            filtered_questions = questions
    
    # 排序
    if is_aggregated:
        if sort_by == "準確率由低到高":
            filtered_questions.sort(key=lambda x: x.get('run_accuracy', 0))
        elif sort_by == "準確率由高到低":
            filtered_questions.sort(key=lambda x: x.get('run_accuracy', 0), reverse=True)
        elif sort_by == "題目 ID":
            filtered_questions.sort(key=lambda x: x.get('question_id', 0))
    else:
        if sort_by == "準確率由低到高":
            filtered_questions.sort(key=lambda x: x.get('is_correct', False))
        elif sort_by == "準確率由高到低":
            filtered_questions.sort(key=lambda x: x.get('is_correct', False), reverse=True)
        elif sort_by == "題目 ID":
            filtered_questions.sort(key=lambda x: x.get('question_id', 0))
    
    # 分頁
    total_items = len(filtered_questions)
    total_pages = (total_items - 1) // items_per_page + 1 if total_items > 0 else 1
    
    # 顯示過濾後的統計
    if section_key == "individual" and len(questions) > 0:
        original_count = len(questions)
        filtered_correct = sum(1 for q in filtered_questions if q.get('is_correct', False))
        filtered_incorrect = total_items - filtered_correct
        if total_items != original_count:
            st.warning(f"⚠️ 根據分數範圍 {score_filter[0]}-{score_filter[1]}% 過濾後，顯示 {total_items}/{original_count} 個結果（{filtered_correct} 個正確，{filtered_incorrect} 個錯誤）")
        else:
            st.info(f"📊 共 {total_items} 個結果（{filtered_correct} 個正確，{filtered_incorrect} 個錯誤）")
    
    page_key = f"page_{section_key}"
    if page_key not in st.session_state:
        st.session_state[page_key] = 1
    
    # 分頁控制
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("上一頁", disabled=st.session_state[page_key] <= 1, key=f"prev_{section_key}"):
            st.session_state[page_key] -= 1
            st.rerun()
    
    with col2:
        st.write(f"第 {st.session_state[page_key]} 頁，共 {total_pages} 頁 (總共 {total_items} 題)")
    
    with col3:
        if st.button("下一頁", disabled=st.session_state[page_key] >= total_pages, key=f"next_{section_key}"):
            st.session_state[page_key] += 1
            st.rerun()
    
    # 顯示當前頁面的題目
    start_idx = (st.session_state[page_key] - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    current_questions = filtered_questions[start_idx:end_idx]
    
    for i, question in enumerate(current_questions, start=start_idx + 1):
        if is_aggregated:
            # 聚合資料顯示
            accuracy_status = f"{question.get('run_accuracy', 0):.1f}% ({question.get('correct_count', 0)}/{question.get('run_count', 0)} 輪正確)"
            with st.expander(f"題目 {question.get('question_id', i)} - {accuracy_status}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown("**題目內容：**")
                    st.write(question.get('question', 'N/A'))
                    
                    st.markdown("**正確答案：**")
                    st.write(question.get('correct_answer', 'N/A'))
                    
                    # 顯示各輪次的輸出結果
                    if 'all_runs_data' in question:
                        st.markdown("**各輪次模型輸出：**")
                        for run_idx, run_data in enumerate(question['all_runs_data']):
                            is_correct = "✅" if run_data.get('is_correct') else "❌"
                            with st.expander(f"第 {run_idx + 1} 輪 {is_correct}", expanded=False):
                                st.write(f"**輸出：** {run_data.get('llm_output', 'N/A')}")
                                if run_data.get('predicted_answer'):
                                    st.write(f"**解析答案：** {run_data.get('predicted_answer', 'N/A')}")
                
                with col2:
                    st.markdown("**聚合統計：**")
                    st.metric("評測輪次", question.get('run_count', 0))
                    st.metric("正確次數", question.get('correct_count', 0))
                    st.metric("準確率", f"{question.get('run_accuracy', 0):.1f}%")
                    
                    # 顯示 Token 使用量（取平均值）
                    if 'all_runs_data' in question:
                        all_runs = question['all_runs_data']
                        if all_runs and 'usage_total_tokens' in all_runs[0]:
                            avg_total_tokens = sum(run.get('usage_total_tokens', 0) for run in all_runs) / len(all_runs)
                            st.metric("平均總 Token", f"{avg_total_tokens:.0f}")
        else:
            # 單次結果顯示
            correct_status = question.get('is_correct', False)
            status_text = '✅ 正確' if correct_status else '❌ 錯誤'
            
            # 如果是來自多檔案聚合，顯示更詳細的標題
            if section_key == "individual" and 'source_run' in question:
                title = f"題目 {question.get('question_id', i)} (第 {question['source_run'] + 1} 輪) - {status_text}"
            else:
                title = f"題目 {question.get('question_id', i)} - {status_text}"
            
            with st.expander(title):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown("**題目內容：**")
                    st.write(question.get('question', 'N/A'))
                    
                    st.markdown("**正確答案：**")
                    st.write(question.get('correct_answer', 'N/A'))
                    
                    st.markdown("**模型輸出：**")
                    st.write(question.get('llm_output', 'N/A'))
                    
                    if question.get('predicted_answer'):
                        st.markdown("**解析後答案：**")
                        st.write(question.get('predicted_answer', 'N/A'))
                
                with col2:
                    st.markdown("**統計資訊：**")
                    st.metric("答案正確性", "正確" if correct_status else "錯誤")
                    if 'source_run' in question:
                        st.metric("評測輪次", f"第 {question['source_run'] + 1} 輪")
                    if 'usage_total_tokens' in question:
                        st.metric("總 Token 數", question['usage_total_tokens'])
                    if 'usage_prompt_tokens' in question:
                        st.metric("提示 Token", question['usage_prompt_tokens'])
                    if 'usage_completion_tokens' in question:
                        st.metric("完成 Token", question['usage_completion_tokens'])

def main():
    # 標題區域包含 Logo
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # 顯示 Twinkle Logo
        try:
            st.image("../assets/twinkle_AI_llm_lab.png", width=200)
        except:
            # 如果找不到 logo，顯示 emoji
            st.markdown('<div style="text-align: center; font-size: 4rem;">✨</div>', unsafe_allow_html=True)
        
        # 主標題
        st.markdown('<h1 class="main-header">Twinkle Eval Analyzer</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; color: #666; margin-bottom: 2rem;">分析 .json / .jsonl 格式的評測結果</p>', unsafe_allow_html=True)
    
    # 側邊欄：檔案上傳和設定
    with st.sidebar:
        st.header("選擇 Twinkle Eval 檔案")
        
        uploaded_files = st.file_uploader(
            "請上傳 Twinkle Eval 檔案",
            type=['json', 'jsonl'],
            help="支援格式：.json (評測結果) 或 .jsonl (個別題目結果)\n檔案大小限制：200MB\n可同時上傳多個 JSONL 檔案進行聚合分析",
            accept_multiple_files=True
        )
        
        st.markdown("---")
        
        # 過濾設定
        st.header("顯示設定")
        
        score_filter = st.slider(
            "分數範圍過濾",
            min_value=0,
            max_value=100,
            value=(0, 100),
            step=1,
            help="以 0-100 顯示題目分數範圍"
        )
        
        items_per_page = st.selectbox(
            "每頁顯示幾個項目",
            options=[10, 20, 50, 100],
            index=1,
            help="選擇每頁顯示的項目數量"
        )
        
        sort_by = st.selectbox(
            "排序方式",
            options=["題目 ID", "準確率由高到低", "準確率由低到高"],
            index=0,
            help="選擇資料排序方式"
        )
    
    # 主要內容區域
    if uploaded_files:
        # 處理多檔案上傳
        if len(uploaded_files) == 1:
            # 單一檔案處理
            with st.spinner("正在載入檔案..."):
                raw_data = load_json_data(uploaded_files[0])
            
            if raw_data:
                # 解析資料
                parsed_data = parse_evaluation_results(raw_data)
                uploaded_file = uploaded_files[0]  # 為了向下相容
        else:
            # 多檔案處理 - 只支援 JSONL 格式
            jsonl_files = [f for f in uploaded_files if f.name.endswith('.jsonl')]
            json_files = [f for f in uploaded_files if f.name.endswith('.json')]
            
            if json_files:
                st.warning("⚠️ 多檔案上傳模式下暫不支援 .json 檔案，請只上傳 .jsonl 檔案")
            
            if jsonl_files:
                with st.spinner(f"正在載入 {len(jsonl_files)} 個 JSONL 檔案..."):
                    files_data = []
                    file_names = []
                    
                    for file in jsonl_files:
                        data = load_json_data(file)
                        if data and isinstance(data, list):
                            files_data.append(data)
                            file_names.append(file.name)
                        else:
                            st.error(f"載入檔案失敗：{file.name}")
                
                if files_data:
                    # 聚合多個 JSONL 檔案
                    parsed_data = aggregate_multiple_jsonl_files(files_data)
                    parsed_data['file_names'] = file_names  # 保存檔案名稱資訊
                    raw_data = True  # 標記資料已載入
                else:
                    raw_data = None
            else:
                st.error("請上傳至少一個 .jsonl 檔案")
                raw_data = None
        
        if raw_data and parsed_data:
            
            # 顯示基本資訊
            if 'file_names' in parsed_data:
                # 多檔案聚合結果
                st.success(f"✅ 成功聚合 {len(parsed_data['file_names'])} 個 JSONL 檔案")
                
                # 顯示聚合統計
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("載入檔案數", len(parsed_data['file_names']))
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("題目總數", parsed_data['total_questions'])
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col3:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("總評測輪次", parsed_data['total_runs'])
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col4:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("整體準確率", f"{parsed_data['overall_accuracy']:.2f}%")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # 顯示檔案清單
                with st.expander("📁 載入的檔案清單", expanded=False):
                    for i, filename in enumerate(parsed_data['file_names'], 1):
                        st.write(f"{i}. {filename}")
                
                st.markdown("---")
                
                # 顯示聚合題目結果
                st.header("📊 多輪評測聚合結果")
                st.info("以下顯示每題在多輪評測中的表現統計")
                
                # 修改 display_individual_questions 調用以使用聚合資料
                display_individual_questions(
                    parsed_data.get('aggregated_questions', []),
                    score_filter,
                    items_per_page,
                    sort_by,
                    is_aggregated=True,
                    section_key="aggregated"
                )
                
                # 也可以顯示所有原始結果
                if st.checkbox("顯示所有原始評測結果（包含重複題目）", key="show_raw_results"):
                    st.header("📝 所有原始評測結果")
                    
                    # 添加調試資訊
                    individual_questions = parsed_data.get('individual_questions', [])
                    if individual_questions:
                        total_count = len(individual_questions)
                        correct_count = sum(1 for q in individual_questions if q.get('is_correct', False))
                        st.info(f"原始結果統計：總共 {total_count} 個問題回答，其中 {correct_count} 個正確，{total_count - correct_count} 個錯誤")
                        
                        # 顯示當前篩選和排序設定的影響
                        st.info(f"🔍 當前設定：分數範圍 {score_filter[0]}-{score_filter[1]}%，排序：{sort_by}，每頁顯示 {items_per_page} 項")
                    
                    display_individual_questions(
                        individual_questions,
                        score_filter,
                        items_per_page,
                        sort_by,
                        is_aggregated=False,
                        section_key="individual"
                    )
            
            elif 'config' in parsed_data and 'timestamp' in parsed_data:
                st.success(f"✅ 成功載入 Twinkle Eval 結果檔案：{uploaded_files[0].name if len(uploaded_files) == 1 else '檔案'}")
                
                # 顯示評測資訊
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("評測時間", parsed_data['timestamp'])
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    model_name = parsed_data['config'].get('model', {}).get('name', 'N/A')
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("模型名稱", model_name)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col3:
                    duration = parsed_data.get('duration_seconds', 0)
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("評測時長", f"{duration:.1f}秒")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col4:
                    repeat_runs = parsed_data['config'].get('evaluation', {}).get('repeat_runs', 1)
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("重複執行次數", repeat_runs)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown("---")
                
                # 顯示結果
                if 'results' in parsed_data and parsed_data['results']:
                    st.header("📊 評測結果總覽")
                    
                    # 準確率圖表
                    accuracy_chart = create_accuracy_chart(parsed_data['results'])
                    st.plotly_chart(accuracy_chart, use_container_width=True)
                    
                    # 詳細結果
                    st.header("📋 詳細結果")
                    
                    for result in parsed_data['results']:
                        with st.container():
                            st.markdown('<div class="dataset-card">', unsafe_allow_html=True)
                            
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric(
                                    "資料集",
                                    result['file'].split('/')[-1],
                                    help=result['file']
                                )
                            
                            with col2:
                                accuracy_percent = result['accuracy_mean'] * 100
                                st.metric(
                                    "平均準確率",
                                    f"{accuracy_percent:.2f}%",
                                    delta=f"±{result['accuracy_std']*100:.2f}%"
                                )
                            
                            with col3:
                                if 'individual_runs' in result and 'accuracies' in result['individual_runs']:
                                    runs_count = len(result['individual_runs']['accuracies'])
                                    st.metric("執行次數", runs_count)
                            
                            # 多輪比較圖表
                            if 'individual_runs' in result:
                                runs_chart = create_runs_comparison_chart(result)
                                st.plotly_chart(runs_chart, use_container_width=True)
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                
                # 處理空結果的情況
                elif 'dataset_results' in parsed_data:
                    st.header("📊 評測狀態")
                    st.warning("⚠️ 評測檔案載入成功，但沒有找到評測結果")
                    
                    # 顯示資料集資訊
                    dataset_info = parsed_data['dataset_results']
                    
                    with st.expander("📋 詳細資訊", expanded=True):
                        for dataset_path, dataset_data in dataset_info.items():
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("資料集路徑", dataset_path)
                            
                            with col2:
                                results_count = len(dataset_data.get('results', []))
                                st.metric("結果數量", results_count)
                            
                            with col3:
                                avg_accuracy = dataset_data.get('average_accuracy', 0)
                                st.metric("平均準確率", f"{avg_accuracy:.2f}%")
                        
                        st.info("""
                        **可能的原因：**
                        - 評測過程中發生錯誤或被中斷
                        - 資料集檔案格式不正確
                        - API 連接問題導致評測失敗
                        - 評測尚未完成
                        
                        **建議檢查：**
                        - 查看 logs/ 資料夾中的評測日誌
                        - 確認資料集檔案格式正確
                        - 檢查 API 連接設定
                        """)
                
                # 顯示個別題目結果（如果是 JSONL 格式）
                elif 'individual_questions' in parsed_data:
                    st.header("📝 個別題目結果")
                    display_individual_questions(
                        parsed_data['individual_questions'],
                        score_filter,
                        items_per_page,
                        sort_by,
                        is_aggregated=False,
                        section_key="jsonl_single"
                    )
                
                else:
                    st.warning("⚠️ 未找到可顯示的評測結果資料")
            
            elif isinstance(raw_data, list):
                # 處理純 JSONL 個別題目格式
                st.success(f"✅ 成功載入個別題目結果檔案：{uploaded_file.name}")
                
                # 統計資訊
                total_questions = len(raw_data)
                correct_questions = sum(1 for q in raw_data if q.get('is_correct', False))
                accuracy = (correct_questions / total_questions) * 100 if total_questions > 0 else 0
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("總題目數", total_questions)
                with col2:
                    st.metric("答對題目", correct_questions)
                with col3:
                    st.metric("整體準確率", f"{accuracy:.2f}%")
                
                st.markdown("---")
                
                st.header("📝 個別題目結果")
                display_individual_questions(raw_data, score_filter, items_per_page, sort_by, is_aggregated=False, section_key="raw_jsonl")
            
            else:
                st.error("❌ 無法識別的檔案格式，請確認上傳的是有效的 Twinkle Eval 結果檔案")
    
    else:
        # 歡迎畫面
        st.markdown("""
        ## 歡迎使用 Twinkle Eval Analyzer! 👋
        
        這個工具可以幫助你分析 Twinkle Eval 的評測結果，支援以下功能：
        
        - 📁 **檔案支援**：支援 `.json` 和 `.jsonl` 格式的評測結果
        - 📊 **視覺化圖表**：準確率分析、多輪評測比較
        - 🔍 **詳細檢視**：個別題目結果、錯誤分析
        - ⚙️ **靈活設定**：分數過濾、排序、分頁等功能
        
        ### 開始使用
        請在左側邊欄上傳你的 Twinkle Eval 結果檔案來開始分析！
        
        ### 支援格式
        - **results_*.json**：完整評測結果檔案
        - **eval_results_*_run*.jsonl**：個別題目詳細結果檔案
        """)

if __name__ == "__main__":
    main()