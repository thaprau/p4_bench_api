class Table(object):
    def __init__(self, id, name, alias, match_fields, action_refs, size) -> None:
        self.id = id
        self.name = name
        self.alias = alias
        self.match_fields = match_fields
        self.action_refs = action_refs
        self.size = size


class Match_Field(object):
    def __init__(self, id, name, bitwidth, match_type) -> None:
        self.id = id
        self.name = name
        self.bitwidth = bitwidth
        self.match_type = match_type


class Action(object):
    def __init__(self, id, name, alias, params) -> None:
        self.id = id
        self.name = name
        self.alias = alias
        self.params = params


class Action_Params(object):
    def __init__(self, id, name, bitwidth) -> None:
        self.id = id
        self.name = name
        self.bitwidth = bitwidth
