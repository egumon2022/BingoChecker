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

def create_bingo_card_manually():
    st.subheader("ビンゴカードの手動登録")

    # Get card number
    card_number = st.text_input("＊カード番号を入力してください", key="card_number_input")

    # Get bingo numbers
    numbers = []
    rows_valid = True
    for i in range(5):
        if i != 2:
            prompt = f"行{i+1}の数字を空白区切りで入力してください (例: 13 22 42 49 61)"
        else:
            prompt = "※真ん中（FREE）は 0 を入力してください (例: 13 22 0(=FREE) 49 61)"
        
        row = st.text_input(prompt, key=f"row_input_{i}")
        
        try:
            if row:
                row_numbers = [int(num) for num in row.split()]
                if len(row_numbers) == 5:
                    numbers.append(row_numbers)
                else:
                    rows_valid = False
        except ValueError:
            rows_valid = False

    # Create BingoCard object only if all inputs are valid
    if card_number and len(numbers) == 5 and rows_valid:
        return BingoCard(card_number, numbers)
    return None

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

def main():
    # layout Setting
    st.set_page_config(layout="wide")
    # Title for APP
    st.title("BINGO GAME Checker")
    st.markdown(" <br> ********************************", unsafe_allow_html=True)
    
    # 【追加部分】アクセスIDの入力とセッションステートへの保存
    if 'access_id' not in st.session_state:
        st.sidebar.subheader("アクセスID設定")
        user_input = st.sidebar.text_input("アクセスID（任意の半角英数字）を入力してください", key="user_access_id_input")
        if st.sidebar.button("IDを決定"):
            if user_input:
                st.session_state.access_id = user_input
                st.rerun()
            else:
                st.sidebar.error("IDを入力してください")
        
        # IDが未設定の場合は、これ以降の処理を中断
        if 'access_id' not in st.session_state:
            st.warning("左のサイドバーからアクセスIDを入力して、データを分離してください。")
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

    # フォームリセットフラグの初期化
    if 'reset_form' not in st.session_state:
        st.session_state.reset_form = False

    # Manual card registration
    registration_option = st.selectbox("ビンゴカードの登録方法を選択", ["自動認識", "手動入力", "今はしない"])
    if registration_option == "手動入力":
        new_card = create_bingo_card_manually()
        if st.button("カードを登録する"):
            if new_card is not None:
                if any(card.card_number == new_card.card_number for card in st.session_state.cards):
                    st.warning("このカード番号は既に登録されています")
                else:
                    st.session_state.cards.append(new_card)
                    # 修正: USER_DATA_FILE を引数に追加
                    save_cards(st.session_state.cards, USER_DATA_FILE)
                    st.success(f"カード No.{new_card.card_number} が登録されました")
                    # フォームリセットフラグを設定
                    st.session_state.reset_form = True
                    # ページを再読み込み
                    st.rerun()
            else:
                st.error("全ての入力フィールドを正しく入力してください")
    elif registration_option == "今はしない":
        pass
    # TODO: Implement automatic registration

    # Display called numbers
    st.subheader("＿＿今、呼ばれた番号＿＿")
    col1, col2 = st.columns([1, 5])
    with col1:
        number = st.number_input("番号を入力してください (1-75):", min_value=1, max_value=75, step=1)
    with col2:
        if st.button("マークする"):
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
                    # ★ データが変更された場合、ファイルを保存
                    if data_changed: 
                    # 修正: USER_DATA_FILE を引数に追加
                    save_cards(st.session_state.cards, USER_DATA_FILE)

    # Display used numbers
    st.subheader("これまでに呼ばれた番号")
    used_numbers_str = ", ".join(map(str, sorted(list(st.session_state.used_numbers))))
    st.markdown(f"`{used_numbers_str}`")

    # Display Bingo'd card numbers
    st.subheader("BINGOになったカードまとめ")
    bingo_card_numbers = [card.card_number for card in st.session_state.cards if card.bingo_lines]
    bingo_card_numbers_str = ", ".join(map(str, sorted(bingo_card_numbers)))
    st.markdown(f"`{bingo_card_numbers_str}`")
    
    # Display cards
    st.subheader("～～ビンゴカード一覧～～")
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
    
    st.write("©egumon2022 2025/11/7 version_7", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
