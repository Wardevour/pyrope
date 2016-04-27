from collections import OrderedDict

from pyrope.exceptions import FrameParsingError, PropertyParsingError
from pyrope.netstream_property_parsing import _read_int, read_property_value
from pyrope.utils import (BOOL, read_byte_vector, read_int32_max,
                          read_serialized_int, read_serialized_vector,
                          reverse_bytewise)


class Frame:
    _actor_alive = {}  # Map of ActorID:Archtype shared across Frames

    def __init__(self):
        self.current = None
        self.delta = None
        self.actors = None

    def parse_frame(self, netstream, objects, propertymapper):
        self.current = reverse_bytewise(netstream.read('bits:32')).floatle
        self.delta = reverse_bytewise(netstream.read('bits:32')).floatle

        if self.current < 0.001 or self.delta < 0.001:
            raise FrameParsingError("Last Frame caused some offset. Nextbits: %s" % netstream.read('bits:64').hex)

        self.actors = self._parse_actors(netstream, objects, propertymapper)

    def _parse_actors(self, netstream, objects, propertymapper):
        actors = OrderedDict()  # Ordered Dict to reflect order of appearance in json output

        while True:
            actor = {}
            startpos = netstream.pos
            actor_present = netstream.read(BOOL)

            if not actor_present:
                break

            actor['id'] = read_int32_max(netstream, 1023)

            channel = netstream.read(BOOL)

            # Actor is active within the game.
            if channel:
                new = netstream.read(BOOL)

                # Actor is new in this frame.
                if new:
                    actor = self._parse_new_actor(actor, netstream, objects, propertymapper)
                    self._actor_alive[actor['id']] = actor['type_name']

                    short_name = '{}n_{}'.format(
                        actor['id'],
                        self._actor_alive[actor['id']].split('.')[-1].split(':')[-1]
                    )

                # Actor already existed.
                else:
                    actor = self._parse_existing_actor(actor, netstream, objects, propertymapper)

                    short_name = '{}e_{}'.format(
                        actor['id'],
                        self._actor_alive[actor['id']].split('.')[-1].split(':')[-1]
                    )

                actors[short_name] = {
                    'startpos': startpos,
                    'actor_id': actor['id'],
                    'actor_type': self._actor_alive.get(actor['id'], None),
                    'new': new,
                    'open': channel,
                    'data': actor,
                }

            # Deleted (player left the game etc..)
            else:
                actor = self._parse_deleted_actor(actor, propertymapper)

                if actor['id'] in self._actor_alive:
                    short_name = '{}d_{}'.format(
                        actor['id'],
                        self._actor_alive[actor['id']].split('.')[-1].split(':')[-1]
                    )

                    actors[short_name] = {
                        'startpos': startpos,
                        'actor_id': actor['id'],
                        'actor_type': self._actor_alive[actor['id']],
                        'open': channel,
                    }

                    del self._actor_alive[actor['id']]

        return actors

    def _parse_existing_actor(self, actor, netstream, objects, propertymapper):
        actor['state'] = 'existing'
        actor_type = self._actor_alive[actor['id']]

        while netstream.read(BOOL):
            property_id = read_serialized_int(
                netstream,
                propertymapper.get_property_max_id(actor_type)
            )
            property_name = objects[propertymapper.get_property_name(actor_type, property_id)]

            try:
                property_value = read_property_value(property_name, netstream)
            except PropertyParsingError as e:
                e.args += ({
                    "Props_till_err": actor
                },)

                raise e

            actor[property_name] = property_value

        return actor

    def _parse_new_actor(self, actor, netstream, objects, propertymapper):
        actor['state'] = 'new'
        actor['flag'] = netstream.read(BOOL)
        actor['type_id'] = _read_int(netstream)
        actor['type_name'] = objects[actor['type_id']]
        actor['class_name'] = propertymapper._arch_to_class(actor['type_name'])

        if actor['class_name'].startswith('.'):
            actor['class_name'] = 'TAGame{}'.format(actor['class_name'])

        if actor['class_name'] in ['TAGame.CrowdActor_TA', 'TAGame.CrowdManager_TA', 'TAGame.VehiclePickup_Boost_TA', 'Core.Object']:
            return actor

        actor['position'] = read_serialized_vector(netstream)

        if actor['class_name'] in ['TAGame.Ball_TA', 'TAGame.Car_TA', 'TAGame.Car_Season_TA']:
            actor['rotation'] = read_byte_vector(netstream)

        return actor

    def _parse_deleted_actor(self, actor, propertymapper):
        actor['state'] = 'deleted'

        if actor['id'] in self._actor_alive:
            actor['type_id'] = self._actor_alive[actor['id']]
            actor['type_name'] = self._actor_alive[actor['id']]
            actor['class_name'] = propertymapper._arch_to_class(actor['type_name'])

            if actor['class_name'].startswith('.'):
                actor['class_name'] = 'TAGame{}'.format(actor['class_name'])

        return actor
