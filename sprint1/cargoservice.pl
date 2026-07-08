%====================================================================================
% cargoservice description   
%====================================================================================
request( load, load(CLIENT_ID) ).
reply( reserved, reserved(SLOT) ).  %%for load
reply( retrylater, retrylater(REASON) ).  %%for load
reply( reject, reject(REASON) ).  %%for load
dispatch( distance, distance(D) ).
dispatch( sonar_ok, sonar_ok(D) ).
dispatch( sonar_fail, sonar_fail(D) ).
request( move_robot, move_robot(DEST) ).
reply( move_done, move_done(RESULT) ).  %%for move_robot
request( moverobot, moverobot(TARGETX,TARGETY,STEPTIME) ).
reply( moverobotdone, moverobotdone(ARG) ).  %%for moverobot
reply( moverobotfailed, moverobotfailed(PLANDONE,PLANTODO) ).  %%for moverobot
dispatch( start_marking, start_marking(SLOT) ).
dispatch( marking_done, marking_done(SLOT) ).
dispatch( led_state, led_state(STATE) ).
dispatch( display_msg, display_msg(MSG) ).
%====================================================================================
context(ctx_cargoservice, "localhost",  "TCP", "8082").
context(ctx_gui, "localhost",  "TCP", "8083").
context(ctx_picow, "localhost",  "TCP", "8084").
context(ctxrobotsmart, "127.0.0.1",  "TCP", "8020").
 qactor( robotsmart, ctxrobotsmart, "external").
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
