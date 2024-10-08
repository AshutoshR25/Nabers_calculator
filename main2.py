#!/usr/bin/env python3
import pandas as pd
import numpy as np
from functions import NabersPredictor


def main():

    idx = pd.IndexSlice
    alist = [1000, 2000, 3000, 4000, 5000]
    hlist = [40, 50, 60]

    area = 4600
    hours = 48
    elec = 450000

    df1 = pd.read_excel('data/Nabers_3_Star.xlsx', sheet_name='Sheet1')
    df2 = pd.read_excel('data/Nabers_4_Star.xlsx', sheet_name='Sheet1')
    df3 = pd.read_excel('data/Nabers_5_Star.xlsx', sheet_name='Sheet1')
    df = pd.concat([df1, df2, df3])
    df.columns = ['area', 'hours', 'elec', 'stars']
    df.set_index(['stars', 'area', 'hours'], inplace=True)
    df = df.unstack(['stars'])

    # print(df)

    # get normalised electricity allowance
    df1 = df.loc[idx[1000, :], :]
    df1 = df1 / 1000
    df1.index = df1.index.droplevel()

    # get the hours fraction
    h1 = next((i for i in hlist if i > hours), None)
    i = hlist.index(h1)
    h0 = hlist[i - 1]
    f = ((hours - h0) / (h1 - h0))

    # find the benchmark values for each star rating
    dfa = df1.loc[h0]
    dfb = df1.loc[h1]
    print(df1)
    print(dfa)
    dfc = dfa + (dfb - dfa) * f
    dfc.index = dfc.index.droplevel()
    dfc = dfc[::-1]

    # get normalised elec actual
    x = elec / area

    print(dfc)
    print(x)
    stars = np.interp(x, dfc.values, dfc.index, period=-1)
    print('the answer is', stars)


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

