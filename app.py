from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BOARD_SIZE = 14

# 전역 게임 상태
board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
current_player = "black"  # 처음엔 black부터 시작

def check_winner(row, col):
    """현재 돌의 위치에서 가로, 세로, 대각선 4방향으로 연속 5개 이상이면 승리."""
    player = board[row][col]
    if not player:
        return False
    directions = [(1,0), (0,1), (1,1), (1,-1)]
    for dr, dc in directions:
        count = 1
        # 한쪽 방향 검사
        for step in range(1, 5):
            r, c = row + dr*step, col + dc*step
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == player:
                count += 1
            else:
                break
        # 반대쪽 방향 검사
        for step in range(1, 5):
            r, c = row - dr*step, col - dc*step
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == player:
                count += 1
            else:
                break
        if count >= 5:
            return True
    return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/game', methods=['GET'])
def get_game():
    return jsonify({
        "board": board,
        "current_player": current_player
    })

@app.route('/api/move', methods=['POST'])
def make_move():
    global board, current_player
    data = request.get_json()
    row_letter = data.get("row")
    col_val = data.get("col")
    if not row_letter or not col_val:
        return jsonify({"status": "error", "message": "Invalid data"}), 400

    # 행: A -> 0, B -> 1, ... 변환, 열은 1-indexed
    row_index = ord(row_letter.upper()) - ord('A')
    col_index = int(col_val) - 1

    if row_index < 0 or row_index >= BOARD_SIZE or col_index < 0 or col_index >= BOARD_SIZE:
        return jsonify({"status": "error", "message": "Out of board range"}), 400

    if board[row_index][col_index] is not None:
        return jsonify({"status": "error", "message": "Cell already occupied"}), 400

    # 돌 두기
    board[row_index][col_index] = current_player

    # 승리 확인
    win = check_winner(row_index, col_index)
    response = {
        "status": "success",
        "board": board,
        "move": {"row": row_letter.upper(), "col": col_val},
        "current_player": current_player
    }
    if win:
        response["winner"] = current_player
    else:
        # 플레이어 교체
        current_player = "white" if current_player == "black" else "black"
        response["current_player"] = current_player
    return jsonify(response)

@app.route('/api/game/reset', methods=['POST'])
def reset_game():
    global board, current_player
    board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    current_player = "black"
    return jsonify({"status": "success", "message": "Game reset", "board": board, "current_player": current_player})

if __name__ == '__main__':
    app.run(debug=True)
