import os

def patch_cmake():
    path = 'xiaozhi-esp32/main/CMakeLists.txt'
    if not os.path.exists(path):
        print(f"{path} not found!")
        return
    with open(path, 'r') as f:
        text = f.read()
        
    modified = False
    if 'modern_ui.cpp' not in text:
        text = text.replace('lvgl_display.cc', 'lvgl_display.cc\n    "display/lvgl_display/modern_ui.cpp"')
        modified = True
        
    board_hook = "if(CONFIG_BOARD_TYPE_BREAD_COMPACT_WIFI)"
    board_patch = '''if(TRUE)
    set(BOARD_DIR "custom_board_28aio")
    set(BUILTIN_TEXT_FONT font_noto_sans_basic_14_1)
    set(BUILTIN_ICON_FONT font_material_symbols_14_1)
    set(DEFAULT_EMOJI_COLLECTION noto-color-emoji_128)
    set(EMOTE_RESOLUTION "320_240")
elseif(CONFIG_BOARD_TYPE_BREAD_COMPACT_WIFI)'''
    
    if board_hook in text and 'custom_board_28aio' not in text:
        text = text.replace(board_hook, board_patch)
        modified = True
        
    if modified:
        with open(path, 'w') as f:
            f.write(text)
        print("Patched CMakeLists.txt successfully!")

def patch_cpp():
    path = 'xiaozhi-esp32/main/display/lvgl_display/lvgl_display.cc'
    if not os.path.exists(path):
        print(f"{path} not found!")
        return
    with open(path, 'r') as f:
        text = f.read()
    
    modified = False
    if '#include "modern_ui.h"' not in text:
        text = '#include "modern_ui.h"\n' + text
        modified = True
        
    if 'modern_ui_init()' not in text:
        if 'LvglDisplay::LvglDisplay() {' in text:
            text = text.replace('LvglDisplay::LvglDisplay() {', 'LvglDisplay::LvglDisplay() {\n    modern_ui_init();')
            modified = True
        elif 'LvglDisplay::LvglDisplay()' in text:
            idx = text.find('LvglDisplay::LvglDisplay()')
            if idx != -1:
                brace_idx = text.find('{', idx)
                if brace_idx != -1:
                    text = text[:brace_idx+1] + '\n    modern_ui_init();' + text[brace_idx+1:]
                    modified = True

    if modified:
        with open(path, 'w') as f:
            f.write(text)
        print("Patched lvgl_display.cc successfully!")

if __name__ == "__main__":
    patch_cmake()
    patch_cpp()
