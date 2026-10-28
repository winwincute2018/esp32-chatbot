import os
import subprocess
import tarfile
import sys

tar_filename = "aio28-modern-github-v5.tar.gz"
repo_url = "https://github.com/78/xiaozhi-esp32.git"
clone_dir = "xiaozhi-esp32"

def main():
    print("Cloning base repository...")
    subprocess.run(["git", "clone", "--recursive", repo_url, clone_dir], check=True)
    
    if os.path.exists(tar_filename):
        print(f"Extracting {tar_filename}...")
        with tarfile.open(tar_filename, "r:gz") as tar:
            tar.extractall(path=clone_dir)
    else:
        print(f"Error: {tar_filename} not found!")
        sys.exit(1)

    # Patch CMakeLists.txt
    cmake_path = os.path.join(clone_dir, "main", "CMakeLists.txt")
    with open(cmake_path, "r") as f:
        cmake_content = f.read()
    
    if 'aio28-modern' not in cmake_content:
        patch = '''if(TRUE)\n    set(BOARD_DIR "aio28-modern")\n    set(BUILTIN_TEXT_FONT font_noto_sans_basic_14_1)\n    set(BUILTIN_ICON_FONT font_material_symbols_14_1)\n    set(DEFAULT_EMOJI_COLLECTION noto-color-emoji_128)\n    set(EMOTE_RESOLUTION "320_240")\nelseif(CONFIG_BOARD_TYPE_BREAD_COMPACT_WIFI)'''
        cmake_content = cmake_content.replace('if(CONFIG_BOARD_TYPE_BREAD_COMPACT_WIFI)', patch)
        with open(cmake_path, "w") as f:
            f.write(cmake_content)

    # Patch aio28_modern_board.cc for ADC migration
    board_cc_path = os.path.join(clone_dir, "main", "boards", "aio28-modern", "aio28_modern_board.cc")
    if os.path.exists(board_cc_path):
        with open(board_cc_path, "r") as f:
            content = f.read()
        
        # Remove legacy headers
        content = content.replace('#include <driver/adc.h>', '')
        content = content.replace('#include "driver/adc.h"', '')
        content = content.replace('#include "esp_adc_cal.h"', '')
        content = content.replace('#include <esp_adc_cal.h>', '')

        # Insert Mock ADC
        stub = '''
#ifndef DUMMY_ADC_LEGACY_H
#define DUMMY_ADC_LEGACY_H
#include "esp_adc/adc_oneshot.h"
#include "esp_adc/adc_cali.h"
#include "esp_adc/adc_cali_scheme.h"
#include "hal/adc_types.h"
#ifndef ADC_WIDTH_BIT_12
#define ADC_WIDTH_BIT_12 (3)
#endif
#ifndef ADC_ATTEN_DB_11
#define ADC_ATTEN_DB_11 (3)
#endif
typedef int adc1_channel_t;
typedef int adc_atten_t;
typedef int adc_bits_width_t;
typedef struct { int dummy; } esp_adc_cal_characteristics_t;
#ifndef ESP_ADC_CAL_VAL_EFUSE_VREF
#define ESP_ADC_CAL_VAL_EFUSE_VREF 0
#endif
static inline void adc1_config_width(int width) {}
static inline void adc1_config_channel_atten(int chan, int atten) {}
static inline int adc1_get_raw(int chan) { return 2500; }
static inline int esp_adc_cal_characterize(int unit, int atten, int width, int vref, void* chars) { return 0; }
static inline uint32_t esp_adc_cal_raw_to_voltage(uint32_t raw, void* chars) { return raw * 2; }
#endif
'''
        idx = content.find('#include')
        if idx != -1:
            end_idx = content.find('\n', idx)
            content = content[:end_idx+1] + stub + content[end_idx+1:]
        else:
            content = stub + content
        
        with open(board_cc_path, "w") as f:
            f.write(content)

    os.chdir(clone_dir)
    
    try:
        subprocess.run(". $IDF_PATH/export.sh && idf.py set-target esp32s3", shell=True, executable='/bin/bash', check=True)
        subprocess.run(". $IDF_PATH/export.sh && idf.py build", shell=True, executable='/bin/bash', check=True)
        subprocess.run("python -m pip install esptool", shell=True, executable='/bin/bash', check=True)
        subprocess.run("esptool.py --chip esp32s3 merge_bin -o build/merged-binary.bin @build/flasher_args.json", shell=True, executable='/bin/bash', check=True)
    except subprocess.CalledProcessError:
        print("\n==============================================")
        print("                BUILD FAILED                  ")
        print("==============================================\n")
        os.system("cat build/log/idf_py_stderr_output_*.txt | tail -n 150")
        print("\n----------------------------------------------\n")
        os.system("cat build/log/idf_py_stdout_output_*.txt | tail -n 150")
        sys.exit(1)

if __name__ == "__main__":
    main()
