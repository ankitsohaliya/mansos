//pattern P [900,300,900];       // miliseconds
//pattern Q [900us,300us,900us]; // microseconds
//use RedLed, pattern P;
//use Bar, pattern Q;

//define Params, param1 1000, param2 1s, param3 1500ms;
//use Foobar, parameters Params;
//a;

//read Light, period 2s;
// read Humidity, period 3s;
// output Serial, baudrate 38400, aggregate;
// output Radio;

when Humidity.value > 100:
     // Note: "Humidity" is synonym to "Humidity.value"!
     use Print, once, format "Humidity > 100, value=%d\n", arg1 Humidity;
end

when Humidity.isError:
     use Print, once, format "Humidity sensor failed!\n";
end