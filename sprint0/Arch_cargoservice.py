### conda install diagrams
from diagrams import Cluster, Diagram, Edge
from diagrams.custom import Custom
import os
os.environ['PATH'] += os.pathsep + 'C:/Program Files/Graphviz/bin/'

graphattr = {     #https://www.graphviz.org/doc/info/attrs.html
    'fontsize': '22',
}

nodeattr = {   
    'fontsize': '22',
    'bgcolor': 'lightyellow'
}

eventedgeattr = {
    'color': 'red',
    'style': 'dotted'
}
evattr = {
    'color': 'darkgreen',
    'style': 'dotted'
}
with Diagram('cargoserviceArch', show=False, outformat='png', graph_attr=graphattr) as diag:
  with Cluster('env'):
     sys = Custom('','./qakicons/system.png')
### see https://renenyffenegger.ch/notes/tools/Graphviz/attributes/label/HTML-like/index
     with Cluster('ctx_cargoservice', graph_attr=nodeattr):
          cargoservice=Custom('cargoservice','./qakicons/symActorWithobjSmall.png')
          cargorobot=Custom('cargorobot','./qakicons/symActorWithobjSmall.png')
          marker=Custom('marker','./qakicons/symActorWithobjSmall.png')
     with Cluster('ctx_gui', graph_attr=nodeattr):
          ioport=Custom('ioport','./qakicons/symActorWithobjSmall.png')
     with Cluster('ctx_picow', graph_attr=nodeattr):
          sonar=Custom('sonar','./qakicons/symActorWithobjSmall.png')
          led=Custom('led','./qakicons/symActorWithobjSmall.png')
     cargoservice >> Edge(color='magenta', style='solid', decorate='true', label='<move_robot<font color="darkgreen"> move_done</font> &nbsp; >',  fontcolor='magenta') >> cargorobot
     marker >> Edge(color='blue', style='solid',  decorate='true', label='<marking_done &nbsp; >',  fontcolor='blue') >> cargoservice
     sonar >> Edge(color='blue', style='solid',  decorate='true', label='<sonar_data &nbsp; >',  fontcolor='blue') >> cargoservice
     cargoservice >> Edge(color='blue', style='solid',  decorate='true', label='<start_marking &nbsp; >',  fontcolor='blue') >> marker
     cargoservice >> Edge(color='blue', style='solid',  decorate='true', label='<display_update &nbsp; >',  fontcolor='blue') >> ioport
     cargoservice >> Edge(color='blue', style='solid',  decorate='true', label='<led_cmd &nbsp; >',  fontcolor='blue') >> led
diag
