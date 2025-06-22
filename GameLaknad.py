import pygame
import sys
import random

# Inisialisasi Pygame
pygame.init()

# Dapatkan ukuran layar HP secara otomatis
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h

# Buat layar fullscreen
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Flappy Bird Fullscreen")

# Warna
SKY_BLUE = (113, 197, 207)
GREEN = (76, 175, 80)
RED = (231, 76, 60)
YELLOW = (241, 196, 15)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Variabel game
clock = pygame.time.Clock()
FPS = 60
gravity = 0.5
bird_movement = 0
score = 0
high_score = 0
game_active = False

# Hitung ukuran relatif berdasarkan layar
bird_radius = max(30, HEIGHT // 50)
pipe_width = max(60, WIDTH // 12)
pipe_gap = max(150, HEIGHT // 4)
#Kekuatan terbang burung
bird_flap_power = -HEIGHT // 450

# Font (ukuran responsif)
font_size = max(24, HEIGHT // 30)
big_font_size = max(50, HEIGHT // 15)
font = pygame.font.SysFont(None, font_size)
big_font = pygame.font.SysFont(None, big_font_size)

class Bird:
    def __init__(self):
        self.x = WIDTH // 4
        self.y = HEIGHT // 2
        self.radius = bird_radius
        self.flap_power = bird_flap_power
    
    def draw(self):
        pygame.draw.circle(screen, YELLOW, (self.x, int(self.y)), self.radius)
        # Mata
        pygame.draw.circle(screen, BLACK, (self.x + self.radius//2, int(self.y) - self.radius//4), self.radius//4)
        # Paruh
        pygame.draw.polygon(screen, RED, [
            (self.x + self.radius*0.8, int(self.y)),
            (self.x + self.radius*1.5, int(self.y) - self.radius//3),
            (self.x + self.radius*1.5, int(self.y) + self.radius//3)
        ])
    
    def update(self):
        global bird_movement
        bird_movement += gravity
        self.y += bird_movement
        
        # Batas atas/bawah
        if self.y < self.radius:
            self.y = self.radius
        if self.y > HEIGHT - self.radius:
            self.y = HEIGHT - self.radius
    
    def flap(self):
        global bird_movement
        bird_movement = self.flap_power

class Pipe:
    def __init__(self):
        self.gap = pipe_gap
        self.width = pipe_width
        self.x = WIDTH
        self.top_height = random.randint(HEIGHT//6, HEIGHT - HEIGHT//3 - self.gap)
        self.bottom_y = self.top_height + self.gap
        self.speed = max(3, WIDTH // 200)
        self.passed = False
    
    def draw(self):
        # Pipa atas (terbalik)
        pygame.draw.rect(screen, BLACK, (self.x, 0, self.width, self.top_height))
        # Pipa bawah
        pygame.draw.rect(screen, GREEN, (self.x, self.bottom_y, self.width, HEIGHT - self.bottom_y))
        
        # Tutup pipa (agar terlihat 3D)
        pygame.draw.rect(screen, (60, 140, 60), (self.x - 3, self.top_height - 20, self.width + 6, 20))
        pygame.draw.rect(screen, (60, 140, 60), (self.x - 3, self.bottom_y, self.width + 6, 20))
    
    def update(self):
        self.x -= self.speed
    
    def collide(self, bird):
        # Deteksi tabrakan dengan pipa
        bird_rect = pygame.Rect(bird.x - bird.radius, bird.y - bird.radius, bird.radius * 2, bird.radius * 2)
        top_pipe = pygame.Rect(self.x, 0, self.width, self.top_height)
        bottom_pipe = pygame.Rect(self.x, self.bottom_y, self.width, HEIGHT - self.bottom_y)
        
        return bird_rect.colliderect(top_pipe) or bird_rect.colliderect(bottom_pipe)

# Buat objek burung
bird = Bird()

# List pipa
pipes = []
SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, 1500)  # Setiap 1.5 detik

# PERBAIKAN: Tombol virtual yang lebih besar dan jelas
flap_button_size = min(500, HEIGHT//1)  # Lebih besar dari sebelumny
flap_button = pygame.Rect(
    WIDTH - flap_button_size - 30,  # Posisi kanan dengan margin lebih besar
    HEIGHT - flap_button_size - 50,  # Posisi bawah dengan margin lebih besar
    flap_button_size, 
    flap_button_size
)

start_button_width = min(450, WIDTH*0.8)  # Lebih lebar
start_button_height = min(100, HEIGHT//10)  # Lebih tinggi
start_button = pygame.Rect(
    WIDTH//2 - start_button_width//2, 
    HEIGHT//2 + HEIGHT//8,  # Posisi lebih rendah
    start_button_width, 
    start_button_height
)

# Fungsi untuk membuat pipa baru
def create_pipe():
    pipes.append(Pipe())

# PERBAIKAN: Fungsi untuk menggambar tombol dengan lebih jelas
def draw_button(rect, text, color):
    # Gambar background tombol
    pygame.draw.rect(screen, color, rect, border_radius=int(rect.height/4))
    
    # Gambar outline yang lebih tebal dan kontras
    pygame.draw.rect(screen, (0, 0, 0), rect, 5, border_radius=int(rect.height/4))
    
    # Gambar efek 3D sederhana
    pygame.draw.rect(screen, (min(255, color[0]+40), min(255, color[1]+40), min(255, color[2]+40)), 
                   (rect.x, rect.y, rect.width, rect.height//3), 
                   border_radius=int(rect.height/4))
    
    # Teks dengan shadow untuk kontras
    text_surf = font.render(text, True, (0, 0, 0))
    text_rect = text_surf.get_rect(center=rect.center)
    
    # Shadow teks
    shadow_surf = font.render(text, True, (100, 100, 100))
    shadow_rect = shadow_surf.get_rect(center=(rect.centerx+2, rect.centery+2))
    screen.blit(shadow_surf, shadow_rect)
    
    # Teks utama
    screen.blit(text_surf, text_rect)

# Fungsi untuk gambar awan
def draw_cloud(x, y, size):
    radius = int(size * 0.9)
    pygame.draw.circle(screen, WHITE, (x, y), radius)
    pygame.draw.circle(screen, WHITE, (x + radius, y - radius//2), radius//1.5)
    pygame.draw.circle(screen, WHITE, (x - radius, y - radius//2), radius//1.5)
    pygame.draw.circle(screen, WHITE, (x + radius//2, y + radius//3), radius//1.8)
    pygame.draw.circle(screen, WHITE, (x - radius//2, y + radius//3), radius//1.8)

# PERBAIKAN: Tambahkan fungsi untuk menggambar tombol FLAP dengan ikon
def draw_flap_button(rect):
    # Background tombol
    pygame.draw.rect(screen, (100, 255, 100), rect, border_radius=int(rect.height/2))
    pygame.draw.rect(screen, (0, 0, 0), rect, 5, border_radius=int(rect.height/2))
    
    # Gambar ikon sayap
    center_x = rect.centerx
    center_y = rect.centery
    
    # Gambar sayap
    points = [
        (center_x - rect.width//3, center_y),
        (center_x, center_y - rect.height//3),
        (center_x + rect.width//3, center_y),
        (center_x, center_y + rect.height//3)
    ]
    pygame.draw.polygon(screen, (0, 100, 0), points)
    pygame.draw.polygon(screen, (0, 0, 0), points, 2)
    
    # Teks "FLAP"
    text_surf = font.render("FLAP", True, (0, 0, 0))
    text_rect = text_surf.get_rect(center=(center_x, center_y + rect.height//20))
    screen.blit(text_surf, text_rect)

# Game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Deteksi sentuhan/jepret
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Jika tombol FLAP disentuh
            if flap_button.collidepoint(mouse_pos) and game_active:
                bird.flap()
            
            # Jika tombol START disentuh
            if start_button.collidepoint(mouse_pos) and not game_active:
                game_active = True
                bird.y = HEIGHT // 2
                bird_movement = 1
                pipes.clear()
                score = 0
        
        # Event untuk membuat pipa baru
        if event.type == SPAWNPIPE and game_active:
            create_pipe()
    
    # Background
    screen.fill(SKY_BLUE)
    
    # Gambar awan (bergerak)
    cloud_speed = pygame.time.get_ticks() // 100
    draw_cloud((cloud_speed) % (WIDTH + 200) - 100, HEIGHT//6, HEIGHT//10)
    draw_cloud((cloud_speed + 400) % (WIDTH + 300) - 150, HEIGHT//4, HEIGHT//12)
    draw_cloud((cloud_speed + 700) % (WIDTH + 250) - 100, HEIGHT//3, HEIGHT//15)
    
    if game_active:
      
        # Update dan gambar burung
        bird.update()
        bird.draw()
        
        # Update dan gambar pipa
        for pipe in pipes[:]:
            pipe.update()
            pipe.draw()
            
            # Deteksi jika burung melewati pipa
            if not pipe.passed and pipe.x + pipe.width < bird.x:
                pipe.passed = True
                score += 1
            
            # Hapus pipa yang sudah lewat
            if pipe.x + pipe.width < 0:
                pipes.remove(pipe)
            
            # Deteksi tabrakan
            if pipe.collide(bird):
                game_active = False
                high_score = max(score, high_score)
        
        # Deteksi jatuh ke tanah
        if bird.y >= HEIGHT - bird.radius - 20:  # 30 adalah tinggi tanah
            game_active = False
            high_score = max(score, high_score)
        
        # PERBAIKAN: Gambar tombol FLAP dengan ikon khusus
        draw_flap_button(flap_button)
        
        # Gambar skor
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (20, 20))
    else:
        # Gambar judul
        title = big_font.render("GAME LAKNAD", True, BLACK)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//6))
        
        # Gambar burung di tengah
        pygame.draw.circle(screen, YELLOW, (WIDTH//2, HEIGHT//2 - HEIGHT//10), bird_radius*1.5)
        
        # Gambar skor tertinggi
        high_score_text = font.render(f"High Score: {high_score}", True, BLACK)
        screen.blit(high_score_text, (WIDTH//2 - high_score_text.get_width()//2, HEIGHT//2))
        
        # Gambar tombol start
        draw_button(start_button, "START GAME", (100, 255, 100))
    
    # Gambar tanah
    pygame.draw.rect(screen, GREEN, (0, HEIGHT - 30, WIDTH, 30))
    # Gambar rumput di atas tanah
    pygame.draw.rect(screen, (50, 50, 50), (0, HEIGHT - 100, WIDTH, 10))
    
     
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()