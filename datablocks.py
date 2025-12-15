
#from set_up_game import game, set_up

#set_up(1, 1, "Player")

inventory_items = None#game.inventory
#  $$$                                           $$$$                                             $
inv2_=[
"$$  1.                                            $$$7.                                          $$$$",
"$$  2.                                            $$$8.                                          $$$$",
"$$  3.                                            $$$9.                                          $$$$",
"$$  4.                                            $$$10.                                         $$$$",
"$$  5.                                            $$$11.                                         $$$$",
"$$  6.                                            $$$12.                                         $$$$"]


inv_3_=[
"$$  *.                                            $$$*.                                          $$$$",
"$$  *.                                            $$$*.                                          $$$$",
"$$  *.                                            $$$*.                                          $$$$",
"$$  *.                                            $$$*.                                          $$$$",
"$$  *.                                            $$$*.                                          $$$$"]

inv_=[
"$$  *.                           $$$*.                           $$$*.                           $$$$",
"$$  *.                           $$$*.                           $$$*.                           $$$$",
"$$  *.                           $$$*.                           $$$*.                           $$$$",
"$$  *.                           $$$*.                           $$$*.                           $$$$",
"$$  *.                           $$$*.                           $$$*.                           $$$$",
]

## 12 total $

playerdata_=[
"$                                      $",
f"$  HEALTH:  *                          $",
f"$  CARRYWEIGHT:  *                     $",
"$  **********************************   $",
"$  **********************************   $",
"$                                      $"]

#loc_spaces = len(game.place)
#loc_spacing = 20 - loc_spaces
#loc_spacing = (" " * loc_spacing)

#wthr_spaces = len(game.place)
#wthr_spacing = 50 - wthr_spaces
#wthr_spacing = (" " * wthr_spacing)

#tod_spaces = len(game.place)
#tod_spacing = 50 - tod_spaces
#tod_spacing = (" " * tod_spacing)

worldstate_=[
"$                                       $",
"$  CURRENT LOCATION: *                  $",
"$  WEATHER: *                           $",
"$  TIME OF DAY: *                       $",
"$                            DAY *      $",
"$                                       $"]
#
commands_ = [
"$$$ COMMANDS:  `1` for first option, `2` for second, etc.  $ $$   i` for inventory   $$$   'd' to describe surroundings                               $$$",
"$$$$           `'drop <item_name>'/'separate <item_name>' to drop/separate <item>   $$$   <item_name> to examine <item>   $$   q/quit` to quit.       $$"
]


intro = [
    #First run setup
    # ascii from https://patorjk.com/software/taag/#p=display&f=Big+Money-ne&t=paths&x=none&v=4&h=4&w=80&we=false
    "                          /================================ #",
    "                         /                                  #",
    "   # ===================/     /$$     /$$                   #",
    "   #                         | $$    | $$                   #",
    "   #     /$$$$$$   /$$$$$$  /$$$$$$  | $$$$$$$   /$$$$$$$   #",
    "   #    /$$__  $$ |____  $$|_  $$_/  | $$__  $$ /$$_____/   #",
    r"   #   | $$  \ $$  /$$$$$$$  | $$    | $$  \ $$|  $$$$$$    #",
    r"   #   | $$  | $$ /$$__  $$  | $$ /$$| $$  | $$ \____  $$   #",
    "   #   | $$$$$$$/|  $$$$$$$  |  $$$$/| $$  | $$ /$$$$$$$/   #",
    r"   #   | $$____/  \_______/   \___/  |__/  |__/|_______/    #",
    "   #   | $$                                                 #",
    "   #   | $$       /======================================== #",
    "   #   |__/      /",
    "   #            /",
    "   # ==========/",
    " ",
    " ",
    "To play: ",
    "Type the words in parentheses, or select by number",
    "    eg: for [[  (stay) or (go))  ]], '1' would choose 'stay'."
]

intro_wide = [
    "                          /================================ #",
    "                         /                                  #",
    "   # ===================/     /$$     /$$                   #",
    "   #                         | $$    | $$                   #",
    "   #     /$$$$$$   /$$$$$$  /$$$$$$  | $$$$$$$   /$$$$$$$   #            To play: ",
    "   #    /$$__  $$ |____  $$|_  $$_/  | $$__  $$ /$$_____/   #",
    r"   #   | $$  \ $$  /$$$$$$$  | $$    | $$  \ $$|  $$$$$$    #        Type the words in parentheses, or select by number",
    r"   #   | $$  | $$ /$$__  $$  | $$ /$$| $$  | $$ \____  $$   #            eg: for [[  (stay) or (go))  ]], '1' would choose 'stay'."
    "   #   | $$$$$$$/|  $$$$$$$  |  $$$$/| $$  | $$ /$$$$$$$/   #",
    r"   #   | $$____/  \_______/   \___/  |__/  |__/|_______/    #",
    "   #   | $$                                                 #",
    "   #   | $$       /======================================== #",
    "   #   |__/      /",
    "   #            /",
    "   # ==========/",
]
