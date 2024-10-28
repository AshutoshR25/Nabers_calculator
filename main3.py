#!/usr/bin/env python3
from pathlib import Path
import colorlog
import json
import logging
import numpy as np
import os
import pandas as pd
import sys

log = logging.getLogger()


def main():

    # StarCalculator(ratedArea=100, ratedHours=50, elec=200000, year='2023')
    # StarCalculator(ratedArea=10000, ratedHours=50, elec=200000, year='2023')
    # StarCalculator(ratedArea=2708, ratedHours=50, elec=210000, year='2024')
    # StarCalculator(ratedArea=5084.3, ratedHours=50, year='2020')
    # StarCalculator(ratedArea=5084.3, ratedHours=50, year='2024')
    # StarCalculator(ratedArea=1000, ratedHours=50, year='2020')

    # StarCalculator(ratedArea=3000, ratedHours=54, elec=200000, year='2024')
    StarCalculator(ratedArea=5084.3, ratedHours=50, year='2020')


class StarCalculator():

    def __init__(self, **kwargs):
        self.stars = None
        self.starsClip = None
        self.set_params(**kwargs)
        self.set_energy(**kwargs)
        self.check_year()
        self.get_emission_factors()
        self.get_emission_allowance()
        self.calc_emissions()
        self.calc_energy()
        self.calc_stars()
        self.calc_limits()
        self.show_settings()
        self.show_results()
        self.show_limits()

    def set_params(self, year='2024', state='Victoria', ratedArea=2000, ratedHours=50, **kwargs):
        self.year = year
        self.state = state
        self.ratedArea = ratedArea
        self.ratedHours = ratedHours

    def set_energy(self, elec=0, gas=0, diesel=0, **kwargs):
        self.elec = elec
        self.gas = gas
        self.diesel = diesel

    def show_settings(self):
        log.info('-------------------------------------------')
        log.info('ratedArea {:}'.format(self.ratedArea))
        log.info('ratedHours {:}'.format(self.ratedHours))
        log.info('elec {:} kWh'.format(self.elec))
        log.info('gas {:} MJ'.format(self.gas))
        log.info('diesel {:} L'.format(self.diesel))
        log.info('state {:}'.format(self.state))
        log.info('year {:} ({:})'.format(self.year, self.yearNGA))
        log.info('factor_elec_scope2 {:}'.format(self.factor_elec_scope2))
        log.info('factor_elec_scope3 {:}'.format(self.factor_elec_scope3))
        log.info('factor_gas_scope1 {:}'.format(self.factor_gas_scope1))
        log.info('factor_diesel_scope1 {:}'.format(self.factor_diesel_scope1))

    def show_results(self):
        if self.stars:
            log.info('energy intensity {:.1f} MJ/m2'.format(self.energyIntensity))
            log.info('total emissions {:.0f} kgCO2-e'.format(self.emissions))
            log.info('stars {:.2f}'.format(self.stars))
            log.info('stars clipped {:.1f}'.format(self.starsClip))

    def show_limits(self):
        log.info('star limits')
        factor_elec = self.factor_elec_scope2 + self.factor_elec_scope3
        # factor_elec = self.factor_elec_scope2
        print(factor_elec)
        df = pd.Series(self.limits).to_frame()
        df.columns = ['kgCO2-e']
        df['kWh'] = df['kgCO2-e'] / factor_elec
        df = df.astype(int)
        print(df)
        # for s, e in self.limits.items():
        #     ekWh = e * (self.factor_elec_scope2 + self.factor_elec_scope2)
        #     log.info('   {:4} {:8.0f} {:8.0f}'.format(s, e, eKwh))

    def check_year(self):
        self.yearNGA = self.year
        return
        if self.year in ['2020', '2021', '2022', '2023', '2024']:
            self.yearNGA = '2020'
        elif self.year in ['2025', '2026', '2027', '2028', '2029']:
            self.yearNGA = '2025'

    def get_emission_factors(self):
        appdir = Path(__file__).parents[1]
        appdir = Path(__file__).parent
        fname = os.path.join(appdir, 'data', 'nabers_emission_factors.json')
        with open(fname, 'r') as file:
            data = json.load(file)
        self.factor_elec_scope2 = data['elec_scope2'][self.yearNGA][self.state]
        self.factor_elec_scope3 = data['elec_scope3'][self.yearNGA][self.state]
        self.factor_gas_scope1 = data['gas_scope1'][self.yearNGA][self.state]
        self.factor_diesel_scope1 = data['diesel_scope1'][self.yearNGA][self.state]

    def get_emission_allowance(self):

        # emissions per m2 is a constant for each star rating and rated hours
        appdir = Path(__file__).parents[1]
        appdir = Path(__file__).parent
        fname = os.path.join(appdir, 'data', 'nabers_star_allowance.json')
        fname = os.path.join(appdir, 'data', 'nabers_star_allowance.json')
        with open(fname, 'r') as file:
            data = json.load(file)
        data = data[self.state]

        # create the dataframe
        df = pd.DataFrame(data)
        df['eNorm'] = df['emissions'] / df['ratedArea']
        df.set_index(['stars', 'ratedHours'], inplace=True)
        df = df['eNorm'].unstack()

        # get the equation for each star
        x1, x2 = df.columns
        df['m'] = (df[x2] - df[x1]) / (x2 - x1)   # dy / dx
        df['c'] = df[x1] - df['m'] * x1           # y = mx + c, c = y - mx
        df.columns.name = None
        self.df = df[['m', 'c']]

    def calc_emissions(self):
        e1 = self.elec * (self.factor_elec_scope2 + self.factor_elec_scope3)
        e2 = self.gas * self.factor_gas_scope1
        e3 = self.diesel * self.factor_diesel_scope1
        self.emissions = e1 + e2 + e3

    def calc_energy(self):
        energy = self.elec * 3.6 + self.gas
        self.energyIntensity = energy / self.ratedArea

    def calc_stars(self):

        if self.emissions == 0:
            return

        # calculate eNorm for rated hours
        df = self.df.copy()
        df['eNorm'] = df['m'] * self.ratedHours + df['c']
        df['emissions'] = df['eNorm'] * self.ratedArea
        df.reset_index(inplace=True)

        # get the bounding dataframe rows
        eNorm = self.emissions / self.ratedArea
        i1 = next((i for i, row in df.iterrows() if row['eNorm'] < eNorm), None)
        df = df.loc[i1-1:i1]

        # interpolate stars
        # np interp needs monotonically increasing values (hence negative sign)
        slist = list(df['stars'])
        elist = list(-df['eNorm'])
        value = np.interp(-eNorm, elist, slist)
        valueClip = np.floor(value * 2) / 2
        self.stars = value
        self.starsClip = valueClip

    def calc_limits(self):

        # calculate eNorm for rated hours
        df = self.df.copy()
        df['eNorm'] = df['m'] * self.ratedHours + df['c']

        # construct the dictionary
        df['emissions'] = df['eNorm'] * self.ratedArea
        sdict = dict(df['emissions'])
        sdict[2.5] = (sdict[2] + sdict[3]) / 2
        sdict[3.5] = (sdict[3] + sdict[4]) / 2
        sdict[4.5] = (sdict[4] + sdict[5]) / 2
        sdict[5.5] = (sdict[5] + sdict[6]) / 2
        self.limits = dict(sorted(sdict.items()))


if __name__ == '__main__':

    log.setLevel(logging.DEBUG)

    # set up the stdout logger
    formatter = colorlog.ColoredFormatter('%(log_color)s%(levelname)-8s %(module)-18s %(funcName)-25s %(message)s')
    sh = colorlog.StreamHandler(stream=sys.stdout)
    sh.setLevel(logging.INFO)
    sh.setFormatter(formatter)
    log.addHandler(sh)

    main()