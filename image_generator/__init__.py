from datetime import datetime


def get_positions_from_file(conf_path):
    variables = {}
    with open(conf_path, "r") as conf_file:
        conf_data = conf_file.readlines()
    for line in conf_data:
        try:
            var = line.strip().split('=')
            v_name = var[0].strip(' ')
            v_val = (int(var[1].split(',')[0]), int(var[1].split(',')[1]))
            variables[v_name] = (-1, v_val)
        except Exception as E:
            print('skipping none variable line')
    return variables


class Scoreboard:
    frame = 0
    old_frame = 0
    ticking = False
    shotclock_ticking = False
    time_change = 0
    log_file = []
    debug = False
    status = False
    period = 0

    def __init__(self, scoreboard_id, debug=False, period=0):
        self.debug = debug
        self.position_file = ''
        self.sizes_file = ''
        v = -1
        x = 0
        y = 0
        self.id = scoreboard_id
        self.areas = {
            "HomeScoreOnes": (v, (x, y)),
            "HomeScoreTens": (v, (x, y)),
            "HomeScoreHundreds": (v, (x, y)),
            "AwayScoreOnes": (v, (x, y)),
            "AwayScoreTens": (v, (x, y)),
            "AwayScoreHundreds": (v, (x, y)),
            "Period": (v, (x, y)),
            "MinutesTens": (v, (x, y)),
            "MinutesOnes": (v, (x, y)),
            "SecondsOnes": (v, (x, y)),
            "SecondsTens": (v, (x, y)),
            "HomeFouls": (v, (x, y)),
            "AwayFouls": (v, (x, y)),
            "ShotClockTens": (v, (x, y)),
            "ShotClockOnes": (v, (x, y))
        }

    def init_scoreboard(self, cwd):
        self.position_file = r'{}/scoreboards/{}/positions.txt'.format(cwd, str(self.id))
        self.sizes_file = r'{}/scoreboards/{}/sizes.txt'.format(cwd, str(self.id))
        position_vars = get_positions_from_file(self.position_file)
        for var in position_vars:
            self.areas[var] = position_vars[var]

    def set_area(self, area, value, position):
        self.areas[area] = (value, (position))

    def set_value(self, area, value):
        self.areas[area] = (value, self.areas[area][1])

    def get_forced(self):
        forced_list = []
        for area in self.areas:
            if self.areas[area][1] != (0,0):
                forced_list.append(area)
        return forced_list

    def on(self):
        on_list = []
        for area in self.areas:
            if self.areas[area][1] != (0, 0):
                if self.areas[area][0] != -1:
                    self.areas[area] = (self.areas[area][0], self.areas[area][1])
                else:
                    self.areas[area] = (0, self.areas[area][1])
                on_list.append(area)
        return on_list

    def off(self):
        off_list = []
        for area in self.areas:
            if self.areas[area][0] != -1:
                self.areas[area] = (-1, self.areas[area][1])
                off_list.append(area)
        return off_list

    def clock_direction(self, direction):
        self.time_change = -1 if str(direction).lower() == 'down' else 1

    def clock_pause(self):
        self.ticking = False

    def clock_start(self):
        self.ticking = True

    def set_score(self, team, score):
        modified_list = []
        str_score = str(int(score))
        new_score = '0' * (3 - len(str_score)) + str_score
        if str(team).lower() == 'home':
            if str(new_score)[2] != str(self.areas["HomeScoreOnes"]):
                self.set_value("HomeScoreOnes", int(new_score[2]))
                modified_list.append("HomeScoreOnes")
            if str(new_score)[1] != str(self.areas["HomeScoreTens"]):
                self.set_value("HomeScoreTens", int(new_score[1]))
                modified_list.append("HomeScoreTens")
            if (str(new_score)[0] != str(self.areas["HomeScoreHundreds"])) and self.areas["HomeScoreHundreds"][1] != (0, 0):
                self.set_value("HomeScoreHundreds", int(new_score[0]))
                modified_list.append("HomeScoreHundreds")
        else:
            if str(new_score)[2] != str(self.areas["AwayScoreOnes"]):
                self.set_value("AwayScoreOnes", int(new_score[2]))
                modified_list.append("AwayScoreOnes")
            if str(new_score)[1] != str(self.areas["AwayScoreTens"]):
                self.set_value("AwayScoreTens", int(new_score[1]))
                modified_list.append("AwayScoreTens")
            if (str(new_score)[0] != str(self.areas["AwayScoreHundreds"])) and self.areas["AwayScoreHundreds"][1] != (0, 0):
                self.set_value("AwayScoreHundreds", int(new_score[0]))
                modified_list.append("AwayScoreHundreds")
        return modified_list

    def get_data(self):
        data = {}
        data['score'] = {}
        data['score']['home'] = (self.areas["HomeScoreOnes"][0]) + (
            self.areas["HomeScoreTens"][0] * 10 if self.areas["HomeScoreTens"][0] > -1 else 0) + (
                self.areas["HomeScoreHundreds"][0] * 10 if self.areas["HomeScoreHundreds"][0] > -1 else 0)
        data['score']['away'] = (self.areas["AwayScoreOnes"][0]) + (
            self.areas["AwayScoreTens"][0] * 10 if self.areas["AwayScoreTens"][0] > -1 else 0) + (
                self.areas["AwayScoreHundreds"][0] * 10 if self.areas["AwayScoreHundreds"][0] > -1 else 0)
        data['period'] = self.areas["Period"][0]
        data['home'] = {}
        data['home']['score'] = data['score']['home']
        data['home']['fouls'] = self.areas["HomeFouls"][0]
        data['away'] = {}
        data['away']['score'] = data['score']['away']
        data['away']['fouls'] = self.areas["AwayFouls"][0]
        data['clock'] = {}
        data['clock']['clock'] = "{}{}:{}{}".format(str(self.areas['MinutesTens'][0]), str(self.areas['MinutesOnes'][0]),
                                                 str(self.areas['SecondsTens'][0]), str(self.areas['SecondsOnes'][0]))
        data['clock']['shotclock'] = (self.areas["ShotClockOnes"][0]) + (
            self.areas["ShotClockTens"][0] * 10 if self.areas["ShotClockTens"][0] > -1 else 0)
        return data



    def log(self, log_line):
        self.log_file.append(datetime.now().strftime("%d/%m/%Y %H:%M:%S: " + log_line))
