import matplotlib.pyplot as plt
#import japanize_matplotlib  # 日本語文字化け防止
# Windowsの標準日本語フォント（MS Gothic）を直接指定して文字化けを防ぐ
plt.rcParams['font.family'] = 'MS Gothic'

def run_slot_tool():
    print("=== パチスロ実戦データ解析ツール（Lかぐや対応・最新版） ===")
    
    BASE_GAMES = 31.0          # 50枚あたりの回転数（ベース：50枚で31G）
    YEN_PER_MEDAL = 1000 / 46  # 1枚あたりの金額（1,000円＝46枚貸出約21.74円）
    
    # 消化スピードの設定（7分で100回転 → 1分あたりの回転数 = 100 / 7）
    RPM = 100 / 7 

    machines = []
    
    while True:
        machine_num = len(machines) + 1
        print(f"\n========================================")
        print(f"         【 第 {machine_num} 台目のデータ入力 】")
        print(f"========================================")
        
        sessions = []
        
        while True:
            session_num = len(sessions) + 1
            print(f"\n--- [台{machine_num}] 第 {session_num} 回目の当たりデータ ---")
            
            # 1. 何回目のCZで当たったか（天井8回を考慮）
            while True:
                try:
                    cz_times = int(input("何回目のCZで当たりましたか？（例: 1〜8 ※直撃なら0）: "))
                    if cz_times < 0:
                        print("0以上の整数を入力してください。")
                        continue
                    
                    # 9回以上の場合の警告チェック
                    if cz_times >= 9:
                        print(f"\n[!] 注意: CZスルー天井は通常8回のはずですが、「{cz_times}回」と入力されています。")
                        check = input("本当に入力した回数で合っていますか？ (y/もう一度入力し直すn): ").strip().lower()
                        if check != 'y':
                            continue
                            
                    break
                except ValueError:
                    print("数字で正しく入力してください。")
                    
            # 2. 各CZにかかったゲーム数の入力
            cz_games_list = []
            for i in range(1, cz_times + 1):
                while True:
                    try:
                        g = float(input(f"  -> 【CZ {i}回目】にかかったゲーム数(G): "))
                        if g < 0:
                            print("0以上の数値を入力してください。")
                            continue
                        cz_games_list.append(g)
                        break
                    except ValueError:
                        print("数字で正しく入力してください。")
            
            # 3. 当たりまでの最終ゲーム数
            while True:
                try:
                    final_games = float(input("CZ当選からボーナス確定までのゲーム数(G): "))
                    if final_games < 0:
                        print("0以上の数値を入力してください。")
                        continue
                    break
                except ValueError:
                    print("数字で正しく入力してください。")
                    
            total_cz_games = sum(cz_games_list)
            total_game = total_cz_games + final_games
            
            # 4. 獲得枚数
            while True:
                try:
                    get_coins = float(input("獲得枚数（枚）を入力: "))
                    break
                except ValueError:
                    print("数字で正しく入力してください。")
                    
            # 計算処理
            # 投資枚数 ＝ 総ゲーム数 ÷ 50枚あたりの回転数(31G) × 50枚
            invest_coins = (total_game / BASE_GAMES) * 50
            invest_yen = invest_coins * YEN_PER_MEDAL
            diff_coins = get_coins - invest_coins
            
            # 消化時間の計算（7分で100回転をベースに算出）
            time_minutes = total_game / RPM

            # 入力内容の確認
            print(f"  [確認] 当たりまで計 {total_game:.0f}G | 投資 {invest_coins:.1f}枚 | 獲得 {get_coins}枚 | 差枚 {diff_coins:+.1f}枚 | 予想時間 {time_minutes:.1f}分")
            confirm = input("この内容で確定しますか？ (y/修正するn): ").strip().lower()
            if confirm == 'n':
                print("-> この回の入力をやり直します。")
                continue

            sessions.append({
                "cz_times": cz_times,
                "cz_games": cz_games_list,
                "final_games": final_games,
                "total_game": total_game,
                "invest_coins": invest_coins,
                "invest_yen": invest_yen,
                "get_coins": get_coins,
                "diff_coins": diff_coins,
                "time_minutes": time_minutes
            })
            
            cont = input(f"\n[台{machine_num}] 次の当たりのデータを続けますか？ (y/n): ").strip().lower()
            if cont != 'y':
                break
                
        if sessions:
            machines.append({
                "machine_num": machine_num,
                "sessions": sessions
            })
            
        next_machine = input("\n別の台（次の台）のデータを入力しますか？ (y/n): ").strip().lower()
        if next_machine != 'y':
            break

    # --- 入力完了後の「データ修正・確認タイム」 ---
    while True:
        print("\n" + "="*40)
        print("          【 入力データの確認・修正 】")
        print("="*40)
        for m in machines:
            print(f"■ 台 {m['machine_num']} （全 {len(m['sessions'])} 回の当たり）")
            for idx, s in enumerate(m['sessions'], 1):
                print(f"   - 当たり #{idx}: 総G数 {s['total_game']:.0f}G / 投資 {s['invest_coins']:.1f}枚 / 獲得 {s['get_coins']}枚 / 差枚 {s['diff_coins']:+.1f}枚")
        
        fix_choice = input("\nデータを修正したい箇所はありますか？\n(修正するなら '台番号-回数' 例: 1-2 / そのまま集計に進むなら 'ok'): ").strip()
        
        if fix_choice.lower() == 'ok':
            break
            
        try:
            m_idx_str, s_idx_str = fix_choice.split('-')
            target_m = int(m_idx_str)
            target_s = int(s_idx_str)
            
            found = False
            for m in machines:
                if m["machine_num"] == target_m:
                    if 1 <= target_s <= len(m["sessions"]):
                        found = True
                        print(f"\n--- 【台 {target_m} - 第 {target_s} 回目の再入力】 ---")
                        
                        cz_times = int(input("何回目のCZで当たりましたか？（直撃なら0）: "))
                        cz_games_list = []
                        for i in range(1, cz_times + 1):
                            g = float(input(f"  -> 【CZ {i}回目】にかかったゲーム数(G): "))
                            cz_games_list.append(g)
                        final_games = float(input("CZ当選からボーナス確定までのゲーム数(G): "))
                        total_cz_games = sum(cz_games_list)
                        total_game = total_cz_games + final_games
                        get_coins = float(input("獲得枚数（枚）を入力: "))
                        
                        invest_coins = (total_game / BASE_GAMES) * 50
                        invest_yen = invest_coins * YEN_PER_MEDAL
                        diff_coins = get_coins - invest_coins
                        time_minutes = total_game / RPM
                        
                        m["sessions"][target_s - 1] = {
                            "cz_times": cz_times,
                            "cz_games": cz_games_list,
                            "final_games": final_games,
                            "total_game": total_game,
                            "invest_coins": invest_coins,
                            "invest_yen": invest_yen,
                            "get_coins": get_coins,
                            "diff_coins": diff_coins,
                            "time_minutes": time_minutes
                        }
                        print("-> 修正が完了しました！")
            if not found:
                print("指定した台番号や回数が見つかりませんでした。")
        except Exception:
            print("入力形式が正しくありません。'1-2' のように入力するか 'ok' と入力してください。")

    # --- 全体の集計と出力 ---
    if not machines:
        print("データが入力されませんでした。")
        return

    print("\n" + "="*50)
    print("          【 全台トータル＆各台の集計結果 】")
    print("="*50)

    grand_total_games = 0
    grand_total_invest_coins = 0
    grand_total_invest_yen = 0
    grand_total_get_coins = 0
    grand_total_diff_coins = 0
    grand_total_time = 0

    all_diff_history = [0]
    current_balance = 0

    for m in machines:
        m_num = m["machine_num"]
        m_games = sum(s["total_game"] for s in m["sessions"])
        m_invest_c = sum(s["invest_coins"] for s in m["sessions"])
        m_invest_y = sum(s["invest_yen"] for s in m["sessions"])
        m_get_c = sum(s["get_coins"] for s in m["sessions"])
        m_diff_c = sum(s["diff_coins"] for s in m["sessions"])
        m_time = sum(s["time_minutes"] for s in m["sessions"])
        
        m_payout = (m_get_c / m_invest_c * 100) if m_invest_c > 0 else 0

        grand_total_games += m_games
        grand_total_invest_coins += m_invest_c
        grand_total_invest_yen += m_invest_y
        grand_total_get_coins += m_get_c
        grand_total_diff_coins += m_diff_c
        grand_total_time += m_time

        print(f"\n■ 【台 {m_num}】")
        print(f"  - 当たり回数     : {len(m['sessions'])} 回")
        print(f"  - 総ゲーム数     : {m_games:.0f} G")
        print(f"  - 投資枚数/金額  : {m_invest_c:.1f} 枚 (約 {m_invest_y:,.0f} 円)")
        print(f"  - 獲得枚数       : {m_get_c:.1f} 枚")
        print(f"  - 差枚数         : {m_diff_c:+.1f} 枚")
        print(f"  - 機械割         : {m_payout:.1f} %")
        print(f"  - 推定消化時間   : 約 {m_time:.1f} 分 ({m_time/60:.1f} 時間)")

        for s in m["sessions"]:
            current_balance += s["diff_coins"]
            all_diff_history.append(current_balance)

    grand_payout = (grand_total_get_coins / grand_total_invest_coins * 100) if grand_total_invest_coins > 0 else 0

    print("\n" + "="*50)
    print("                【 総合計 】")
    print("="*50)
    print(f" 視察台数         : {len(machines)} 台")
    print(f" 総ゲーム数       : {grand_total_games:.0f} G")
    print(f" 総投資枚数/金額  : {grand_total_invest_coins:.1f} 枚 (約 {grand_total_invest_yen:,.0f} 円)")
    print(f" 総獲得枚数       : {grand_total_get_coins:.1f} 枚")
    print(f" 【総合トータル差枚】: {grand_total_diff_coins:+.1f} 枚")
    print(f" 全体機械割       : {grand_payout:.1f} %")
    print(f" 総消化時間       : 約 {grand_total_time:.1f} 分 ({grand_total_time/60:.1f} 時間)")
    print("="*50)

    # --- スランプグラフの描画 ---
    try:
        plt.figure(figsize=(10, 5))
        plt.plot(all_diff_history, marker='o', linestyle='-', color='b', linewidth=2)
        plt.title('Slot Slump Graph (Cumulative Diff Coins)', fontsize=14)
        plt.xlabel('Hit Count (Sequence)', fontsize=12)
        plt.ylabel('Diff Coins (枚)', fontsize=12)
        plt.axhline(0, color='r', linestyle='--', alpha=0.7)
        plt.grid(True)
        print("\n[INFO] スランプグラフを表示します。ウィンドウを閉じるとプログラムが終了します。")
        plt.show()
    except Exception as e:
        print(f"\n[NOTE] グラフ描画スキップ: {e}")

if __name__ == "__main__":
    run_slot_tool()