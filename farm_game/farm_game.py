import tkinter as tk
from tkinter import filedialog
from typing import Callable, Union, Optional
from farm_game_support import *
from model import *
from constants import *


class InfoBar(AbstractGrid):
    """InfoBar class represents a grid with 2 rows and 3 columns,
    displaying information to the user about the number of
    days elapsed in the game,
    as well as the player's energy and money.
    It inherits from AbstractGrid.
    """

    def __init__(self, master: tk.Tk | tk.Frame) -> None:
        """Sets up this InfoBar to be an
        AbstractGrid with the appropriate number of rows and columns, and the appropriate
        width and height (see constants.py)

        Parameters:
            master (tk.Tk | tk.Frame): The master frame for this Canvas.
        """
        super().__init__(
            master, (2, 3), (FARM_WIDTH + INVENTORY_WIDTH, INFO_BAR_HEIGHT)
        )

    def redraw(self, day: int, money: int, energy: int) -> None:
        """Clears the InfoBar and redraws it to display the provided day, money, and energy

        Parameters:
            day (int): the current day
            money (int): the amount of money the player has
            energy (int): the amount of energy the player has
        """
        self.clear()

        # Annotate appropriate heading text
        self.annotate_position((0, 0), "Day:", font=HEADING_FONT)
        self.annotate_position((0, 1), "Money:", font=HEADING_FONT)
        self.annotate_position((0, 2), "Energy:", font=HEADING_FONT)

        # Annotate the day
        self.annotate_position((1, 0), str(day))

        # Annotate the money
        self.annotate_position((1, 1), "$" + str(money))

        # Annotate the energy
        self.annotate_position((1, 2), str(energy))


class FarmView(AbstractGrid):
    """A grid-based view class representing the farm map, player, and plants.
    This class inherits from the AbstractGrid class defined in 'a3_support.py' module.
    """

    def __init__(
        self,
        master: tk.Tk | tk.Frame,
        dimensions: tuple[int, int],
        size: tuple[int, int],
        **kwargs,
    ) -> None:
        """Sets up the FarmView to be an AbstractGrid
        with the appropriate dimensions and size, and creates an instance attribute of an empty
        dictionary to be used as an image cache.

        Parameters:
            master: The master frame for this Canvas.
            dimensions (tuple[int,int]): (#rows, #columns)
            size (tuple[int,int]): (width in pixels, height in pixels)
        """
        super().__init__(master, dimensions, size)

        self.cache = {}
        self.root = master
        self.dimensions = dimensions

        # Store cell size of map
        self.cell_size = FarmView.get_cell_size(self)

    def redraw(
        self,
        ground: list[str],
        plants: dict[tuple[int, int], Plant],
        player_position: tuple[int, int],
        player_direction: str,
    ) -> None:
        """Clears the farm view, then creates (on the FarmView instance) the images for the ground,
        then the plants, then the player.
        That is, the player and plants should render in front of the
        ground, and the player should render in front of the plants.

        Parameters:
            ground (list[str]): list of strings after calling read_map on the map
            player_position (tuple[int, int]): the position of the player at a coordinate.
            player_direction (str): the directino the player is facing.
        """
        self.clear()

        # Store the ground images in variables
        grass = get_image("images/grass.png", self.cell_size, self.cache)
        soil = get_image("images/soil.png", self.cell_size, self.cache)
        untilled_soil = get_image(
            "images/untilled_soil.png", self.cell_size, self.cache
        )

        # Iterate over the map and create relevant ground images
        for row_index, row in enumerate(ground):
            for letter_index, letter in enumerate(row):
                position = self.get_midpoint((row_index, letter_index))

                if letter == "G":
                    self.create_image(position[0], position[1], image=grass)
                elif letter == "S":
                    self.create_image(position[0], position[1], image=soil)
                elif letter == "U":
                    self.create_image(position[0], position[1], image=untilled_soil)

        # Iterate through plants and render plants at relevant stages and locations
        for position in plants:
            plant_coordinates = self.get_midpoint(position)
            plant = plants[position]
            plant_image_name = f"images/{get_plant_image_name(plant)}"
            plant_image = get_image(plant_image_name, self.cell_size, self.cache)
            self.create_image(
                plant_coordinates[0], plant_coordinates[1], image=plant_image
            )

        # Store player images in variables
        player_w = get_image("images/player_w.png", self.cell_size, self.cache)
        player_a = get_image("images/player_a.png", self.cell_size, self.cache)
        player_s = get_image("images/player_s.png", self.cell_size, self.cache)
        player_d = get_image("images/player_d.png", self.cell_size, self.cache)

        # Draw player at given position and with given direction
        player_coordinates = self.get_midpoint(player_position)

        if player_direction == "w":
            self.create_image(
                player_coordinates[0], player_coordinates[1], image=player_w
            )

        elif player_direction == "a":
            self.create_image(
                player_coordinates[0], player_coordinates[1], image=player_a
            )

        elif player_direction == "s":
            self.create_image(
                player_coordinates[0], player_coordinates[1], image=player_s
            )

        elif player_direction == "d":
            self.create_image(
                player_coordinates[0], player_coordinates[1], image=player_d
            )


class ItemView(tk.Frame):
    """A frame displaying relevant information and buttons for a single item.
    Inherits from tk.Frame.
    """

    def __init__(
        self,
        master: tk.Frame,
        item_name: str,
        amount: int,
        select_command: Optional[Callable[[str], None]] = None,
        sell_command: Optional[Callable[[str], None]] = None,
        buy_command: Optional[Callable[[str], None]] = None,
    ) -> None:
        """Sets up ItemView to operate as a tk.Frame, and creates all internal widgets.
        Sets the commands for the buy and sell buttons
        to the buy command and sell command each called with the appropriate item name respectively.
        Binds the select command to be called with the
        appropriate item name when either the ItemView frame or label is left clicked

        Parameters:
            master (tk.Frame): The master frame for this Canvas.
            item_name (str): The name of the item
            amount (int): The amount of the item
            select_command (Optional[Callable[[str], None]): the command for selecting items
            sell_command: (Optional[Callable[[str], None]): the command for selling items
            buy_command: (Optional[Callable[[str], None]): the command for buying items
        """

        super().__init__(master, bg=INVENTORY_EMPTY_COLOUR, width=200)
        self._select_command = select_command
        self._sell_command = sell_command
        self._buy_command = buy_command
        self._item_name = item_name
        self.selected_item = None

        # Create the item label text
        item_label_text = (
            f"{self._item_name}: {amount}\nSell price: ${SELL_PRICES[item_name]}\n"
        )
        if self._item_name in BUY_PRICES:
            item_label_text += f"Buy price: ${BUY_PRICES[item_name]}"
        else:
            item_label_text += "Buy price: $N/A"

        # Create the label for displaying item information
        self._item_label = tk.Label(
            self, text=item_label_text, bg=INVENTORY_EMPTY_COLOUR, padx=20, pady=17
        )
        self._item_label.pack(side=tk.LEFT)

        # Create the buy button if available, and bind the buy command
        if item_name in BUY_PRICES:
            self.buy_button = tk.Button(
                self, text="Buy", command=lambda: self._buy_command(self._item_name)
            )
            self.buy_button.pack(side=tk.LEFT)

        # Create the sell button, and bind the sell command
        self.sell_button = tk.Button(
            self, text="Sell", command=lambda: self._sell_command(self._item_name)
        )
        self.sell_button.pack(side=tk.LEFT)

        # Bind the select command
        self.bind(
            "<Button-1>",
            lambda event, item_name=self._item_name: self._select_command(item_name),
        )
        self._item_label.bind(
            "<Button-1>",
            lambda event, item_name=self._item_name: self._select_command(item_name),
        )

    def update(self, amount: int, selected: bool = False) -> None:
        """Updates the text on the label, and the colour of this ItemView appropriately.

        Parameters:
            amount (int): the amount of the item
        """
        # Change background colour according to amount and if item is selected
        if amount > 0:
            if selected is False:
                self.config(bg=INVENTORY_COLOUR)
                self._item_label.config(bg=INVENTORY_COLOUR)
            else:
                self.config(bg=INVENTORY_SELECTED_COLOUR)
                self._item_label.config(bg=INVENTORY_SELECTED_COLOUR)
        else:
            self.config(bg=INVENTORY_EMPTY_COLOUR)
            self._item_label.config(bg=INVENTORY_EMPTY_COLOUR)

        # Update item label text
        label_text = f"{self._item_name}: {amount}\nSell price: ${SELL_PRICES[self._item_name]}\n"
        if self._item_name in BUY_PRICES:
            label_text += f"Buy price: ${BUY_PRICES[self._item_name]}"
        else:
            label_text += "Buy price: $N/A"

        self._item_label.config(text=label_text)


class FarmGame:
    """FarmGame is the controller class for the overall game.
    The controller is responsible for creating and
    maintaining instances of the model and view classes, event handling,
    and facilitating communication between the model and view classes
    """

    def __init__(self, master: tk.Tk, map_file: str) -> None:
        """Sets up the FarmGame.
        This method initializes the FarmGame controller class and sets up the game environment.

        Parameters:
            master (tk.Tk): The master frame for this Canvas.
            map_file (str): The file path to the map file.
        """
        self._root = master
        self._root.title("Farm Game")
        self._map = read_map(map_file)
        self.item_dict = {}

        # Create the title banner and keep reference to the image
        header = get_image(
            "images/header.png",
            (FARM_WIDTH + INVENTORY_WIDTH, BANNER_HEIGHT),
            {"images": ImageTk.PhotoImage},
        )
        self._header_label = tk.Label(self._root, image=header)
        self._header_label.pack(side=tk.TOP)
        self._header_label.image = header

        # Create the FarmModel instance and store relevant information
        self._model = FarmModel(map_file)
        self._player = self._model.get_player()

        # Create a frame to contain farmview and inventory
        self._farm_inventory_frame = tk.Frame(
            self._root, width=FARM_WIDTH + INVENTORY_WIDTH
        )
        self._farm_inventory_frame.pack(side=tk.TOP)

        # Create the farmview
        self._farm_view = FarmView(
            self._farm_inventory_frame,
            self._model.get_dimensions(),
            (FARM_WIDTH, FARM_WIDTH),
        )
        self._farm_view.redraw(
            self._model.get_map(), self._model.get_plants(), (0, 0), "s"
        )
        self._farm_view.pack(side=tk.LEFT)

        # Create a frame to contain the itemviews
        self._item_view_frame = tk.Frame(
            self._farm_inventory_frame, width=INVENTORY_WIDTH, height=FARM_WIDTH
        )
        self._item_view_frame.pack(side=tk.LEFT)

        # Create an itemview instance for each item_name and add to dictionary
        for item_name in ITEMS:
            self.item_dict[item_name] = ItemView(
                self._item_view_frame,
                item_name,
                0,
                select_command=self.select_item,
                sell_command=self.sell_item,
                buy_command=self.buy_item,
            )
            self.item_dict[item_name].pack(side=tk.TOP, expand=tk.TRUE, fill=tk.BOTH)

            # Update item views with initial inventory
            if item_name in self._player.get_inventory():
                self.item_dict[item_name].update(
                    self._player.get_inventory()[item_name]
                )

        # Create the InfoBar
        self._info_bar = InfoBar(self._root)
        self._info_bar.redraw(1, 0, 100)
        self._info_bar.pack(side=tk.TOP)

        # Create the next day button
        def new_day_redraw():
            """Increments the day and calls redraw commands from widgets"""
            self._model.new_day()
            self.redraw()

        self._next_day = tk.Button(self._root, text="Next day", command=new_day_redraw)
        self._next_day.pack(side=tk.TOP)

        # Bind handlekeypress
        self._key_press = self._root.bind("<KeyPress>", self.handle_keypress)

    def redraw(self) -> None:
        """Redraws the entire game based on the current model state."""
        # Redraw info bar
        self._info_bar.redraw(
            self._model.get_days_elapsed(),
            self._player.get_money(),
            self._player.get_energy(),
        )

        # Redraw farm view
        self._farm_view.redraw(
            self._model.get_map(),
            self._model.get_plants(),
            self._player.get_position(),
            self._player.get_direction(),
        )

        # Update item views according to the amount and if it is the selected item
        for item_name in ITEMS:
            if item_name in self._player.get_inventory():
                if self._player.get_selected_item() == item_name:
                    self.item_dict[item_name].update(
                        self._player.get_inventory()[item_name], selected=True
                    )
                else:
                    self.item_dict[item_name].update(
                        self._player.get_inventory()[item_name], selected=False
                    )
            else:
                self.item_dict[item_name].update(0)

    def handle_keypress(self, event: tk.Event) -> None:
        """An event handler to be called when a keypress event occurs.
        Triggers the relevant behavior and updates the view accordingly.

        Parameters:
            event (tk.Event): The keypress event object containing information about the event.

        Notes:
            If a key is pressed that does not correspond to an event in Table 1, it is ignored.
        """
        # Create player movement events
        if event.keysym == "w":
            self._model.move_player(UP)

        elif event.keysym == "a":
            self._model.move_player(LEFT)

        elif event.keysym == "s":
            self._model.move_player(DOWN)

        elif event.keysym == "d":
            self._model.move_player(RIGHT)

        elif event.keysym == "t":
            self._model.till_soil(self._player.get_position())

        elif event.keysym == "u":
            self._model.untill_soil(self._player.get_position())

        # Create plant events
        elif event.keysym == "p":
            # Check if position contains soil
            row, col = self._player.get_position()
            if self._model.get_map()[row][col] == SOIL:
                # Check the selected item is a seed and it is in the inventory
                if self._player.get_selected_item() in self._player.get_inventory():
                    if self._player.get_selected_item() in SEEDS:
                        # Check what the plant name is and instantiate relevant Plant class
                        plant_name = self._player.get_selected_item().split()[0]
                        if plant_name == "Potato":
                            plant = PotatoPlant()
                        elif plant_name == "Kale":
                            plant = KalePlant()
                        elif plant_name == "Berry":
                            plant = BerryPlant()
                        # Add the plant and remove seed from inventory if successful
                        if (
                            self._model.add_plant(self._player.get_position(), plant)
                            is True
                        ):
                            self._player.remove_item(
                                (self._player.get_selected_item(), 1)
                            )

        elif event.keysym == "r":
            self._model.remove_plant(self._player.get_position())

        elif event.keysym == "h":
            # if plant harvest is successful add to inventory
            harvest = self._model.harvest_plant(self._player.get_position())
            if harvest is not None:
                self._player.add_item(harvest)

        self.redraw()

    def select_item(self, item_name: str) -> None:
        """Sets the selected item to the specified item name and redraws the view.

        Parameters:
            item_name (str): The name of the item to be selected.
        """
        selected_item = self._player.get_selected_item()

        # Unselect previously selected item and update itemview accordingly
        if selected_item is not None:
            if selected_item not in self._player.get_inventory():
                self.item_dict[selected_item].update(0, selected=False)
            else:
                self.item_dict[selected_item].update(
                    self._player.get_inventory()[selected_item], selected=False
                )

        # Select the item given and update itemview accordingly
        self._player.select_item(item_name)
        selected_item = self._player.get_selected_item()
        if selected_item in self._player.get_inventory():
            self.item_dict[selected_item].update(
                self._player.get_inventory()[selected_item], selected=True
            )

    def buy_item(self, item_name: str) -> None:
        """Attempts to buy the item with the specified name at the specified price from BUY PRICES.
        After the purchase attempt, the method redraws the view to reflect the changes.

        Parameters:
            item_name (str): The name of the item to be bought.
        """
        self._player.buy(item_name, BUY_PRICES[item_name])
        self.redraw()

    def sell_item(self, item_name: str) -> None:
        """The callback method used for selling items.

        This method allows the player to attempt to sell the item with the given item name.
        The selling price is determined by the SELL PRICES dictionary. After the item is sold,
        the view is redrawn to reflect the updated state.

        Parameters:
            item_name (str): The name of the item to be sold.
        """
        self._player.sell(item_name, SELL_PRICES[item_name])
        self.redraw()


def play_game(root: tk.Tk, map_file: str) -> None:
    """Plays the game by constructing the controller instance using the given map file
    and the root tk.Tk parameter. Ensures that the root window stays open and listens
    for events using the mainloop function.

    Parameters:
        root (tk.Tk): The root Tk instance for the game.
        map_file (str): The path to the map file to be used in the game.
    """
    FarmGame(root, map_file)
    root.mainloop()


def main() -> None:
    """The main function that constructs the root tk.Tk instance and calls the play_game
    function, passing in the newly created root tk.Tk instance and the path to a map file.
    """
    root = tk.Tk()
    play_game(root, "maps/map1.txt")


if __name__ == "__main__":
    main()
