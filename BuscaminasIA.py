import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 400, 450
GRID_SIZE = 10
CELL_SIZE = WIDTH // GRID_SIZE
MINE_COUNT = 4

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Create the window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Buscaminas con IA integrada")

# Font
font = pygame.font.Font(None, 36)

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.neighbor_mines = 0

    def draw(self):
        rect = pygame.Rect(self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        if self.is_revealed:
            pygame.draw.rect(screen, WHITE, rect)
            if self.is_mine:
                pygame.draw.circle(screen, BLACK, rect.center, CELL_SIZE // 4)
            elif self.neighbor_mines > 0:
                text = font.render(str(self.neighbor_mines), True, BLACK)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)
        else:
            pygame.draw.rect(screen, GRAY, rect)
        
        if self.is_flagged:
            pygame.draw.polygon(screen, RED, [
                (self.x * CELL_SIZE + CELL_SIZE // 4, self.y * CELL_SIZE + CELL_SIZE // 4),
                (self.x * CELL_SIZE + CELL_SIZE // 4, self.y * CELL_SIZE + CELL_SIZE * 3 // 4),
                (self.x * CELL_SIZE + CELL_SIZE * 3 // 4, self.y * CELL_SIZE + CELL_SIZE // 2)
            ])
        
        pygame.draw.rect(screen, BLACK, rect, 1)

class Game:
    def __init__(self):
        self.grid = [[Cell(x, y) for y in range(GRID_SIZE)] for x in range(GRID_SIZE)]
        self.place_mines()
        self.calculate_neighbor_mines()
        self.game_over = False
        self.won = False

    def place_mines(self):
        mines_placed = 0
        while mines_placed < MINE_COUNT:
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if not self.grid[x][y].is_mine:
                self.grid[x][y].is_mine = True
                mines_placed += 1

    def calculate_neighbor_mines(self):
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                if not self.grid[x][y].is_mine:
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and self.grid[nx][ny].is_mine:
                                self.grid[x][y].neighbor_mines += 1

    def reveal(self, x, y):
        if self.grid[x][y].is_revealed or self.grid[x][y].is_flagged:
            return

        self.grid[x][y].is_revealed = True

        if self.grid[x][y].is_mine:
            self.game_over = True
        elif self.grid[x][y].neighbor_mines == 0:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                        self.reveal(nx, ny)

        if self.check_win():
            self.won = True
            self.game_over = True

    def flag(self, x, y):
        if not self.grid[x][y].is_revealed:
            self.grid[x][y].is_flagged = not self.grid[x][y].is_flagged

    def check_win(self):
        for row in self.grid:
            for cell in row:
                if not cell.is_mine and not cell.is_revealed:
                    return False
        return True

    def draw(self):
        for row in self.grid:
            for cell in row:
                cell.draw()

        if self.game_over:
            text = "La IA gano" if self.won else "La IA perdio"
            text_surface = font.render(text, True, BLACK)
            text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT - 25))
            screen.blit(text_surface, text_rect)

class LogicalAI:
    def __init__(self, game):
        self.game = game

    def get_neighbors(self, x, y):
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and (nx, ny) != (x, y):
                    neighbors.append((nx, ny))
        return neighbors

    def get_safe_moves(self):
        safe_moves = []
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                cell = self.game.grid[x][y]
                if cell.is_revealed and cell.neighbor_mines > 0:
                    neighbors = self.get_neighbors(x, y)
                    unrevealed_neighbors = [(nx, ny) for nx, ny in neighbors if not self.game.grid[nx][ny].is_revealed]
                    flagged_neighbors = [(nx, ny) for nx, ny in neighbors if self.game.grid[nx][ny].is_flagged]
                    
                    if len(flagged_neighbors) == cell.neighbor_mines:
                        safe_moves.extend([(nx, ny) for nx, ny in unrevealed_neighbors if not self.game.grid[nx][ny].is_flagged])
        
        return list(set(safe_moves))

    def get_certain_mines(self):
        certain_mines = []
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                cell = self.game.grid[x][y]
                if cell.is_revealed and cell.neighbor_mines > 0:
                    neighbors = self.get_neighbors(x, y)
                    unrevealed_neighbors = [(nx, ny) for nx, ny in neighbors if not self.game.grid[nx][ny].is_revealed]
                    flagged_neighbors = [(nx, ny) for nx, ny in neighbors if self.game.grid[nx][ny].is_flagged]
                    
                    if len(unrevealed_neighbors) + len(flagged_neighbors) == cell.neighbor_mines:
                        certain_mines.extend([(nx, ny) for nx, ny in unrevealed_neighbors if not self.game.grid[nx][ny].is_flagged])
        
        return list(set(certain_mines))

    def make_move(self):
        # First, check for any certain mines and flag them
        certain_mines = self.get_certain_mines()
        for x, y in certain_mines:
            self.game.flag(x, y)

        # Then, check for any safe moves
        safe_moves = self.get_safe_moves()
        if safe_moves:
            x, y = random.choice(safe_moves)
            self.game.reveal(x, y)
            return x, y

        # If no safe moves, make a random move on an unrevealed, unflagged cell
        unrevealed_cells = [(x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE) 
                            if not self.game.grid[x][y].is_revealed and not self.game.grid[x][y].is_flagged]
        if unrevealed_cells:
            x, y = random.choice(unrevealed_cells)
            self.game.reveal(x, y)
            return x, y

        return None

def main():
    game = Game()
    ai = LogicalAI(game)
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not game.game_over:
            move = ai.make_move()
            if move:
                x, y = move
                pygame.draw.rect(screen, GREEN, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 2)
            else:
                game.game_over = True

        screen.fill(WHITE)
        game.draw()
        pygame.display.flip()
        clock.tick(1)  # Limit to 1 FPS for visibility

    pygame.quit()

if __name__ == "__main__":
    main()