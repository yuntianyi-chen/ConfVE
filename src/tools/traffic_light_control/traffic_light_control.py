from dataclasses import dataclass
from random import randint, shuffle, random
from typing import Dict
from config import SCENARIO_UPPER_LIMIT
from tools.hdmap.MapParser import MapParser


@dataclass
class TCSection:
    initial: Dict[str, str]
    final: Dict[str, str]
    duration_g: float
    duration_y: float
    duration_b: float

    def calculate_transition(self):
        result = dict()
        for k in self.initial:
            if self.initial[k] == 'GREEN' and self.final[k] == 'RED':
                result[k] = 'YELLOW'
            else:
                result[k] = self.initial[k]
        return result

    def get_config_with_color(self, color: str):
        result = dict()
        for k in self.initial:
            result[k] = color
        return result

    @staticmethod
    def generate_config(preference=[]):
        ma = MapParser.get_instance()
        result = dict()
        signals = list(ma.get_signals())
        shuffle(signals)
        while len(signals) > 0:
            if len(preference) > 0:
                curr_sig = preference.pop()
                signals.remove(curr_sig)
            else:
                curr_sig = signals.pop()

            result[curr_sig] = 'GREEN'
            relevant = ma.get_signals_wrt(curr_sig)
            for sig, cond in relevant:
                if sig in preference:
                    preference.remove(sig)
                if sig in signals:
                    signals.remove(sig)
                    if cond == 'EQ':
                        result[sig] = 'GREEN'
                    else:
                        # NE
                        result[sig] = 'RED'
        return result

    @staticmethod
    def get_one():
        init = TCSection.generate_config()
        final = TCSection.generate_config(
            preference=[x for x in init if init[x] == 'RED'])
        return TCSection(
            initial=init,
            final=final,
            duration_g=randint(5, int(SCENARIO_UPPER_LIMIT/2)),
            duration_y=3,
            duration_b=2
        )

    @staticmethod
    def get_random_duration_g():
        return randint(5, int(SCENARIO_UPPER_LIMIT/2))


def mut_tc_section(ind: TCSection):
    mut_pb = random()

    if mut_pb < 0.3:
        ind.initial = TCSection.generate_config()
        return ind
    elif mut_pb < 0.6:
        ind.final = TCSection.generate_config()
    elif mut_pb < 0.9:
        ind.duration_g = TCSection.get_random_duration_g()

    return TCSection.get_one()