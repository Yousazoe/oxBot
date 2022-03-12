import random

from sc2.bot_ai import BotAI  # parent class we inherit from
from sc2.data import Difficulty, Race
from sc2.ids.unit_typeid import UnitTypeId  # difficulty for bots, race for the 1 of 3 races
from sc2.main import run_game  # function that facilitates actually running the agents in games
from sc2.player import Bot, Computer  #wrapper for whether or not the agent is one of your bots, or a "computer" player
from sc2 import maps  # maps method for loading maps to play in.
from sc2.ids.unit_typeid import UnitTypeId

class IncrediBot(BotAI): # inhereits from BotAI (part of BurnySC2)
    async def on_step(self, iteration: int): # on_step is a method that is called every step of the game.
        print(f"{iteration}, n_workers: {self.workers.amount}, n_idle_workers: {self.workers.idle.amount},",
              f"minerals: {self.minerals}, gas: {self.vespene}, cannons: {self.structures(UnitTypeId.PHOTONCANNON).amount},",
              f"pylons: {self.structures(UnitTypeId.PYLON).amount}, nexus: {self.structures(UnitTypeId.NEXUS).amount}",
              f"gateways: {self.structures(UnitTypeId.GATEWAY).amount}, cybernetics cores: {self.structures(UnitTypeId.CYBERNETICSCORE).amount}",
              f"stargates: {self.structures(UnitTypeId.STARGATE).amount}, voidrays: {self.units(UnitTypeId.VOIDRAY).amount}, supply: {self.supply_used}/{self.supply_cap}")

        # begin logic:

        await self.distribute_workers() # put idle workers back to work

        if self.townhalls:  # do we have a nexus?
            nexus = self.townhalls.random  # select one (will just be one for now)

            if self.structures(UnitTypeId.VOIDRAY).amount < 10 and self.can_afford(UnitTypeId.VOIDRAY):
                for sg in self.structures(UnitTypeId.STARGATE).ready.idle:
                    sg.train(UnitTypeId.VOIDRAY)


            supply_remaining = self.supply_cap - self.supply_used

            if nexus.is_idle and self.can_afford(UnitTypeId.PROBE) and supply_remaining > 4:
                nexus.train(UnitTypeId.PROBE)  # train a probe


            # if we dont have *any* pylons, we'll build one close to the nexus.
            elif not self.structures(UnitTypeId.PYLON) and self.already_pending(UnitTypeId.PYLON) == 0:
                if self.can_afford(UnitTypeId.PYLON):
                    await self.build(UnitTypeId.PYLON, near=nexus)


            elif self.structures(UnitTypeId.PYLON).amount < 5:
                if self.can_afford(UnitTypeId.PYLON):
                    # build from the closest pylon towards the enemy
                    target_pylon = self.structures(UnitTypeId.PYLON).closest_to(self.enemy_start_locations[0])
                    # build as far away from target_pylon as possible:
                    pos = target_pylon.position.towards(self.enemy_start_locations[0], random.randrange(8, 15))
                    await self.build(UnitTypeId.PYLON, near=nexus)

            elif self.structures(UnitTypeId.ASSIMILATOR).amount < 2:
                vespenes = self.vespene_geyser.closer_than(15, nexus)
                for vespene in vespenes:
                    if self.can_afford(UnitTypeId.ASSIMILATOR) and not self.already_pending(UnitTypeId.ASSIMILATOR):
                        await self.build(UnitTypeId.ASSIMILATOR, vespene)


            elif not self.structures(UnitTypeId.FORGE):  # if we don't have a forge:
                if self.can_afford(UnitTypeId.FORGE):  # and we can afford one:
                    # build one near the Pylon that is closest to the nexus:
                    await self.build(UnitTypeId.FORGE, near=self.structures(UnitTypeId.PYLON).closest_to(nexus))

            # if we have less than 3 cannons, let's build some more if possible:
            elif self.structures(UnitTypeId.FORGE).ready and self.structures(UnitTypeId.PHOTONCANNON).amount < 3:
                if self.can_afford(UnitTypeId.PHOTONCANNON):  # can we afford a cannon?
                    await self.build(UnitTypeId.PHOTONCANNON, near=nexus)  # build one near the nexus


            buildings = [UnitTypeId.GATEWAY, UnitTypeId.CYBERNETICSCORE, UnitTypeId.STARGATE]
            for building in buildings:
                if not self.structures(building) and self.already_pending(building) == 0:
                    if self.can_afford(building):
                        await self.build(building, near=self.structures(UnitTypeId.PYLON).closest_to(nexus))
                    break



            '''# a gateway? this gets us towards cyb core > stargate > void ray
            elif not self.structures(UnitTypeId.GATEWAY):
                if self.can_afford(UnitTypeId.GATEWAY):
                    await self.build(UnitTypeId.GATEWAY, near=self.structures(UnitTypeId.PYLON).closest_to(nexus))

            # a cyber core? this gets us towards stargate > void ray
            elif not self.structures(UnitTypeId.CYBERNETICSCORE):
                if self.can_afford(UnitTypeId.CYBERNETICSCORE):
                    await self.build(UnitTypeId.CYBERNETICSCORE, near=self.structures(UnitTypeId.PYLON).closest_to(nexus))

            # a stargate? this gets us towards void ray
            elif not self.structures(UnitTypeId.STARGATE):
                if self.can_afford(UnitTypeId.STARGATE):
                    await self.build(UnitTypeId.STARGATE, near=self.structures(UnitTypeId.PYLON).closest_to(nexus))'''



        else:
            if self.can_afford(UnitTypeId.NEXUS):  # can we afford one?
                await self.expand_now()  # build one!


        if self.units(UnitTypeId.VOIDRAY).amount >= 2:
            if self.enemy_units:
                for vr in self.units(UnitTypeId.VOIDRAY).idle:
                    vr.attack(random.choice(self.enemy_units))

            elif self.enemy_structures:
                for vr in self.units(UnitTypeId.VOIDRAY).idle:
                    vr.attack(random.choice(self.enemy_units))

            else:
                for vr in self.units(UnitTypeId.VOIDRAY).idle:
                    vr.attack(self.enemy_start_locations[0])



run_game(  # run_game is a function that runs the game.
    maps.get("BloodBoilLE"), # the map we are playing on
    [Bot(Race.Protoss, IncrediBot()), # runs our coded bot, protoss race, and we pass our bot object
     Computer(Race.Terran, Difficulty.Hard)], # runs a pre-made computer agent, zerg race, with a hard difficulty.
    realtime=True, # When set to True, the agent is limited in how long each step can take to process.
)