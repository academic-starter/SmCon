echo  "analyze MoonCatRescue 0x60cd862c9c687a9de49aecdc3a99b74a4fc54ab6"
python3 -m invconplus.main --address 0x60cd862c9c687a9de49aecdc3a99b74a4fc54ab6 --configuration ./result/0x60cd862c9c687a9de49aecdc3a99b74a4fc54ab6-MoonCatRescue-config.json --maxCount 2000 >> MoonCatResuce.log 2>&1 


echo "mine MoonCatRescue automata 0x60cd862c9c687a9de49aecdc3a99b74a4fc54ab6"
python3 -m invconplus.core.ConMiner ./result 0x60cd862c9c687a9de49aecdc3a99b74a4fc54ab6 MoonCatRescue ./result/0x60cd862c9c687a9de49aecdc3a99b74a4fc54ab6-MoonCatRescue.inv.json ./result/0x60cd862c9c687a9de49aecdc3a99b74a4fc54ab6-MoonCatRescue-config.json ./result/0x60cd862c9c687a9de49aecdc3a99b74a4fc54ab6-MoonCatRescue-trace_slices.json >> MoonCatResuce.log 2>&1

