import pygame
import sys
import collections

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
BOUNDARY_COLOR = WHITE

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game Map Region Coloring - Boundary Fill")
clock = pygame.time.Clock()

def draw_map_boundaries(surface):
    """Draws enclosed regions to simulate a game map."""
    surface.fill(BLACK)
    
    # Draw various intersecting polygons and lines to create regions
    pygame.draw.polygon(surface, BOUNDARY_COLOR, [(100, 100), (300, 100), (400, 250), (200, 350), (50, 200)], 3)
    pygame.draw.circle(surface, BOUNDARY_COLOR, (600, 200), 100, 3)
    pygame.draw.rect(surface, BOUNDARY_COLOR, (400, 300, 250, 200), 3)
    pygame.draw.polygon(surface, BOUNDARY_COLOR, [(150, 400), (350, 400), (300, 550), (100, 500)], 3)
    
    # Additional lines to divide regions
    pygame.draw.line(surface, BOUNDARY_COLOR, (100, 100), (600, 500), 3)
    pygame.draw.line(surface, BOUNDARY_COLOR, (400, 300), (600, 200), 3)


def boundary_fill(surface, start_x, start_y, fill_color, boundary_color):
    """
    Iterative Boundary Fill Algorithm (4-connected) using Pygame PixelArray.
    Uses a Queue for Breadth-First-Search to prevent RecursionError.
    Boundary Fill fills until it hits the specific 'boundary_color'.
    """
    width, height = surface.get_size()
    
    # Ensure start coordinates are within bounds
    if not (0 <= start_x < width and 0 <= start_y < height):
        return

    # Lock the surface for pixel modification
    pixels = pygame.PixelArray(surface)
    
    fill_color_mapped = surface.map_rgb(fill_color)
    boundary_color_mapped = surface.map_rgb(boundary_color)
    
    target_start_color = pixels[start_x, start_y]
    
    # If the starting pixel is already the boundary or the fill color, do nothing
    if target_start_color == boundary_color_mapped or target_start_color == fill_color_mapped:
        pixels.close()
        return

    # Queue for filling process
    queue = collections.deque([(start_x, start_y)])
    
    # Track visited pixels to avoid redundant queue additions
    visited = set([(start_x, start_y)])

    while queue:
        cx, cy = queue.popleft()
        
        # Color the current pixel
        pixels[cx, cy] = fill_color_mapped
        
        # Check and add 4-connected neighbors
        neighbors = [
            (cx + 1, cy),
            (cx - 1, cy),
            (cx, cy + 1),
            (cx, cy - 1)
        ]
        
        for nx, ny in neighbors:
            if 0 <= nx < width and 0 <= ny < height:
                if (nx, ny) not in visited:
                    neighbor_color = pixels[nx, ny]
                    # Boundary Fill logic: Fill if NOT boundary and NOT already this fill color
                    if neighbor_color != boundary_color_mapped and neighbor_color != fill_color_mapped:
                        visited.add((nx, ny))
                        queue.append((nx, ny))
                        
    # Unlock surface
    pixels.close()

def main():
    # Draw the initial map layout
    draw_map_boundaries(screen)
    
    colors = [RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA]
    color_index = 0
    current_fill_color = colors[color_index]
    
    running = True
    print("Welcome to Game Map Region Coloring!")
    print("Left Click inside an empty shape to fill it (auto-cycles colors).")
    print("Right Click inside a colored shape to deselect it.")
    print("Press SPACE to change the fill color manually.")
    print("Press 'R' to reset the map.")
    print("Press 'Q' or ESC to quit.")
    
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_SPACE:
                    color_index = (color_index + 1) % len(colors)
                    current_fill_color = colors[color_index]
                    print(f"Fill color changed.")
                elif event.key == pygame.K_r:
                    draw_map_boundaries(screen)
                    print("Map reset.")
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                current_pixel_color = screen.get_at((mouse_x, mouse_y))
                # Get the integer mapped colors directly from the surface using map_rgb
                boundary_color_mapped = screen.map_rgb(BOUNDARY_COLOR)
                
                # We need to map the current color first to verify the surface format
                mapped_fill_color = screen.map_rgb(current_fill_color)
                
                if event.button == 1: # Left click
                    # Fill logic: Check if we are clicking on empty space (Black) or an already colored space
                    # We only prevent filling if we click exactly on the boundary line
                    if current_pixel_color != boundary_color_mapped:
                        # If the pixel is already the color we want to paint it, do nothing to prevent infinite loops
                        if current_pixel_color != mapped_fill_color:
                            print(f"Applying Boundary Fill at ({mouse_x}, {mouse_y}) with color {current_fill_color}")
                            boundary_fill(screen, mouse_x, mouse_y, current_fill_color, BOUNDARY_COLOR)
                            # Cycle to the next color for the next click
                            color_index = (color_index + 1) % len(colors)
                            current_fill_color = colors[color_index]
                elif event.button == 3: # Right click
                    black_mapped = screen.map_rgb(BLACK)
                    if current_pixel_color != boundary_color_mapped and current_pixel_color != black_mapped:
                        print(f"Deselecting region at ({mouse_x}, {mouse_y})")
                        boundary_fill(screen, mouse_x, mouse_y, BLACK, BOUNDARY_COLOR)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
