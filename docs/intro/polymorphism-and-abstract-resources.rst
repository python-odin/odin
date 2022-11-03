###################################
Polymorphism and abstract resources
###################################

Just like Python itself through the use of ABCs Odin supports the concept of Polymorphic data structures.

For this example we are going to use animals as an example, first we define a basic base class and provide the
``abstract`` option to indicate this is not an instantiatable object

.. code-block:: python

    import odin

    class Animal(odin.AnnotatedResource, abstract=True)
        name: str


Next we can defined specific types of animal (very loose types!)

.. code-block:: python

    class Dog(Animal):
        pass

    class Cat(Animal):
        colour: str

    class Bird(Animal):
        flightless: bool
        beak_colour: str


Finally we can define a resource that contains a resource that supports multiple types of ``Animal``:

.. code-block:: python

    class Family(odin.AnnotateResource):
        pets: List[Animal]


With this definition we an define a families pets, each of them has a name but also includes other characteristics.

When this data is exported using a codec sub-types of an abstract resource can be specified, eg with JSON:

.. code-block:: json

    {
      "$": "Family",
      "pets": [
        {
          "$": "Cat",
          "name": "Gypsy Sun & Rainbows",
          "colour": "Tortoise shell"
        },
        {
          "$": "Bird",
          "name": "Squeek",
          "flightless": false,
          "beak_colour": "Orange"
        }
      ]
    }

Through the use of the `type_field` ("$" by default) the codecs can resolve the correct type and validate that the
type is supported.

.. tip:: The type_field value can be changed via the Meta block.
