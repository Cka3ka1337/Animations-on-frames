import os
import sys
import json
import random

import win32api
import win32con
import win32gui
import pygame

from ctypes import wintypes, WinDLL


def window_config(hwnd) -> None:
    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)

    win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0, 0, 0), 0, win32con.LWA_COLORKEY)

    user32.SetWindowPos.restype = wintypes.HWND
    user32.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, wintypes.INT, wintypes.INT, wintypes.INT, wintypes.INT, wintypes.UINT]
    user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001)


def SetWindowPos(hwnd, pos: tuple) -> None:
    user32.SetWindowPos(hwnd, -1, *pos, 0, 0, 0x0001)


def main(data):
    pygame.init()
    pygame.display.set_caption("Overlay")
    
    clock = pygame.time.Clock()
    sc = pygame.display.set_mode((1,1), pygame.NOFRAME)
    
    filenames = {x: sorted(os.listdir(x)) for x in data}
    frames = {x: [pygame.image.load(f'./{x}/{i}').convert_alpha() for i in filenames[x]] for x in filenames}

    
    _max = 0
    for key in frames:
        _height = frames[key][0].get_height() * data[key]['scale']
        if _height > _max:
            _max = _height
    
    # print(_max)
    
    
    sc = pygame.display.set_mode((win32api.GetSystemMetrics(0), _max), pygame.NOFRAME)
    hwnd = pygame.display.get_wm_info()["window"]
    window_config(hwnd)
    pygame.display.update()
    sc.fill((0, 0, 0))
    desktop_hwnd = win32gui.GetDesktopWindow()
    

    for key in frames:
        frames[key] = [pygame.transform.scale(frame, (frame.get_width() * data[key]['scale'], frame.get_height() * data[key]['scale'])) for frame in frames[key]]
    
    
    current_key = random.choice(list(frames.keys()))
    count_iter = data[current_key]['iters']
    current_frame = 0
    x = 0.5
    
    pygame.time.set_timer(pygame.USEREVENT, int((1 / data[current_key]['fps']) * 1000))

    while not win32api.GetAsyncKeyState(win32con.VK_PAUSE):
        try:
            hwnd_foregorund = win32gui.GetForegroundWindow()
            active_window_class = win32gui.GetClassName(hwnd_foregorund)
            if hwnd_foregorund == desktop_hwnd or active_window_class in ['Program', 'WorkerW']:
                x1, y1, x2, y2 = win32gui.GetWindowRect(hwnd_foregorund)
                width = (x2 - x1) / 2
                y1 = y2
            else:
                x1, y1, x2, y2 = win32gui.GetWindowRect(hwnd_foregorund)
                width = x2 - x1
            
            SetWindowPos(hwnd, (x1, y1 - sc.get_height()))
        except:
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            elif event.type == pygame.USEREVENT:
                current_frame = (current_frame + 1) % len(frames[current_key])
                if not current_frame:
                    count_iter -= 1
                    
                    if data[current_key]['update_pos']:
                        scale = frames[current_key][current_frame].get_width() / (width + 1e-9)
                        x = random.uniform(scale, 1.0 - scale)
                    
                if count_iter <= 0:
                    next_key = current_key
                    while next_key == current_key and len(frames) != 1:
                        next_key = random.choice(list(frames.keys()))
                        
                    scale = frames[current_key][current_frame].get_width() / (width + 1e-9)
                    x = random.uniform(scale, 1.0 - scale)
    
                    current_key = next_key
                    count_iter = data[current_key]['iters']
                    pygame.time.set_timer(pygame.USEREVENT, int((1 / data[current_key]['fps']) * 1000))

        sc.fill((0, 0, 0))
        # pygame.draw.rect(sc, (255, 0, 0), (width * 0.5, 0, 1, sc.get_height()))
        # pygame.draw.rect(sc, (255, 255, 255), (width * x, 0, 1, sc.get_height()))
        # print(clock.get_fps())
        sc.blit(
            frames[current_key][current_frame],
            (
                width * x - frames[current_key][current_frame].get_width() / 2,
                sc.get_height() - frames[current_key][current_frame].get_height()
            )
        )
        
        clock.tick(128)
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    
    user32 = WinDLL("user32")
    
    with open('config.json', 'r') as file:
        data = json.load(file)
        
    main(data=data)