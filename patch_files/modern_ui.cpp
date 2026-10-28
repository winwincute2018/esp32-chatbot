#include "modern_ui.h"
#include "esp_log.h"

static const char *TAG = "ModernUI";
static lv_obj_t * status_bar;
static lv_obj_t * battery_label;
static lv_obj_t * wifi_label;
static lv_obj_t * time_label;
static lv_obj_t * app_grid;

static void app_click_event_cb(lv_event_t * e) {
    int app_id = (int)(long)lv_event_get_user_data(e);
    switch(app_id) {
        case 1: ESP_LOGI(TAG, "Mo App Nhac"); break;
        case 2: ESP_LOGI(TAG, "Mo Thoi Tiet"); break;
        case 3: ESP_LOGI(TAG, "Mo SmartHome"); break;
        case 4: ESP_LOGI(TAG, "Mo Ghi am"); break;
        case 5: ESP_LOGI(TAG, "Mo Anh"); break;
        case 6: ESP_LOGI(TAG, "Mo Cai dat"); break;
    }
}

static void create_app_icon(lv_obj_t * parent, const char * icon_symbol, const char * app_name, int app_id) {
    lv_obj_t * btn = lv_obj_create(parent);
    lv_obj_set_size(btn, 80, 80);
    lv_obj_set_flex_flow(btn, LV_FLEX_FLOW_COLUMN);
    lv_obj_set_flex_align(btn, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    lv_obj_add_event_cb(btn, app_click_event_cb, LV_EVENT_CLICKED, (void*)(long)app_id);
    
    lv_obj_t * icon = lv_label_create(btn);
    lv_label_set_text(icon, icon_symbol);
    
    lv_obj_t * label = lv_label_create(btn);
    lv_label_set_text(label, app_name);
}

void modern_ui_init(void) {
    lv_obj_t * scr = lv_scr_act();
    lv_obj_clean(scr);

    status_bar = lv_obj_create(scr);
    lv_obj_set_size(status_bar, LV_PCT(100), 30);
    lv_obj_align(status_bar, LV_ALIGN_TOP_MID, 0, 0);
    lv_obj_set_flex_flow(status_bar, LV_FLEX_FLOW_ROW);
    lv_obj_set_flex_align(status_bar, LV_FLEX_ALIGN_SPACE_BETWEEN, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    
    time_label = lv_label_create(status_bar);
    lv_label_set_text(time_label, "12:00");
    
    lv_obj_t * right_icons = lv_obj_create(status_bar);
    lv_obj_set_style_border_width(right_icons, 0, 0);
    lv_obj_set_style_bg_opa(right_icons, 0, 0);
    lv_obj_set_flex_flow(right_icons, LV_FLEX_FLOW_ROW);
    
    wifi_label = lv_label_create(right_icons);
    lv_label_set_text(wifi_label, LV_SYMBOL_WIFI);
    
    battery_label = lv_label_create(right_icons);
    lv_label_set_text(battery_label, LV_SYMBOL_BATTERY_FULL " 100%");

    app_grid = lv_obj_create(scr);
    lv_obj_set_size(app_grid, LV_PCT(100), LV_PCT(100) - 30);
    lv_obj_align(app_grid, LV_ALIGN_BOTTOM_MID, 0, 0);
    lv_obj_set_flex_flow(app_grid, LV_FLEX_FLOW_ROW_WRAP);
    lv_obj_set_flex_align(app_grid, LV_FLEX_ALIGN_SPACE_EVENLY, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_START);

    create_app_icon(app_grid, LV_SYMBOL_AUDIO, "Nhac", 1);
    create_app_icon(app_grid, LV_SYMBOL_IMAGE, "Thoi tiet", 2);
    create_app_icon(app_grid, LV_SYMBOL_HOME, "SmartHome", 3);
    create_app_icon(app_grid, LV_SYMBOL_PLAY, "Ghi am", 4);
    create_app_icon(app_grid, LV_SYMBOL_IMAGE, "Anh", 5);
    create_app_icon(app_grid, LV_SYMBOL_SETTINGS, "Cai dat", 6);
}

void modern_ui_update_status(int battery_percent, bool wifi_connected, const char* time_str) {
    if(time_label) lv_label_set_text(time_label, time_str);
    if(wifi_label) lv_label_set_text(wifi_label, wifi_connected ? LV_SYMBOL_WIFI : "");
    if(battery_label) lv_label_set_text_fmt(battery_label, " %d%%", battery_percent);
}
