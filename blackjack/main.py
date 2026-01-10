import copy 
import random
import pygame
pygame.mixer.init()

pygame.font.init()
# game variables
cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
one_deck = 4 * cards 
decks = 4
WIDTH = 600
HEIGHT = 900
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('Pygame Blackjack!')
fps = 60 
timer = pygame.time.Clock()
font = pygame.font.SysFont('Verdana', 42, bold=True)
smaller_font = pygame.font.SysFont('Verdana', 30)
active = False
# win, loss, draw
records = [0, 0, 0]
player_score = 0
dealer_score = 0
initial_deal = False 
my_hand = []
dealer_hand = []
outcome = 0
reveal_dealer = False
hand_active = False
outcome = 0
add_scores = False
results = ['', 'PLAYER BUSTED :/', 'PLAYER WINS! :)', 'DEALER WINS :(', 'TIE GAME...' ]
deal_sfx = pygame.mixer.Sound('sounds/deal.mp3')
deal_sfx.set_volume(0.02)
win_sfx = pygame.mixer.Sound('sounds/youwin.mp3')
lose_sfx = pygame.mixer.Sound('sounds/ohno.mp3')
card_anim_y = -300
card_anim_speed = 25



# deal cards by selecting randomly from deck, and make function for one card at a time
def deal_cards(current_hand, current_deck):
    card = random.randint(0, len(current_deck))
    current_hand.append(current_deck[card - 1])
    current_deck.pop(card - 1)
    deal_sfx.play()
    return current_hand, current_deck




# draw scores for player and dealer on screen 
def draw_scores(player, dealer):
    screen.blit(font.render(f'PLAYER: {player}', True, 'white'), (310, 410))
    if reveal_dealer:
        screen.blit(font.render(f'DEALER: {dealer}', True, 'white'), (310, 110))



#draw cards cisually onto screen
def draw_cards(player, dealer, reveal):
    for i in range(len(player)):
        pygame.draw.rect(screen, 'white', [70 + (70 * i), 460 + (5 * i) + card_anim_y, 120, 220], 0, 5)
        screen.blit(font.render(player[i], True, 'black'), (75 + 70 * i, 465 + 5 * i + card_anim_y))
        screen.blit(font.render(player[i], True, 'black'), (75 + 70 * i, 635 + 5 * i + card_anim_y))
        pygame.draw.rect(screen, 'red', [70 + (70 * i), 460 + (5 * i), 120, 220], 5, 5)
    
    #if player hasn't finished turn, dealer will hide one card 
    for i in range(len(dealer)):
        pygame.draw.rect(screen, 'white', [70 + (70 * i), 160 + (5 * i) + card_anim_y, 120, 220], 0, 5)
        if i != 0 or reveal:
            screen.blit(font.render(dealer[i], True, 'black'), (75 + 70 * i, 165 + 5 * i + card_anim_y))
            screen.blit(font.render(dealer[i], True, 'black'), (75 + 70 * i, 335 + 5 * i + card_anim_y))
        else: 
            screen.blit(font.render('???', True, 'black'), (75 + 70 * i, 165 + 5 * i + card_anim_y))
            screen.blit(font.render('???', True, 'black'), (75 + 70 * i, 335 + 5 * i + card_anim_y))

        pygame.draw.rect(screen, 'blue', [70 + (70 * i), 160 + (5 * i), 120, 220], 5, 5)
    

# pass in player or dealer hand and get best score possibollke
def calculate_score(hand):
    #calculate hand score fresh every time, check how many aces we have
    hand_score = 0 
    aces_count = hand.count('A')
    for i in range(len(hand)):
        # for 2, 3, 4, 5, 6, 7, 8, 9 - just ad the number to total 
        for j in range(8):
            if hand[i] == cards[j]:
                hand_score += int(hand[i])
        # fpr 10 and face cards, add 10
        if hand[i] in ['10', 'J', 'Q', 'K']:
            hand_score += 10
        # for aces start by adding 11, we'll check if we need to reduce afterwards 
        # kan ook else want ace zou laatste kaart moeten zijn, maar dit is voor extra vcoorzichtig te zijn
        elif hand[i] == 'A': 
            hand_score += 11
     # determine how many aces need to be 1 instead of 11 to get under 21 if possible
    if hand_score > 21 and aces_count > 0:
        for i in range(aces_count):
            if hand_score > 21: 
                hand_score -= 10
    return hand_score 
            


# draw game conditions and buttons
def draw_game(act, record, result):
    button_list = []
    # initialy on startop (not active) only option is to deal new hand 
    if not act:
        deal = pygame.draw.rect(screen, 'white', [150, 20, 300, 100], 0, 5)
        pygame.draw.rect(screen, 'green', [150, 20, 300, 100], 3, 5)
        deal_text = font.render('DEAL HAND', True, 'black')
        screen.blit(deal_text, (165, 50))
        button_list.append(deal)
    # once game started, shot hit and stand buttons and win/loss records
    else:
        hit = pygame.draw.rect(screen, 'white', [0, 700, 300, 100], 0, 12)
        if hit.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(screen, (46, 204, 113), hit, 4, 12)  # licht groen
        else:
             pygame.draw.rect(screen, (39, 174, 96), hit, 3, 12)  # donker groen
        hit_text = font.render('HIT ME', True, (20, 20, 20))
        screen.blit(hit_text, (60, 735))
        button_list.append(hit)
        stand = pygame.draw.rect(screen, 'white', [300, 700, 300, 100], 0, 12)

        if stand.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(screen, (231, 76, 60), stand, 4, 12)  # rood hover
        else:
            pygame.draw.rect(screen, (192, 57, 43), stand, 3, 12)

        stand_text = font.render('STAND', True, (20, 20, 20))
        screen.blit(stand_text, (370, 735))

        button_list.append(stand)

        score_text = smaller_font.render(f'Wins: {record[0]}   Losses: {record[1]}   Draws: {record[2]}', True, 'white')
        screen.blit(score_text, (15, 840))
    # if there is an outcome for hand that was played, display a restart button and tell user what happend
    if result != 0:
        screen.blit(font.render(results[result], True, 'white'), (15, 25))
        deal = pygame.draw.rect(screen, 'white', [150, 220, 300, 100], 0, 5)
        pygame.draw.rect(screen, 'green', [150, 220, 300, 100], 3, 5)
        pygame.draw.rect(screen, 'black', [153, 223, 294, 84], 3, 5)
        deal_text = font.render('NEW HAND', True, 'black')
        screen.blit(deal_text, (165, 250))
        button_list.append(deal)
    return button_list

# check endgame conditions function
def check_endgame(hand_act, deal_score, play_score, result, totals, add):
    # check end game scenarios if player has stood, busted or blackjacked
    # result 1-player bust, 2-win, 3-loss, 4-push
    if not hand_act and deal_score >= 17:
        if play_score > 21:
            result = 1
        elif deal_score < play_score <= 21 or deal_score > 21:
            result = 2
        elif play_score < deal_score <= 21:
            result = 3
        else: 
            result = 4
        if add:
            if result == 1 or result == 3:
                totals[1] += 1
                lose_sfx.play()
            elif result == 2:
                totals[0] += 1
                win_sfx.play()
            else:
                totals[2] += 1
            add = False
    return result, totals, add



# main game loop
run = True
while run:
    # run game at our framerate and fill screen with bg color groen!!!
    timer.tick(fps)
    # achtergrond
    screen.fill((18, 32, 47))  # donker blauw
    # tafel
    pygame.draw.rect(screen, (39, 174, 96), [20, 140, 560, 560], border_radius=30)
    pygame.draw.rect(screen, (20, 120, 70), [20, 140, 560, 560], 4, border_radius=30)

    # initial deal to player and dealer
    if initial_deal:
        for i in range(2):
            my_hand, game_deck = deal_cards(my_hand, game_deck)
            dealer_hand, game_deck = deal_cards(dealer_hand, game_deck)   
        initial_deal = False
    # once game is activated, and dealt, calculate scores and display cards
    if active:
        player_score = calculate_score(my_hand)
        if card_anim_y < 0:
            card_anim_y += card_anim_speed
            if card_anim_y > 0:
                card_anim_y = 0

        draw_cards(my_hand, dealer_hand, reveal_dealer)
        if reveal_dealer:
            dealer_score = calculate_score(dealer_hand)
            if dealer_score < 17:
                pygame.time.delay(500)
                dealer_hand, game_deck = deal_cards(dealer_hand, game_deck)
        draw_scores(player_score, dealer_score)
    buttons = draw_game(active, records, outcome)
    mouse_over_button = False
    for button in buttons:
        if button.collidepoint(pygame.mouse.get_pos()):
           mouse_over_button = True

    if mouse_over_button:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)


    # event handling, if quit pressed, then exit game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONUP:
            if not active:
                if buttons[0].collidepoint(event.pos):
                    card_anim_y = -300
                    active = True
                    initial_deal = True
                    game_deck = copy.deepcopy(decks * one_deck) 
                    my_hand = []
                    dealer_hand = []
                    outcome = 0
                    hand_active = True
                    reveal_dealer = False
                    outcome = 0
                    add_scores = True
            else:
                # if player can hit, allow them to draw a card
                if buttons[0].collidepoint(event.pos) and player_score < 21 and hand_active:
                    my_hand, game_deck = deal_cards(my_hand, game_deck)
                    card_anim_y
                # allow player to end turn (stand)
                elif buttons [1].collidepoint(event.pos) and not reveal_dealer:
                    reveal_dealer = True
                    hand_active = False
                elif len(buttons) == 3:
                    if buttons[2].collidepoint(event.pos):
                        card_anim_y = -300
                        active = True
                        initial_deal = True
                        game_deck = copy.deepcopy(decks * one_deck) 
                        my_hand = []
                        dealer_hand = []
                        outcome = 0
                        hand_active = True
                        reveal_dealer = False
                        outcome = 0
                        add_scores = True
                        dealer_score = 0
                        player_score = 0

    # if player busts, automatically end turn - treat like a stand 
    if hand_active and player_score >= 21:
        hand_active = False 
        reveal_dealer = True         


    outcome, records, add_scores = check_endgame(hand_active, dealer_score, player_score, outcome, records, add_scores) 

      

                 



    pygame.display.flip()    
pygame.quit()