#!/usr/bin/env python3
import pandas as pd
import numpy as np
from functions import NabersPredictor


def main():

    idx = pd.IndexSlice
    alist = [1000, 2000, 3000, 4000, 5000]
    hlist = [40, 50, 60]

    area = 5900
    hours = 38
    elec = 481748

    df1 = pd.read_excel('data/Nabers_3_Star.xlsx', sheet_name='Sheet1')
    df2 = pd.read_excel('data/Nabers_4_Star.xlsx', sheet_name='Sheet1')
    df3 = pd.read_excel('data/Nabers_5_Star.xlsx', sheet_name='Sheet1')
    df = pd.concat([df1, df2, df3])
    df.columns = ['area', 'hours', 'elec', 'stars']
    df.set_index(['stars', 'area', 'hours'], inplace=True)
    df = df.unstack(['stars'])

    #print(df)

    # get normalised electricity allowance
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
    #print(df1)
    #print(dfa)
    dfc = dfa + (dfb - dfa) * f
    dfc.index = dfc.index.droplevel()
    dfc = dfc[::-1]
    print(dfc)

    dfc = pd.DataFrame(list(dfc.items()), columns=['stars', 'elec']).set_index('stars')
    dfc['elec'] = dfc['elec'].round(2)

    print(dfc)

    # get normalised elec actual
    x = elec / area
    print(x)

    smaller_values = dfc[dfc['elec'] <= x]
    larger_values = dfc[dfc['elec'] >= x]
    closest_smaller_row = smaller_values.iloc[-1] if not smaller_values.empty else None
    closest_larger_row = larger_values.iloc[0] if not larger_values.empty else None

    if closest_smaller_row is not None:
        closest_smaller_value = closest_smaller_row['elec']
        smaller_star_rating = closest_smaller_row.name 
    else:
        closest_smaller_value = None
        smaller_star_rating = None

    if closest_larger_row is not None:
        closest_larger_value = closest_larger_row['elec']
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
        print(f"The interpolated star rating for electricity {elec} is: {interpolated_star_rating}")
    else:
        print("Could not find suitable values for interpolation.")



# Jon has Commented code
# def main():

#     df1 = pd.read_excel('data/Nabers_3_Star.xlsx', sheet_name='Sheet1')
#     df2 = pd.read_excel('data/Nabers_4_Star.xlsx', sheet_name='Sheet1')
#     df3 = pd.read_excel('data/Nabers_5_Star.xlsx', sheet_name='Sheet1')
#     df = pd.concat([df1, df2, df3])
#     df.columns = ['area', 'hours', 'elec', 'stars']
#     df.set_index(['stars', 'area', 'hours'], inplace=True)
#     df = df.unstack('stars')
#     df.columns = df.columns.droplevel()



#     # df.reset_index(inplace=True)
#     alist = [1000, 2000, 3000, 4000, 5000]
#     hlist = [40, 50, 60]

#     area = 4600
#     hours = 45
#     elec = 450000

#     a1 = next((i for i in alist if i > area), None)
#     i = alist.index(a1)
#     a0 = alist[i - 1]

#     h1 = next((i for i in hlist if i > hours), None)
#     i = hlist.index(h1)
#     h0 = hlist[i - 1]

#     print('--------------')
#     print(df)
#     # filter by area / hours
#     idx = pd.IndexSlice
#     df1 = df.loc[idx[a0, h0:h1], :]
#     df2 = df.loc[idx[a1, h0:h1], :]

#     # filter by hours
#     # df1 = df1.loc[idx[a0, :], :]
#     # df2 = df2.loc[idx[a1, :], :]



#     print('--------------')
#     print(df1)
#     print('--------------')
#     print(df2)

#     # print('--------------')
#     # print('--------------')
#     # print(df1 - elec)
#     # print('--------------')
#     # print(df2 - elec)

#     # f = ((area - a0) / (a1 - a0))
#     # print(f)
#     # dfx = df1 + df2 * f
#     # print(dfx)

#     # df = df[df['area'] < a]


if __name__ == '__main__':
    main()

