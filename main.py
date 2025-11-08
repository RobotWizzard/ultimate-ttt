from game.board import Board
from ai.random_agent import RandomAgent

def main():
    board = Board()
    agent = RandomAgent()
    while not board.is_terminal():
        print(board)
        big_row = int(input("Enter big row (0-2): "))
        big_col = int(input("Enter big column (0-2): "))
        small_row = int(input("Enter small row (0-2): "))
        small_col = int(input("Enter small column (0-2): "))
        board.make_move((big_row, big_col), (small_row, small_col))
        if board.is_terminal():
            break
        ai_move = agent.choose_move(board)
        board.make_move(ai_move[0], ai_move[1])

if __name__ == "__main__":
    main()
