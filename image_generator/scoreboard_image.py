from PIL import Image

log = []


def get_sizes_from_file(conf_path):
    vars = {}
    with open(conf_path, "r") as conf_file:
        conf_data = conf_file.readlines()
    for line in conf_data:
        try:
            var = line.strip().split('=')
            v_name = var[0].strip(' ')
            v_val = (int(var[1].split(',')[0]),int(var[1].split(',')[1]))
            vars[v_name] = v_val
        except Exception as E:
            log.append('skipping none variable line')
    return vars


def create_assets(scoreboard, cwd, font=0):
    vars = get_sizes_from_file(scoreboard.sizes_file)
    for d in range(11):
        digit = Image.open(r'{}/scoreboards/{}/{}/{}.png'.format(cwd, str(scoreboard.id), str(font), d-1), 'r')
        for v in vars:
            new_dig = digit.resize(vars[v])
            new_dig.save('assets/{}_{}.png'.format(str(d-1),v))
    board = Image.open(r'{}/scoreboards/{}/board.jpg'.format(cwd, str(scoreboard.id)), 'r')
    board.save('assets/board.png')
    try:
        board.save('output/out_{}.png'.format(str(scoreboard.frame)))
        if scoreboard.debug:
            board.save('output/debug/{}/out_{}.png'.format(scoreboard.id,str(scoreboard.frame)))
    except:
        log.append('!! ERR create_assets !!')
        return False
    return True


def publish_image(scoreboard, board, frames):
    global log
    log.append('saving image')
    try:
        board.save('output/out_{}.png'.format(str(frames)))
        log.append('image output/out_{}.png saved'.format(str(frames)))
        if scoreboard.debug:
            board.save('output/debug/{}/out_{}.png'.format(scoreboard.id,str(frames)))
    except:
        log.append('!! ERR publish_image !!')


def load_base_image(frame_path):
    global log
    log.append('loading base image {}'.format(frame_path))
    try:
        board = Image.open(frame_path, 'r')
    except:
        log.append('!! ERR load_base_image !!')
        return
    return board


def load_digit_image(frame_path):
    global log
    log.append('loading digit image {}'.format(frame_path))
    try:
        digit = Image.open(frame_path, 'r')
    except:
        log.append('!! ERR load_digit_image !!')
    return digit


def paste(board, digit, offset):
    global log
    log.append('pasting digit to board')
    try:
        board.paste(digit, offset)
    except:
        log.append('!! ERR paste !!')
    return board


def make_a_change(scoreboard, change, board):
    global log
    log.append('putting {} in {}'.format(str(scoreboard.areas[change][0]),str(change)))
    try:
        digit = load_digit_image('assets/{}_{}Size.png'.format(str(scoreboard.areas[change][0]),change))
        new_board = paste(board, digit, scoreboard.areas[change][1])
    except:
        log.append('!! ERR make_a_change !!')
    try:
        return new_board
    except:
        return scoreboard


def changes_in_image(scoreboard, change_areas, cwd, frames):
    global log
    log = []
    try:
        board = load_base_image('{}/output/out_{}.png'.format(cwd,str(scoreboard.frame)))
        for area in change_areas:
            if scoreboard.areas[area][1]!=(0,0):
                try:
                    board = make_a_change(scoreboard, area, board)
                except:
                    print('!! ERR changes_in_image Change {} !!'.format(area))
                    log.append('!! ERR changes_in_image Change {} !!'.format(area))
            else:
                print(area + ' not found on board, not changing...')
                log.append(area + ' not found on board, not changing...')
        try:
            publish_image(scoreboard, board, frames)
            return True, log
        except:
            print('!! ERR changes_in_image PUBLISH !!')
            log.append('!! ERR changes_in_image PUBLISH !!')
            return False, log
    except:
        log.append('!! ERR changes_in_image !!')
        return False, log


if __name__ == '__main__':
    print('Running from Main')
