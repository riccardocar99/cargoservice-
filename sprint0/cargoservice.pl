%====================================================================================
% cargoservice description   
%====================================================================================
request( load, load(CLIENT_ID) ).
reply( reserved, reserved(SLOT) ).  %%for load
reply( retrylater, retrylater(REASON) ).  %%for load
reply( reject, reject(REASON) ).  %%for load
dispatch( distance, distance(D) ).
request( move_robot, move_robot(DEST) ).
reply( move_done, move_done(RESULT) ).  %%for move_robot
dispatch( start_marking, start_marking(SLOT) ).
dispatch( marking_done, marking_done(SLOT) ).
dispatch( led_state, led_state(STATE) ).
dispatch( display_msg, display_msg(MSG) ).
%====================================================================================
context(ctx_cargoservice, "localhost",  "TCP", "8082").
 qactor( cargoservice, ctx_cargoservice, "it.unibo.cargoservice.Cargoservice").
 static(cargoservice).
  qactor( cargorobot, ctx_cargoservice, "it.unibo.cargorobot.Cargorobot").
 static(cargorobot).
  qactor( customer, ctx_cargoservice, "it.unibo.customer.Customer").
 static(customer).
  qactor( sonar, ctx_cargoservice, "it.unibo.sonar.Sonar").
 static(sonar).
  qactor( led, ctx_cargoservice, "it.unibo.led.Led").
 static(led).
  qactor( marker, ctx_cargoservice, "it.unibo.marker.Marker").
 static(marker).
  qactor( ioport, ctx_cargoservice, "it.unibo.ioport.Ioport").
 static(ioport).
