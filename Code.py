import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button, Slider
from collections import deque

class MemoryVisualizer:
    def __init__(self):
        # Initialize simulation parameters
        self.total_frames = 4
        self.page_size = 1
        self.algorithm = "FIFO"
        self.page_sequence = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
        self.current_step = 0
        self.page_faults = 0
        
        # Data structures
        self.physical_memory = []
        self.page_table = {}
        self.access_history = deque(maxlen=100)
        
        # Create figure
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8))
        plt.subplots_adjust(bottom=0.3)
        
        # Create UI controls
        self.create_controls()
        
        # Initial draw
        self.update_visualization()
        
    def create_controls(self):
        # Algorithm selector
        ax_alg = plt.axes([0.3, 0.15, 0.4, 0.05])
        self.alg_btn = Button(ax_alg, 'Algorithm: FIFO')
        self.alg_btn.on_clicked(self.toggle_algorithm)
        
        # Step controls
        ax_prev = plt.axes([0.3, 0.1, 0.15, 0.04])
        ax_next = plt.axes([0.55, 0.1, 0.15, 0.04])
        self.prev_btn = Button(ax_prev, 'Previous')
        self.next_btn = Button(ax_next, 'Next')
        self.prev_btn.on_clicked(self.prev_step)
        self.next_btn.on_clicked(self.next_step)
        
        # Sequence input
        ax_seq = plt.axes([0.1, 0.02, 0.8, 0.05])
        self.seq_slider = Slider(ax_seq, 'Sequence Step', 0, len(self.page_sequence)-1, 
                                valinit=0, valstep=1)
        self.seq_slider.on_changed(self.set_step)
    
    def toggle_algorithm(self, event):
        self.algorithm = "LRU" if self.algorithm == "FIFO" else "FIFO"
        self.alg_btn.label.set_text(f'Algorithm: {self.algorithm}')
        self.reset_simulation()
        self.update_visualization()
    
    def reset_simulation(self):
        self.physical_memory = []
        self.page_table = {}
        self.access_history = deque(maxlen=100)
        self.page_faults = 0
        self.current_step = 0
    
    def prev_step(self, event):
        if self.current_step > 0:
            self.current_step -= 1
            self.seq_slider.set_val(self.current_step)
    
    def next_step(self, event):
        if self.current_step < len(self.page_sequence)-1:
            self.current_step += 1
            self.seq_slider.set_val(self.current_step)
    
    def set_step(self, val):
        self.current_step = int(val)
        self.update_visualization()
    
    def handle_page_access(self, page_num):
        page_id = f"P{page_num}"
        
        # Check if page is already in memory
        if page_id in self.page_table and self.page_table[page_id]['valid']:
            self.access_history.append(page_id)
            return False  # No page fault
        
        # Page fault occurred
        self.page_faults += 1
        
        if len(self.physical_memory) < self.total_frames:
            # There's free space
            frame = len(self.physical_memory)
            self.physical_memory.append((frame, page_id))
            self.page_table[page_id] = {'frame': frame, 'valid': True}
        else:
            # Need to replace a page
            victim = self.select_victim()
            frame = self.page_table[victim]['frame']
            
            # Update page tables
            self.page_table[victim]['valid'] = False
            self.physical_memory[frame] = (frame, page_id)
            self.page_table[page_id] = {'frame': frame, 'valid': True}
        
        self.access_history.append(page_id)
        return True  # Page fault occurred
    
    def select_victim(self):
        if self.algorithm == "FIFO":
            return self.physical_memory[0][1]  # First-in page
        else:  # LRU
            # Find least recently used page
            lru_page = None
            min_index = float('inf')
            for frame, page_id in self.physical_memory:
                try:
                    last_used = len(self.access_history) - 1 - self.access_history[::-1].index(page_id)
                    if last_used < min_index:
                        min_index = last_used
                        lru_page = page_id
                except ValueError:
                    return page_id  # If page isn't in history, it's the best candidate
            return lru_page
    
    def update_visualization(self):
        # Process all steps up to current
        self.reset_simulation()
        for i in range(self.current_step + 1):
            page_num = self.page_sequence[i]
            self.handle_page_access(page_num)
        
        # Clear axes
        self.ax1.clear()
        self.ax2.clear()
        
        # Draw physical memory
        self.ax1.set_title(f'Physical Memory (Frames: {self.total_frames})')
        for i in range(self.total_frames):
            self.ax1.add_patch(plt.Rectangle((i, 0), 0.8, 0.8, fill=True if i < len(self.physical_memory) else False,
                                           ec='black', lw=2))
            if i < len(self.physical_memory):
                self.ax1.text(i + 0.4, 0.4, self.physical_memory[i][1], ha='center', va='center')
        self.ax1.set_xlim(0, self.total_frames)
        self.ax1.set_ylim(0, 1)
        self.ax1.set_xticks(np.arange(0.4, self.total_frames, 1))
        self.ax1.set_xticklabels(range(self.total_frames))
        self.ax1.set_yticks([])
        
        # Draw access sequence
        self.ax2.set_title(f'Page Access Sequence (Algorithm: {self.algorithm}, Faults: {self.page_faults})')
        for i, page_num in enumerate(self.page_sequence):
            color = 'red' if i <= self.current_step and self.page_sequence[i] == self.page_sequence[self.current_step] else 'blue'
            alpha = 1.0 if i <= self.current_step else 0.3
            self.ax2.add_patch(plt.Rectangle((i, 0), 0.8, 0.8, fill=True, color=color, alpha=alpha))
            self.ax2.text(i + 0.4, 0.4, f'P{page_num}', ha='center', va='center')
        
        self.ax2.set_xlim(0, len(self.page_sequence))
        self.ax2.set_ylim(0, 1)
        self.ax2.set_xticks(np.arange(0.4, len(self.page_sequence), 1))
        self.ax2.set_xticklabels(range(len(self.page_sequence)))
        self.ax2.set_yticks([])
        
        plt.draw()

# Run the visualizer
visualizer = MemoryVisualizer()
plt.show()
