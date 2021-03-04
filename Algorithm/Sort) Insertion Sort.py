#



# def insertion_sort(list):
#     new_list=[]
#     new_list.append(list[0:2])

#     for i in range(len(list)-1):
#         new_list[i] < new_list [i+1]


def insertion_sort(list):
    for end in range(1, len(list)):
        for i in range(end, 0, -1):
             if list[i - 1] > list[i]:
                 list[i - 1], list[i] = list[i], list[i - 1]
    print(list)



list = [12,457,4568,12,7654,9786,1251345134]
insertion_sort(list)