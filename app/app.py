import sys
import os
DIR=os.path.dirname(os.path.abspath(__file__))
# sys.path.append(f'{DIR}\\lib\\win32')
# sys.path.append(f'{DIR}\\lib\\win32\\lib')
import getpass
from colorama import Fore, Back, Style, init
import paramiko
import requests_negotiate_sspi


init(autoreset=True)

def display_welcome_message():
    print(f"{Fore.CYAN + Style.BRIGHT  }############## CENOP ############")
    print(f"{Fore.YELLOW + Style.BRIGHT}Check Environment, No Password :)\n")

def display_colors():
    print(f"\n{Style.DIM}Foreground colors:")
    print(f"{Fore.BLACK}BLACK")
    print(f"{Fore.RED}RED")
    print(f"{Fore.GREEN}GREEN")
    print(f"{Fore.YELLOW}YELLOW")
    print(f"{Fore.BLUE}BLUE")
    print(f"{Fore.MAGENTA}MAGENTA")
    print(f"{Fore.CYAN}CYAN")
    print(f"{Fore.WHITE}WHITE")


    print(f"{Style.BRIGHT}Foreground colors (BRIGHT):")
    print(f"{Style.BRIGHT + Fore.BLACK}BRIGHT BLACK")
    print(f"{Style.BRIGHT + Fore.RED}BRIGHT RED")
    print(f"{Style.BRIGHT + Fore.GREEN}BRIGHT GREEN")
    print(f"{Style.BRIGHT + Fore.YELLOW}BRIGHT YELLOW")
    print(f"{Style.BRIGHT + Fore.BLUE}BRIGHT BLUE")
    print(f"{Style.BRIGHT + Fore.MAGENTA}BRIGHT MAGENTA")
    print(f"{Style.BRIGHT + Fore.CYAN}BRIGHT CYAN")
    print(f"{Style.BRIGHT + Fore.WHITE}BRIGHT WHITE")
   

    print(f"\n{Style.BRIGHT}Background colors:")
    print(f"{Back.BLACK}{Fore.WHITE}BLACK BACKGROUND{Style.RESET_ALL}")
    print(f"{Back.RED}RED BACKGROUND{Style.RESET_ALL}")
    print(f"{Back.GREEN}GREEN BACKGROUND{Style.RESET_ALL}")
    print(f"{Back.YELLOW}YELLOW BACKGROUND{Style.RESET_ALL}")
    print(f"{Back.BLUE}BLUE BACKGROUND{Style.RESET_ALL}")
    print(f"{Back.MAGENTA}MAGENTA BACKGROUND{Style.RESET_ALL}")
    print(f"{Back.CYAN}CYAN BACKGROUND{Style.RESET_ALL}")
    print(f"{Back.WHITE}{Fore.BLACK}WHITE BACKGROUND{Style.RESET_ALL}")

    print(f"\n{Style.BRIGHT}Text styles:")
    print(f"{Style.DIM}DIM")
    print(f"{Style.NORMAL}NORMAL")
    print(f"{Style.BRIGHT}BRIGHT")

def display_menu(user):
    print(f"{Fore.YELLOW}1. Check user [{Fore.YELLOW+Style.BRIGHT}{user}{Style.RESET_ALL}{Fore.YELLOW}]")
    print(f"{Fore.YELLOW}2. Check another user")
    print(f"{Fore.YELLOW}3. Show console colors")
    print(f"{Fore.YELLOW}q. Quit")

def handle_choice(choice, user):
    if choice == '1' or not choice:
        check(user)
    elif choice == '2':
        user = input('User: ')
        check(user)
    elif choice == '3':
        display_colors()
    elif choice == 'q':
        print(f"{Fore.RED}Exiting...")
    else:
        print(f"{Fore.RED}Invalid choice, please select again")
    return user 

def check(user):
    print(f'Checking {user}]...')


def main():
    user = getpass.getuser()
    display_welcome_message()
    choice = None

    while choice != 'q':
        display_menu(user)
        choice = input("Your choice [1]: ").lower()
        user = handle_choice(choice, user)



if __name__ == "__main__":

    main()
