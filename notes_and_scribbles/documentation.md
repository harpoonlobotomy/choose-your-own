I need to start doing some documentation of a sort.

* All items are moved (whether to/from a location, to/from inventory, etc) through `def move_item` in itemRegistry.
* Items are run through `def is_event_trigger` in eventRegistry to check for relevant event triggers.
* All player movement is controlled by `def relocate` in player_movement if changing .place, or .
* Player movement that travels through transition objects to/from internal locations (eg the shed in the graveyard) is routed through `def move_through_trans_obj` in verb_actions to check the door is open and how close the player is to the internal location to determine the data sent to def relocate.

* `logging_fn` is run at the top of every function (and in some additional places) to provided function traversal data with `logging` or `logging args` is set.

EVENTS JSON:

"event_name": {
    "starts_current": true, # if event is running at game_start
    "end_trigger": # What triggers the event to end. Currently only items, but possible could be something else later.
      {"item_trigger": {
          "trigger_name": "padlock",
          "trigger_location": "north work shed", # starting loc of trigger item for instance identification
          "trigger": ["item_broken", "item_unlocked"], The specific action that will trigger the event end
          "item_flags": {
            "while_event": {"can_pick_up": false, "requires_key": "iron key"},  flags that are set at event start
            "flags_on_event_end": {"can_pick_up": true}} flags that are set at event end
            }
        },
    "effects": {
        "limit_travel": {"cannot_leave": ["work shed", "graveyard"]}, # limits travel to the named locations
        "hold_item": { # item cannot be picked up while held (but can be interacted with otherwise)
            "item_name": "padlock",
            "item_loc": "north graveyard"},
        "lock_item": { # item is locked/closed while event running, 'flags_on_event_end' gives the updated state on end.
            "item_name": "gate",
            "item_loc": "north graveyard",
            "while_event": {
                "is_locked": true,
                "is_closed": true},
            "on_event_end": {
                "is_locked": false,
                "is_closed": false}}},
    "messages": {
        "start_msg": "", Message to play at the start of the event (not used for starts_current)
        "end_msg": "As the padlock falls to the ground and the chain unravells, the graveyard gate creaks open.", #msg to print when event ends
        "held_msg": "Until the gate's unlocked, you don't see a way out of here."} # Message that plays when trying to leave limited locations if limit_travel.
  },

Other triggers/effects:
      {"item_trigger": {
          "trigger_name": "local map",
          "trigger_location": "north work shed",
          "trigger": ["item_in_inv"],
          "item_flags": {}
      }
    },
    "effects": {
        "hide_item": {
            "item_name": "iron key",
            "item_loc": "north work shed"
            "while_event: {is_hidden: true},
            "on_event_end: {is_hidden: false}}},


eventRegistry:
(How entries compare, common terms, etc:)

effects:
    self.limits_travel = True # simply marks that the event limits travel, bool
    limit travel == self.travel_limited_to.add(location) (placeInstances)

    hide_item:
        self.hidden_items[hidden_items["item_name"]] = hidden_items["item_loc"]
        self.items.add(attr["effects"]["hide_item"]["item_name"]) # 'items' == obj affected by the event.

    hold_item:
        self.held_items[(attr["effects"]["hold_item"]["item_name"])] = attr["effects"]["hold_item"]["item_loc"]
        self.items.add(attr["effects"]["hold_item"]["item_name"]) # 'items' == obj affected by the event.

triggers:
    for start_trigger and end_trigger:
        self.keys.add(attr[trigger]["item_trigger"]["trigger_name"])
        setattr(self, f"{trigger}_location", attr[trigger]["item_trigger"]["trigger_location"])

Messages:

    self.msgs = attr.get("messages")

Event state:
    Event state is an int, 0 == past/completed, 1 == current/ongoing, 2 == future/yet to start.

    Stored on the eventInstance as self.state:int

    to find by state:
        self.by_state[state]

