// use 64-bit counter
config "USE_LONG_LIFETIME=y";
config "CONST_CONDITION_EVALUATION_INTERVAL=10000";
config "CONST_RADIO_CHIP=RADIO_CHIP_AMB8420";

const ADC_INTERNAL_VOLTAGE 11;

// define red led to blink
define HelperLed RedLed, blink;

define Battery AnalogIn, channel ADC_INTERNAL_VOLTAGE;

// define light sensor
when Variables.localAddress != 0x0796:
    define MyLight Light;
else:
    define MyLight SQ100Light;
end

// alternative: define light sensor
//define TheLight Light;
//define MyHumidity Humidity, associate HelperLed, turnOnOff;

// define all sensors to read
define AllSensors sync(MyLight, Humidity, Temperature, Battery);

// define our action
read AllSensors, period 10min, associate HelperLed, turnOnOff;

// define our outputs
output SdCard;
output Network, protocol SAD, routing SAD;
output Serial;