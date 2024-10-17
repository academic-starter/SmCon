nvm install v10.24.1 && npm use v10.24.1
cd contracts && npm install  
npm i -D @types/node@latest && npm run build
npm run test 
# change truffle.js {solc: "^0.8.11",} to {solc: "0.8.11",}
# create an another terminal to setup ganache-cli testrpc
ganache-cli -e=1000 --mnemonic "test"