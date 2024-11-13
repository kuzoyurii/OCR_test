import tkinter as tk
from PIL import ImageTk
from PIL import Image
from PIL import ImageFile
import time
import os.path
import sys
import glob
import ctypes
import datetime


def player_log(text):
    with open('player.log', 'a+') as file:
        file.write(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S: " + text + '\n'))


def max_win():
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry("%dx%d+0+0" % (w, h))
    # if on_debug:
    #     root.geometry("%dx%d+0+0" % (w, h))
    #     return
    #root.attributes('-fullscreen', True)


def callback():
    global frame_num, can_remove
    try:
        player_log('Opening: ' + str(frame_num))
        image = Image.open(r'{}/out_{}.png'.format(play_path,str(frame_num)))
        img2 = ImageTk.PhotoImage(image)
        img2 = img2._PhotoImage__photo.zoom(zoom)
        panel.configure(image=img2)
        panel.image = img2
        try:
            os.remove(r'{}/out_{}.png'.format(play_path,str(frame_num-10)))
        except:
                      pass
        #if not on_debug and can_remove:
        #    os.remove(r'{}\out_{}.png'.format(play_path,str(can_remove)))
        can_remove = frame_num
    except Exception as e:
        player_log('Exception: ' + str(e))
        time.sleep(render_time + 0.1)
    frame_num += 1
    player_log('next playing frame: {}'.format(str(frame_num)))


def clear_unneeded(up_to_frame):
    files = glob.glob('{}/*'.format('output'))
    for file in files:
        if os.path.isfile(file):
            try:
                file_val = int(file.split('.')[0].split('out_')[1])
                if file_val < int(up_to_frame) and (file_val > 0):
                    try:
                        os.remove(file)
                    except:
                        player_log('Error removing file...')
            except:
                player_log('unable to remove file...')


def find_last_frame():
    last_frame = frame_num * -1
    return_frame = last_frame
    try:
        while True:
            if os.path.exists(r'{}/out_{}{}'.format(play_path, str(last_frame), '.png')):
                return_frame = last_frame
                last_frame += 1
            else:
                break
        player_log('return last frame: ' + str(last_frame))
        return return_frame
    except Exception as e:
        player_log('Exception: ' + str(e) + '\n' + str(last_frame))
        return return_frame


def load_starting_image():
    global panel, frame_num
    if frame_num < 0:
        frame_num = find_last_frame()
    if not on_debug:
        clear_unneeded(frame_num)
    try:
        image = Image.open(r'{}/out_{}{}'.format(play_path,str(frame_num), '.png'))
        img = ImageTk.PhotoImage(image)
        img = img._PhotoImage__photo.zoom(zoom)
        panel = tk.Label(root, image=img)
        panel.pack(side="bottom", fill="both", expand="yes")
        panel.configure(cursor='none') #bg='black')
        max_win()
    except Exception as e:
        player_log('error loading starting image')
        if os.path.isfile(r'{}/out_{}{}'.format(play_path, str(frame_num), '.png')):
            player_log(e)
        else:
            if os.path.isfile(r'{}/out_0.png'.format(play_path)) and frame_num != 0:
                player_log('starting frame not found, trying to start from frame 0')
                frame_num = 0
                time.sleep(render_time)
                load_starting_image()
            else:
                player_log('error staring player, exiting...')
                close()


def close():
    global running
    running = False
    time.sleep(1)


def set_globals(frame_start=1, zoom_level=2, topmost=True):
    global frame_num, zoom, root, Button
    ImageFile.LOAD_TRUNCATED_IMAGES = False
    root = tk.Tk()
    # root.configure(bg='black')
    root.title("OCR Simulator Player")
    root.attributes('-topmost', topmost)
    root.attributes('-fullscreen', topmost)
    root.protocol("WM_DELETE_WINDOW", close)
    frame_num = frame_start
    zoom = zoom_level


def main_loop(frame_start=0, zoom_level=1, topmost=True, debug_mode='False', refresh_time=0.5, debug_path=''):
    global frame_num, running, run_on_debug, root, render_time, play_path, can_remove, on_debug
    on_debug = False
    can_remove = ''
    render_time = float(refresh_time)
    player_log(debug_mode)
    play_path = 'output'
    if debug_mode.lower() != 'false':
        on_debug = True
        play_path += r'/debug/{}'.format(debug_path)
    player_log(play_path)
    running = True
    set_globals(int(frame_start), int(zoom_level), topmost)
    load_starting_image()
    while running:
        if os.path.isfile(r'output/quit.command'):
            os.remove(r'output/quit.command')
            close()
            break
        time_start = time.time()
        root.update()
        callback()
        time_sec = time.time()
        if time_sec - time_start < render_time:
            time.sleep(render_time - (time_sec - time_start))
    root.destroy()
    return 1


if __name__ == '__main__':
    #ctypes.windll.kernel32.SetThreadExecutionState(0x80000002)
    try:
        main_loop(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
    except:
        player_log('Unable to start Player, make sure all arguments are entered')
    #ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
