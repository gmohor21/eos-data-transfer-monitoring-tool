#!/bin/bash

#!/bin/bash

for instance in `cat instances.txt`
do
   session=$instance-kpi
   tmux new-session -d -s $session
   tmux send-keys "time ./replay_historical_data.sh  --instance $instance --year 2022" C-m
   tmux detach -s $session
done

