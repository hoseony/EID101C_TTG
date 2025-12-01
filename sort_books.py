def sort_call_numbers(tup):
    t = tup.replace('.', ' ').split()
    if len(t) >=3:
        return t[0]

def find_out_of_order(codes):
    converted = [sort_call_numbers(c) for c in codes if sort_call_numbers(c)]
    print(converted)
    out_of_order_positions = []

    for i in range(len(converted) - 1):
        if not (converted[i] <= converted[i+1]):
            out_of_order_positions.append(i + 2)
    return out_of_order_positions


