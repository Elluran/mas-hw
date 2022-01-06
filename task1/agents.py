import time
import asyncio
import random
import requests
import os
import logging
from spade import agent, quit_spade
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message
from spade.template import Template
from aioxmpp import PresenceShow, PresenceState
from spade.behaviour import FSMBehaviour, State

host = os.environ.get('DOMAIN')
jabber_host = os.environ.get('JABBER')

STATE_ONE = "STATE_ONE"
STATE_TWO = "STATE_TWO"
STATE_THREE = "STATE_THREE"
STATE_FOUR = "STATE_FOUR"

red_verts = set()
grey_verts = set()
answer = "?"


class StateOne(State):
    async def run(self):
        num = int(self.agent.name[5:])
        for i in range(0, self.agent.N):
            if self.agent.topology[num][i]:
                self.agent.presence.subscribe(f"smith{i}@{jabber_host}")

        await asyncio.sleep(1)
        
        if self.agent.name == "smith0":
            self.agent.compute = True
            self.set_next_state(STATE_THREE)
            return
        self.set_next_state(STATE_TWO)


class StateTwo(State):
    async def run(self):
        while not self.agent.compute:
            await asyncio.sleep(1)
        
        self.set_next_state(STATE_THREE)


class StateThree(State):
    async def run(self):
        red_verts.add(self.agent.name[5:])
        if self.agent.name == "smith0":
            await asyncio.sleep(10)
        for contact in self.agent.presence.get_contacts():
            contact = str(contact)

            contact_id = int(contact.split('@')[0][5:])

            
            if contact_id >= self.agent.N:
                continue

            self.id = int(self.agent.name[5:])
            if not self.agent.topology[contact_id][self.id]:
                continue

            if contact == str(self.agent.sender):
                continue
            
            if str(contact) + "/resource" == self.agent.sender:
                print(self.agent.sender, str(contact) + "/resource")
                continue

            await asyncio.sleep(random.uniform(0, 0.2))

            

            msg = Message(to=contact)
            msg.set_metadata("compute", "compute")  
            msg.body = "compute"                   
            msg.to = str(contact) + "/resource"

            await asyncio.sleep(random.uniform(0, 0.2))
            
            await self.send(msg)
            print("1Message sent! to ", str(contact) + "/resource", "from ", self.agent.name)

            msg = await self.receive(timeout=5)

            while msg and msg.body == "Not okay":
                msg = await self.receive(timeout=5)

            if msg and msg.body == "Okay":
                self.agent.agents += 1


        self.set_next_state(STATE_FOUR)

class StateFour(State):
    async def run(self):
        print("STATE_FOUR", self.agent.name)
        self.agent.result += self.agent.number
        while self.agent.agents != 0:
            await asyncio.sleep(1)
        
        if str(self.agent.sender) != "":
            msg = Message(to=str(self.agent.sender)) 
            msg.set_metadata("number", "number")  
            msg.body = "number " + str(self.agent.result)                  
            msg.to = str(self.agent.sender)

            await self.send(msg)
            self.agent.agents += 1

        requests.get(f'http://{host}:5000/update_vert/' + str(self.agent.name[5:]) + "/" + str(self.agent.result))

        if self.agent.name == "smith0":
            print("Answer:", self.agent.result / self.agent.N)
            global answer
            answer = self.agent.result / self.agent.N
        await asyncio.sleep(0.5)


class myFSMBehaviour(FSMBehaviour):
    async def on_start(self):
        self.agent.sender = ""
        self.agent.agents = 0
        self.agent.compute = False

    async def on_end(self):
        grey_verts.add(self.agent.name[5:])
        await self.agent.stop()


class Reader2(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=3)
        if not self.agent.compute:
            if msg and msg.body == "compute":
                self.agent.sender = msg.sender
                msg = Message(to=str(msg.sender))     
                msg.set_metadata("reply", "reply")  
                msg.body = "Okay"                   
                msg.to = str(self.agent.sender)

                self.agent.compute = True
                await self.send(msg)
        else:
            if msg:
                sender = msg.sender
                msg = Message(to=str(sender))     
                msg.set_metadata("reply", "reply")  
                msg.body = "Not okay"                   
                msg.to = str(sender)

                await self.send(msg)

class Reader(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=3) 
        if msg and msg.body.split()[0] == "number":
            self.agent.result += int(msg.body.split()[1])
            self.agent.agents -= 1


class Agent(agent.Agent):
            
    async def setup(self):
        self.fsm = myFSMBehaviour()
        self.fsm.add_state(name=STATE_ONE, state=StateOne(), initial=True)
        self.fsm.add_state(name=STATE_TWO, state=StateTwo())
        self.fsm.add_state(name=STATE_THREE, state=StateThree())
        self.fsm.add_state(name=STATE_FOUR, state=StateFour())
        self.fsm.add_transition(source=STATE_ONE, dest=STATE_TWO)
        self.fsm.add_transition(source=STATE_TWO, dest=STATE_THREE)
        self.fsm.add_transition(source=STATE_ONE, dest=STATE_THREE)
        self.fsm.add_transition(source=STATE_THREE, dest=STATE_FOUR)
        template1 = Template()
        template1.set_metadata("reply", "reply")
        template1.to = str(self.jid)
        self.add_behaviour(self.fsm, template1)
        # 
        
        reader = Reader()
        template2 = Template()
        template2.set_metadata("number", "number")
        template2.to = str(self.jid)

        self.add_behaviour(reader, template2)
        # 

        reader2 = Reader2()
        template3 = Template()
        template3.set_metadata("compute", "compute")
        template3.to = str(self.jid)

        self.add_behaviour(reader2, template3)

    
    def configure(self, number, N, topology):
        self.number = number
        self.topology = topology
        self.N = N
        self.waiting = 2
        self.result = 0
        if self.name == "smith0":
            self.waiting = 1
        requests.get(f'http://{host}:5000/update_vert/' + str(self.name[5:]) + "/" + str(number))

def main(N, topology):

    agents = [Agent(f"smith{i}@{jabber_host}/resource", "followthewhiterabbit") for i in range(N)]

    for i in range(N):   
        agents[i].configure(i + 1, N, topology)  
        future = agents[i].start()
        future.result()


    while True and not agents[0].fsm.is_killed():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break


    for i in range(N):   
        agents[i].stop()  
