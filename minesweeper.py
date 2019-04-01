from random import sample
from tkinter import DISABLED, SUNKEN, Button, Menu, Tk, messagebox, simpledialog


class Tile:
    '''
    The Tile object contains grid content of board.

    Args:
        key (tuple): The arg is used for handling index of element in dict.
        x (int): The arg is used for holding row of tile.
        y (int): The arg is used for holding column of tile.
        tile_type (int): The arg is used to check if tile is bomb, number or empty.
        is_revealed (bool): The arg is used to check if tile is revealed.
        button (Button): The tkinter button object

    Attributes:
        self.nearby_mines (int): Handles nearby mines of tile. Initialized with value 0
    '''
    COLORS = ['#FFFFFF', '#0000FF', '#008200', '#FF0000', '#000084', '#840000', '#008284', '#840084', '#000000']

    def __init__(
        self,
        key: tuple,
        x: int,
        y: int,
        tile_type: int,
        is_revealed: bool,
        button: Button
    ):
        self.key = key
        self.x = x
        self.y = y
        self.tile_type = tile_type
        self.is_revealed = is_revealed
        self.button = button
        self.nearby_mines = 0

    def get_tile_key(self) -> tuple:
        return self.key

    def get_tile_type(self) -> int:
        return self.tile_type

    def set_tile_type(self, tile_type: int):
        self.tile_type = tile_type

    def get_nearby_mines(self) -> int:
        return self.nearby_mines

    def increase_nearby_mines(self):
        self.nearby_mines = self.nearby_mines + 1
    
    def change_to_flag(self):
        if self.button['text'] == 'F':
            self.button.config(text = ' ')
        else:
            self.button.config(text = 'F')

    def reveal(self):
        '''
        Reveals tile.
        If tile is mine bg is set to red and text to '*'
        If tile is empty bg is set to white and text to ' '
        If tile has nearby_mines and not mine bg is set to white with text to 'nearby_mines'
        '''
        if self.tile_type == -1:            
            self.button.config(background='red', foreground='black', relief=SUNKEN, state=DISABLED, text='*')
        if self.tile_type == 0:
            self.button.config(background='white', relief = SUNKEN, state=DISABLED, text=' ')
        if self.nearby_mines > 0 and self.tile_type != -1:
            self.button.config(background='white', foreground=self.COLORS[self.nearby_mines], relief=SUNKEN, state=DISABLED, text=str(self.nearby_mines))
        self.is_revealed = True


class Board:
    '''
    The Board object contains tiles and handles board clickes.

    Args:
        window (Tk): The arg is used for handling restarting of game, tile placement.
        dimension (int): The arg is used for declaring dimensions of board.
        mine_count (int): The arg is used for adding mines to board.

    Attributes:
        current_click_count (int): Mouse click count handles victory event.
        is_gameover (bool): Handles clickablety of board.
        tiles (dict): Holds tiles.
        mine_tiles (list): Hold mine inserted tiles.
    '''
    NEIGHBOURS = ((-1, -1), (-1,  0), (-1,  1),
                  (0, -1),           (0,  1),
                  (1, -1), (1,  0), (1,  1))

    def __init__(self, window: Tk, dimension: int, mine_count: int):
        self.window = window
        self.dimension = dimension
        self.mine_count = mine_count
        self.current_click_count = 0
        self.is_gameover = False
        self.tiles = dict()
        self.tiles.clear()
        self.mine_tiles = list()
        self.mine_tiles.clear()
        self.create_board()

    def create_board(self):
        for x in range(0, self.dimension):
            for y in range(0, self.dimension):
                button = Button(
                    self.window,
                    text=' ',
                    width=4,
                    height=2,
                    borderwidth=4,
                    background='green'
                )
                # Left click bind
                button.bind('<1>', lambda event, x=x, y=y: self.on_left_click(x, y))
                # Right click bind
                button.bind('<3>', lambda event, x=x, y=y: self.on_right_click(x, y))
                button.grid(row=x, column=y)
                tile = Tile((x, y), x, y, 0, False, button)
                self.tiles[(x, y)] = tile

        self.place_mine_tiles()

    def place_mine_tiles(self):
        # Randomly sample tiles from self.tiles dict
        self.mine_tiles = [tile_sample for tile_sample in sample(list(self.tiles), self.mine_count)]
        for tile in self.tiles.values():
            if tile.get_tile_key() in self.mine_tiles:
                # Set to mine
                tile.set_tile_type(-1)
                self.update_neighbours(tile)
                        
    def update_neighbours(self, tile: Tile):
        for (row, col) in self.NEIGHBOURS:
            neighbour_tile = (tile.x + row, tile.y + col)
            if 0 <= neighbour_tile[0] < self.dimension and 0 <= neighbour_tile[1] < self.dimension:
                self.tiles[neighbour_tile].increase_nearby_mines()
    
    def on_left_click(self, x: int, y: int):
        # If game over dont allow click
        if not self.is_gameover:
            clicked_tile = self.tiles[(x, y)]
            if not clicked_tile.is_revealed:
                # Is tile a mine?
                if clicked_tile.get_tile_type() == -1:
                    clicked_tile.reveal()
                    self.reveal_mines()
                    self.gameover()
                else:
                    # If empty tile is clicked ripple
                    if clicked_tile.get_tile_type() == 0 and clicked_tile.get_nearby_mines() == 0:
                        self.reveal_tiles(clicked_tile)
                    # Else if number is clicked just reveal it and increase click count.
                    elif clicked_tile.get_nearby_mines() > 0:
                        self.current_click_count = self.current_click_count + 1 
                        clicked_tile.reveal()
                    # If user clicked enough tiles to select all tiles without mines call victory method.
                    if self.current_click_count == (self.dimension**2 - self.mine_count):
                        self.victory()


    def on_right_click(self, x: int, y: int):
        if not self.is_gameover:
            clicked_tile = self.tiles[(x, y)]
            if not clicked_tile.is_revealed:
                clicked_tile.change_to_flag()

    def reveal_tiles(self, tile: Tile):
        '''
        Reculsively travel all not revealed and non mine tiles.

        Args:
            tile (Tile): Tile to be revealed and get neighbours.
        '''
        # If tile is revealed or is mine dont travel it.
        if not tile.is_revealed and tile.get_tile_type() != -1:
            # Increase click count to check if user will win after ripple effect.
            self.current_click_count = self.current_click_count + 1 
            tile.reveal()
            # If the tile has no number then get its neighbours else dont.
            if tile.get_nearby_mines() == 0:
                for (row, col) in self.NEIGHBOURS:
                    neighbour_tile = (tile.x + row, tile.y + col)
                    if 0 <= neighbour_tile[0] < self.dimension and 0 <= neighbour_tile[1] < self.dimension:
                        self.reveal_tiles(self.tiles[neighbour_tile])

    def reveal_mines(self):
        for mine in self.mine_tiles:
            self.tiles[mine].reveal()

    def gameover(self):
        self.is_gameover = True
        messagebox.showinfo('Gameover', 'You lost.')
        self.restart()
    
    def victory(self):
        self.is_gameover = True
        messagebox.showinfo('Gaveover', 'You are victorious.')
        self.restart()

    def restart(self):
        result = messagebox.askokcancel('Replay?', 'Would you like to replay with the same settings?')
        if result:
            for tkitem in self.window.winfo_children():
                if type(tkitem) != Menu:
                    tkitem.destroy()
            self.current_click_count = 0
            self.is_gameover = False
            self.tiles.clear()
            self.mine_tiles.clear()
            self.create_board()
        else:
            self.window.destroy()
        
class InputHandler:
    '''
    Handles input related errors and checks.

    Attributes:
        REQUEST_SIZE_INPUT (str): Constant that contains dimension input request string.
        REQUEST_MINE_INPUT (str): Constant that contains mine count input request string.
    '''
    REQUEST_SIZE_INPUT = 'Enter row/column value:'
    REQUEST_MINE_INPUT = 'Enter total number of mines:'

    def get_error(self, value: str) -> str:
        return 'You have entered invalid ' + value + ' please enter numbers bigger then 0 and smaller then 50'

    def validate_input(self, value: int) -> bool:
        return value is None or type(value) != int or value <= 0


class GUI:
    '''
    Creates GUI and Handles Messages
    '''

    def __init__(self, window: Tk):
        self.window = window
        self.input_handler = InputHandler()
        self.create_menu()

    def create_menu(self):
        menu = Menu(self.window)
        game = Menu(self.window, tearoff=0)
        game.add_command(label='5x5 with 10 mines', command=lambda: self.create_board(5, 10))
        game.add_command(label='10x10 with 20 mines', command=lambda:  self.create_board(10, 20))
        game.add_command(label='Custom', command=lambda:  self.create_board(*self.get_board_arguments()))
        menu.add_cascade(label='Game', menu=game)
        self.window.config(menu=menu)

    def get_board_arguments(self) -> tuple:
        dimension = simpledialog.askinteger('Custom Dimension', self.input_handler.REQUEST_SIZE_INPUT)
        print(dimension)
        # Validate dimension
        if self.input_handler.validate_input(dimension) or dimension > 50:
            error = self.input_handler.get_error('dimension') + ' ' + self.input_handler.REQUEST_SIZE_INPUT
            dimension = simpledialog.askinteger('ERROR', error)
        
        mine_count = simpledialog.askinteger('Custom Mine', self.input_handler.REQUEST_MINE_INPUT)
        # Validate mine_count
        if self.input_handler.validate_input(mine_count) or mine_count > dimension**2:
            error = self.input_handler.get_error('mine count') + ' ' + self.input_handler.REQUEST_MINE_INPUT
            mine_count = simpledialog.askinteger('ERROR',  error)

        return dimension, mine_count

    def create_board(self, dimension: int, mine_count: int):
        for tkitem in self.window.winfo_children():
            if type(tkitem) != Menu:
                tkitem.destroy()
        self.board = Board(self.window, dimension, mine_count)

class Minesweeper:
    def __init__(self):
        self.window = Tk()
        self.gui = GUI(self.window)

    def start_game(self):        
        self.window.mainloop()

minesweeper = Minesweeper()
minesweeper.start_game()
