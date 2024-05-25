from __future__ import annotations
import asyncio
import websockets


class PlayerClient:
    def __init__(self, player_number: int, socket: websockets.WebSocketClientProtocol, loop: asyncio.AbstractEventLoop):
        self._loop = loop
        self._socket = socket
        self._player_number = player_number
        self.p1Actions = ['U034', 'B037', 'J266', 'M149', 'O763', 'R0A3', 'F0C6', 'K113', 'T021', 'L5D2', 'G251', 'E291', 'D057', 'A053']
        self.p2Actions = ['A0AA', 'B098', 'N0A5', 'L659', 'K33B', 'J027', 'E2B9', 'C267', 'U07C', 'M3AD', 'O2BB', 'R41C']
        self.p1turn = 0
        self.p2turn = 0

    @property
    def player_number(self) -> int:
        return self._player_number

    async def close(self):
        await self._socket.close()

    async def play(self):
        while True:
            board = await self._socket.recv()
            action = self.create_action(board)
            await self._socket.send(action)
            if action == 'X000':
                raise SystemExit
    
    def string_to_2d_array(self, string):
        # 行に分割
        rows = string.split("\n")
        # 最初の行を無視
        rows = rows[1:]
        # 各行の最初の文字を無視して二次元配列を作成
        array_2d = [list(row[1:]) for row in rows]
        return array_2d
    
    # def find_all_dots_with_diagonal_o(self, board_2d):
    #     rows = len(board_2d)
    #     cols = len(board_2d[0]) if rows > 0 else 0
    #     result = []

    #     for i in range(rows):
    #         for j in range(cols):
    #             if board_2d[i][j] == '.':
    #                 # Check diagonal directions for 'o'
    #                 if (i > 0 and j > 0 and board_2d[i-1][j-1] == 'o') or \
    #                 (i > 0 and j < cols - 1 and board_2d[i-1][j+1] == 'o') or \
    #                 (i < rows - 1 and j > 0 and board_2d[i+1][j-1] == 'o') or \
    #                 (i < rows - 1 and j < cols - 1 and board_2d[i+1][j+1] == 'o'):
    #                     result.append((i, j))
    #     return result

    def find_all_dots_with_diagonal_o(self, board_2d):
        rows = len(board_2d)
        cols = len(board_2d[0]) if rows > 0 else 0
        result = []

        for i in range(rows):
            for j in range(cols):
                if board_2d[i][j] == '.':
                    # Check diagonal directions for 'o'
                    diagonal_o = (
                        (i > 0 and j > 0 and board_2d[i-1][j-1] == 'o') or
                        (i > 0 and j < cols - 1 and board_2d[i-1][j+1] == 'o') or
                        (i < rows - 1 and j > 0 and board_2d[i+1][j-1] == 'o') or
                        (i < rows - 1 and j < cols - 1 and board_2d[i+1][j+1] == 'o')
                    )
                    
                    # Check if there's no 'o' in the four adjacent cells
                    no_adjacent_o = (
                        (i <= 0 or board_2d[i-1][j] != 'o') and  # up
                        (i >= rows - 1 or board_2d[i+1][j] != 'o') and  # down
                        (j <= 0 or board_2d[i][j-1] != 'o') and  # left
                        (j >= cols - 1 or board_2d[i][j+1] != 'o')  # right
                    )
                    
                    if diagonal_o and no_adjacent_o:
                        result.append((i, j))
                        
        return result

    def create_action(self, board):
        actions: list[str]
        turn: int

        print("now board\n")
        print("aaa",board[5])
        print(type(board))
        board_2d = self.string_to_2d_array(board)
        # print(board_2d)
        put_available = self.find_all_dots_with_diagonal_o(board_2d)
        print(f"Available positions to put: {put_available}")

        if self.player_number == 1:
            actions = self.p1Actions
            turn = self.p1turn
            self.p1turn += 1
        else:
            actions = self.p2Actions
            turn = self.p2turn
            self.p2turn += 1

        if len(actions) > turn:
            return actions[turn]
        else:
            # パスを選択
            return 'X000'
    
    @staticmethod
    async def create(url: str, loop: asyncio.AbstractEventLoop) -> PlayerClient:
        socket = await websockets.connect(url)
        print('PlayerClient: connected')
        player_number = await socket.recv()
        print(f'player_number: {player_number}')
        return PlayerClient(int(player_number), socket, loop)
