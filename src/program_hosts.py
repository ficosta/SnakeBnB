from colorama import Fore
from dateutil import parser

from infrastructure.switchlang import switch
import infrastructure.state as state
import services.data_services as svc

def run():
    print(' ****************** Welcome host **************** ')
    print()

    show_commands()

    while True:
        action = get_action()

        with switch(action) as s:
            s.case('c', create_account)
            s.case('a', log_into_account)
            s.case('l', list_cages)
            s.case('r', register_cage)
            s.case('u', update_availability)
            s.case('v', view_bookings)
            s.case('m', lambda: 'change_mode')
            s.case(['x', 'bye', 'exit', 'exit()'], exit_app)
            s.case('?', show_commands)
            s.case('', lambda: None)
            s.default(unknown_command)

        if action:
            print()

        if s.result == 'change_mode':
            return


def show_commands():
    print('What action would you like to take:')
    print('[C]reate an account')
    print('Login to your [a]ccount')
    print('[L]ist your cages')
    print('[R]egister a cage')
    print('[U]pdate cage availability')
    print('[V]iew your bookings')
    print('Change [M]ode (guest or host)')
    print('e[X]it app')
    print('[?] Help (this info)')
    print()


def create_account():
    print(' ****************** REGISTER **************** ')
    name = input('Qual o seu nome? ')
    email = input('Seu email? ').strip().lower()

    old_account = svc.find_account_by_email(email)

    if old_account:
        error_msg(f"ERRO: A conta com o email {email} já existe.")
        return

    state.active_account = svc.create_account(name, email)
    success_msg(f"Nova conta com o id {state.active_account.id} criada com sucesso!")

def log_into_account():
    print(' ****************** LOGIN **************** ')

    email = input("Qual o seu email? ").strip().lower()
    account = svc.find_account_by_email(email)

    if not account:
        error_msg(f"Nao foi possivel encontrar suas conta com o email: {email}")

    state.active_account = account
    success_msg("Login com sucesso")


def register_cage():
    print(' ****************** REGISTER CAGE **************** ')

    if not state.active_account:
        error_msg("Voce precisa estar logado para continuar.")
        return

    meters = input("Quantos metros quadrados é a gaiola? ")
    if not meters:
        error_msg("Cancelado")
        return

    meters = float(meters)
    carpeted = input("Tem carpete [y, n]? ").lower().startswith('y')
    has_toys = input("Tem brinquedos [y, n]? ").lower().startswith('y')
    allow_dangerous = input("Pode receber cobras venenosas [y, n]? ").lower().startswith('y')
    name = input("Qual o nome? ")
    price = float(input("Qual o valor? "))

    cage = svc.register_cage(
        state.active_account, name,
        allow_dangerous, has_toys, carpeted, meters, price
    )

    state.reload_account()
    success_msg(f"Gaiola com o id {cage.id} registrada")




def list_cages(suppress_header=False):
    if not suppress_header:
        print(' ******************     Your cages     **************** ')

    if not state.active_account:
        error_msg("Voce precisa estar logado para continuar.")
        return

    cages = svc.find_cages_for_user(state.active_account)
    print(f"Você tem {len(cages)} gaiolas.")

    for idx, c in enumerate(cages):
        print(f' {idx}.  {c.name} tem {c.square_meters} metros.')
        for b in c.bookings:
            reserva = 'Sim' if b.booked_date is not None else 'Não'
            print(f"Reserva: {b.check_in_date}, {(b.check_out_date - b.check_in_date).days} dias. Reservado? {reserva}")


def update_availability():
    print(' ****************** Add available date **************** ')

    if not state.active_account:
        error_msg("Voce precisa estar logado para continuar.")
        return

    list_cages(suppress_header=True)

    cage_number = input("Digite o numero da gaiola: ")
    if not cage_number.strip():
        error_msg("Cancelado")
        print()
        return

    cage_number = int(cage_number)

    cages = svc.find_cages_for_user(state.active_account)
    selected_cage = cages[cage_number - 1]

    success_msg(f"Gaiola {selected_cage.name} selecionada")

    start_date = parser.parse(
        input("Digite a data disponivel [yyyy-mm-dd]:")
    )
    days = int(input("Quantos dias?"))

    svc.add_available_date(
        selected_cage,
        start_date,
        days
    )

    success_msg(f"Data adicionada para a gaiola {selected_cage.name}")

    # TODO: Choose cage
    # TODO: Set dates, save to DB.

    print(" -------- NOT IMPLEMENTED -------- ")


def view_bookings():
    print(' ****************** Your bookings **************** ')

    # TODO: Require an account
    # TODO: Get cages, and nested bookings as flat list
    # TODO: Print details for each

    print(" -------- NOT IMPLEMENTED -------- ")


def exit_app():
    print()
    print('bye')
    raise KeyboardInterrupt()


def get_action():
    text = '> '
    if state.active_account:
        text = f'{state.active_account.name}> '

    action = input(Fore.YELLOW + text + Fore.WHITE)
    return action.strip().lower()


def unknown_command():
    print("Sorry we didn't understand that command.")


def success_msg(text):
    print(Fore.LIGHTGREEN_EX + text + Fore.WHITE)


def error_msg(text):
    print(Fore.LIGHTRED_EX + text + Fore.WHITE)
