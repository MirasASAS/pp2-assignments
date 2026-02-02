# method_overriding.py

class Animal:
    def sound(self):
        print("Animal makes a sound")

class Dog(Animal):
    def sound(self):   # overriding
        print("Dog barks")

class Cat(Animal):
    def sound(self):   # overriding
        print("Cat meows")

a = Animal()
d = Dog()
c = Cat()

a.sound()  # Animal makes a sound
d.sound()  # Dog barks
c.sound()  # Cat meows
