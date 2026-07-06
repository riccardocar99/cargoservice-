%====================================================================================
% cargoservice description   
%====================================================================================
request( load, load(CLIENT_ID) ).
reply( reserved, reserved(SLOT) ).  %%for load
reply( retrylater, retrylater(REASON) ).  %%for load
reply( reject, reject(REASON) ).  %%for load
dispatch( sonar_data, sonar_data(D) ).
dispatch( sonar_ok, sonar_ok(D) ).
dispatch( sonar_fail, sonar_fail(D) ).
request( move_robot, move_robot(DEST) ).
reply( move_done, move_done(RESULT) ).  %%for move_robot
dispatch( start_marking, start_marking(SLOT) ).
dispatch( marking_done, marking_done(SLOT) ).
dispatch( led_cmd, led_cmd(CMD) ).
dispatch( display_update, display_update(STATE) ).
%====================================================================================
context(ctx_cargoservice, "localhost",  "TCP", "8082").
context(ctx_gui, "localhost",  "TCP", "8083").
context(ctx_picow, "localhost",  "TCP", "8084").
 qactor( cargoservice, ctx_cargoservice, "it.unibo.cargoservice.Cargoservice").
 static(cargoservice).
  qactor( cargorobot, ctx_cargoservice, "it.unibo.cargorobot.Cargorobot").
 static(cargorobot).
  qactor( sonar, ctx_picow, "it.unibo.sonar.Sonar").
 static(sonar).
  qactor( led, ctx_picow, "it.unibo.led.Led").
 static(led).
  qactor( marker, ctx_cargoservice, "it.unibo.marker.Marker").
 static(marker).
  qactor( ioport, ctx_gui, "it.unibo.ioport.Ioport").
 static(ioport).
