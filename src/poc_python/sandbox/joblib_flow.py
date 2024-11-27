from time import sleep


def slow():
    print("computing")
    sleep(10)
    return 5

def kek(a = slow()):
    print(a)

print("pre run")
kek()
sleep(5)
print("rerun")
kek()