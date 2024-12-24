import json
import pyray as rl
from pprint import pprint
from load_toml_data import GameConfig 


def load_assets(data):
    return (rl.load_texture(data.bg.src),
            rl.load_texture(data.bildings[0].src),
            rl.load_texture(data.bildings[1].src))

def update(data):
    mx = rl.get_mouse_x()
    my = rl.get_mouse_y()
    if rl.is_mouse_button_pressed(rl.MOUSE_BUTTON_LEFT):
       if data.bildings[0].is_in(mx, my):
           print(data.bildings[0].name)
       elif data.bildings[1].is_in(mx, my):
           print(data.bildings[1].name)
       else:
           print(data.bg.name)


def draw(data, textures):
    bg_texture, h1_texture, h2_texture = textures

    rl.begin_drawing()


    rl.clear_background(rl.WHITE)
    rl.draw_texture(bg_texture, 0, 0, rl.WHITE)
    rl.draw_texture(h1_texture, data.bildings[0].x, data.bildings[0].y, rl.WHITE)
    rl.draw_texture(h2_texture, data.bildings[1].x, data.bildings[1].y, rl.WHITE)

    rl.end_drawing()


def main():
    data = GameConfig.load('tmp.toml')

    bg = data.bg
    bilds = data.bildings

    rl.init_window(bg.w, bg.h, 'h3-town')
    rl.set_target_fps(60)
    
    textures = load_assets(data)
    
    while not rl.window_should_close():
        update(data)     
        draw(data, textures)
   
    rl.close_window()

if __name__ == '__main__':
    main()
