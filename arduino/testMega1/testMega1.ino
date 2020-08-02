/*
 *  Code for Mega1
 *  Control Pump, Servo and Reset Mega2
 */

enum state_machine {HOME, READY, RUNNING, STOP};

String receive_from_pi();
String receive_from_mega();
void state_machine_mega1(String cmd);
void convert_to_data(String cmd, int data[]);
void run_pump();
void run_servo();

uint8_t state = HOME;

void setup()
{
  Serial.begin(9600);
  Serial1.begin(9600);
}

void loop()
{
  String pi_cmd = "";
  pi_cmd = receive_from_pi();
  if(pi_cmd == "stop")
  {
    state = STOP;
  }
  state_machine_mega1(mega_cmd);
}

String receive_from_pi(){}
String receive_from_mega(){}
void state_machine_mega1()
{
  switch(state)
  {
    case HOME:
      Serial1.print("home");
      if(receive_from_mega() == "done") state = READY;
      break;
    case READY:
      Serial.println("get_data.");
      String cmd = receive_from_pi();
      if(cmd != "")
      {
        convert_to_data(cmd, data);
        Serial1.println("running.");
        state = RUNNING;
      }
      break;
    case RUNNING:
      mega_cmd = receive_from_mega()
      if(mega_cmd == "done") state = HOME;
      else if (mega_cmd == "servo") run_servo();
      else if (mega_cmd == "pump") run_pump();
      break;
    case STOP:
      if(receive_from_mega() == "home") state = HOME;
      break;
  }
}

void convert_to_data(String cmd, int data[]){}
void run_servo(){}
void run_pump(){}