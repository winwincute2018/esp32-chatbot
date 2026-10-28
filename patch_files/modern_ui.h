#pragma once
#include "lvgl.h"
#ifdef __cplusplus
extern "C" {
#endif
void modern_ui_init(void);
void modern_ui_update_status(int battery_percent, bool wifi_connected, const char* time_str);
#ifdef __cplusplus
}
#endif
