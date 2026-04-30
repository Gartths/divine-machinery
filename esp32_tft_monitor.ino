#include <WiFi.h>
#include <HTTPClient.h>
#include <TFT_eSPI.h>
#include <ArduinoJson.h>
#include <SPI.h>

// ==================== WIFI CONFIG ====================
const char* ssid = "YOUR_SSID";
const char* password = "YOUR_PASSWORD";
const char* serverURL = "http://192.168.36.106:5000/stats";

// ==================== TFT CONFIG ====================
TFT_eSPI tft = TFT_eSPI();

// ==================== COLORS (Modern Dark Theme) ====================
#define COLOR_BG 0x0C12
#define COLOR_CARD_BG 0x1041
#define COLOR_ACCENT 0x00FF
#define COLOR_ACCENT_WARM 0xFF80
#define COLOR_ACCENT_COOL 0x07FF
#define COLOR_TEXT_PRIMARY 0xFFFF
#define COLOR_TEXT_SECONDARY 0x8C71
#define COLOR_SUCCESS 0x07E0
#define COLOR_WARNING 0xFD20
#define COLOR_DANGER 0xF800
#define COLOR_BORDER 0x2104

// ==================== UI STATE ====================
uint32_t lastUpdateTime = 0;
uint32_t updateInterval = 2000;
bool showDetailsScreen = false;

// ==================== BUTTON AREAS ====================
struct Button {
  uint16_t x, y, w, h;
  const char* label;
};

Button btnDetails = {10, 280, 110, 30, "Details"};
Button btnRefresh = {130, 280, 110, 30, "Refresh"};

// ==================== DATA STRUCTURE ====================
struct SystemStats {
  float cpu_temp = 0.0;
  float gpu_temp = 0.0;
  float cpu_load = 0.0;
  float ram_usage = 0.0;
  uint32_t lastFetch = 0;
} stats;

// ==================== SPRITES ====================
TFT_eSprite spr_main = TFT_eSprite(&tft);

// ==================== FORWARD DECLARATIONS ====================
void connectWiFi();
void fetchStats();
bool parseJSON(const String& payload);
void drawMainScreen();
void drawDetailsScreen();
void drawProgressBar(int16_t x, int16_t y, uint16_t w, uint16_t h, float percent, uint16_t color);
void drawButton(Button& btn, bool hover = false);
void handleTouch();
uint16_t getColorForTemp(float temp);
uint16_t getColorForLoad(float load);

// ==================== SETUP ====================
void setup() {
  Serial.begin(115200);
  delay(500);
  
  Serial.println("\n\n=== ESP32 System Monitor ===");
  
  // Initialize TFT
  tft.init();
  tft.setRotation(0);  // Portrait mode (240x320)
  tft.fillScreen(COLOR_BG);
  
  // Create sprite
  spr_main.createSprite(240, 320);
  spr_main.setColorDepth(16);
  
  // Show splash screen
  tft.fillScreen(COLOR_BG);
  tft.setTextColor(COLOR_ACCENT_COOL);
  tft.setFreeFont(&FreeSansBold24pt7b);
  tft.drawString("Connecting...", 120, 140, MC_DATUM);
  
  // Connect to WiFi
  connectWiFi();
  
  // Initial fetch
  fetchStats();
  
  lastUpdateTime = millis();
}

// ==================== MAIN LOOP ====================
void loop() {
  uint32_t currentTime = millis();
  
  // Handle touch
  handleTouch();
  
  // Update data every 2 seconds
  if (currentTime - lastUpdateTime >= updateInterval) {
    fetchStats();
    lastUpdateTime = currentTime;
  }
  
  // Draw appropriate screen
  if (showDetailsScreen) {
    drawDetailsScreen();
  } else {
    drawMainScreen();
  }
  
  delay(50);
}

// ==================== WIFI CONNECTION ====================
void connectWiFi() {
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi Connected!");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
    
    tft.fillScreen(COLOR_BG);
    tft.setTextColor(COLOR_SUCCESS);
    tft.setFreeFont(&FreeSansBold18pt7b);
    tft.drawString("WiFi OK", 120, 160, MC_DATUM);
  } else {
    Serial.println("\nFailed to connect WiFi");
    tft.fillScreen(COLOR_BG);
    tft.setTextColor(COLOR_DANGER);
    tft.setFreeFont(&FreeSansBold18pt7b);
    tft.drawString("WiFi Failed", 120, 160, MC_DATUM);
  }
  
  delay(2000);
}

// ==================== FETCH DATA FROM SERVER ====================
void fetchStats() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not connected");
    return;
  }
  
  HTTPClient http;
  http.setTimeout(5000);
  
  Serial.print("Fetching from: ");
  Serial.println(serverURL);
  
  if (http.begin(serverURL)) {
    int httpCode = http.GET();
    
    if (httpCode == HTTP_CODE_OK) {
      String payload = http.getString();
      Serial.println("Data received:");
      Serial.println(payload);
      
      if (parseJSON(payload)) {
        stats.lastFetch = millis();
        Serial.println("JSON parsed successfully");
      }
    } else {
      Serial.print("HTTP error: ");
      Serial.println(httpCode);
    }
    
    http.end();
  } else {
    Serial.println("Failed to connect to server");
  }
}

// ==================== PARSE JSON ====================
bool parseJSON(const String& payload) {
  StaticJsonDocument<200> doc;
  DeserializationError error = deserializeJson(doc, payload);
  
  if (error) {
    Serial.print("JSON parse error: ");
    Serial.println(error.f_str());
    return false;
  }
  
  stats.cpu_temp = doc["cpu_temp"] | 0.0;
  stats.gpu_temp = doc["gpu_temp"] | 0.0;
  stats.cpu_load = doc["cpu_load"] | 0.0;
  stats.ram_usage = doc["ram_usage"] | 0.0;
  
  Serial.printf("CPU Temp: %.1f°C\n", stats.cpu_temp);
  Serial.printf("GPU Temp: %.1f°C\n", stats.gpu_temp);
  Serial.printf("CPU Load: %.1f%%\n", stats.cpu_load);
  Serial.printf("RAM Usage: %.1f%%\n", stats.ram_usage);
  
  return true;
}

// ==================== DRAW MAIN SCREEN ====================
void drawMainScreen() {
  spr_main.fillSprite(COLOR_BG);
  
  // ===== HEADER =====
  spr_main.setTextColor(COLOR_TEXT_PRIMARY);
  spr_main.setFreeFont(&FreeSansBold24pt7b);
  spr_main.drawString("System Monitor", 120, 20, MC_DATUM);
  
  // ===== STATUS INDICATOR =====
  uint16_t statusColor = (millis() - stats.lastFetch < 3000) ? COLOR_SUCCESS : COLOR_WARNING;
  spr_main.fillCircle(225, 20, 5, statusColor);
  
  // ===== BIG CPU TEMP CARD =====
  uint16_t cpuColor = getColorForTemp(stats.cpu_temp);
  
  // Card background
  spr_main.fillRoundRect(10, 50, 220, 100, 15, COLOR_CARD_BG);
  spr_main.drawRoundRect(10, 50, 220, 100, 15, COLOR_BORDER);
  
  // CPU temp title
  spr_main.setTextColor(COLOR_TEXT_SECONDARY);
  spr_main.setFreeFont(&FreeSans12pt7b);
  spr_main.drawString("CPU Temperature", 120, 65, MC_DATUM);
  
  // CPU temp value - using 32pt instead of 48pt
  spr_main.setTextColor(cpuColor);
  spr_main.setFreeFont(&FreeSansBold24pt7b);
  char cpuStr[10];
  sprintf(cpuStr, "%.1f", stats.cpu_temp);
  spr_main.drawString(cpuStr, 90, 115, MC_DATUM);
  
  // Temperature unit
  spr_main.setFreeFont(&FreeSansBold18pt7b);
  spr_main.drawString("°C", 150, 100, MC_DATUM);
  
  // ===== GPU TEMP CARD =====
  uint16_t gpuColor = getColorForTemp(stats.gpu_temp);
  
  spr_main.fillRoundRect(10, 160, 105, 80, 12, COLOR_CARD_BG);
  spr_main.drawRoundRect(10, 160, 105, 80, 12, COLOR_BORDER);
  
  spr_main.setTextColor(COLOR_TEXT_SECONDARY);
  spr_main.setFreeFont(&FreeSans9pt7b);
  spr_main.drawString("GPU", 62, 172, MC_DATUM);
  
  spr_main.setTextColor(gpuColor);
  spr_main.setFreeFont(&FreeSansBold24pt7b);
  sprintf(cpuStr, "%.1f", stats.gpu_temp);
  spr_main.drawString(cpuStr, 62, 205, MC_DATUM);
  
  spr_main.setFreeFont(&FreeSans9pt7b);
  spr_main.drawString("°C", 62, 225, MC_DATUM);
  
  // ===== CPU LOAD CARD =====
  uint16_t loadColor = getColorForLoad(stats.cpu_load);
  
  spr_main.fillRoundRect(125, 160, 105, 80, 12, COLOR_CARD_BG);
  spr_main.drawRoundRect(125, 160, 105, 80, 12, COLOR_BORDER);
  
  spr_main.setTextColor(COLOR_TEXT_SECONDARY);
  spr_main.setFreeFont(&FreeSans9pt7b);
  spr_main.drawString("CPU Load", 177, 172, MC_DATUM);
  
  spr_main.setTextColor(loadColor);
  spr_main.setFreeFont(&FreeSansBold24pt7b);
  sprintf(cpuStr, "%.0f", stats.cpu_load);
  spr_main.drawString(cpuStr, 177, 205, MC_DATUM);
  
  spr_main.setFreeFont(&FreeSans9pt7b);
  spr_main.drawString("%", 177, 225, MC_DATUM);
  
  // ===== USAGE BARS =====
  spr_main.setTextColor(COLOR_TEXT_SECONDARY);
  spr_main.setFreeFont(&FreeSans9pt7b);
  
  // CPU Load bar
  spr_main.drawString("CPU Usage", 20, 260, TL_DATUM);
  drawProgressBar(20, 273, 200, 8, stats.cpu_load, getColorForLoad(stats.cpu_load));
  
  // RAM Usage bar
  spr_main.drawString("RAM Usage", 20, 265 + 15, TL_DATUM);
  drawProgressBar(20, 288, 200, 8, stats.ram_usage, getColorForLoad(stats.ram_usage));
  
  // ===== BUTTONS =====
  drawButton(btnDetails, false);
  drawButton(btnRefresh, false);
  
  // Push sprite to display
  spr_main.pushSprite(0, 0);
}

// ==================== DRAW DETAILS SCREEN ====================
void drawDetailsScreen() {
  spr_main.fillSprite(COLOR_BG);
  
  // ===== HEADER =====
  spr_main.setTextColor(COLOR_TEXT_PRIMARY);
  spr_main.setFreeFont(&FreeSansBold24pt7b);
  spr_main.drawString("Detailed Stats", 120, 20, MC_DATUM);
  
  // ===== DETAILED INFO =====
  int y_pos = 70;
  int line_height = 50;
  char tempStr[20];
  
  // CPU Temperature Details
  spr_main.fillRoundRect(10, y_pos, 220, 45, 10, COLOR_CARD_BG);
  spr_main.drawRoundRect(10, y_pos, 220, 45, 10, COLOR_BORDER);
  spr_main.setTextColor(COLOR_TEXT_SECONDARY);
  spr_main.setFreeFont(&FreeSans9pt7b);
  spr_main.drawString("CPU Temperature", 20, y_pos + 10, TL_DATUM);
  spr_main.setTextColor(getColorForTemp(stats.cpu_temp));
  spr_main.setFreeFont(&FreeSansBold18pt7b);
  sprintf(tempStr, "%.2f°C", stats.cpu_temp);
  spr_main.drawString(tempStr, 220, y_pos + 15, TR_DATUM);
  
  // GPU Temperature Details
  y_pos += line_height;
  spr_main.fillRoundRect(10, y_pos, 220, 45, 10, COLOR_CARD_BG);
  spr_main.drawRoundRect(10, y_pos, 220, 45, 10, COLOR_BORDER);
  spr_main.setTextColor(COLOR_TEXT_SECONDARY);
  spr_main.setFreeFont(&FreeSans9pt7b);
  spr_main.drawString("GPU Temperature", 20, y_pos + 10, TL_DATUM);
  spr_main.setTextColor(getColorForTemp(stats.gpu_temp));
  spr_main.setFreeFont(&FreeSansBold18pt7b);
  sprintf(tempStr, "%.2f°C", stats.gpu_temp);
  spr_main.drawString(tempStr, 220, y_pos + 15, TR_DATUM);
  
  // CPU Load Details
  y_pos += line_height;
  spr_main.fillRoundRect(10, y_pos, 220, 45, 10, COLOR_CARD_BG);
  spr_main.drawRoundRect(10, y_pos, 220, 45, 10, COLOR_BORDER);
  spr_main.setTextColor(COLOR_TEXT_SECONDARY);
  spr_main.setFreeFont(&FreeSans9pt7b);
  spr_main.drawString("CPU Load", 20, y_pos + 10, TL_DATUM);
  spr_main.setTextColor(getColorForLoad(stats.cpu_load));
  spr_main.setFreeFont(&FreeSansBold18pt7b);
  sprintf(tempStr, "%.1f%%", stats.cpu_load);
  spr_main.drawString(tempStr, 220, y_pos + 15, TR_DATUM);
  
  // RAM Usage Details
  y_pos += line_height;
  spr_main.fillRoundRect(10, y_pos, 220, 45, 10, COLOR_CARD_BG);
  spr_main.drawRoundRect(10, y_pos, 220, 45, 10, COLOR_BORDER);
  spr_main.setTextColor(COLOR_TEXT_SECONDARY);
  spr_main.setFreeFont(&FreeSans9pt7b);
  spr_main.drawString("RAM Usage", 20, y_pos + 10, TL_DATUM);
  spr_main.setTextColor(getColorForLoad(stats.ram_usage));
  spr_main.setFreeFont(&FreeSansBold18pt7b);
  sprintf(tempStr, "%.1f%%", stats.ram_usage);
  spr_main.drawString(tempStr, 220, y_pos + 15, TR_DATUM);
  
  // Back button
  Button btnBack = {10, 280, 220, 30, "Back"};
  drawButton(btnBack, false);
  
  spr_main.pushSprite(0, 0);
}

// ==================== DRAW PROGRESS BAR ====================
void drawProgressBar(int16_t x, int16_t y, uint16_t w, uint16_t h, float percent, uint16_t color) {
  // Clamp percent to 0-100
  if (percent > 100) percent = 100;
  if (percent < 0) percent = 0;
  
  // Background
  spr_main.fillRect(x, y, w, h, COLOR_BORDER);
  
  // Progress
  uint16_t fillWidth = (uint16_t)((w - 2) * (percent / 100.0f));
  spr_main.fillRect(x + 1, y + 1, fillWidth, h - 2, color);
  
  // Percentage text
  spr_main.setTextColor(COLOR_TEXT_SECONDARY);
  spr_main.setFreeFont(&FreeSans9pt7b);
  char percentStr[10];
  sprintf(percentStr, "%.0f%%", percent);
  spr_main.drawString(percentStr, x + w + 10, y + h / 2, ML_DATUM);
}

// ==================== DRAW BUTTON ====================
void drawButton(Button& btn, bool hover) {
  uint16_t bgColor = hover ? COLOR_ACCENT : COLOR_CARD_BG;
  uint16_t borderColor = hover ? COLOR_ACCENT : COLOR_BORDER;
  uint16_t textColor = hover ? COLOR_BG : COLOR_TEXT_PRIMARY;
  
  spr_main.fillRoundRect(btn.x, btn.y, btn.w, btn.h, 8, bgColor);
  spr_main.drawRoundRect(btn.x, btn.y, btn.w, btn.h, 8, borderColor);
  
  spr_main.setTextColor(textColor);
  spr_main.setFreeFont(&FreeSans9pt7b);
  spr_main.drawString(btn.label, btn.x + btn.w / 2, btn.y + btn.h / 2, MC_DATUM);
}

// ==================== HANDLE TOUCH ====================
void handleTouch() {
  uint16_t x = 0, y = 0;
  
  // Simple touch detection - check if touch happened
  if (tft.touched()) {
    // Get the touch coordinates from the library
    // Note: exact coordinates depend on your calibration
    tft.getTouch(&x, &y);
    
    Serial.printf("Touch: X=%d, Y=%d\n", x, y);
    
    if (showDetailsScreen) {
      // Check Back button (10, 280, 220, 30)
      if (x >= 10 && x <= 230 && y >= 280 && y <= 310) {
        showDetailsScreen = false;
        delay(300);
      }
    } else {
      // Check Details button (10, 280, 110, 30)
      if (x >= btnDetails.x && x <= (btnDetails.x + btnDetails.w) &&
          y >= btnDetails.y && y <= (btnDetails.y + btnDetails.h)) {
        showDetailsScreen = true;
        Serial.println("Details button pressed");
        delay(300);
      }
      
      // Check Refresh button (130, 280, 110, 30)
      if (x >= btnRefresh.x && x <= (btnRefresh.x + btnRefresh.w) &&
          y >= btnRefresh.y && y <= (btnRefresh.y + btnRefresh.h)) {
        fetchStats();
        Serial.println("Refresh button pressed");
        delay(300);
      }
    }
  }
}

// ==================== GET COLOR FOR TEMPERATURE ====================
uint16_t getColorForTemp(float temp) {
  if (temp < 40) return COLOR_SUCCESS;      // Green - Cool
  if (temp < 60) return COLOR_ACCENT_COOL;   // Cyan - Normal
  if (temp < 75) return COLOR_ACCENT_WARM;   // Orange - Warm
  return COLOR_DANGER;                       // Red - Hot
}

// ==================== GET COLOR FOR LOAD ====================
uint16_t getColorForLoad(float load) {
  if (load < 30) return COLOR_SUCCESS;       // Green - Low
  if (load < 60) return COLOR_ACCENT_COOL;   // Cyan - Medium
  if (load < 85) return COLOR_ACCENT_WARM;   // Orange - High
  return COLOR_DANGER;                       // Red - Critical
}
