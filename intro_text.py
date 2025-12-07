
col_dict = {
    "style": {
                0: {"standard": "0"},
                1: {"bold": 1},
                2: {"italics": 3},
                3: {"underline": 4},
                4: {"invert": 7} #  BG and FG.
    },
    "foreground": {
                0: {"black": 30},
                1: {"red": 31},
                2: {"green": 32},
                3: {"yellow": 33},
                6: {"blue": 34},
                5: {"magenta": 35},
                4: {"cyan": 36}, # swapped from blue to cyan
                7: {"white": 37},
                8: {"green": 38},
                9: {"red": 39}},
    "background": {
                0: {"black": 40},
                1: {"red": 41},
                2: {"green": 42},
                3: {"yellow": 43},
                4: {"blue": 44},
                5: {"magenta": 45},
                6: {"cyan": 46},
                7: {"white": 47}}
    }
counter = 0

def alt_col(counter, text:list=None, col_index:list=None):

    line=[]
    if col_index == None:
        col_index = [2,4,2] # default 'outside, main, outside'


    for i, section in enumerate(text):
        section = section.replace("     ", "    \u00A0")
        if col_index[i] > 7:
            if col_index[i] == 8:
                fg = 8
        fg = col_dict["foreground"].get(col_index[i])
        style=0
        fg = list(fg.values())[0]
        if fg==32:
            style=4
        elif fg in (33,35):
            style=1
        elif fg in (34, 36):
            style=1
        elif fg==37:
            style=3
        elif fg==38:
            style=3
            fg=32
        elif fg==39:
            style=4
            fg=31
        format = ';'.join([str(style), str(fg), str(40)])
        s1 = f'\x1b[%sm{section}\x1b[0m' % (format)#, format)
        line.append(s1)

    counter += 1
    if len(str(counter)) < 2:
        counter_str = "0" + str(counter)
    else:
        counter_str=str(counter)
    line_str=""
    line_str = line_str.join(line)
    print(f"line {counter_str}: {line_str}") # counter just exists for line numbers, can remove later.
    return counter


print("\n")
counter=alt_col(counter, ["                        ", "                                    "], [7, 9])
counter=alt_col(counter, ["                        ", "\==================================#|"], [7, 1])
counter=alt_col(counter, ["                        ", "/", "                                  ", "#|"], [7, 1, 2, 1])
counter=alt_col(counter, ["  ", "|#===================/", "       ", "/$", "$","      ", "/$", "$", "                ", "#|_.", "                                      ", "_", "¬\\|", "."], [7, 1, 2, 4, 7, 2, 4, 7, 2, 1, 1, 2, 5, 8])
counter=alt_col(counter, ["   ", "|#", "               \u00A0         ","| $", "$","    ", "| $", "$","                 ", "#", "     v. ", "  ", "¬\\",".", "¦/", "       \u00A0            ", "    .", "/"], [7, 1, 2, 4, 7, 2, 4, 7, 2, 1, 2, 7, 3, 5, 3, 7, 2, 8])
counter=alt_col(counter, ["   ", "|#", "    ", "/$$$", "$$$", "   ", "/$$", "$$$$", "  ", "/$$$$", "S$", "  ", "| $$$", "$$$$", "   ", "/$$", "$$$$$", "  ", "#", " ", "       \\", "  ^\\/^ .", "             ", " vV ", "/    ", "   .. ."], [7, 1, 2, 4, 7, 2, 4, 7, 2, 4, 7, 2, 4, 7, 2, 4, 7, 2, 1, 2, 8, 2, 8, 2, 8, 2, 8, 1])
counter=alt_col(counter, ["   ", "|#", "   ", "/$$__  $", "$", " ", "|____  $", "$", "|_  $$_/","  ", "| $$__  $", "$", " /$$_____/", "  ", "#", "-. ..     \u00A0", "      \\", "     \u00A0   \u00A0 ", "/   ", "    .", "/"], [7, 1, 2, 4, 7, 2, 4, 7, 4, 2, 4, 7, 4, 2, 1, 2, 8, 2, 8, 2, 8])
counter=alt_col(counter, ["   ", "|#", "  ", r"| $$  \ $", "$", "  ", "/$$$$$$", "$", "  ", "| $", "$", "    ", "| $$", "  ", r"\ $", "$", "|  $$$", "$$$", "   ", "#", "   ", "        \\", "-.              \u00A0   ", "/"], [7, 1, 2, 4, 7, 2, 4, 7, 2, 4, 7, 2, 4, 2, 4, 7, 4, 7, 2,1, 2, 8, 2, 8])
counter=alt_col(counter, ["   ", "|#", "  ", "| $$  | $", "$", " /$$__  $", "$", "  ", "| $", "$", " /", "$$", "| $$", "  ", "| $", "$", " ", r"\____  $", "$", "  ", "#", "  "], [7, 1, 2, 4, 7, 4, 7, 2, 4, 7, 4, 7, 4, 2, 4, 7, 2, 4, 7, 2, 1, 2])
counter=alt_col(counter, ["   ", "|#", "  ", "| $$$$$$$/|  $$$$$$$","  ","| $$$$/", " ", "| $$", "  ", "| $$ /$$$$$$$/", "  ", "#", " "], [7, 1, 2, 4, 2, 4, 7, 4, 2, 4, 2, 1, 2])
counter=alt_col(counter, ["   ", "|#", "  ", "| $$____/","  ", r"\_______/","   ",r"\___/","  ","|__/", "  ", "|__/|_______/", "   ", "#|`"], [7, 1, 2, 4, 2, 4, 2, 4, 2, 4, 2, 4, 2, 1])
counter=alt_col(counter, ["   ", "|#", "  ", "| $$", "                                                ", "#|"], [7, 1, 2, 4, 2, 1])
counter=alt_col(counter, ["   ", "|#", "  ", "| $$", "       ", "/========================================#|"], [7, 1, 2, 4, 2, 1])
counter=alt_col(counter, ["   ", "|#", " ", "/_//", "      ", "/"], [7, 1, 2, 4, 2, 1])
counter=alt_col(counter, ["   ", "|#", "          \u00A0", "/"], [7, 1, 2, 1])
counter=alt_col(counter, ["  |", "#===========\\"], [1, 9])
print("\n")

#alt_col(r"   #   | $$  | $$ /$$__  $$  | $$ /$$| $$  | $$ \____  $$   #")
#alt_col("   #   | $$$$$$$/|  $$$$$$$  |  $$$$/| $$  | $$ /$$$$$$$/   #")

def colour_text(text="", fg="green", style="standard", bg="black", text2="", fg2="blue", style2="bold", bg2="black", text3="", fg3="green", style3="standard", bg3="black", text4="", fg4="white", style4="standard", bg4="black"): # for printing specific text

    def colourise(text, fg, style="standard", bg="black"):

        if col_dict["foreground"].get(fg):
            fg = col_dict["foreground"].get(fg)
        if col_dict["background"].get(bg):
            bg = col_dict["background"].get(bg)
        if col_dict["style"].get(style):
            style = int(col_dict["style"].get(style))
        format = ';'.join([str(style), str(fg), str(bg)])
        s1 = ''
        s1 += f'\x1b[%sm{text}\x1b[0m' % (format)#, format)
        return s1

    if text:
        formatted = colourise(text, fg, style, bg) # hardcoded parts with colours. More convenient because you don't need to specify colour each time, but means it only works with specific parts in specific orders. Could be amended to not be sequential, and just have 'colour blocks' in any order. Would be worth doing this.

        if text2:
            formatted = formatted + colourise(text2, fg2, style2, bg3)

            if text3:
                formatted = formatted + colourise(text3, fg3, style3, bg3)

                if text4:
                    formatted = formatted + colourise(text4, fg4, style4, bg4)


    print(formatted)

#colour_text("This is text.", style="italics")

def introduction_text():

    # ascii from https://patorjk.com/software/taag/#p=display&f=Big+Money-ne&t=paths&x=none&v=4&h=4&w=80&we=false
    print("\n")
    colour_text("                          /================================ #")
    colour_text("                         /                                  #")
    colour_text("   # ===================/     ", text2="/$$     /$", text3="$                   ", fg3="white", text4="#", fg4="green")
    colour_text("   #                         ", text2="| $$    | $$", text3="                   #")
    colour_text("   #     ", text2="/$$$$$$   /$$$$$$  /$$$$$$  | $$$$$$$   /$$", text3="$$$$$   ", fg3="white", text4="#", fg4="green")
    colour_text("   #    ", text2="/$$__  $$ |____  $$|_  $$_/  | $$__  $$ /$$_____/   ", text3="#")
    colour_text(r"   #   ", text2=r"| $$  \ $$  /$$$$$$$  | $$    | $$  \ $$|  $$$$$$    ", text3="#")
    colour_text(r"   #   ", text2=r"| $$  | $$ /$$__  $$  | $$ /$$| $$  | $$ \____  $$   ", text3="#")
    colour_text("   #   ", text2="| $$$$$$$/|  $$$$$$$  |  $$$$/| $$  | $$ /$$$$$$$/   ", text3="#")
    colour_text(r"   #   ", text2=r"| $$____/  \_______/   \___/  |__/  |__/|_______/    ", text3="#")
    colour_text("   #   ", text2="| $$                                                 ", text3="#")
    colour_text("   #   ", text2="| $$       ", text3="/======================================== #")
    colour_text("   #   ", text2="|__/      ", text3="/")
    colour_text("   #            /")
    colour_text("   # ==========/")
    print("\n")
    print("To play: ")
    print("Type the words in parentheses, or select by number")
    print("    eg: for [[  (stay) or (go))  ]], '1' would choose 'stay'.")

#introduction_text() ## can do highlights but only only a couple before it gets too ungainly.

#Why the hell is this printing:
#
#& "C:/Program Files/Python313/python.exe" d:/Git_Repos/choose-your-own/intro_text.py
#Pick a direction to investigate, or go elsewhere?
#    (north, south, east, west) or (go)
#
# -- It was a VS code issue, running an old script from cache for some reason.

# Had to do this:
#
# Press Ctrl+Shift+P
#
# Type → Python: Restart Language Server
#
# Also run → Python: Restart REPL (if it exists)
#
# Close all open terminals
#
# Open a new terminal

#def colour_by_character(text):
#    text = text.replace()
#    col_1 = ["#", "=", "/"]
#    col_2 = ["$"]

#    if text:
    #    s1 += f'\x1b[%sm{text}\x1b[0m' % (format)#, format)
    #    fg = col_dict["foreground"].get(fg)
    #    bg = col_dict["background"].get(bg)
    #    style = col_dict["style"].get(style)
    #    format = ';'.join([str(style), str(fg), str(bg)])
    #    s1 = ''
    #    #s1 += '\x1b[%sm %s \x1b[0m' % (format, format)
    #    s1 += f'\x1b[%sm{text}\x1b[0m' % (format)#, format)
    #    print(s1)
 #       for i in list(text):
#            print(i)
