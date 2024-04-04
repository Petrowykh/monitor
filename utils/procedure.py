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

    for key in sorted(lfh.keys()):
        lfh_m = lfh_m + lfh[key]
        qy = len(lfh[key])
        for i in range(qy):
            lfh_y.append(key)

    new_list = [lfh_y]
    new_list.append(lfh_m)

    return new_list


def change_time(x):
    x1, x2, x3 = x.split(':')
    if x1.isdigit() and x2.isdigit:
        return int(x1) + int(x2)/60 
    
def define_status(x):
    if x > 12: return 3
    elif x > 6: return 2
    elif x > 3: return 1
    else: return 0

def define_bonus(x):
    if x > 100: return 2
    elif x > 80: return 1
    else: return 0

def get_data_personal(df, start, end):
    return df['tab_id'][(df['start_status'] == start) & (df['end_status'] == end)].count()

def get_data_motivation(df, end, bonus):
    return df['tab_id'][(df['end_status'] == end) & (df['bonus_status'] == bonus)].count()

def get_list_diagram(df):
    
    color_list = ["lightblue", "lightgreen", "lightpink", "yellow"]
    diagram_value = [[0, 4], [0, 0], [0, 1], [1, 4], [1, 1], [1, 2], [2, 4], [2, 2], [2, 3], [3, 4], [3, 3]]

    source = []
    target = []
    value = []
    color = []
    
    for dv in diagram_value:
        flag = get_data_personal(df, dv[0], dv[1])
        if flag:
            source.append(dv[0])
            if dv[1] == 4:
                target.append(dv[1])
            else:
                target.append(dv[1]+5)
            value.append(flag)
            color.append(color_list[dv[0]])
        
    return source, target, value, color


def get_list_motivation(df):
    
    color_list = ["lightblue", "lightgreen", "lightpink", "yellow"]
    diagram_value = [[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2], [2, 0], [2, 1], [2,2], [3, 0], [3, 1], [3, 2]]

    source = []
    target = []
    value = []
    color = []
    
    for dv in diagram_value:
        flag = get_data_motivation(df, dv[0], dv[1])
        if flag:
            source.append(dv[0])
            if dv[1] == 4:
                target.append(dv[1])
            else:
                target.append(dv[1]+4)
            value.append(flag)
            color.append(color_list[dv[0]])
        
    return source, target, value, color


def get_burden(on_shift, income):
    burden = int(income/on_shift)
    if burden > 3000: return "высокая"
    elif burden > 1500: return "средняя"
    else: return "низкая"