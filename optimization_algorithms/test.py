"""
Name:
UCINetID:
"""
class NoStaircaseSizeException(Exception):
    pass
class IntegerOutOfRangeException(Exception):
    pass
''' This functions asks the user for the number of steps
they want to climb, gets the value provided by the user
and returns it to the calling function. This function will
raise any exceptions related to none integer user inputs.'''
def getUserInput():
    # your code belongs here
    step = input("Please input your staircase size: \n")
    if step == "DONE":
        return "DONE"
    return step
''' This function takes the number of steps as an input parameter,
creates a string that contains the entire steps based on the user input
and returns the steps string to the calling function. This function will raise
any exceptions resulting from invalid integer values.
'''
def printSteps(stepCount):
    #your code belongs here
    Stair = ""
    if int(stepCount) == 0:
        raise NoStaircaseSizeException
    elif int(stepCount) < 0 or int(stepCount) >= 1000:
        raise IntegerOutOfRangeException
    Stair += (" " * (int(stepCount) * 2 - 2) + "+-+")
    for i in range(int(stepCount)):
        Stair += "\n"
        Stair += (" " * (int(stepCount) * 2 - (i + 1) * 2) + "| |")
        Stair += "\n"
        if i == int(stepCount) - 1 or i is int(stepCount):
            Stair += ("+-+")
        else:
            Stair += (" " * ((int(stepCount) * 2 - (i + 1) * 2) - 2) + "+-+-+")
    return Stair

'''This function kicks off the running of your program. Once it starts
it will continuously run your program until the user explicitly chooses to
end the running of the program based on the requirements. This function returns
the string "Done Executing" when it ends. Additionally, all exceptions will be
handled (caught) within this function.'''
def runProgram():
    #your code belongs here
    while True:
        try:
            step = getUserInput()
            if step == "DONE":
                return "Done Executing"
        except ValueError:
            print("Invalid staircase value entered.")
            continue
        try:
            Stair = printSteps(step)
            print(Stair)
        except NoStaircaseSizeException:
            print("I cannot draw a staircase with no steps.")
        except IntegerOutOfRangeException:
            print("That staircase size is out of range.")

'''Within this condition statement you are "Invalid staircase value entered."to write the code that kicks off
your program. When testing your code the code below this
should be the only code not in a function and must be within the if
statement. I will explain this if statement later in the course.'''
if __name__ == "__main__":
    #your code belongs here
    runProgram()