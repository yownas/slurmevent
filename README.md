# slurmevent
Simple server/client to let users get events from the slurmctld.log

# Usage:

Start a server on the controlhost: ```slurmeventd```

Users can connect and wait for a job to start: ```slurmevent -r 12345```
