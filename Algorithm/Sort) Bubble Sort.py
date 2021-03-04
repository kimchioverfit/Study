def BubbleSort(list):
    list_length = len(list)

    #length가 4라면
    #바깥 루프는 3번 돌아야 하므로
    #range()는 0, 1, 2까지 즉 range(3)이 되야 하므로
    #range(list_length-1)이 되어야 한다.
    for i in range(list_length-1):
        #안쪽 루프는 1번당 3-> 2-> 1
        #즉 range(4 - 0 - 1) ->
        #range(4 - 1 - 1) ->
        #range(4 - 2 - 1)
        #range(list_leng - i - 1)
        for j in range(list_length-i-1):
            #만약 앞에 있는 값이 크다면 두 개를 교환
            if list[j] > list[j+1]:
                list[j], list[j+1] = list[j+1], list[j]


if __name__ == "__main__":
    list = [2, 3, 1, 4, 6, 123 ,25]
    BubbleSort(list)
    print(list)