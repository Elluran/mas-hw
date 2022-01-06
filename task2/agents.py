import time
import random
import json
import asyncio
import requests
import os
from spade import agent, quit_spade
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message
from spade.template import Template
from aioxmpp import PresenceShow, PresenceState
from spade.behaviour import FSMBehaviour, State

host = os.environ.get('DOMAIN')
jabber_host = os.environ.get('JABBER')
PORT = os.environ.get('PORT')

red_edges = set()
green_edges = set()


class Sender(CyclicBehaviour):
    async def on_start(self):
        await asyncio.sleep(5)
        num = int(self.agent.name[5:])
        for i in range(0, self.agent.N):
            if self.agent.topology[num][i]:
                self.agent.presence.subscribe(f"smith{i}@{jabber_host}")

    async def run(self):
        for contact in self.agent.presence.get_contacts():
            contact = str(contact)

            contact_id = int(contact.split('@')[0][5:])
      
            if contact_id >= self.agent.N:
                continue

            
            if not self.agent.topology[self.agent.id][contact_id]:
                continue
            
            edge = f"n{contact_id}n{self.agent.id}"

            if random.choices([True, False], [self.agent.loss_prob, 1 - self.agent.loss_prob])[0]:
                red_edges.add(edge)
                if edge in green_edges:
                    green_edges.remove(edge)
                await asyncio.sleep(0.05)
                continue
            if edge in red_edges:
                red_edges.remove(edge)
            green_edges.add(edge)

            msg = Message()
            msg.set_metadata("number", "number")  
            msg.to = str(contact) + "/resource2"
            noise = self.agent.noise_distribution
            msg.body = "number " + str(self.agent.number + random.uniform(-noise, noise))                  

            
            await self.send(msg)
            await asyncio.sleep(0.05)

            resp = requests.get(f'http://{host}:{PORT}/get_parameters')
            if resp.json()['stop']:
                await self.agent.stop()

class Reader(CyclicBehaviour):
    async def run(self):
        resp = requests.get(f'http://{host}:{PORT}/get_parameters')
        if resp.json()['stop']:
            await self.agent.stop()


        msg = await self.receive(timeout=3) 
        if msg and msg.body.split()[0] == "number":
            num = float(msg.body.split()[1])
            if random.choices([True, False], [self.agent.delay_prob, 1 - self.agent.delay_prob])[0]:
                await asyncio.sleep(0.5)
                msg = Message()
                msg.set_metadata("number", "number")  
                msg.to = str(self.agent.jid) + "/resource2"
                msg.body = "number " + str(num)                  
                await self.send(msg)
            else:
                self.agent.number += self.agent.alpha * (num - self.agent.number)

        requests.get(f'http://{host}:{PORT}/update_vert/{self.agent.id}/{self.agent.number}')

class Agent(agent.Agent):
            
    async def setup(self):
        reader = Reader()
        template = Template()
        template.set_metadata("number", "number")
        template.to = str(self.jid)
        self.add_behaviour(reader, template)


        self.sender = Sender()
        self.add_behaviour(self.sender)

    
    def configure(self, number, N, topology):
        self.number = number
        self.topology = topology
        self.id = int(self.name[5:])
        resp = requests.get(f'http://{host}:{PORT}/get_parameters')
        self.alpha = resp.json()['alpha']
        self.noise_distribution = resp.json()['noise']
        self.loss_prob = resp.json()['prob']
        self.delay_prob = resp.json()['delay']
        self.N = N

        requests.get(f'http://{host}:{PORT}/update_vert/' + str(self.name[5:]) + "/" + str(number))

def main(N, topology):
    global red_edges
    global green_edges

    agents = [Agent(f"smith{i}@{jabber_host}/resource2", "followthewhiterabbit") for i in range(N)]

    for i in range(N):   
        agents[i].configure(i + 1, N, topology)  
        future = agents[i].start()
        future.result()


    while True and not agents[0].sender.is_killed():
        try:
            time.sleep(0.5)
            
            data = {
                'red' : list(red_edges),
                'green' : list(green_edges)
            }
            requests.post(f"http://{host}:{PORT}/redgreen", json=data)
            red_edges = set()
            green_edges = set()

        except KeyboardInterrupt:
            break

    for i in range(N):   
        requests.get(f'http://{host}:{PORT}/update_vert/' + str(i) + "/0")
        agents[i].stop()  

    red_edges = set()
    green_edges = set()
    data = {
                'red' : list(red_edges),
                'green' : list(green_edges)
            }
    requests.post(f"http://{host}:{PORT}/redgreen", json=data)