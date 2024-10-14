#!/usr/bin/env python3
import pandas as pd
import json

def main():

    idx = pd.IndexSlice
    #alist = [1000, 2000, 3000, 4000, 5000]
    hlist = [40, 50, 60]

    #df_scope2 = pd.read_excel('data/Scopes.xlsx', sheet_name='scope2_emissions')
    #df_scope3 = pd.read_excel('data/Scopes.xlsx', sheet_name='scope3_emissions')
    
    with open('data/Scopes.json') as file:
        data = json.load(file)
    
    df_scope2 = pd.DataFrame(data['scope2_emissions'])
    df_scope3 = pd.DataFrame(data['scope3_emissions'])

    # Set 'state' as the index
    df_scope2.set_index('state', inplace=True)
    df_scope3.set_index('state', inplace=True)

    print(df_scope2)
    print(df_scope3)

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

    df1 = pd.read_excel('data/Nabers_3_Star.xlsx', sheet_name='Sheet1')
    df2 = pd.read_excel('data/Nabers_4_Star.xlsx', sheet_name='Sheet1')
    df3 = pd.read_excel('data/Nabers_5_Star.xlsx', sheet_name='Sheet1')
    df = pd.concat([df1, df2, df3])
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
    print(h1)
    h0 = hlist[i - 1]
    print(h0)
    f = ((hours - h0) / (h1 - h0))
    print(f)

    # find the benchmark values for each star rating
    dfa = df1.loc[h0]
    dfb = df1.loc[h1]
    dfc = dfa + (dfb - dfa) * f
    dfc.index = dfc.index.droplevel()
    dfc = dfc[::-1]
    print(dfc)

    dfc = pd.DataFrame(list(dfc.items()), columns=['stars', 'emissions']).set_index('stars')
    dfc['emissions'] = dfc['emissions'].round(2)

    #print(dfc)

    # get normalised emissions actual
    x = emissions / area

    smaller_values = dfc[dfc['emissions'] <= x]
    larger_values = dfc[dfc['emissions'] >= x]
    closest_smaller_row = smaller_values.iloc[-1] if not smaller_values.empty else None
    closest_larger_row = larger_values.iloc[0] if not larger_values.empty else None

    # Will remove this if condition once we have 1 star 2 star and 6 star data.
    if closest_smaller_row is not None:
        closest_smaller_value = closest_smaller_row['emissions']
        smaller_star_rating = closest_smaller_row.name 
    else:
        closest_smaller_value = None
        smaller_star_rating = None

    if closest_larger_row is not None:
        closest_larger_value = closest_larger_row['emissions']
        larger_star_rating = closest_larger_row.name  
    else:
        closest_larger_value = None
        larger_star_rating = None

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
        print(f"The interpolated star rating for emissions {emissions} is: {interpolated_star_rating}")
    else:
        print("Could not find suitable values for interpolation.")


if __name__ == '__main__':
    main()