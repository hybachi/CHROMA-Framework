# SwarmStatus.msg
# Provides distributed swarm awareness to allow dynamic adaptation

std_msgs/Header header      
string robot_id             
string robot_type           
Capability[] capabilities   
string latest_rejection_reason