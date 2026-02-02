class Person:
  def __init__(self, name, age):
    self.name = name
    self.age = age

p1 = Person("Emil", 36)

print(p1.name)
print(p1.age)
#The __init__() method is used to assign values to object properties, or to perform operations that are necessary when the object is being created.