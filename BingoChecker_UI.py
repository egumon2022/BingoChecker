# -*- coding: utf-8 -*-
"""
Created on Fri Nov  9 17:00:00 2024

@author: egumon
"""

import streamlit as st
import pandas as pd
import json # <--- 追加
import os   # <--- ファイルの存在チェックのために追加

#DATA_FILE = "bingo_data.json" # 保存ファイル名を定義

class BingoCard:
    def __init__(self, card_number, numbers):
        self.card_number = card_number
        self.numbers = numbers
        self.marked = [[False for _ in range(5)] for _ in range(5)]
        self.marked[2][2] = True  # FREE space
        self.bingo_lines = set()

    def mark_number(self, number):
        marked = False
        for i in range(5):
            for j in range(5):
                if self.numbers[i][j] == number:
                    self.marked[i][j] = True
                    marked = True
        return marked

    def check_bingo(self):
        new_bingo_patterns = []
        
        # Check rows
        for i in range(5):
            line_key = f"row_{i}"
            if line_key not in self.bingo_lines and all(self.marked[i][j] for j in range(5)):
                new_bingo_patterns.append(f"横{i+1}行目")
                self.bingo_lines.add(line_key)

        # Check columns
        for j in range(5):
            line_key = f"col_{j}"
            if line_key not in self.bingo_lines and all(self.marked[i][j] for i in range(5)):
                new_bingo_patterns.append(f"縦{j+1}列目")
                self.bingo_lines.add(line_key)

        # Check diagonals
        if "diagonal1" not in self.bingo_lines and all(self.marked[i][i] for i in range(5)):
            new_bingo_patterns.append("斜め（左上から右下）")
            self.bingo_lines.add("diagonal1")

        if "diagonal2" not in self.bingo_lines and all(self.marked[i][4-i] for i in range(5)):
            new_bingo_patterns.append("斜め（右上から左下）")
            self.bingo_lines.add("diagonal2")

        return new_bingo_patterns
    
    def to_dict(self): # <--- 追加: 辞書に変換するメソッド
        return {
            "card_number": self.card_number,
            "numbers": self.numbers,
            # marked は True/False の二重リストなのでそのまま保存可能
            "marked": self.marked,
            # setはJSONにできないのでlistに変換
            "bingo_lines": list(self.bingo_lines) 
        }

def create_bingo_display(card):
    # Create DataFrame for display
    display_data = []
    if len(card.numbers) != 5 or any(len(row) != 5 for row in card.numbers):
        st.error("Invalid bingo card format: The card should have a 5x5 grid of numbers.")
        return pd.DataFrame()

    for i in range(5):
        row = []
        for j in range(5):
            if i == 2 and j == 2:
                cell = "FREE"
            else:
                number = card.numbers[i][j]
                marked = card.marked[i][j]
                cell = f"{number}{'✓' if marked else ''}"
            row.append(cell)
        display_data.append(row)
    return pd.DataFrame(display_data)

def save_cards(cards, data_file): # <-- data_file を引数に追加
    """ビンゴカードのリストをJSONファイルに保存する"""
    data_to_save = [card.to_dict() for card in cards]
    # data_file を使用
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=4)

def load_cards(data_file): # <-- data_file を引数に追加
    """JSONファイルからビンゴカードを読み込む"""
    # data_file を使用
    if not os.path.exists(data_file):
        return []
        
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        cards = []
        for d in data:
            # 辞書からBingoCardオブジェクトを再構築 (ここは変更なし)
            card = BingoCard(d['card_number'], d['numbers'])
            card.marked = d['marked']
            card.bingo_lines = set(d['bingo_lines']) # setに戻す
            cards.append(card)
        return cards
def reset_manual_input_fields():
    """手動登録フォームの入力フィールドをセッションステートから削除する"""
    if "card_number_input" in st.session_state:
        del st.session_state["card_number_input"]
        
    for i in range(5):
        key = f"row_input_{i}"
        if key in st.session_state:
            del st.session_state[key]
            
def main():
    # layout Setting
    st.set_page_config(layout="wide")
    # Title for APP
    st.title("BINGO GAME Checker")
    st.markdown(" <br> ********************************", unsafe_allow_html=True)
    
    # 【修正部分】アクセスIDの入力とセッションステートへの保存
    if 'access_id' not in st.session_state:
        # メイン画面にコンテナを配置して入力エリアを作成
        with st.container():
            st.subheader("🔑 アクセスID設定")
            st.warning("アクセスIDは、お客様ご自身のデータ（ビンゴカードやマーク状態）を分離・保存するために必要です。同じアクセスIDを使用することで、任意の端末で同期することができます。")
            
            col_input, col_button = st.columns([3, 1])
            with col_input:
                user_input = st.text_input("アクセスID（任意の半角英数字）を入力してください", key="user_access_id_input_main")
            
            with col_button:
                # ボタンを少し下に配置して見やすくする
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("IDを決定"):
                    if user_input:
                        st.session_state.access_id = user_input
                        st.rerun()
                    else:
                        st.error("IDを入力してください")
        
        # IDが未設定の場合は、これ以降の処理を中断
        if 'access_id' not in st.session_state:
            # 既に上のコンテナで警告を表示しているので、returnで中断
            return
    
    # ユーザー固有のデータファイルパスを定義
    # 例: "bingo_data_userA.json", "bingo_data_userB.json" のように分かれる
    USER_DATA_FILE = f"bingo_data_{st.session_state.access_id}.json"


    # Initialize session state
    if 'cards' not in st.session_state:
        # 【修正】定義したユーザー固有のファイルパスを渡してロード
        st.session_state.cards = load_cards(USER_DATA_FILE)
    
    if 'used_numbers' not in st.session_state:
        st.session_state.used_numbers = set()

    # 【新規追加】登録モードの状態管理
    if 'registration_mode' not in st.session_state:
        # False: ビンゴモード (初期状態) / True: 登録モード
        st.session_state.registration_mode = False 
        
    st.subheader("⚙️ **ビンゴカードの管理モード**")
    col_reg_btn, col_start_btn, col_other_btn = st.columns([1, 1, 1])

    is_reg_mode = st.session_state.registration_mode # 現在の状態

    with col_reg_btn:
       # カードを登録するモードに入るボタン
        if st.button("📝 カード登録", 
                     type="primary" if is_reg_mode else "secondary", # 登録モードなら青
                     use_container_width=True):
            st.session_state.registration_mode = True
            st.rerun()

    with col_start_btn:
        # ビンゴモード（マーク画面）に入るボタン
        if st.button("🎯 番号マーク", 
                     type="primary" if not is_reg_mode else "secondary", # ビンゴモードなら青
                     use_container_width=True):
            st.session_state.registration_mode = False
            st.rerun()
            
    with col_other_btn:
        st.button("🖼️ 画像認識 (準備中)", disabled=True, use_container_width=True)
        
    st.markdown("---") # 区切り線

    # Manual card registration (登録モードの場合にのみ表示)
    if st.session_state.registration_mode:
        
        # st.form でフォーム全体をラップし、フォーム送信時にリセットさせる
        with st.form(key='manual_bingo_card_form'):
            
            st.subheader("✍️ **カード登録フォーム**")
            
            # フォーム内の変数定義
            card_number = st.text_input("🆔 **カード番号を入力してください**", key="form_card_number_input")
            
            numbers = []
            rows_valid = True
            
            # 5x5の数字入力フィールドを定義
            for i in range(5):
                if i != 2:
                    prompt = f"行{i+1}の数字を空白区切りで入力してください (例: 13 22 42 49 61)"
                else:
                    prompt = "※真ん中（FREE）は 0 を入力してください (例: 13 22 0 49 61)"
                
                # key を form_row_input_i に変更 (フォーム内キーは固有である必要があります)
                # ここで入力が行われる
                row_input = st.text_input(prompt, key=f"form_row_input_{i}") 
                
                # フォームが送信されるまで、入力値を使ってnumbersを構築
                if row_input:
                    try:
                        row_numbers = [int(num) for num in row_input.split()]
                        if len(row_numbers) == 5:
                            numbers.append(row_numbers)
                        else:
                            rows_valid = False
                    except ValueError:
                        rows_valid = False

            # フォーム送信ボタン
            submitted = st.form_submit_button("💾 このカードを登録し、次へ", type="primary")

            # フォーム送信後の処理
            if submitted:
                # フォーム送信時、 numbers が 5x5 のリストになっているか最終チェック
                is_numbers_complete = (len(numbers) == 5)
                
                if card_number and is_numbers_complete and rows_valid:
                    # 登録対象のカードオブジェクトを作成
                    new_card = BingoCard(card_number, numbers)
                    
                    if any(card.card_number == new_card.card_number for card in st.session_state.cards):
                        st.warning("このカード番号は既に登録されています")
                        # 警告を表示してもフォームはクリアされる
                    else:
                        st.session_state.cards.append(new_card)
                        save_cards(st.session_state.cards, USER_DATA_FILE)

                        # 成功メッセージはフォームの外に出して、クリアされないようにします
                        st.session_state.last_registered_card = new_card.card_number
                        st.rerun() # 成功メッセージを表示するために再描画
                else:
                    st.error("全ての入力フィールドを正しく入力してください")

        st.markdown("---")

        # 登録成功メッセージをフォームの外で表示
        if 'last_registered_card' in st.session_state:
            st.success(
                f"🎉 **カード No.{st.session_state.last_registered_card}** が登録されました！"
                f"続けて次のカードを登録できます。"
            )
            del st.session_state['last_registered_card'] # 一度表示したら削除

    # Display called numbers
    if not st.session_state.registration_mode: # 【条件追加】ビンゴモードのみ表示
        st.subheader("🎯 今、呼ばれた番号")
        col1, col2 = st.columns([1, 5])
        with col1:
            number = st.number_input("🔢 **番号を入力してください** (1-75):", min_value=1, max_value=75, step=1, key="called_number_input")
        with col2:
            if st.button("✅ マークする", type="primary"):
                if number in st.session_state.used_numbers:
                    st.warning(f"番号 {number} は既に使用されています")
                else:
                    st.session_state.used_numbers.add(number)
                    
                    # マーク/ビンゴ判定後にカードデータを保存する必要があるかチェック
                    data_changed = False
                    for card in st.session_state.cards:
                        if card.mark_number(number):
                            data_changed = True # マークされたらデータ変更フラグを立てる
                            st.success(f"Card No.{card.card_number}でマークされました！")
                        
                        patterns = card.check_bingo()
                        if patterns:
                            data_changed = True # ビンゴが発生してもデータ変更フラグを立てる
                            
                            st.balloons()
                            st.success(f"BINGO! Card No.{card.card_number}で新しいビンゴが発生しました！")
                            for pattern in patterns:
                                st.write(f"- {pattern}")
                      # --- [END] for ループ ---
                    
                    # ★ データが変更された場合、ファイルを保存 (ループの外で一度だけ呼び出す)
                    if data_changed: 
                        save_cards(st.session_state.cards, USER_DATA_FILE)

    # Display used numbers
    if not st.session_state.registration_mode: # 【追加】ビンゴモードのみ表示
        st.subheader("🗒️ **これまでに呼ばれた番号**")
        used_numbers_str = ", ".join(map(str, sorted(list(st.session_state.used_numbers))))
        st.markdown(f"`{used_numbers_str}`")
        
        # Display Bingo'd card numbers
        st.subheader("👑 **BINGOになったカード番号**")
        bingo_card_numbers = [card.card_number for card in st.session_state.cards if card.bingo_lines]
        bingo_card_numbers_str = ", ".join(map(str, sorted(bingo_card_numbers)))
        st.markdown(f"`{bingo_card_numbers_str}`")
    
    # Display cards
    st.subheader("📋 **ビンゴカード一覧**")
    for i, card in enumerate(st.session_state.cards):
        st.write(f"Card No.{card.card_number}")
        st.dataframe(create_bingo_display(card), use_container_width=True)
        if card.bingo_lines:
            st.write("ビンゴライン:", list(card.bingo_lines))
        if st.button(f"カード No.{card.card_number}を削除", key=f"delete_{i}"):
            removed_card_number = st.session_state.cards[i].card_number
            st.session_state.cards.pop(i)
            # 修正: USER_DATA_FILE を引数に追加
            save_cards(st.session_state.cards, USER_DATA_FILE)
            st.success(f"カード No.{removed_card_number} を削除しました")
            st.rerun() # 削除後に即座に表示を更新するためリロード
    
    st.write("©egumon2022 2025/11/7 version_12", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
