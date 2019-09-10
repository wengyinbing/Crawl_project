with open('nothing.txt','r',encoding='UTF-8') as f:
    meaningless_file = f.read().splitlines()
    print(meaningless_file)
    f.close()