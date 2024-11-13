import tkinter as tk
import glob
from PIL import Image, ImageTk
from tkinter import StringVar
import os.path


def write_values(delete=False):
    dir = fname.split('.')[0]
    if not os.path.exists(dir):
        os.makedirs(dir)
    if allset() or delete:
        vp = fname2 if delete else var_pos
        vs = fname2+'Size' if delete else var_size
        files = [dir + r'\positions.txt', dir + r'\sizes.txt']
        for filename in files:
            if not os.path.exists(filename):
                open(filename, 'w').close()
            with open(filename, "r+") as f:
                d = f.readlines()
                f.seek(0)
                for i in d:
                    if not i.startswith(str(vp).split('=')[0]):
                        f.write(i)
                f.truncate()
                print('append')
                if not delete:
                    if 'positions.txt' in filename:
                        f.write(vp+'\n')
                    else:
                        f.write(vs+'\n')


def saveval(e):
    global v, var_size, var_pos, lock_x, lock_y
    var_pos = '{}={},{}'.format(fname2, str(x), str(y))
    var_size = '{}Size={},{}'.format(fname2, str(sx), str(sy))
    print('{}: {} in {},{} - Size {},{}'.format(fname, fname2, str(x), str(y), str(sx), str(sy)))
    update_v()
    write_values()
    lock_x = False
    lock_y = False


def showing_area(e):
    global fname2
    try:
        n2 = areas.curselection()
        fname2 = areas.get(n2)
        print(fname2)
        load_areas(fname2)
        update_v()
    except:
        pass


def clearfiles(e, delete=True):
    dir = fname.split('.')[0]
    if not os.path.exists(dir):
        os.makedirs(dir)
    if delete:
        print('clear all saved settings')
        files = [dir + r'\positions.txt', dir + r'\sizes.txt']
        for f in files:
            open(f, 'w').close()
    all_clear()


def all_clear():
    global lock_x, lock_y, first_x, x_diff, fname2, x, y, sx, sy
    lock_x = False
    lock_y = False
    first_x = None
    x_diff = None
    fname2 = 'HomeScoreTens'
    x = ''
    y = ''
    sx = ''
    sy = ''


def showing_sport(e):
    global filename, fname, v, fname2, x, y, sx, sy, img, image, dir
    try:
        n = sports.curselection()
        fname = 'scoreboards\\' + sports.get(n)
        img = Image.open(fname)
        img.save('scoreboards/current.png')
        image = ImageTk.PhotoImage(img)
        lab.config(image=image)
        lab.image = image
        print(fname)
        clearfiles(e, delete=False)
        dir = fname.split('.')[0]
        if not os.path.exists(dir + r'/board.jpg'):
            img.save(dir + r'/board.jpg')
        all_clear()
        update_v()
    except:
        pass


def draw(load_original=True):
    global first_x, x_diff
    dir = fname.split('.')[0]
    org = Image.open(dir + '/board.jpg', 'r')
    img = Image.open('scoreboards/current.png')
    digset = Image.open('scoreboards/digset.png')
    digset = digset.resize((int(sx), int(sy)))
    if load_original:
        org.paste(digset, (int(x), int(y)))
        org.save('scoreboards/current.png')
    else:
        print('update_current_image')
        img.paste(digset, (int(x), int(y)))
        img.save('scoreboards/current.png')
    img = Image.open('scoreboards/current.png')
    image = ImageTk.PhotoImage(img)
    lab.config(image=image)
    lab.image = image
    if x_diff is None and first_x is not None:
        x_diff = (int(x) - int(first_x))
    if first_x is None:
        first_x = (int(x))
    saved_sizes[fname2] = (int(sx), int(sy))
    saved_positions[fname2] = (int(x), int(y))
    print('first_X ' + str(first_x))
    print('diff_x' + str(x_diff))


def allset():
    return True if str(x) and str(y) and str(sx) and str(sy) and str(fname) and str(fname2) else False


def cleararea(e):
    write_values(delete=True)


def update_v():
    fname_v = fname if fname else "<Select Image>"
    fname2_v = fname2 if fname2 else "<Select Area>"
    loc_v = str(str(x) + ',' + str(y)) if (str(x) and str(y)) else "<Missing Location>"
    size_v = str(str(sx) + ',' + str(sy)) if (str(sx) and str(sy)) else "<Missing Size>"
    v.set('{}: {} in {} - Size {}'.format(fname_v, fname2_v, loc_v, size_v))


def locations(event):
    global x
    global y
    if not lock_x:
        x = event.x
    if not lock_y:
        y = event.y
    apply_locations()


def apply_locations(load_original=True):
    print('{}, {}'.format(x, y))
    update_v()
    if allset():
        draw(load_original)


def sizes(event):
    global x2
    global y2
    global sx
    global sy
    x2, y2 = event.x, event.y
    print('release {}, {}'.format(x2, y2))
    if x2 != x and y2 != y:
        sx = x2-x
        sy = y2-y
    update_v()
    if allset():
        draw()


def help_popup(e):
    msg = '- INSTRUCTIONS -\n' \
          'STEP 1: Choose image from images list\n' \
          'STEP 2: Select Area from Areas List\n' \
          'STEP 3: Over the image, hold left button on top of the left corner of the area,  \n ' \
          '             release on bottom right\n' \
          'STEP 4: Hit <RETURN> To add the area to configurations\n' \
          'STEP 5: Continue to the next relevant Area, size is kept until modified \n\n' \
          'KEYS: \n' \
          '<+/->            [UNDER DEV] Resize image (current settings will become invalid)\n'  \
          '<Return>         Write area to files\n' \
          '<Arrow keys>     Use Down to continue to the next area\n' \
          '<w/a/s/d>        Move selection one pixel\n' \
          '<W/A/S/D>        Resize selection one pixel\n' \
          '<p>              Smart Positioning - Will auto choose position\n' \
          '<y/x>            Lock/Unlock y/x Axis\n' \
          '<l>              Load current settings from files\n' \
          '<Backspace>      Will delete the SELECTED area from configurations\n' \
          '<Ctrl+Backspace> Clear all values from scoreboard configurations'
    popup = tk.Toplevel(root)
    popup.wm_title("Help")
    popup.tkraise(root)
    tk.Label(popup, text=msg, justify='left', anchor='w').pack(side="top", fill="both", pady=10, anchor='w')
    tk.Button(popup, text="Okay", command=popup.destroy).pack()


def change_location(arrow):
    global x, y
    print(image.height())
    if arrow == 'up' and y > 0:
        y -= 1
    if arrow == 'down' and y + sy < image.height():
        print(image.height())
        y += 1
    if arrow == 'left' and x > 0:
        x -= 1
    if arrow == 'right' and x + sx < image.width():
        print(image.width())
        x += 1
    apply_locations()


def change_size(arrow):
    global sx, sy
    if arrow == 'up' and sy > 0:
        sy -= 1
    if arrow == 'down' and y + sy < image.height():
        print(image.height())
        sy += 1
    if arrow == 'left' and x > 0:
        sx -= 1
    if arrow == 'right' and x + sx < image.width():
        print(image.width())
        sx += 1
    apply_locations()


def resize_image(larger_smaller):
    global img, image, lab, new_image
    img_w = int(image.width())
    img_h = int(image.height())
    if larger_smaller == 'larger':
        new_image = img.resize((int(img_w * 1.1), int(img_h * 1.1)), Image.ANTIALIAS)
    else:
        new_image = img.resize((int(img_w * 0.9), int(img_h * 0.9)), Image.ANTIALIAS)
        print(str(new_image.width))
    dir = fname.split('\\')[1].split('.')[0]
    new_image.save('/scoreboards/current.png')
    new_image.save(dir + r'/board.jpg')
    image = ImageTk.PhotoImage(new_image)
    lab.config(image=image)
    lab.image = image


def to_lock_x(e):
    global lock_x
    lock_x = True if not lock_x else False


def to_lock_y(e):
    global lock_y
    lock_y = True if not lock_y else False


def smart_pos(e):
    global x, y
    if fname2 in ['HomeScoreOnes', 'MinutesOnes']:
        x = (x + sx + 1) if not x_diff else (x + sx + int(x_diff))
    if fname2 == 'Period':
        x = int(image.width() / 2) - int(sx / 2)
        y = int(image.height() / 2) - int(sy / 2)
    if fname2 in ['AwayScoreTens', 'AwayScoreOnes', 'SecondsTens', 'SecondsOnes']:
        if fname2 == 'AwayScoreTens':
            if 'HomeScoreOnes' in saved_positions:
                x = int(image.width()) - int(sx) - int(saved_positions['HomeScoreOnes'][0])
        if fname2 == 'AwayScoreOnes':
            if 'AwayScoreTens' in saved_positions and x_diff:
                x = int(x_diff) + int(saved_positions['AwayScoreTens'][0])
            elif 'HomeScoreTens' in saved_positions:
                x = int(image.width()) - int(sx) - int(saved_positions['HomeScoreTens'][0])
        if fname2 == 'SecondsTens':
            if 'MinutesOnes' in saved_positions:
                x = int(image.width()) - int(sx) - int(saved_positions['MinutesOnes'][0])
        if fname2 == 'SecondsOnes':
            if 'MinutesTens' in saved_positions:
                x = int(image.width()) - int(sx) - int(saved_positions['MinutesTens'][0])
    apply_locations()


def load_areas(areas_list='all'):
    global x, y, sx, sy, dir, img, image, lab, fname
    dir = fname.split('.')[0]
    img = Image.open(dir + r'/board.jpg')
    img.save('scoreboards/current.png')
    image = ImageTk.PhotoImage(img)
    lab.config(image=image)
    file_p, file_s = dir + r'\positions.txt', dir + r'\sizes.txt'
    with open(file_p, "r") as pos_file:
        for line_pos in pos_file:
            area = line_pos.split('=')[0]
            if areas_list != 'all' and areas_list != area:
                continue
            x, y = line_pos.strip().split('=')[1].split(',')
            with open(file_s, "r") as size_file:
                for line_size in size_file:
                    if line_size.startswith(area):
                        sx, sy = line_size.strip().split('=')[1].split(',')
                        x, y, sx, sy = int(x), int(y), int(sx), int(sy)
                        apply_locations(load_original=False)


def load_file(e):
    try:
        load_areas('all')
    except:
        pass


saved_positions = {}
saved_sizes = {}
root = tk.Tk()
sports = tk.Listbox(root)
sports.pack(side="left", fill=tk.Y, expand=1, anchor='w')
sport_list = [i.split('\\')[1] for i in glob.glob("scoreboards\*jpg")]
areas = tk.Listbox(root)
areas.pack(side="bottom", fill=tk.X, expand=1, anchor='s')
areas_list = [
    "HomeScoreTens",
    "HomeScoreOnes",
    "AwayScoreTens",
    "AwayScoreOnes",
    "HomeScoreHundreds",
    "AwayScoreHundreds",
    "Period",
    "MinutesTens",
    "MinutesOnes",
    "SecondsTens",
    "SecondsOnes",
    "HomeFouls",
    "AwayFouls",
    "ShotClockTens",
    "ShotClockOnes"
]


for fname in sport_list:
    sports.insert(tk.END, fname)
sports.bind("<<ListboxSelect>>", showing_sport)
filename = 'scoreboards\welcome.png'

for fname in areas_list:
    areas.insert(tk.END, fname)
areas.bind("<<ListboxSelect>>", showing_area)

img = ImageTk.PhotoImage(Image.open(filename))
lab = tk.Label(root, text='filename', image=img, cursor='tcross')
lab.pack(anchor='w')

lab.bind('<Button-1>', locations)
lab.bind('<ButtonRelease-1>', sizes)
root.bind('<Return>', saveval)
root.bind('<BackSpace>', cleararea)
root.bind('<Control-BackSpace>', clearfiles)
root.bind('w', lambda c: change_location('up'))
root.bind('s', lambda c: change_location('down'))
root.bind('a', lambda c: change_location('left'))
root.bind('d', lambda c: change_location('right'))
root.bind('W', lambda c: change_size('up'))
root.bind('S', lambda c: change_size('down'))
root.bind('A', lambda c: change_size('left'))
root.bind('D', lambda c: change_size('right'))
root.bind('+', lambda c: resize_image('larger'))
root.bind('-', lambda c: resize_image('smaller'))
root.bind('y', to_lock_y)
root.bind('x', to_lock_x)
root.bind('p', smart_pos)
root.bind('l', load_file)
root.bind('<F1>', help_popup)
root.title("Scoreboard Generator")

lock_x = False
lock_y = False
first_x = None
x_diff = None
fname = 'basketball.jpg'
fname2 = 'HomeScoreTens'
x = ''
y = ''
sx = ''
sy = ''

v = StringVar()

textLabel = tk.Label(root, textvariable=v, justify="left", padx=10)
textLabel.pack(side="left")
v.set('Press F1 for Help')
root.mainloop()
