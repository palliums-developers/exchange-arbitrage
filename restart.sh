#!/bin/bash

sudo docker stop exchange_arbitrage
sudo docker rm exchange_arbitrage
sudo docker image rm exchange_arbitrage
sudo docker image build --no-cache -t exchange_arbitrage .
sudo docker run --name=exchange_arbitrage --network=host -itd exchange_arbitrage