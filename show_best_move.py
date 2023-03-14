#####################################
# Шахматный бот, с возможностью выбора
# шахматного движка.
# For Windows
#####################################

import sys
import cv2
import numpy as np
import pyautogui as pg
import chess
import chess.engine
import time
import threading
from draw import draw_shape

# Получение стартовой позиции и ширины шахматной доски
#from find_board import get_start_position
#position_board = get_start_position()

# Константы для работы бота
BOARD_SIZE = 833#position_board[2]-4
DARK_SQUARE_THRESHOLD = 160
CELL_SIZE = int(BOARD_SIZE / 8)
BOARD_TOP_COORD = 172#position_board[1]+4
BOARD_LEFT_COORD = 519#position_board[0]+3


CONFIDENCE = 0.99 # Уверенность определения фигуры
DETECTION_NOICE_THRESHOLD = 8 
PIECES_PATH = './images/figures/'

# Игрок
WHITE = 0
BLACK = 1

side_to_move = 0

# Выбор игры за белых или черных
try:
    if sys.argv[1] == 'black': side_to_move = BLACK
except:
    print('Используй: "chessbot.py white" или "chessbot.py black"')
    sys.exit(0)

# Содершим координаты квадратов
square_to_coords = []

get_square = [
    'a8', 'b8', 'c8', 'd8', 'e8', 'f8', 'g8', 'h8',
    'a7', 'b7', 'c7', 'd7', 'e7', 'f7', 'g7', 'h7',
    'a6', 'b6', 'c6', 'd6', 'e6', 'f6', 'g6', 'h6',
    'a5', 'b5', 'c5', 'd5', 'e5', 'f5', 'g5', 'h5',
    'a4', 'b4', 'c4', 'd4', 'e4', 'f4', 'g4', 'h4',
    'a3', 'b3', 'c3', 'd3', 'e3', 'f3', 'g3', 'h3',
    'a2', 'b2', 'c2', 'd2', 'e2', 'f2', 'g2', 'h2',
    'a1', 'b1', 'c1', 'd1', 'e1', 'f1', 'g1', 'h1'
];
  
piece_names = {
    'b_rook_w': 'r',
    'b_horse_b': 'n',
    'b_bishop_w': 'b',
    'b_queen_b': 'q',
    'b_king_w': 'k',
    'b_queen_w': 'q',
    'b_king_b': 'k',
    'b_bishop_b': 'b',
    'b_horse_w': 'n',
    'b_rook_b': 'r',
    'b_pawn_b': 'p',
    # 'b_pawn_w': 'p',

    'w_pawn_b': 'P',
    'w_pawn_w': 'P',
    'w_rook_b': 'R',
    'w_horse_w': 'N',
    'w_bishop_b': 'B',
    'w_queen_w': 'Q',
    'w_king_b': 'K',
    'w_queen_b': 'Q',
    'w_king_w': 'K',
    'w_bishop_w': 'B',
    'w_horse_b': 'N',
    'w_rook_w': 'R'
}

def search_piece(piece, piece_locations):
    # Поиск всех фигур определенного типа на экране
    for location in pg.locateAllOnScreen(PIECES_PATH + piece + '.png', confidence=CONFIDENCE):
        # Не найдено совподение
        noise = False

        # Переберает сохраненные положения фигур в поиске совпадения
        for position in piece_locations[piece]:
            # Обнаружение фигуры
            if abs(position.left - location.left) < DETECTION_NOICE_THRESHOLD and \
               abs(position.top - location.top) < DETECTION_NOICE_THRESHOLD:
                noise = True
                break

        # Пропускаем
        if noise:
            continue

        # Сохраняем положение фигуры
        piece_locations[piece].append(location)
      
    return True

def recognize_position():
    piece_locations = {
        # b = black, w = white
        'b_rook_w': [],
        'b_horse_b': [],
        'b_bishop_w': [],
        'b_queen_b': [],
        'b_king_w': [],
        'b_queen_w': [],
        'b_king_b': [],
        'b_bishop_b': [],
        'b_horse_w': [],
        'b_rook_b': [],
        'b_pawn_b': [],
        'b_pawn_w': [],


        'w_pawn_b': [],
        'w_pawn_w': [],
        'w_rook_b': [],
        'w_horse_w': [],
        'w_bishop_b': [],
        'w_queen_w': [],
        'w_king_b': [],
        'w_queen_b': [],
        'w_king_w': [],
        'w_bishop_w': [],
        'w_horse_b': [],
        'w_rook_w': []
    }

    screenshot = cv2.cvtColor(np.array(pg.screenshot()), cv2.COLOR_RGB2BGR)

    # Список потоков
    threads = []

    # Запуск поиска фигур в отдельных потоках
    for piece in piece_names.keys():
        thread = threading.Thread(target=search_piece, args=(piece, piece_locations))
        threads.append(thread)
        thread.start()

    # Дожидаемся завершения работы всех потоков
    for thread in threads:
        thread.join()

    return screenshot, piece_locations


# конвертирукт координаты фигур в FEN
def fen(piece_locations):
    fen = ''
    
    x = BOARD_LEFT_COORD
    y = BOARD_TOP_COORD
    
    # Строки
    for row in range(8):
        empty = 0
    
        # Колонки
        for col in range(8):
            # Инициация квадрата
            square = row * 8 + col
            
            is_piece = ()
            
            # Перебераем типы фигур
            for piece_type in piece_locations.keys():
                # loop over pieces
                for piece in piece_locations[piece_type]:
                    if abs(piece.left - x) < DETECTION_NOICE_THRESHOLD and \
                       abs(piece.top - y) < DETECTION_NOICE_THRESHOLD:
                        if empty:
                            fen += str(empty)
                            empty = 0

                        fen += piece_names[piece_type]
                        is_piece = (square, piece_names[piece_type])

            
            if not len(is_piece):
                empty += 1
            
            # Переходим к следующей колонке
            x += CELL_SIZE
        
        if empty: fen += str(empty)
        if row < 7: fen += '/'
        
        # Переходим к следующей строке
        x = BOARD_LEFT_COORD
        y += CELL_SIZE
    
    # Добавляем FEN строку
    fen += ' ' + 'b' if side_to_move else ' w'
    fen += ' KQkq - 0 1' # Для уточнения рокировки
    
    return fen
            
# Находит лучший ход
def search(fen):
    board = chess.Board(fen=fen)

    # Зпускаием Stockfish engine
    engine = chess.engine.SimpleEngine.popen_uci("./chess_engines/Stockfish/stockfish.exe")
    # Зпускаием BBC engine
    #engine = chess.engine.SimpleEngine.popen_uci("./chess_engines/bbc/bbc.exe")
    # Зпускаием Xiphos engine
    #engine = chess.engine.SimpleEngine.popen_uci("./chess_engines/xiphos/xiphos.exe")
    
    # Получает лучший ход
    best_move = str(engine.play(board, chess.engine.Limit(time=3)).move)
    
    print(best_move)
    engine.quit()

    return best_move


x = BOARD_LEFT_COORD
y = BOARD_TOP_COORD

# Строки
for row in range(8):
    # Колонки
    for col in range(8):
        square = row * 8 + col
        square_to_coords.append((int(x + CELL_SIZE / 2), int(y + CELL_SIZE / 2)))

        # Следующия колонка
        x += CELL_SIZE
    
    # Следующая строка
    x = BOARD_LEFT_COORD
    y += CELL_SIZE



try:
    # Определяет положение фигур
    screenshot, piece_locations = recognize_position()

    fen = fen(piece_locations)

    best_move = search(fen)

    # Получает позицию квадратов для хода
    from_sq = square_to_coords[get_square.index(best_move[0] + best_move[1])]
    to_sq = square_to_coords[get_square.index(best_move[2] + best_move[3])]

    draw_shape(from_sq[0], from_sq[1], to_sq[0], to_sq[1], CELL_SIZE)

    time.sleep(5)
    exit()
    
except: sys.exit(0)
