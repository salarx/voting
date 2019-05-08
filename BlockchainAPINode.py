from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from Blockchain import Blockchain
from sys import argv
from logging import log


# Creating a Web App
app = Flask(__name__)
PORT = argv[1]
# Creating an address for the node on Port 5000
node_address = str(uuid4()).replace('-', '')

currentNodeURl = "http://localhost:" + str(PORT)
# Creating a Blockchain
blockchain = Blockchain()

@app.route("/", methods = ['GET'])
def home():
    return jsonify({'chain' : blockchain.chain, 
    'pendingTransaction': blockchain.pendingTransaction,
    'networkNode' : blockchain.networkNodes})
    # return jsonify({'chain':blockchain.chain, 'networkNodes' : blockchain.networkNodes, 'pendingtransaction' : blockchain.pendingTransaction}), 200

@app.route('/transaction', methods = ['POST'])
def addTransaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all(key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400
    
    index = blockchain.addToPendingTransaction(json)
    response = {'message': 'This transaction will be added to Block '+str(index)}
    return jsonify(response), 201

@app.route('/transaction/broadcast', methods = ['POST'] )
def transactionBroadcast():
    json = request.get_json()
    transaction = blockchain.createNewTransaction(json['amount'], json['sender'], json['receiver'])
    blockchain.addToPendingTransaction(transaction)
    if(len(blockchain.networkNodes)==0):
        return 'empty'
    for node in blockchain.networkNodes:
        requests.post(node + '/transaction', json =json, timeout=0.01 )
    
    return jsonify({'note': 'Transaction created and broadcast successfully.', 
    'pendingTransaction': blockchain.pendingTransaction})

@app.route('/mine', methods = ['GET'])
def mine():
    lastBlock = blockchain.getLastBlock()
    blockData = {
        'transactions' : blockchain.pendingTransaction,
        'index'        : lastBlock['index']+1
        }
    nonce = blockchain.proofOfWork(blockData)
    blockHash = blockchain.hashBlock(blockData, nonce)
    block = blockchain.createBlock(nonce, lastBlock['hash'], blockHash )
    log(1, "block is mined ")
    log(1, "block is being transmitted to peers ")
    for node in blockchain.networkNodes:
        log(1, "the block is transmitted to" + str(node))
        requests.post(node + '/receive-new-block', json={'newBlock' : block})
    

    log(1, "minning fee is being transmitted")
    transaction = {
	    "sender" : '000',
	    "receiver" : node_address, 
	    "amount" : 12.5
    }
    transaction = blockchain.createNewTransaction(transaction['amount'], transaction['sender'], transaction['receiver'])
    blockchain.addToPendingTransaction(transaction)

    for node in blockchain.networkNodes:
        requests.post( node + '/transaction', json=transaction)

    
    # r=requests.post( currentNodeURl + '/transaction/broadcast', json=transaction)
    response = {'message': 'Congratulations, you just mined a block!',
                'block': block}

    log(1, "minning completed successfully")
    return jsonify(response), 200

@app.route('/receive-new-block', methods = ['POST'] )
def receiveNewBlock():
    json = request.get_json()
    newBlock = json['newBlock']
    lastBlock = blockchain.getLastBlock()
    correctHash = lastBlock['hash']==newBlock['previousBlockHash']
    correctIndex = lastBlock['index']+1 ==newBlock['index']
    if(correctHash and correctIndex):
        blockchain.chain.append(newBlock)
        blockchain.pendingTransaction = []
        return jsonify({
			'note': 'New block received and accepted.',
			'newBlock': newBlock
		})
    else:
        return jsonify({
			'note': 'New block received and rejected.',
			'newBlock': newBlock
		})



@app.route('/register-node/broadcast', methods = ['POST'])
def registerBroadcastNode():
    json = request.get_json()
    newNode = json['newNode']
    
    if(newNode==currentNodeURl):
        return "current node cannot be added"
    if(blockchain.networkNodes.__contains__(newNode)):
        return "already exist"
    
    blockchain.addNode(newNode)

    for node in blockchain.networkNodes:
        requests.post(node + '/register-node', json={'newNode' : newNode})
      
    allNetworkNodes = blockchain.networkNodes
    allNetworkNodes.append(currentNodeURl)
    requests.post(newNode + '/register-bulk-nodes', json={'allNetworkNodes' : allNetworkNodes })

    allNetworkNodes.remove(currentNodeURl)
    
    response = {'message': 'All the nodes are now connected. The Blockchain now contains the following nodes:',
               'total_nodes': list(blockchain.networkNodes)}
    return jsonify(response), 201

@app.route('/register-node', methods = ['POST'])
def registerNode():
    json = request.get_json()
    node = json['newNode']
    if(node==currentNodeURl):
        return "current node cannot be added"
    elif(blockchain.networkNodes.__contains__(node)):
        return "already exist"
    else:
        blockchain.addNode(node)
        return jsonify({ 'note': 'New node registered successfully.' })

    
@app.route('/register-bulk-nodes', methods = ['POST'])
def registerBulkNodes():
    allNodes = request.get_json()['allNetworkNodes']
    for node in allNodes:
        if( not blockchain.networkNodes.__contains__(node) ):
            if(node!=currentNodeURl):
                blockchain.addNode(node)
    
    return jsonify({'note' : "bulk registration successfull"}), 200

@app.route('/consensus', methods = ['GET'])
def consensus():
    allBlcockchain = []
    currentChainlen=len(blockchain.chain)
    maxLen  = currentChainlen
    bestChain = []
    newPendingTransaction = []
    for node in blockchain.networkNodes:
        r= requests.get(node + '/')
        allBlcockchain.append(r.json())
    for block in allBlcockchain:
        if True:
            if(len(block['chain'])>maxLen):
                maxLen = len(block['chain'])
                bestChain = block['chain']
                newPendingTransaction = block['pendingTransaction']
    
    if  blockchain.isChainValid(bestChain) and len(bestChain) :
        blockchain.chain = bestChain
        blockchain.pendingTransaction = newPendingTransaction
        return jsonify({'message' : 'This chain has been replaced ','chain' : bestChain})
    else:
        return jsonify({'all' : bestChain, 'best': blockchain.isChainValid(bestChain)})    
    



app.run(host = '0.0.0.0', port = int(PORT))