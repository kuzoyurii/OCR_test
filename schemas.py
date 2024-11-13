shot_clock = 24
schema={}

schema['init'] = {
    'type': 'object',
    'properties': {
        "scoreboard_id":  {'type': 'string'},
        "shotclock": {'type': 'boolean'},
        "debug": {'type': 'boolean'},
        "listen_port": {'type': 'integer', 'minimum': 1000, 'maximum': 99999},
        "font": {'type': 'integer', 'minimum': 0, 'maximum': 9},
        "period": {'type': 'integer', 'minimum': 0, 'maximum': 99},
        "up": {'type': 'boolean'},
        'secret': {'type': 'string'},
        'note': {'type': 'string'}
    },
    'required' : ['scoreboard_id']
}

schema['startClock'] = {
    'type': 'object',
    'properties': {
        "secret": {'type': 'string'},
        "minutes": {'type': 'integer', 'minimum': 0, 'maximum': 99},
        "seconds": {'type': 'integer', 'minimum': 0, 'maximum': 59},
        "direction": {'type': 'string', 'minLength': 2, 'maxLength': 4}
    },
    'required': []
}

schema['startClocks'] = {
    'type': 'object',
    'properties': {
        "secret": {'type': 'string'},
        "minutes": {'type': 'integer', 'minimum': 0, 'maximum': 99},
        "seconds": {'type': 'integer', 'minimum': 0, 'maximum': 59},
        "shotclock": {'type': 'integer', 'minimum': 0, 'maximum': shot_clock},
        "direction": {'type': 'string', 'minLength': 2, 'maxLength': 4}
    },
    'required': []
}

schema['setTeamScore'] = {
    'type': 'object',
    'properties': {
        "secret": {'type': 'string'},
        "homeScore": {'type': 'integer', 'minimum': 0, 'maximum': 999},
        "awayScore": {'type': 'integer', 'minimum': 0, 'maximum': 999}
    },
    'required': []
}

schema['setPeriod'] = {
    'type': 'object',
    'properties': {
        "secret": {'type': 'string'},
        "period": {'type': 'integer', 'minimum': 0, 'maximum': 9}
    },
    'required': ['period']
}

schema['setFouls'] = {
    'type': 'object',
    'properties': {
        "secret": {'type': 'string'},
        "homeFouls": {'type': 'integer', 'minimum': 0, 'maximum': 9},
        "awayFouls": {'type': 'integer', 'minimum': 0, 'maximum': 9}
    },
    'required': []
}

schema['startShotClock'] = {
    'type': 'object',
    'properties': {
        "secret": {'type': 'string'},
        "seconds": {'type': 'integer', 'minimum': 0, 'maximum': shot_clock},
    },
    'required': []
}

schema['setShotClock'] = {
    'type': 'object',
    'properties': {
        "secret": {'type': 'string'},
        "seconds": {'type': 'integer', 'minimum': 0, 'maximum': shot_clock},
    },
    'required': ['seconds']
}

schema['player'] = {
    'type': 'object',
    'properties': {
        "secret": {'type': 'string'},
        "frame": {'type': 'integer', 'minimum': 0},
        "zoom": {'type': 'integer', 'minimum': 1, 'maximum': 3},
        "top": {'type': 'boolean'},
        "debug": {'type': 'boolean'},
        "debug_path": {'type': 'string'}
    },
    'required': []
}

schema['export'] = {
    'type': 'object',
    'properties': {
        "secret": {'type': 'string'},
        "scoreboard_id": {'type': 'string'},
        "shotclock": {'type': 'boolean'}
    },
    'required': ["scoreboard_id"]
}

schema['actionList'] = {
    'type': 'object',
    'properties': {
        "secret": {'type': 'string'},
        "minutes": {'type': 'integer', 'minimum': 0, 'maximum': 99},
        "seconds": {'type': 'integer', 'minimum': 0, 'maximum': 59},
        "direction": {'type': 'string', 'minLength': 2, 'maxLength': 4}
    },
    'required': []
}

