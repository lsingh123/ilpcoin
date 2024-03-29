#!usr/bin/env python3

from ilpcoin.common.blockchain import Block, Transaction
from ilpcoin.common.constants import HARDNESS, PORT, QUEUE_HOST, QUEUE_PORT, HOST
from ilpcoin.common.ilp import Ilp, IlpSolution
import requests
import random
from typing import List, Optional
import uuid
import pickle
from time import sleep

class InvalidResponseError(Exception):
    '''Raised when this miner received a response to a web request that it cannot deal with.'''
    pass

class ClientPeer:
    '''Represents a miner. 
    
    Does not contain any important state; simply wraps the mining routine.'''

    def __init__(self, host="localhost", id:int=0, buggy:bool=False) -> None:
        '''Initialize the miner state.'''
        self.host = host
        self.port:str = str(8000 + id)
        self.id:str = str(id)
        self.reset_neighbors(5)
        self.buggy = buggy # for testing

    def reset_neighbors(self, n) -> None:
        '''Clear a stale list of neighbors.'''
        self.neighbors = self.get_n_neighbors(n)

    def get_n_neighbors(self, n:int) -> List[str]:
        '''Query the queue for n verifiers. '''
        url = f"http://{QUEUE_HOST}:{QUEUE_PORT}/get_neighbors/{n}"
        r = requests.get(url)
        if r.status_code != 200:
            raise InvalidResponseError("No neighbors found.")
        neighbors = pickle.loads(r.content)
        return neighbors

    def start_mine(self):
        '''Run the mining routine forever.'''
        while True:
            r = requests.get(f"http://{QUEUE_HOST}:{QUEUE_PORT}/get_top_ilp")
            ilp_text = r.text
            ilp = Ilp.deserialize_s(ilp_text) 
            neighbors_valid = False
            neighbor_port = None
            while not neighbors_valid:
                neighbor = random.choice(self.neighbors)
                neighbor_port = PORT + int(neighbor)
                url = f"http://{HOST}:{neighbor_port}/get_previous"
                r = requests.get(url)

                print(f"get_previous status code {r.status_code}")
                if r.status_code == 200:
                    neighbors_valid = True
                sleep(1)

            previous_block_text = r.content
            prev_block: Block = Block().deserialize(previous_block_text)
            prev_ilp_id = prev_block.ILP
            top_ilp_id = ilp.uid

            # print(f"Top ILP has ID {top_ilp_id} and prev block has id {prev_ilp_id}")
            if prev_ilp_id != top_ilp_id - 1:
                continue

            solved_ilp = ilp.solve()
            if solved_ilp is None:
                continue
            
            prev_hash = prev_block.hash()
            transaction = Transaction(self.id, self.id, 5)
            new_block = Block([transaction], str(prev_hash))
            new_block.ILP = ilp.get_id()
            new_block.ILP_solution = solved_ilp
            mx = 2 ** 32 - 1
            while True and not self.buggy:
                new_block.nonce = random.randrange(mx)
                if new_block.validate_nonce(HARDNESS):
                    break

            url = f"http://{HOST}:{neighbor_port}/send_block/{self.id}"
            print(f"about to post to {url}")
            '''payload = {
                "block": new_block.serialize()
            }'''
            headers = {"Content-Type":"application/binary",}
            r = requests.put(url, data=new_block.serialize(),headers=headers)

            print(f"sent a block w code {r.status_code}")

    """
    def broadcast_transaction(self, Transaction):
        payload = Transaction.serialize()
        for neighbor in self.neighbors:
            url = self.host + ":" + str(neighbor) + "/send_transaction"
            requests.post(url, data=payload)
    
    def broadcast_block(self, Block):
        payload = Block.serialize()
        for neighbor in self.neighbors:
            url = self.host + ":" + neighbor + "/send_block"
            requests.post(url, data=payload)
    """


        




