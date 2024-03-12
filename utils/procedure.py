def period_to_2list(yp, mp: list, df_data) -> list:
    lfh = {}
    lfh_y = []
    lfh_m = []
    
    ggg =[]

    for i_year in yp:
        lfh[i_year] = []

    for i_month in mp:
        
        for i_year in yp:
            if i_month in df_data['month_p'][df_data['year_p'] == i_year].values:
                ggg = lfh[i_year]
                ggg.append(i_month)
                lfh[i_year] = sorted(ggg)

    #print(dict(sorted(lfh.items())))

    for key in sorted(lfh.keys()):
        lfh_m = lfh_m + lfh[key]
        qy = len(lfh[key])
    for i in range(qy):
        lfh_y.append(key)

    new_list = [lfh_y]
    new_list.append(lfh_m)

    return new_list