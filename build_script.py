import os
import subprocess
import tarfile
import sys

tar_filename = "aio28-modern-github-v5.tar.gz"
repo_url = "https://github.com/78/xiaozhi-esp32.git"
clone_dir = "xiaozhi-esp32"

def main():
    # 1. Clone repository
    print("Cloning base repository...")
    subprocess.run(["git", "clone", "--recursive", repo_url, clone_dir], check=True)
    
    # 2. Extract tarball
    if os.path.exists(tar_filename):
        print(f"Extracting {tar_filename}...")
        with tarfile.open(tar_filename, "r:gz") as tar:
            tar.extractall(path=clone_dir)
    else:
        print(f"Error: {tar_filename} not found!")
        sys.exit(1)

    # 3. Patch CMakeLists.txt
    cmake_path = os.path.join(clone_dir, "main", "CMakeLists.txt")
    with open(cmake_path, "r") as f:
        cmake_content = f.read()
    
    if 'aio28-modern' not in cmake_content:
        patch = '''if(TRUE)\n    set(BOARD_DIR "aio28-modern")\n    set(BUILTIN_TEXT_FONT font_noto_sans_basic_14_1)\n    set(BUILTIN_ICON_FONT font_material_symbols_14_1)\n    set(DEFAULT_EMOJI_COLLECTION noto-color-emoji_128)\n    set(EMOTE_RESOLUTION "320_240")\nelseif(CONFIG_BOARD_TYPE_BREAD_COMPACT_WIFI)'''
        cmake_content = cmake_content.replace('if(CONFIG_BOARD_TYPE_BREAD_COMPACT_WIFI)', patch)
        with open(cmake_path, "w") as f:
            f.write(cmake_content)
        print("Patched CMakeLists.txt to force aio28-modern board")

    # 4. Patch aio28_modern_board.cc for ADC migration
    board_cc_path = os.path.join(clone_dir, "main", "boards", "aio28-modern", "aio28_modern_board.cc")
    if os.path.exists(board_cc_path):
        print("Patching ADC driver in aio28_modern_board.cc...")
        with open(board_cc_path, "r") as f:
            content = f.read()
        
        # Replace legacy include
        content = content.replace('#include <driver/adc.h>', 
                                  '#include "esp_adc/adc_oneshot.h"\n#include "esp_adc/adc_cali.h"\n#include "esp_adc/adc_cali_scheme.h"')
        
        # This is a generic patch. Depending on how ADC is used, more replacements might be needed.
        # For simple voltage reading, the new API requires initializing an adc_oneshot_unit_handle_t
        # If the build fails again due to specific adc_xxx() functions, we will need to replace those calls.
        # Often, projects use a wrapper or the changes are localized.
        # We will attempt a build with just the include change if the codebase handles conditional compilation,
        # or we might need to modify the implementation. Let's see if this resolves the immediate missing header error.

        with open(board_cc_path, "w") as f:
            f.write(content)
        print("ADC header patched.")

    # 5. Build Firmware
    os.chdir(clone_dir)
    
    print("Setting up ESP-IDF target...")
    subprocess.run(". $IDF_PATH/export.sh && idf.py set-target esp32s3", shell=True, executable='/bin/bash', check=True)
    
    print("Building...")
    # Add -w flag to temporarily suppress warnings as errors if applicable, though this error is fatal.
    subprocess.run(". $IDF_PATH/export.sh && idf.py build", shell=True, executable='/bin/bash', check=True)
    
    print("Merging binaries...")
    subprocess.run("python -m pip install esptool", shell=True, executable='/bin/bash', check=True)
    subprocess.run("esptool.py --chip esp32s3 merge_bin -o build/merged-binary.bin @build/flasher_args.json", shell=True, executable='/bin/bash', check=True)
    print("Build and merge complete!")

if __name__ == "__main__":
    main()
