import socket
import pickle
import pygame
from gamedata import *
import comm

class Client():
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def input_addr(self):
        server_ip = input("Enter server IP: ")
        server_port = input("Enter server port: ")
        self.addr = (server_ip, int(server_port))

    def connect(self):
        try:
            self.socket.connect(self.addr)
        except:
            print('Connection failed')
            pass

class Game():
    def __init__(self, client):
        pygame.init()

        field_dimensions = (500, 500)
        self.client = client
        self.window = pygame.display.set_mode(field_dimensions)

    def render(self, game_data):
        self.window.fill((0, 0, 0))
        snakes = game_data.snakes
        for snake in snakes:
            for body_part in snake:
                rect = (body_part.position[0], body_part.position[1], body_part.width - 2, body_part.width - 2)
                pygame.draw.rect(self.window, body_part.color, rect);
        pygame.display.update()

    def get_direction(self):
        direction = None
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]):
            direction = (-1, 0)
        elif (keys[pygame.K_RIGHT] or keys[pygame.K_d]):
            direction = (1, 0)
        elif (keys[pygame.K_UP] or keys[pygame.K_w]):
            direction = (0, -1)
        elif (keys[pygame.K_DOWN] or keys[pygame.K_s]):
            direction = (0, 1)
        return direction

    def game_loop(self):
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.client.socket.send(pickle.dumps(comm.Signal.QUIT))
                    self.running = False
            if not self.running: break
            self.client.socket.send(pickle.dumps(self.get_direction()))
            
            size_as_bytes = comm.receive_data(self.client.socket, comm.MSG_LEN)
            length = comm.size_as_int(size_as_bytes)
            game_data = pickle.loads(comm.receive_data(self.client.socket, length))
            self.render(game_data)
        pygame.quit()

def main():
    client = Client()
    client.input_addr()
    client.connect()
    game = Game(client)
    game.game_loop()

if __name__ == "__main__":
    main()
