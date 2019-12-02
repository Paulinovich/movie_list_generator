import random

def get_users_shuffled():
    """
    (none) --> list
    
    asks for the names of the viewers and saves the input in a list containing the names in a random order.
    """
    print("\nPlease enter the names of the specators.\nWhen finished, just press enter.\n")
    name="start"
    number=1
    list_names=[]
    while len(name)!=0:
        name=input("Viewer {0} : ".format(number))
        if len(name)!=0:
            list_names.append(name)
        number+=1
    random.shuffle(list_names)
    return list_names

def print_users(list_names):
    #for now shows them all at once, will later be changed to show the names when they have to pick (with user interface)
    for user in list_names:
        print(user+"\n")
        
    
    
        
    

