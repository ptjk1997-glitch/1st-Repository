#함수를 정의
def add(a, b):
    return a + b

#함수를 호출
result = add(3, 4)
print(result)

lst = ["사과", "배", "감", "귤", "포도"]
print(lst)

for fruit in lst:
    print(fruit)


lst.append("바나나")
print(lst)

lst.remove("감")
print(lst)

#Tuple은 한방에 입력과 출력을 하는 배열

tp=(100, 200, 300, 400, 500)
print(len(tp))
print(type(tp))
for item in tp:
    print(item)


#함수 정의
def times(a, b):
    return a + b, a * b

result=times(3, 4)
print(result)
