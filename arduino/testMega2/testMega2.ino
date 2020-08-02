/*
 *  Code for Mega2.
 *  Control Stepper motor
 */

enum state_machine {HOME, READY, RUNNING, STOP};

String receive_from_mega();
void state_machine_mega();
void go_home();

uint8_t state = STOP;

void setup()
{
  Serial1.begin(9600);
}

void loop()
{
  String cmd = receive_from_mega();
  if(cmd == "home") state = HOME;
  state_machine_mega2();
}

String receive_from_mega(){}
void state_machine_mega2()
{
  switch(state)
  {
    case HOME:
      go_home();
  }
}

void go_home(){}
