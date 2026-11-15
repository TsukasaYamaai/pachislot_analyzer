import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd

# グラフのフォント設定（文字化け防止）
plt.rcParams['font.family'] = 'MS Gothic'

# ページの設定
st.set_page_config(page_title="パチスロ実戦データ解析ツール", layout="wide")

st.title("🎰 パチスロ実戦データ解析ツール（店舗・日付・台番号管理版）")
st.write("店舗名、日付、台番号を指定してデータをまとめ、柔軟に絞り込んで集計・編集できます。")

# --- 設定パラメータ（サイドバー） ---
st.sidebar.header("⚙️ 機種・環境設定")
base_games = st.sidebar.number_input("50枚あたりの回転数（ベース）", value=31.0, step=0.1)
yen_per_medal = 1000 / 46  # 1,000円＝46枚貸出

# 消化スピード（7分で100回転 → 1分あたりの回転数）
rpm = 100 / 7
min_30_games = rpm * 30

# --- セッション状態の初期化 ---
if "records" not in st.session_state:
    st.session_state.records = []

if "current_sessions" not in st.session_state:
    st.session_state.current_sessions = []

# リセット確認の状態管理用
if "show_reset_confirm" not in st.session_state:
    st.session_state.show_reset_confirm = False

# --- サイドバー：実戦データ入力 ---
st.sidebar.markdown("---")
st.sidebar.header("📝 実戦データ入力")

current_hit_num = len(st.session_state.current_sessions) + 1

store_name = st.sidebar.text_input("店舗名", value="ラカータ大宮")
play_date = st.sidebar.date_input("実戦日付")
machine_id = st.sidebar.text_input("台番号（例: 123番台）", value="101")

st.sidebar.markdown("---")
st.sidebar.markdown(f"**【 {current_hit_num}回目の当たりデータ 】**")

cz_times = st.sidebar.number_input("何回目のCZで当たりましたか？", min_value=0, max_value=20, value=None, step=1, placeholder="例: 3")

cz_games_list = []
if cz_times is not None and cz_times > 0:
    for i in range(1, int(cz_times) + 1):
        g = st.sidebar.number_input(f"CZ {i}回目にかかったゲーム数(G)", min_value=0, value=None, step=1, key=f"cz_game_{i}", placeholder="例: 150")
        cz_games_list.append(g)

final_games = st.sidebar.number_input("CZ当選からボーナス確定までのゲーム数(G)", min_value=0, value=None, step=1, placeholder="例: 30")

ren_count = st.sidebar.number_input("連チャン数（単発なら1）", min_value=1, max_value=50, value=1, step=1)

ren_games_list = []
ren_coins_list = []
for r in range(1, int(ren_count) + 1):
    st.sidebar.markdown(f"**--- {r}連目の詳細 ---**")
    rg = st.sidebar.number_input(f"{r}連目で消化したゲーム数(G)", min_value=0, value=None, step=1, key=f"ren_game_{r}", placeholder="例: 100")
    rc = st.sidebar.number_input(f"{r}連目で獲得した枚数(枚)", min_value=0, value=None, step=10, key=f"ren_coin_{r}", placeholder="例: 500")
    
    ren_games_list.append(rg)
    ren_coins_list.append(rc)

st.sidebar.markdown("---")

def process_and_save_session():
    actual_cz_times = cz_times if cz_times is not None else 0
    actual_cz_games = [g if g is not None else 0 for g in cz_games_list]
    actual_final_games = final_games if final_games is not None else 0
    actual_ren_games = [g if g is not None else 0 for g in ren_games_list]
    actual_ren_coins = [c if c is not None else 0 for c in ren_coins_list]

    total_cz_games = sum(actual_cz_games)
    base_normal_games = total_cz_games + actual_final_games
    total_at_games = sum(actual_ren_games)
    total_get_coins = sum(actual_ren_coins)
    
    total_game = base_normal_games + total_at_games
    invest_coins = (total_game / base_games) * 50
    invest_yen = invest_coins * yen_per_medal
    diff_coins = total_get_coins - invest_coins
    time_minutes = total_game / rpm

    session_data = {
        "cz_times": actual_cz_times,
        "total_game": total_game,
        "invest_coins": invest_coins,
        "invest_yen": invest_yen,
        "get_coins": total_get_coins,
        "diff_coins": diff_coins,
        "time_minutes": time_minutes
    }
    return session_data

# 「次の当たりデータを入力」ボタン
if st.sidebar.button("➕ 次の当たりデータを入力"):
    unfilled = []
    if cz_times is None: unfilled.append("CZ回数")
    if cz_times is not None and cz_times > 0:
        for idx, val in enumerate(cz_games_list, 1):
            if val is None: unfilled.append(f"CZ {idx}G")
    if final_games is None: unfilled.append("ボーナス確定までのG数")
    for idx, (rg_val, rc_val) in enumerate(zip(ren_games_list, ren_coins_list), 1):
        if rg_val is None: unfilled.append(f"{idx}連目G数")
        if rc_val is None: unfilled.append(f"{idx}連目枚数")

    if unfilled:
        st.sidebar.error(f"⚠️ 未入力の項目があります ({', '.join(unfilled)})。数値を入力してください。")
    else:
        session_data = process_and_save_session()
        st.session_state.current_sessions.append(session_data)
        st.sidebar.success(f"{current_hit_num}回目までのデータを一時保存しました！")
        st.rerun()

# 1つ前のデータを修正するボタン
if st.session_state.current_sessions:
    if st.sidebar.button("↩️ 1つ前のデータを修正する（やり直す）"):
        st.session_state.current_sessions.pop()
        st.sidebar.warning("直前の当たりデータを取り消しました。再度入力してください。")
        st.rerun()

# --- 現在入力中のデータ確認用プレビュー ---
if st.session_state.current_sessions:
    st.sidebar.markdown(f"**📌 現在入力中（{machine_id}番台）のまとめ状況**")
    st.sidebar.write(f"・確定済みの当たり: {len(st.session_state.current_sessions)} 回")
    curr_g = sum(s["total_game"] for s in st.session_state.current_sessions)
    curr_diff = sum(s["diff_coins"] for s in st.session_state.current_sessions)
    st.sidebar.write(f"・合計G数: {curr_g:.0f} G / 差枚: `{curr_diff:+.1f}枚`")
    st.sidebar.markdown("---")

# 「この台のデータをまとめて確定する」ボタン
if st.sidebar.button("💾 この台のデータをまとめて確定する", key="btn_confirm_machine"):
    if st.session_state.current_sessions:
        machine_record = {
            "store": store_name,
            "date": str(play_date),
            "machine_id": machine_id,
            "sessions": st.session_state.current_sessions
        }
        st.session_state.records.append(machine_record)
        st.session_state.current_sessions = []
        st.sidebar.success(f"【{store_name} / {machine_id}番台】のデータを集計に反映しました！")
        st.rerun()
    else:
        st.sidebar.warning("確定するデータ（当たりデータ）がありません。「次の当たりデータを入力」を押してデータを追加してください。")

# --- すべてのリセットボタン（確認ステップ付き） ---
st.sidebar.markdown("---")
if not st.session_state.show_reset_confirm:
    if st.sidebar.button("🔄 すべてのデータをリセット"):
        st.session_state.show_reset_confirm = True
        st.rerun()
else:
    st.sidebar.warning("⚠️ すべてのデータが削除されます。本当に実行しますか？")
    col_yes, col_no = st.sidebar.columns(2)
    if col_yes.button("はい（削除）"):
        st.session_state.records = []
        st.session_state.current_sessions = []
        st.session_state.show_reset_confirm = False
        st.rerun()
    if col_no.button("いいえ（キャンセル）"):
        st.session_state.show_reset_confirm = False
        st.rerun()

# --- メイン画面：集計結果とグラフ、編集機能の表示 ---
records = st.session_state.records

if not records and not st.session_state.current_sessions:
    st.info("👈 左側のサイドバーから店舗名・日付・台番号を設定し、1回目の当たりデータを入力して「次の当たりデータを入力」を押してください。")
else:
    st.header("📊 集計結果 & 履歴")
    
    if st.session_state.current_sessions:
        st.warning(f"⚠️ 現在入力中の【{machine_id}番台】（計 {len(st.session_state.current_sessions)} 回の当たり）は、まだ「この台のデータをまとめて確定する」ボタンが押されていないため集計に反映されていません。")

    if records:
        st.markdown("### 🔍 データ絞り込み・選択")
        filter_col1, filter_col2, filter_col3 = st.columns(3)

        all_stores = list(set(r["store"] for r in records))
        selected_store = filter_col1.selectbox("ホール（店舗）で絞り込み", ["すべて"] + all_stores)

        all_dates = list(set(r["date"] for r in records))
        selected_date = filter_col2.selectbox("日付で絞り込み", ["すべて"] + all_dates)

        all_machines = list(set(r["machine_id"] for r in records))
        selected_machine = filter_col3.selectbox("台番号で絞り込み", ["すべて"] + all_machines)

        filtered_records = records
        if selected_store != "すべて":
            filtered_records = [r for r in filtered_records if r["store"] == selected_store]
        if selected_date != "すべて":
            filtered_records = [r for r in filtered_records if r["date"] == selected_date]
        if selected_machine != "すべて":
            filtered_records = [r for r in filtered_records if r["machine_id"] == selected_machine]

        if filtered_records:
            st.markdown("#### 📋 対象データの範囲選択")
            max_idx = len(filtered_records)
            range_col1, range_col2 = st.columns(2)
            start_idx = range_col1.number_input("開始する台番号（#番目）", min_value=1, max_value=max_idx, value=1, step=1)
            end_idx = range_col2.number_input("終了する台番号（#番目）", min_value=1, max_value=max_idx, value=max_idx, step=1)

            if start_idx <= end_idx:
                target_records = filtered_records[start_idx-1:end_idx]
            else:
                target_records = filtered_records

            is_filtered = (selected_store != "すべて") or (selected_date != "すべて") or (selected_machine != "すべて") or (start_idx > 1 or end_idx < max_idx)
            
            if not is_filtered:
                result_title = "🏆 トータル結果"
            else:
                title_parts = []
                if selected_store != "すべて": title_parts.append(f"店:{selected_store}")
                if selected_date != "すべて": title_parts.append(f"日:{selected_date}")
                if selected_machine != "すべて": title_parts.append(f"台:{selected_machine}")
                if start_idx > 1 or end_idx < max_idx: title_parts.append(f"#{start_idx}-#{end_idx}")
                result_title = f"🏆 選択結果 ({' '.join(title_parts)})"

            grand_total_games = 0
            grand_total_invest_coins = 0
            grand_total_invest_yen = 0
            grand_total_get_coins = 0
            grand_total_diff_coins = 0
            grand_total_time = 0
            win_machine_count = 0

            graph_x = [0]
            graph_y = [0]
            current_games = 0
            current_balance = 0

            st.subheader("📋 登録済み台データ一覧")
            for m_idx, m in enumerate(target_records, 1):
                m_games = sum(s["total_game"] for s in m["sessions"])
                m_invest_c = sum(s["invest_coins"] for s in m["sessions"])
                m_invest_y = sum(s["invest_yen"] for s in m["sessions"])
                m_get_c = sum(s["get_coins"] for s in m["sessions"])
                m_diff_c = sum(s["diff_coins"] for s in m["sessions"])

                if m_diff_c > 0:
                    win_machine_count += 1

                st.write(f"**#{m_idx}** | 日付: {m['date']} | 店舗: **{m['store']}** | 台番号: **{m['machine_id']}番台** (当たり計 {len(m['sessions'])}回) | 総G数: {m_games:.0f}G | 投資: {m_invest_c:.1f}枚 (約{m_invest_y:,.0f}円) | 獲得: {m_get_c}枚 | 差枚: `{m_diff_c:+.1f}枚`")

                grand_total_games += m_games
                grand_total_invest_coins += m_invest_c
                grand_total_invest_yen += m_invest_y
                grand_total_get_coins += m_get_c
                grand_total_diff_coins += m_diff_c
                grand_total_time += sum(s["time_minutes"] for s in m["sessions"])

                for s in m["sessions"]:
                    current_games += s["total_game"]
                    current_balance += s["diff_coins"]
                    graph_x.append(current_games)
                    graph_y.append(current_balance)

            grand_payout = (grand_total_get_coins / grand_total_invest_coins * 100) if grand_total_invest_coins > 0 else 0
            win_rate = (win_machine_count / len(target_records) * 100) if len(target_records) > 0 else 0

            st.markdown("---")
            st.subheader(result_title)
            
            metric_col1, metric_col2, metric_col3, metric_col4, metric_col5, metric_col6 = st.columns(6)
            metric_col1.metric("総ゲーム数", f"{grand_total_games:.0f} G")
            metric_col2.metric("総投資枚数", f"{grand_total_invest_coins:.1f} 枚")
            metric_col3.metric("総投資金額", f"約 {grand_total_invest_yen:,.0f} 円")
            metric_col4.metric("総合差枚", f"{grand_total_diff_coins:+.1f} 枚")
            metric_col5.metric("全体機械割", f"{grand_payout:.1f} %")
            metric_col6.metric("勝率", f"{win_rate:.1f} % ({win_machine_count}/{len(target_records)}台)")
            
            st.write(f"⏱ **総消化時間目安**: 約 {grand_total_time/60:.1f} 時間（{grand_total_time:.1f}分）")

            # --- スランプグラフの描画 ---
            st.subheader("📈 スランプグラフ")
            
            fig, ax = plt.subplots(figsize=(10, 4))
            
            ax.plot(graph_x, graph_y, marker='o', linestyle='-', color='#1f77b4', linewidth=2)
            ax.set_title('スランプグラフ（推移）', fontsize=14)
            ax.set_xlabel('累積ゲーム数 (G)', fontsize=12)
            ax.set_ylabel('差枚数 (枚)', fontsize=12)
            
            ax.yaxis.set_major_locator(ticker.MultipleLocator(500))
            ax.xaxis.set_major_locator(ticker.MultipleLocator(min_30_games))
            
            ax.axhline(0, color='r', linestyle='--', alpha=0.7)
            ax.grid(True, which='both', linestyle=':', alpha=0.7)
            
            st.pyplot(fig)

            # --- 登録済みデータの編集・削除セクション ---
            st.markdown("---")
            st.subheader("✏️ 登録済みデータの編集・削除")
            
            record_labels = [f"#{i+1} | {r['date']} | {r['store']} | {r['machine_id']}番台 (当たり{len(r['sessions'])}回)" for i, r in enumerate(records)]
            selected_to_edit_label = st.selectbox("編集・削除する台データを選択", record_labels)
            selected_edit_idx = record_labels.index(selected_to_edit_label)
            target_record = records[selected_edit_idx]

            edit_col1, edit_col2 = st.columns(2)
            new_store = edit_col1.text_input("店舗名を変更", value=target_record["store"], key="edit_store")
            new_machine_id = edit_col2.text_input("台番号を変更", value=target_record["machine_id"], key="edit_machine_id")

            col_update, col_delete = st.columns(2)
            if col_update.button("🔄 この台の基本情報を更新する"):
                records[selected_edit_idx]["store"] = new_store
                records[selected_edit_idx]["machine_id"] = new_machine_id
                st.success("台情報を更新しました！")
                st.rerun()

            if col_delete.button("🗑️ この台のデータを削除する"):
                records.pop(selected_edit_idx)
                st.warning("台データを削除しました。")
                st.rerun()