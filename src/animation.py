# -*- coding: utf-8 -*-
"""
Animation recorder for the VNS search process.

Records improvement frames and exports them as an MP4 video using FFmpeg.
Only improvement steps are recorded to keep file sizes manageable.
"""

from copy import deepcopy
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter

from config import DEFAULT_FPS, DEFAULT_ANIMATION_FILENAME


class VNSAnimationRecorder:
    """
    Records VNS improvement frames and exports an animated video.

    Only frames where the objective cost strictly improves are stored
    (plus the initial solution), so the video shows the progression
    of solution quality over time.
    """

    def __init__(self, coords, initial_solution, initial_cost):
        self.coords = coords
        self.frames = []
        self.add_frame(initial_solution, initial_cost, "Initial Solution", "", force=True)

    def add_frame(self, solution, cost, operation, details, force=False):
        """
        Add a frame to the recording.

        A frame is only stored if it represents a cost improvement over the
        last stored frame, or if force=True (e.g. for the initial solution).
        """
        if force or not self.frames or cost < self.frames[-1]['cost'] - 1e-6:
            self.frames.append({
                'solution': deepcopy(solution),
                'cost': cost,
                'operation': operation,
                'details': details,
            })

    def create_animation(self, filename=DEFAULT_ANIMATION_FILENAME, fps=DEFAULT_FPS):
        """
        Render and save the animation as an MP4 video.

        Parameters
        ----------
        filename : output file path
        fps      : frames per second

        Returns
        -------
        FuncAnimation object (keep a reference to prevent garbage collection).
        """
        n_frames = len(self.frames)
        print(f"\nCreating animation with {n_frames} improvement frames...")

        if n_frames <= 1:
            print("Not enough frames to animate (need at least 2).")
            return None

        fig, ax = plt.subplots(figsize=(14, 10))
        colors = plt.cm.tab20.colors

        def update(frame_idx):
            ax.clear()
            frame = self.frames[frame_idx]
            solution = frame['solution']
            cost = frame['cost']
            operation = frame['operation']
            details = frame['details']

            # Depot
            ax.scatter(
                self.coords[0][0], self.coords[0][1],
                c="red", marker="s", s=400, label="Depot",
                zorder=3, edgecolors='black', linewidths=3,
            )

            # Customers
            for i in range(1, len(self.coords)):
                ax.scatter(
                    self.coords[i][0], self.coords[i][1],
                    c="lightblue", s=100, zorder=2,
                    edgecolors='black', linewidths=1.5,
                )

            # Routes
            for i, route in enumerate(solution):
                xs = [self.coords[c][0] for c in route]
                ys = [self.coords[c][1] for c in route]
                ax.plot(xs, ys, color=colors[i % len(colors)],
                        linewidth=3, alpha=0.7)

            title = (
                f"VNS for CVRP — Improvement {frame_idx + 1}/{n_frames}\n"
                f"Operation: {operation}\n"
                f"Cost: {cost:.2f} | Routes: {len(solution)}"
            )
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

            if details:
                ax.text(
                    0.02, 0.98, details, transform=ax.transAxes,
                    fontsize=10, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8),
                )

            ax.set_xlabel("X coordinate", fontsize=12)
            ax.set_ylabel("Y coordinate", fontsize=12)
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.axis('equal')

        anim = FuncAnimation(fig, update, frames=n_frames,
                             interval=1000 / fps, repeat=True)

        try:
            writer = FFMpegWriter(fps=fps, bitrate=1800)
            anim.save(filename, writer=writer)
            print(f"✓ Animation saved as {filename}")
            plt.close(fig)
        except Exception as e:
            print(f"✗ Could not save video (ffmpeg may not be installed): {e}")
            print("  Displaying animation instead...")
            plt.show()

        return anim
