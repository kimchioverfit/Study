
#최적화가 없는 mergesort
#list를 slice할 때 배열의 복제가 일어나기 때문에 메모리 사용효율 낮음
#https://gmlwjd9405.github.io/2018/05/08/algorithm-merge-sort.html

def mergesort(list):
    if len(list)<2:
        return list

    idx = len(list)//2
    left_list=list[:idx]
    right_list=list[idx:]

    new_list=[]

    i=j=0
    while i <len(left_list) and j < len(right_list):
        if left_list[i] < right_list[j]:
            new_list.append(left_list[i])
            i+=1
        else:
            new_list.append(right_list[j])
            j+=1
    new_list += left_list[i:]
    new_list += right_list[j:]

    print(new_list)
    return new_list





list = [12,457,4568,12,7654,9786,1251345134]
mergesort(list)