# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 16:00:00 2024

@author: egumon
"""
class BingoCard:
    def __init__(self, card_number, numbers):
        """
        ビンゴカードを初期化する
        :param card_number: カード番号
        :param numbers: 5x5の数字リスト
        """
        self.card_number = card_number
        self.numbers = numbers
        self.marked = [[False for _ in range(5)] for _ in range(5)]
        # 中央のFREEマスを既にマークされた状態にする
        self.marked[2][2] = True

    def mark_number(self, called_number):
        """
        呼ばれた番号をマークする
        :param called_number: 呼ばれた番号
        :return: マークされたかどうか
        """
        if called_number.upper() == 'FREE':
            return False
            
        try:
            number = int(called_number)
            for i in range(5):
                for j in range(5):
                    if self.numbers[i][j] == number:
                        self.marked[i][j] = True
                        return True
            return False
        except ValueError:
            return False

    def check_bingo(self):
        """
        ビンゴになっているかチェックする
        :return: ビンゴパターンのリスト
        """
        bingo_patterns = []

        # 横のチェック
        for i, row in enumerate(self.marked):
            if all(row):
                bingo_patterns.append(f"横{i+1}行目")

        # 縦のチェック
        for j in range(5):
            if all(self.marked[i][j] for i in range(5)):
                bingo_patterns.append(f"縦{j+1}列目")

        # 斜めのチェック（左上から右下）
        if all(self.marked[i][i] for i in range(5)):
            bingo_patterns.append("斜め（左上から右下）")

        # 斜めのチェック（右上から左下）
        if all(self.marked[i][4-i] for i in range(5)):
            bingo_patterns.append("斜め（右上から左下）")

        return bingo_patterns

    def display(self):
        """
        現在のカードの状態を表示する
        """
        print(f"Card No.{self.card_number}")
        for i in range(5):
            for j in range(5):
                if i == 2 and j == 2:
                    print("FREE\t", end="")
                else:
                    mark = "X" if self.marked[i][j] else " "
                    print(f"{self.numbers[i][j]}{mark}\t", end="")
            print()
        print()

def run_interactive_bingo(cards):
    """
    対話形式でビンゴゲームを実行する
    :param cards: BingoCardのリスト
    """
    bingo_cards = {}  # カードごとのビンゴパターンを記録
    used_numbers = set()
    flag=0
    bingo_history = []  # ビンゴの履歴を保持する
    
    while True:
        # 現在のカードの状態を表示
        print("********************************************************")
        print("\n現在のカードの状態:")
        for card in cards:
            card.display()
            
        # 入力を受け付ける
        input_str = input("\n*番号を入力してください（終了する場合は'q'を入力）: ").strip()
            
        # 終了条件をチェック
        if input_str.lower() == 'q':
            break

        if input_str.upper() == 'FREE':
            print("FREEは入力できません")
            continue
            
        try:
            # 数値に変換
            number = int(input_str)
            
            # 1-75の範囲チェック
            if number < 1 or number > 75:
                print("エラー: 1から75までの数字を入力してください")
                continue
                
            # 既に使用された番号かチェック
            if number in used_numbers:
                print(f"警告: {number}は既に呼ばれています")
                continue
                
            used_numbers.add(number)
            print(f"\n呼ばれた番号: {number}")
            print(f"\nこれまでのビンゴ数: {flag}")
            
            # 各カードをチェック
            for card in cards:
                if card.mark_number(str(number)):
                    print(f"Card No.{card.card_number}でマークされました！")
                
                # ビンゴチェック
                current_patterns = card.check_bingo()
                if card.card_number not in bingo_cards:
                    bingo_cards[card.card_number] = set()
                
                # 新しいビンゴパターンをチェック
                new_patterns = set(current_patterns) - bingo_cards[card.card_number]
                if new_patterns:
                    print("\n！！！！！！congratulation！！！！！！")
                    print(f"BINGO! Card No.{card.card_number}で新しいビンゴが発生しました！")
                    flag+=1
                    for pattern in new_patterns:
                        print(f"- {pattern}")
                    bingo_cards[card.card_number].update(new_patterns)
                    # ビンゴ履歴に追加
                    bingo_history.append((card.card_number, flag))
            
        except ValueError:
            print("エラー: 有効な数字を入力してください")
            continue
        
        print("\n使用された番号:", sorted(list(used_numbers)))
    # ゲーム終了時のビンゴ履歴を表示
    print("\n========= ビンゴ履歴 =========")
    for card_num, count in bingo_history:
        print(f"Card No.{card_num} - ビンゴ回数: {count}")
    print("=============================")

# カードの初期化
card1 = BingoCard(5890, [
    [13, 22, 42, 49, 61],
    [6, 21, 38, 57, 64],
    [2, 16, 0, 55, 66],  # 0は FREE スペース
    [11, 23, 35, 58, 65],
    [5, 29, 45, 53, 70]
])

card2 = BingoCard(4119, [
    [4, 19, 41, 46, 74],
    [7, 26, 44, 58, 70],
    [12, 27, 0, 60, 65],  # 0は FREE スペース
    [11, 16, 36, 56, 73],
    [8, 17, 33, 51, 63]
])

# プログラムを実行
cards = [card1, card2]
print("ビンゴゲームを開始します！")
run_interactive_bingo(cards)