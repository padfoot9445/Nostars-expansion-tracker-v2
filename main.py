import json
import copy

def deci_to_ac(var):
    decimal = 0
    units = 0
    for i in range(var):
        
        if not decimal == 3:
            decimal += 1
        else: 
            units += 1
            decimal = 0
    return f"{units}{decimal}"

def read_items():
   with open("items.json") as file:
      return json.load(file)

def read_time_file(return_int: bool):
    #returns contents of time.txt in either integer or string format
    if not type(return_int) == bool:
       raise TypeError("return_int was not a boolean.")
    with open("time.txt","r") as file:
       try:
         if return_int:
            return int(file.readline().strip())
         else:
            return file.readline().strip()
       except:
          TypeError("Issue with time.txt data type")
          ValueError("Issue with time.txt data value")
          Exception("Issue with read_time_file function")

def write_items(content):
   with open("items.json","w") as f:
        json.dump(content,f,indent = 2)
   with open("logs.txt","a") as file:
      file.write(f"Wrote {content} to items.json at {read_time_file(False)}")

def log(first_value: str,second_value: str, value_name:str, object: str):
   with open("logs.txt","a") as file:
      file.write(f"modified{object} {value_name} Value: Original: {first_value}; New: {second_value} at {read_time_file(False)}\n")


def check_finished():
    file = read_items()
    for item in file.values():
        if item["cap"]:
         if int(item["times"]) == int(item["cap"]):
               item["finished"] = True
               log(False,True,"finished",item["name"])

    write_items(file)

def repeat():
   #check if the whole thing is finished
   check_finished()
   file = read_items()
   for item in file.values():
      #if the item isnt finished and it has started
      if (not item["finished"]) and item["started"]:
          
            if item["endTime"] == read_time_file(True): #READ TIME HERE
               #increase the repeating counts: ie: amount of times repeated, and amount of items
               item["times"] += 1
               log((item["times"]-1), item["times"], "times", item["name"])
               item["amount"] += item["multiplier"]
               log((item["amount"]-item["multiplier"]), item["amount"], "amount", item["name"])
               #new end time
               old_end_time = item["endTime"]
               item["endTime"] = read_time_file(True) + item["duration"] +item["interval"]
               log(old_end_time, item["endTime"], "endTime", item["name"])
               #if there is an interval, add that to the remaining time
               if item["interval"]:
                     old_remaining_interval = item["remainingInterval"]
                     item["remainingInterval"] += item["interval"]
                     log(old_remaining_interval, item["remainingInterval"], "remainingInterval", item["name"])
                     #and make it so that the item hasn't started yet
                     old_started = item["started"]
                     item["started"] = False
                     log(old_started, item["started"], "started", item["name"])
   write_items(file)

def check_started():
   file = read_items()
   for item in file.values():
      if (not item["started"]) and (item["startTime"]==read_time_file(True)) and (not item["remainingInterval"]) and item["times"] == 0:
         old_started = item["started"]
         item["started"] = True
         log(old_started, item["started"], "started", item["name"])
   write_items(file)

def items_control():
   file = read_items()
   for item in file.values():
      old_remainingTime = item["remainingTime"]
      
      item["remainingTime"] = item["endTime"] - read_time_file(True)
      if item["remainingTime"] < 0:
         item["remainingTime"] = 0
      log(old_remainingTime, item["remainingTime"], "times", item["name"])
   write_items(file)

def user_input_time_reader( user_input:str,return_int:bool):
   "reads user input in format YY.M and returns it as either a string or an integer"
   try:
      #checks for wrong inputs and values, etc
      if not user_input[2] == ".":
         raise ValueError("There was not a decimal.")
      elif not type(user_input) == str:
         raise TypeError("Wrong type of user input.")
      elif not type(return_int) == bool:
         raise TypeError("return_int was not a boolean.")
      elif not len(user_input) == 4:
         raise ValueError("Wrong length of user input")
      if return_int:
         return int(f"{user_input[0]}{user_input[1]}{user_input[3]}")
      else:
         return f"{user_input[0]}{user_input[1]}{user_input[3]}"
   except:
      Exception("user_input_time_reader_exception")


def time_lengthener(time_input:int) ->str:
    if len(str(time_input)) == 1:
       return f"00{time_input}"
    elif len(str(time_input)) == 2:
       return f"0{time_input}"
    elif len(str(time_input)) == 3:
       return f"{time_input}"
    else:
       raise Exception("Wrong amount of digits in time.txt")    


def relative_time(user_input:str,return_int:bool):
   
   if return_int:
      return int(f"{time_lengthener(user_input_time_reader(user_input[1:],True)+read_time_file(True))}")
   else:
      return f"{time_lengthener(user_input_time_reader(user_input[1:],True)+read_time_file(True))}"

def check_rel_time(input:str):
   try:
      if input[:1] == "+":
         return True
      elif input[:1] == "":
         raise ValueError("Time input string was blank")
      else:
         return False
   except:
      Exception("check_rel_time")


def dotted_time_reader( input:str, return_int:bool):
   if check_rel_time(input):
      return relative_time(input, return_int)
   else:
      return user_input_time_reader(input, return_int)

def decimal_calculator(input_unlengthened:int):
   input = time_lengthener(input_unlengthened)
   return int(input[:-1]) * 4 + int(input[-1:])

def file_to_user_time(input) -> str:
    #converts file time to user YY.M time
    input_string = time_lengthener(int(input))
    return f"{input_string[:-1]}.{input_string[-1:]}"

def interval_shift():
   #shift the interval by 1
   file = read_items()
   for item in file.values():
      if item["interval"] and not item["started"]:
         item["remainingInterval"] -= 1
   write_items(file)
   #if the interval is zero, start the item again
   file = read_items()
   for item in file.values():
      if item["interval"] and item["remainingInterval"] == 0:
         item["started"] = True
   write_items(file) 
   

def shift_time():
   #increases time by one and logs it
    new_time = read_time_file(True)+1
    #makes the decimal place base 4 in accordance with how AC time works.
    if int(str(new_time)[-1:]) == 4:
        #"a" is the two digit part before where the decimal would go, ie: 56.2, "a" would be 56. "b" is the number after where the decimal would be, so 2.
        a = int(read_time_file(False)[:-1]) + 1
        b = 0
        new_time = f"{a}{b}"
    log(read_time_file(False),time_lengthener(new_time), "AC time" , "AC time")
    with open("time.txt","w") as file:
       file.write(time_lengthener(new_time))
    
    check_started()
    items_control()
    interval_shift()
    repeat()

def user_input_shift_time():
    """Enter either the new time in format YY.M , keeping in mind that this is AC time and thus formatted differently \n(ask in rp-general what AC time is, you'll need to know anyways), \nor enter the amount of time you want to increase by in format +YY.M\n """

    user_input = input("Input either the new time in format YY.M , keeping in mind that this is AC time and thus formatted differently \n(ask in rp-general what AC time is, you'll need to know anyways), \nor enter the amount of time you want to increase by in format +YY.M\n")
    time = dotted_time_reader(user_input,True)
    #amount of times to shift
    if check_rel_time(time):
      times = decimal_calculator(relative_time(time,True))
    else:
       times = decimal_calculator(time - read_time_file(True))

    for i in range(times):
       #shift by that amount of times
       shift_time()


def new_item():
   #takes name input
   name_input = input(" Input the name of your construciton here:\n")
   name = ""
   #checks for double quotes and escapes them
   for char in name_input:
      if char == "\"":
         name += "\""
      else:
         name += char
   #checks if the name is already in the file
   items = read_items()
   for item in items.values():
      if name == item["name"]:
         raise ValueError("Name already used.")
   #takes start time input

   start_time = dotted_time_reader(input("Input the start time for the entire cyclic operation in either +YY.M format indicating relative time(to current time) or simply YY.M format indicating actual time(ie: if I have a bunch of fighters I want to start producing two years from now, I would enter +02.0.)\n"),True)

   #takes duration input
   duration_input = input(" Input the time needed for a singular instance of your construction below in YY.M format indicating actual time here:\n")
   #converts it into an integer
   try:
      duration = user_input_time_reader(duration_input,True)
   except:
      Exception("Duration exception")
   #enters remaining time
   remaining_time = duration
   #calculates first end time
   end_time = read_time_file(True) + duration

   #takes interval input
   interval_input = input("Input the time between a singular instance of your construction below in similar format. If your construction is non-repeating, or there is no time between two instances, enter 00.0.\n")
   #converts it into an integer
   interval = dotted_time_reader(interval_input,True)

   #takes multiplier input
   multiplier = input("How many items are constructed per cycle?\n")
   try:
      #converts the multiplier input into an integer
      multiplier = int(multiplier)
   except:
      ValueError("Wrong input")
   #takes cap input
   cap = input("What is the max amount of cycles for this item? If there is no max, leave this empty.\n")
   #if cap is blank, make it false. if it is not, convert it into an integer.
   if cap == "":
      cap = False
   else:
      try:
         cap = int(cap)
      except:
         ValueError("Wrong input")
   if start_time <= read_time_file(True):
      started = True
   else:
      started = False
   if cap == 0 and type(cap) == int:
      print("I don't see why you would want a construction cycle that never does anything, but alright")
      finished = True
   times = 0
   amount = 0
   remaining_interval = 0
   finished = False
   #handles start time in the past
   if start_time< read_time_file(True):
      #calculates amount of time in decimals passed since start

      #calculates the difference in time between now and the start and formats it in a three-digit string, andcalculates the decimal equivalent of that time.
      decimals = decimal_calculator(read_time_file(True) - start_time )
      #Calculates the decimal equivalent of the duration...
      decimal_duration = decimal_calculator(int(duration))

      #the decimal equivalent of the interval...
      decimal_interval = decimal_calculator(int(interval))
      #...calculates the amount of cycles already happened...
      temp_times = int(decimals/(decimal_duration+decimal_interval))
      #...and handles the cap.
      for i in range(temp_times):
         if (type(cap) == int and times < cap) or (type(cap) == bool and not cap):
            times += 1
            finished = False
         else:
            finished = True
      #then, we handle the remaining time, if any
      remainder = (decimals - (decimal_duration+decimal_interval) * (decimals// (decimal_duration+decimal_interval)))
    #   times = decimals//(decimal_duration+decimal_interval)
      if remainder < decimal_duration:
         remaining_time = deci_to_ac(decimal_duration - remainder)
      else:
         remaining_time = duration
         remaining_interval = deci_to_ac(remainder) - remaining_time
      end_time = read_time_file(True) + int(remaining_time) + int(remaining_interval)
      #also, sort the amounts out
      amount = multiplier * times
   #write everything
   items[name] = {"name": name,
    "startTime": start_time,
    "duration": duration,
    "remainingTime": remaining_time,
    "endTime": end_time,
    "times": times,
    "amount": amount,
    "interval": interval,
    "remainingInterval": remaining_interval,
    "multiplier": multiplier,
    "cap": cap,
    "started": started,
    "finished": finished}
   write_items(items)


def get_all(amount: bool):
   items = read_items()
   list1 = []
   #gets all items in files
   #if we're not asking for amount
   for item in items.values():
    if not amount:
        
        #adds all relevant data to a list and adds it to list1
        list1.append([
            f'name:{item["name"]}',
            f'starting time = {file_to_user_time(item["startTime"])}AC',
            f'Time per construction = {file_to_user_time(item["duration"])}AC',
            f'remaining time in current construction = {file_to_user_time(item["remainingTime"])}AC',
            f'end-time of current construction = {file_to_user_time(item["endTime"])}AC',
            f'amount of cycles completed = {item["times"]}',
            f'amount of items constructed = {item["amount"]}',
            f'delay between cycles = {item["interval"]}AC',
            f'current remaining delay = {item["remainingInterval"]}AC',
            f'amount of items constructed per cycle = {item["multiplier"]}',
            f'max number of cycles = {item["cap"]}',
            f'items currently under construction? {item["started"]}',
            f'cycle finished? {item["finished"]}',
            "\n\n"
            ])
    else:
        list1.append(
            [
                f'name:{item["name"]} - amount of items constructed = {item["amount"]}'

                ]
        )
      
   return list1

def check_specific(input:str,amount_only: bool) -> str:
   """input the name, being case sensitive, and then this should spit out that item"""
   items = read_items()
   for item in items.values():
      #if the input is equal to the item
      if item["name"] == input:
         #if not amount only, return everything
         if not amount_only:
            return [[
         f'name:{item["name"]}',
         f'starting time = {file_to_user_time(item["startTime"])}AC',
         f'Time per construction = {file_to_user_time(item["duration"])}AC',
         f'remaining time in current construction = {file_to_user_time(item["remainingTime"])}AC',
         f'end-time of current construction = {file_to_user_time(item["endTime"])}AC',
         f'amount of cycles completed = {item["times"]}',
         f'amount of items constructed = {item["amount"]}',
         f'delay between cycles = {item["interval"]}AC',
         f'current remaining delay = {item["remainingInterval"]}AC',
         f'amount of items constructed per cycle = {item["multiplier"]}',
         f'max number of cycles = {item["cap"]}',
         f'items currently under construction? {item["started"]}',
         f'cycle finished? {item["finished"]}',
         "\n\n"
         ]]
         else:
            return[[
               f'name:{item["name"]} - amount of items constructed = {item["amount"]}'

            ]]
        
def check(input, amount:bool):
   with open("output_for_copying.txt","w") as file:
      file.write("")
   if not input:
    list1 = get_all(amount)
    
   else:
    list1 = check_specific(input, amount)
   for item in list1:
      for i in item:
         with open("output_for_copying.txt","a") as file:
            file.write(f"{i}\n")
         print(i)

while 1:
   main_input = int(input(f"""The time now is {file_to_user_time(read_time_file(True))} input below: do you want to
   1: change the time
   2: make a new item
   3: check items
   """))
   if main_input == 1:
      user_input_shift_time()
   elif main_input == 2:
      new_item()
   else:
      check_input = input(f"""If you wish to check a specific item, enter the name. If not, enter \"0\"\n""")
      amount_input = int(input("If you wish to only check the amount of items, enter 1. If not, enter 0.\n"))
      print("\n")
      try:
         check_input = int(check_input)
      except ValueError:
         check(check_input,amount_input)
      else:
         check(check_input, amount_input)
      print("\n")
   





      


