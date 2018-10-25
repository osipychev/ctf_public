import numpy as np
from .. import *

def test_map_shape():
    """
    Test for CreateMap. Output map dimensions testing.
    """

    flag = False
    for s in [10, 20, 100, 500]:
        m1, m2 = CreateMap.gen_map('test', dim=s)
        if m1.shape != (s,s) or m2.shape != (s,s):
            flag = True
            message = 'Map dim test failed at ' + str(s)

    assert flag == False, message

def test_map_population():
    """
    Test for CreateMap. Output map population testing.
    """

    test_val = [[4,2,4,2,4],
                [4,0,4,0,0],
                [1,0,0,0,0],
                [0,0,1,0,0],
                [4,4,4,4,4]]
    flag = False
    for val in test_val:
        NUM_BLUE, NUM_UAV, NUM_RED, NUM_UAV, NUM_GRAY = val
        for s in [10, 20, 100]:
            m1, m2 = CreateMap.gen_map('test', dim=s,
                    map_obj=[NUM_BLUE, NUM_UAV, NUM_RED, NUM_UAV, NUM_GRAY])
            l = list(m1.flatten())
            if (l.count(TEAM1_UGV) != NUM_BLUE or
                l.count(TEAM1_UAV) != NUM_UAV or
                l.count(TEAM2_UGV) != NUM_RED or
                l.count(TEAM2_UAV) != NUM_UAV or
                l.count(TEAM3_UGV) != NUM_GRAY):
                flag = True
                message = 'Map population test failed at ' + str(s) + ',' + str(val)

    assert flag == False, message

def test_map_seed():
    """
    Test for CreateMap. Fixed seed map generation testing.
    """
    flag = False

    m1, m2 = CreateMap.gen_map('test', in_seed=100)
    m1_new, m2_new = CreateMap.gen_map('test', in_seed=100)

    assert (m1_new == m1).all and (m2_new == m2).all, 'Map random seed reproductivity issue'
