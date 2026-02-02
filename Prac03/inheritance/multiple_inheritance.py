# multiple_inheritance.py

class Fly:
    def fly(self):
        print("I can fly")

class Swim:
    def swim(self):
        print("I can swim")

class Duck(Fly, Swim):
    def sound(self):
        print("Quack")

d = Duck()

d.fly()    # I can fly
d.swim()   # I can swim
d.sound()  # Quack
