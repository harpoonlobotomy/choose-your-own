
from set_up_game import game, set_up

set_up(1, 1, "Player")

inventory_items = game.inventory
#  $$$                                           $$$$                                             $
inv_=[
"$$1.                                           $$$$7.                                             $$$",
"$$2.                                           $$$$8.                                             $$$",
"$$3.                                           $$$$9.                                             $$$",
"$$4.                                           $$$$10.                                            $$$",
"$$5.                                           $$$$11.                                            $$$",
"$$6.                                           $$$$12.                                            $$$"]

playerdata_=[
"$                                      $",
f"$HEALTH:  {game.player["hp"]}                             $",
f"$CARRYWEIGHT:  {game.carryweight}                        $",
"$  **********************************   $",
"$  **********************************   $",
"$                                      $"]

loc_spaces = len(game.place)
loc_spacing = 20 - loc_spaces
loc_spacing = (" " * loc_spacing)

wthr_spaces = len(game.place)
wthr_spacing = 50 - wthr_spaces
wthr_spacing = (" " * wthr_spacing)

tod_spaces = len(game.place)
tod_spacing = 50 - tod_spaces
tod_spacing = (" " * tod_spacing)

worldstate_=[
"$                                       $",
f"$CURRENT LOCATION: {game.place}{loc_spacing}$",
f"$WEATHER: {game.weather}{wthr_spacing}$",
f"$TIME OF DAY: {game.time}{tod_spacing}$",
f"$                                DAY {game.day_number}   $",
"$                                       $"]

commands_ = [
"  COMMANDS:     `1` for first option, `2` for second, etc.                                  In inventory: 'drop <item_name>'/'separate <item_name>' to drop/separate <item>  ",
"                          `i` for inventory       'd' to describe surroundings         <item_name> to examine <item>                q/quit` to quit.                         "
]
