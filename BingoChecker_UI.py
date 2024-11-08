# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 19:00:00 2024

@author: egumon
"""

import streamlit as st
import pandas as pd

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

def create_bingo_display(card):
    # Create DataFrame for display
    display_data = []
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

def main():
    # アプリケーションのタイトル
    st.title("ビンゴゲーム")
    
    # Initialize session state
    if 'cards' not in st.session_state:
        st.session_state.cards = [
            BingoCard(5890, [
                [13, 22, 42, 49, 61],
                [6, 21, 38, 57, 64],
                [2, 16, 0, 55, 66],
                [11, 23, 35, 58, 65],
                [5, 29, 45, 53, 70]
            ]),
            BingoCard(4119, [
                [4, 19, 41, 46, 74],
                [7, 26, 44, 58, 70],
                [12, 27, 0, 60, 65],
                [11, 16, 36, 56, 73],
                [8, 17, 33, 51, 63]
            ])
        ]
    
    if 'used_numbers' not in st.session_state:
        st.session_state.used_numbers = set()

    # Input section
    col1, col2 = st.columns([1, 5])
    with col1:
        number = st.number_input("番号を入力してください (1-75):", min_value=1, max_value=75, step=1)
    with col2:
        if st.button("マークする"):
            if number in st.session_state.used_numbers:
                st.warning(f"番号 {number} は既に使用されています")
            else:
                st.session_state.used_numbers.add(number)
                for card in st.session_state.cards:
                    if card.mark_number(number):
                        st.success(f"Card No.{card.card_number}でマークされました！")
                        patterns = card.check_bingo()
                        if patterns:
                            st.balloons()
                            st.success(f"BINGO! Card No.{card.card_number}で新しいビンゴが発生しました！")
                            for pattern in patterns:
                                st.write(f"- {pattern}")

    # Display used numbers
    #st.write("使用された番号:", sorted(list(st.session_state.used_numbers)))
    st.subheader("これまでに呼ばれた番号")
    used_numbers_str = ", ".join(map(str, sorted(list(st.session_state.used_numbers))))
    st.markdown(f"`{used_numbers_str}`")
    
    # Display cards
    st.subheader("ビンゴカード")
    for card in st.session_state.cards:
        st.write(f"Card No.{card.card_number}")
        st.dataframe(create_bingo_display(card), use_container_width=True)
        if card.bingo_lines:
            st.write("ビンゴライン:", list(card.bingo_lines))
        st.divider()

    # Reset button
    if st.button("ゲームをリセット"):
        st.session_state.clear()
        st.experimental_rerun()

if __name__ == "__main__":
    main()