# Design

## Features
* Command classes that define parameters classes and sub-command classes
* Paramters classes which when instantiated create an instance, replacing the class attributes with instance attributes of the same type
* Paramters class can have validation functions defined which use dependency injection for function parameters:
    ```python
    def validate_some_args(from_number, to_number):
        if from_number < to_number:
            return True
        else:
            raise ParamtersValidationException
    ```
* Parameters class will be able to define exclusive parameters

## Implementation

### Parameters
* User defines a class with class attributes
* Attributes are typed, this will be the type that is attempted to be cast
* Function will translate the user's Paramters class into a class instance that copies the class attributes into instance attributes into the new class

### Command
* User defines class with class attributes
* Attributes are typed to Paramters or Command types
* Command implements parsing logic for its own command and parameters
* Parsing method will return instance of Paramterss with populated parameters, remaining parameters, next Command type to execute

### App
* User defines entry Command class
* Implements run method which instantiates the Command class and calls parsing method, if remaining parameters, then tries the next Command class; if no Command class then raise exception
