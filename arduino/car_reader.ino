#include <Wire.h>

typedef struct _rc_map {
  int pin;
  int on;
  char name[32];
} rc_map_t;

#define PIN_RC_FORWARD 3   // YELLOW
#define PIN_RC_BACKWARD 4  // ORANGE
#define PIN_RC_LEFT 5      // WHITE
#define PIN_RC_RIGHT 6     // BLUE

#define N_RC_PINS 4

#define SLAVE_ADDRESS 0x04

static rc_map_t g_rc_map[N_RC_PINS] = {
  { PIN_RC_FORWARD, 0, "PIN_RC_FORWARD" },
  { PIN_RC_BACKWARD, 0, "PIN_RC_BACKWARD" },
  { PIN_RC_LEFT, 0, "PIN_RC_LEFT" },
  { PIN_RC_RIGHT, 0, "PIN_RC_RIGHT" },
};

void setup() {
  
  Serial.begin(9600);
  Wire.begin(SLAVE_ADDRESS);
  Wire.onRequest(sendData);

  for (int i = 0; i < N_RC_PINS; ++i) {
    rc_map_t *rc_map = &g_rc_map[i];
    if (!rc_map) {
      continue;
    }
    pinMode(rc_map->pin, INPUT_PULLUP);
    Serial.print(rc_map->name);
  }
}

void loop() {
  for (int i = 0; i < N_RC_PINS; ++i) {
    rc_map_t *rc_map = &g_rc_map[i];
    if (!rc_map) {
      continue;
    }
    
    int val = digitalRead(rc_map->pin);     // read the input pin 
    rc_map->on = val;
    if (val != 0) {
      Serial.println(rc_map->name);             // debug value
    }
  }
  delay(10);
}

void sendData() {
  int d = 0;
  for (int i = 0; i < N_RC_PINS; ++i) {
    rc_map_t *rc_map = &g_rc_map[i];
    if (!rc_map) {
      continue;
    }
    if (rc_map->on) {
      d |= 1UL << i;
    }
  }
  Wire.write(d);
}

