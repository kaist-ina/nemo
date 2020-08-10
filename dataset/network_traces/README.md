## Network traces 

NEMO evaluated adaptive streaming based on network traces given by Pensieve [1], where each trace is either measured on Norway’s 3G network [2] or U.S. broadband network [3].

Among 952 network traces, we filter out the traces whose average bandwidth is higher than 4.4 Mbps to avoid cases where adaptive streaming does not deliver any benefits; the number of traces we used is 892.

In `network_traces.zip`, network traces for training (692), validation (200 sampled from training), and testing (200) are provided at `train`, `validation`, and `test` respectively.



[1] Hongzi Mao, Ravi Netravali, and Mohammad Alizadeh. 2017. Neural Adaptive Video Streaming with Pensieve. In Proceedings of the ACM Special Interest Group on Data Communication (SIGCOMM). 197–210.

[2] RIISER, H., VIGMOSTAD, P., GRIWODZ, C., AND HALVORSEN, P. Commute path bandwidth traces from 3g networks: analysis and applications. In Proceedings of the ACM Multimedia Systems Conference (MMSys) (2013), pp. 114–118

[3] https://www.fcc.gov/reports-research
