count = 100


def fn():
    global count
    statement = count > 1
    try:
        while count > 1:
            count -= 1
            print(count)
        print("cont is 0")
    except:
        print("finally ended")


fn()
