#!/usr/bin/env python3
import pandas as pd
import json
import math

def main():

    idx = pd.IndexSlice
    #alist = [1000, 2000, 3000, 4000, 5000]
    hlist = [40, 50, 60]
    
    with open('data/Scopes.json', 'r') as file:
        data = json.load(file)

    with open('data/Nabers_stars.json', 'r') as f:
        data_stars = json.load(f)
    
    df_scope2 = pd.DataFrame(data['scope2_emissions'])
    df_scope3 = pd.DataFrame(data['scope3_emissions'])

    # Set 'state' as the index
    df_scope2.set_index('state', inplace=True)
    df_scope3.set_index('state', inplace=True)

    # Get user input
    area = int(input("Enter the area: "))
    hours = int(input("Enter the hours: "))
    elec = int(input("Enter the electricity consumption (kWh): "))
    gas = int(input("Enter the gas consumption: "))
    diesel = int(input("Enter the diesel consumption: "))
    state = input("Enter the state:")
    year = int(input("Enter the year:"))

    if year >= 2020 and year <= 2024:
        year = 2020

    #value = df_scope2.loc[state, int(year)]
    scope2_val = df_scope2.at[str(state), str(year)]
    scope3_val = df_scope3.at[str(state), str(year)]

    scope2_elec = float(scope2_val)
    scope3_elec = float(scope3_val)

    scope1_gas = data['scope1_gas'][0]['value']
    scope1_diesel = data['scope1_diesel'][0]['value']

    emissions = (elec*(scope2_elec+scope3_elec)) + (gas*scope1_gas) + (diesel*scope1_diesel)

    df = pd.DataFrame(data_stars[state])
    df.columns = ['area', 'hours', 'emissions', 'stars']
    df.set_index(['stars', 'area', 'hours'], inplace=True)
    df = df.unstack(['stars'])


    # get normalised emissionstricity allowance
    df1 = df.loc[idx[1000, :], :]
    df1 = df1 / 1000

    #print(df1)
    df1.index = df1.index.droplevel()

    # get the hours fraction
    h1 = next((i for i in hlist if i > hours), None)
    i = hlist.index(h1)
    h0 = hlist[i - 1]
    f = ((hours - h0) / (h1 - h0))


    # find the benchmark values for each star rating
    dfa = df1.loc[h0]
    dfb = df1.loc[h1]
    dfc = dfa + (dfb - dfa) * f
    dfc.index = dfc.index.droplevel()
    dfc = dfc[::-1]

    dfc = pd.DataFrame(list(dfc.items()), columns=['stars', 'emissions']).set_index('stars')
    dfc['emissions'] = dfc['emissions'].round(2)

    #print(dfc)

    # get normalised emissions actual
    x = emissions / area

    smaller_values = dfc[dfc['emissions'] <= x]
    larger_values = dfc[dfc['emissions'] >= x]
    closest_smaller_row = smaller_values.iloc[-1] if not smaller_values.empty else None
    closest_larger_row = larger_values.iloc[0] if not larger_values.empty else None


    closest_smaller_value = closest_smaller_row['emissions']
    smaller_star_rating = closest_smaller_row.name
    closest_larger_value = closest_larger_row['emissions']
    larger_star_rating = closest_larger_row.name

    if closest_smaller_value is not None and closest_larger_value is not None:
        x1, y1 = closest_smaller_value, smaller_star_rating
        x2, y2 = closest_larger_value, larger_star_rating

        if y2 == y1:
            m = 0
        else:
            m = (y2 - y1) / (x2 - x1)  # Slope
        
        c = y1 - m * x1            # constant

        interpolated_star_rating = m * x + c # formula y = mx +c

        print(f"Closest smaller value: {closest_smaller_value} with star rating {smaller_star_rating}")
        print(f"Closest larger value: {closest_larger_value} with star rating {larger_star_rating}")

        integer_part = math.floor(interpolated_star_rating)
        print(integer_part)
        decimal_part = interpolated_star_rating - integer_part
        decimal_part = round(decimal_part, 3)
        print(decimal_part)

        if decimal_part >= 0.501 and decimal_part <= 0.999:
            stars = integer_part + 0.5
        elif decimal_part >= 0.001 and decimal_part <= 0.499:
            stars = integer_part
        else:
            stars = integer_part + 1

        print(f"The interpolated star rating for your office building is: {stars}")

        #print(f"The interpolated star rating for emissions {emissions} is: {interpolated_star_rating}")
    else:
        print("Could not find suitable values for interpolation.")


if __name__ == '__main__':
    main()