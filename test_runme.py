if __name__ == "__main__":

    ## initialise everything ##

    import initialise_all

    initialise_all.initialise_all()

    test_input_list = ["get the paperclip", "pick up the glass jar", "put the paperclip in the wallet", "place the dried flowers on the headstone", "go to the graveyard", "approach the forked tree branch", "look at the moss", "examine the damp newspaper", "read the puzzle mag", "read the fashion mag in the city hotel room", "watch the watch", "depart", "go", "go to the pile of rocks", "take the exact thing", "put the severed tentacle in the glass jar", "open the wallet with the paperclip", "read the mail order catalogue at the forked tree branch", "pick the moss", "pick the watch", "put batteries into watch", "clean a pile of rocks"]

    for i, input_str in enumerate(test_input_list):
        print(f"\nTEST STRING: `{input_str}`")
        import verb_membrane
        verb_membrane.run_membrane(input_str)
        print(f"(That was number {i})\n")
