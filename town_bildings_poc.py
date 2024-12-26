import pyray as rl
from pprint import pprint
from load_toml_data import GameConfig 
from dataclasses import dataclass

def load_assets(data):
    bildings_textures = {}
    for i, bilding in enumerate(data.bildings):
        for lvl, img_src in enumerate(bilding.src):
            # pprint(f'{i=}, {lvl=}, {img_src=}')
            bildings_textures[f'b{i}-lvl{lvl}'] = rl.load_texture(img_src)

    return (rl.load_texture(data.bg.src),
            bildings_textures)


def next_bilding_lvl(state, bilding_id, data):
    num_of_levels = len(data.bildings[bilding_id].src)
    current_lvl = state.bildings_lvl[bilding_id]
    return (current_lvl + 1) % num_of_levels





def update(state, data):
    mx = rl.get_mouse_x()
    my = rl.get_mouse_y()
    if rl.is_mouse_button_pressed(rl.MOUSE_BUTTON_LEFT):
        if state.is_display_bilding_page:
            # TODO: add popup window
            pass             

        else:
            is_click_on_bilding = False
            for i, bilding in enumerate(data.bildings):
                if bilding.is_in(mx, my):
                    is_click_on_bilding = True
                    #state.is_display_bilding_page = True 

                    state.bildings_lvl[i] = next_bilding_lvl(state, i, data)
                    print(bilding.name)
           
            if not is_click_on_bilding:
                print(data.bg.name)


def draw(state, data, textures):
    bg_texture, bildings_textures = textures

    rl.begin_drawing()

    rl.clear_background(rl.WHITE)
    rl.draw_texture(bg_texture, 0, 0, rl.WHITE)
    for i, lvl in enumerate(state.bildings_lvl):
        rl.draw_texture(bildings_textures[f'b{i}-lvl{lvl}'], data.bildings[i].x, data.bildings[i].y, rl.WHITE)

    rl.end_drawing()


@dataclass 
class State:
    bildings_lvl: list[int]
    is_display_bilding_page: bool
    bilding_indx_to_display: int | None


def main():
    data = GameConfig.load('tmp.toml')
    
    state = State([0, 0], False, None)

    pprint(state)
    bg = data.bg
    bilds = data.bildings

    rl.init_window(bg.w, bg.h, 'h3-town')
    rl.set_target_fps(60)
    
    textures = load_assets(data)
    
    while not rl.window_should_close():
        update(state, data)     
        draw(state, data, textures)
   
    rl.close_window()

if __name__ == '__main__':
    main()
