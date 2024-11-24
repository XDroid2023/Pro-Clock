import customtkinter as ctk
from time import strftime
from datetime import datetime
import pyttsx3
import threading
import platform
from daily_messages import DAILY_MESSAGES
import pygame
import os
import random
import math
from tkinter import Canvas

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.velocity = random.uniform(2, 5)
        self.angle = random.uniform(0, 2 * math.pi)
        self.dx = math.cos(self.angle) * self.velocity
        self.dy = math.sin(self.angle) * self.velocity
        self.lifetime = random.randint(20, 40)
        self.alpha = 1.0
        
    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.dy += 0.1  # gravity
        self.lifetime -= 1
        self.alpha = max(0, self.alpha - 0.02)
        return self.lifetime > 0

class Firework:
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.particles = []
        self.colors = ["#ff0000", "#00ff00", "#0000ff", "#ffff00", "#ff00ff", "#00ffff"]
        self.create_particles()
        
    def create_particles(self):
        color = random.choice(self.colors)
        for _ in range(30):
            self.particles.append(Particle(self.x, self.y, color))
    
    def update(self):
        active_particles = []
        for particle in self.particles:
            if particle.update():
                active_particles.append(particle)
        self.particles = active_particles
        return len(self.particles) > 0

class ClockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Clock")
        
        # Configure the window and theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        
        # Initialize pygame for tick sounds
        pygame.mixer.init()
        self.tick_sound = None
        self.load_tick_sound()
        
        # Initialize text-to-speech engine with error handling
        try:
            self.engine = pyttsx3.init()
            if platform.system() == 'Darwin':  # macOS
                voices = self.engine.getProperty('voices')
                if voices:
                    self.engine.setProperty('voice', voices[0].id)
            self.engine.setProperty('rate', 150)
            self.tts_available = True
        except Exception as e:
            print(f"Warning: Text-to-speech initialization failed: {e}")
            self.tts_available = False
        
        # Create main frame with gradient background
        self.main_frame = ctk.CTkFrame(root, fg_color="#1a1a1a")
        self.main_frame.pack(fill="both", expand=True)
        
        # Create fireworks canvas
        self.canvas = Canvas(self.main_frame, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=30, pady=15)
        self.canvas.configure(height=150)  # Set fixed height for fireworks
        
        # Initialize fireworks list
        self.fireworks = []
        self.firework_intensity = 1  # Normal intensity
        
        # Create time section frame
        self.time_frame = ctk.CTkFrame(self.main_frame, fg_color="#252525")
        self.time_frame.pack(fill="x", padx=30, pady=(30, 15))
        
        # Create time label with shadow effect
        self.time_label = ctk.CTkLabel(
            self.time_frame,
            text="",
            font=("SF Pro Display", 80, "bold"),
            text_color="#4a9eff"
        )
        self.time_label.pack(pady=20)
        
        # Create date frame
        self.date_frame = ctk.CTkFrame(self.main_frame, fg_color="#252525")
        self.date_frame.pack(fill="x", padx=30, pady=15)
        
        self.date_label = ctk.CTkLabel(
            self.date_frame,
            text="",
            font=("SF Pro Display", 24),
            text_color="#ffffff"
        )
        self.date_label.pack(pady=15)
        
        # Create countdown frame with glass effect
        self.countdown_frame = ctk.CTkFrame(self.main_frame, fg_color="#2d2d2d")
        self.countdown_frame.pack(fill="x", padx=30, pady=15)
        
        countdown_title = ctk.CTkLabel(
            self.countdown_frame,
            text="NEW YEAR COUNTDOWN",
            font=("SF Pro Display", 16, "bold"),
            text_color="#4CAF50"
        )
        countdown_title.pack(pady=(15, 5))
        
        self.countdown_label = ctk.CTkLabel(
            self.countdown_frame,
            text="",
            font=("SF Pro Display", 28, "bold"),
            text_color="#4CAF50"
        )
        self.countdown_label.pack(pady=(5, 15))
        
        # Create message frame
        self.message_frame = ctk.CTkFrame(self.main_frame, fg_color="#252525")
        self.message_frame.pack(fill="x", padx=30, pady=15)
        
        message_title = ctk.CTkLabel(
            self.message_frame,
            text="TODAY'S INSPIRATION",
            font=("SF Pro Display", 16, "bold"),
            text_color="#e5c07b"
        )
        message_title.pack(pady=(15, 5))
        
        self.greeting_label = ctk.CTkLabel(
            self.message_frame,
            text=self.get_daily_message(),
            font=("SF Pro Display", 18),
            text_color="#e5c07b",
            wraplength=500
        )
        self.greeting_label.pack(pady=(5, 15))
        
        # Create settings frame
        self.settings_frame = ctk.CTkFrame(self.main_frame, fg_color="#252525")
        self.settings_frame.pack(fill="x", padx=30, pady=(15, 30))
        
        # Create voice announcement switch with improved styling
        self.voice_enabled = ctk.CTkSwitch(
            self.settings_frame,
            text="Hourly Announcements",
            command=self.toggle_voice,
            font=("SF Pro Display", 16),
            progress_color="#4a9eff",
            button_color="#4a9eff",
            button_hover_color="#2d7dd2"
        )
        self.voice_enabled.pack(side="left", padx=20, pady=15)
        
        # Create tick sound switch
        self.tick_enabled = ctk.CTkSwitch(
            self.settings_frame,
            text="Tick Sound",
            command=self.toggle_tick,
            font=("SF Pro Display", 16),
            progress_color="#4a9eff",
            button_color="#4a9eff",
            button_hover_color="#2d7dd2"
        )
        self.tick_enabled.pack(side="right", padx=20, pady=15)
        
        # Initialize variables
        self.last_hour = -1
        self.voice_on = True
        self.tick_on = True
        self.voice_enabled.select()
        self.tick_enabled.select()
        
        # Start the clock update
        self.update_clock()
        self.update_fireworks()
    
    def load_tick_sound(self):
        try:
            sound_path = os.path.join("sounds", "tick.wav")
            if not os.path.exists(sound_path):
                print("Warning: Tick sound file not found")
                return
            self.tick_sound = pygame.mixer.Sound(sound_path)
            self.tick_sound.set_volume(0.3)  # Set volume to 30%
        except Exception as e:
            print(f"Warning: Could not load tick sound: {e}")
            self.tick_sound = None
    
    def toggle_tick(self):
        self.tick_on = self.tick_enabled.get()
    
    def play_tick(self):
        if self.tick_on and self.tick_sound:
            try:
                self.tick_sound.play()
            except Exception as e:
                print(f"Warning: Could not play tick sound: {e}")
    
    def get_daily_message(self):
        day_of_year = datetime.now().timetuple().tm_yday
        message_index = min(day_of_year - 1, len(DAILY_MESSAGES) - 1)
        return DAILY_MESSAGES[message_index]
    
    def toggle_voice(self):
        self.voice_on = self.voice_enabled.get()
    
    def speak_time(self, hour):
        if not self.voice_on or not self.tts_available:
            return
        
        # Format hour for natural speech
        if hour == 0:
            hour = 12
            period = "AM"
        elif hour < 12:
            period = "AM"
        elif hour == 12:
            period = "PM"
        else:
            hour -= 12
            period = "PM"
            
        message = f"It's {hour} o'clock {period}"
        
        def speak():
            try:
                self.engine.say(message)
                self.engine.runAndWait()
            except Exception as e:
                print(f"Warning: Text-to-speech failed: {e}")
        
        # Run speech in a separate thread to avoid blocking the UI
        threading.Thread(target=speak, daemon=True).start()
    
    def update_fireworks(self):
        # Clear the canvas
        self.canvas.delete("all")
        
        # Add new fireworks based on intensity
        if random.random() < 0.05 * self.firework_intensity:
            x = random.randint(50, self.canvas.winfo_width() - 50)
            y = random.randint(50, self.canvas.winfo_height() - 50)
            self.fireworks.append(Firework(self.canvas, x, y))
        
        # Update existing fireworks
        active_fireworks = []
        for firework in self.fireworks:
            if firework.update():
                active_fireworks.append(firework)
                # Draw particles
                for particle in firework.particles:
                    size = 2
                    alpha = int(particle.alpha * 255)
                    color = self.adjust_color_alpha(particle.color, alpha)
                    self.canvas.create_oval(
                        particle.x - size, particle.y - size,
                        particle.x + size, particle.y + size,
                        fill=color, outline=color
                    )
        self.fireworks = active_fireworks
        
        # Schedule next update
        self.root.after(16, self.update_fireworks)  # ~60 FPS
    
    def adjust_color_alpha(self, color, alpha):
        # Convert hex color to RGB with alpha
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def update_clock(self):
        # Update time
        time_string = strftime('%H:%M:%S')
        self.time_label.configure(text=time_string)
        
        # Update date
        date_string = strftime('%B %d, %Y')
        self.date_label.configure(text=date_string)
        
        # Update New Year countdown
        now = datetime.now()
        next_year = now.year + 1
        new_year = datetime(next_year, 1, 1)
        time_left = new_year - now
        
        days = time_left.days
        hours = time_left.seconds // 3600
        minutes = (time_left.seconds % 3600) // 60
        seconds = time_left.seconds % 60
        
        countdown_text = f"New Year {next_year} in: {days}d {hours}h {minutes}m {seconds}s"
        self.countdown_label.configure(text=countdown_text)
        
        # Adjust firework intensity based on countdown
        if days == 0:
            if hours == 0:
                if minutes < 5:
                    self.firework_intensity = 5  # Very intense in last 5 minutes
                else:
                    self.firework_intensity = 3  # More intense on last day
            else:
                self.firework_intensity = 2  # Intense on last day
        else:
            self.firework_intensity = 1  # Normal intensity
        
        # Check for hour change and speak if needed
        current_hour = int(strftime('%H'))
        if current_hour != self.last_hour:
            self.last_hour = current_hour
            if time_string.endswith('00:00'):  # Exactly on the hour
                self.speak_time(current_hour)
                # Update daily message at midnight
                if current_hour == 0:
                    self.greeting_label.configure(text=self.get_daily_message())
        
        # Play tick sound
        self.play_tick()
        
        # Schedule the next update
        self.root.after(1000, self.update_clock)

def main():
    root = ctk.CTk()
    app = ClockApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
