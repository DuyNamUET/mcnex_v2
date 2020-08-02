void setup() {
  Serial.begin(9600);

}

void loop()
{
  char cmd = '1';
  Serial.println(cmd);
  delay(1000);
}
