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
dispatch( setrobotstate, setpos(X,Y,D) ).
dispatch( start_marking, start_marking(SLOT) ).
dispatch( marking_done, marking_done(SLOT) ).
dispatch( led_state, led_state(STATE) ).
dispatch( display_msg, display_msg(MSG) ).
event( alarm, alarm(X) ).
dispatch( distance_event, distance_event(D) ).
%====================================================================================
context(ctx_cargoservice, "localhost",  "TCP", "8082").
context(ctxrobotsmart, "127.0.0.1",  "TCP", "8020").
 qactor( robotsmart, ctxrobotsmart, "external").
  qactor( cargoservice, ctx_cargoservice, "it.unibo.cargoservice.Cargoservice").
 static(cargoservice).
  qactor( cargorobot, ctx_cargoservice, "it.unibo.cargorobot.Cargorobot").
 static(cargorobot).
  qactor( sonar, ctx_cargoservice, "it.unibo.sonar.Sonar").
 static(sonar).
  qactor( led, ctx_cargoservice, "it.unibo.led.Led").
 static(led).
  qactor( marker, ctx_cargoservice, "it.unibo.marker.Marker").
 static(marker).
  qactor( ioport, ctx_cargoservice, "it.unibo.ioport.Ioport").
 static(ioport).
