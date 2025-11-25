
col_dict = {
    "style": {
                "standard": "0",
                "bold": 1,
                "italics": 3,
                "underline": 4,
                "invert": 7 #  BG and FG.
    },
    "foreground": {
                "black": 30,
                "red": 31,
                "green": 32,
                "yellow": 33,
                "blue": 34,
                "magenta": 35,
                "cyan": 36,
                "white": 37,},
    "background": {
                "black": 40,
                "red": 41,
                "green": 42,
                "yellow": 43,
                "blue": 44,
                "magenta": 45,
                "cyan": 46,
                "white": 47}
    }


def colour_text(text="", fg="white", style="standard", bg="black", text2="", fg2="white", style2="standard", bg2="black", text3="", fg3="white", style3="standard", bg3="black"): # for printing specific text

    def colourise(text, fg, style, bg):

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
        formatted = colourise(text, fg, style, bg)

        if text2:
            formatted = formatted + colourise(text2, fg2, style2, bg2)

            if text3:
                formatted = formatted + colourise(text3, fg3, style3, bg3)

    print(formatted)

#colour_text("This is text.", style="italics")

def introduction_text():

    # ascii from https://patorjk.com/software/taag/#p=display&f=Big+Money-ne&t=paths&x=none&v=4&h=4&w=80&we=false
    print("\n")
    colour_text("                          /================================ #", fg="green")
    colour_text("                         /                                  #", fg="green")
    colour_text("   # ===================/     ", fg="green", text2="/$$     /$$                   ", fg2="blue", text3="#", fg3="green")
    colour_text("   #                         ", fg="green", text2="| $$    | $$", fg2="blue", text3="                   #", fg3="green")
    print("   #     /$$$$$$   /$$$$$$  /$$$$$$  | $$$$$$$   /$$$$$$$   #")
    print("   #    /$$__  $$ |____  $$|_  $$_/  | $$__  $$ /$$_____/   #")
    print(r"   #   | $$  \ $$  /$$$$$$$  | $$    | $$  \ $$|  $$$$$$    #")
    print(r"   #   | $$  | $$ /$$__  $$  | $$ /$$| $$  | $$ \____  $$   #")
    print("   #   | $$$$$$$/|  $$$$$$$  |  $$$$/| $$  | $$ /$$$$$$$/   #")
    print(r"   #   | $$____/  \_______/   \___/  |__/  |__/|_______/    #")
    print("   #   | $$                                                 #")
    print("   #   | $$       /======================================== #")
    print("   #   |__/      /")
    colour_text("   #            /", fg="green")
    colour_text("   # ==========/", fg="green")
    print("\n")
    print("To play: ")
    print("Type the words in parentheses, or select by number")
    print("    eg: for [[  (stay) or (go))  ]], '1' would choose 'stay'.")

introduction_text()

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
