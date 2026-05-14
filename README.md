# Wayfire Dotfiles

<div align="center">

![Arch Linux](https://img.shields.io/badge/Arch_Linux-1793D1?style=for-the-badge&logo=arch-linux&logoColor=white)
![Wayland](https://img.shields.io/badge/Wayland-Compositor-2F80ED?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

*A minimalist, grey-themed configuration for Wayfire on Arch Linux.*

</div>

## ✨ Features
- **Waybar:** Dual-bar setup (Top status + Bottom dock) with a custom grey theme (`#383c4a`).
- **Rofi:** Custom `sleek-dark` launcher and power menu with matching colors.
- **Notifications:** Integrated with `swaync` for a clean, modern look.
- **Wallpaper:** Managed by `swaybg`.
- **Screenshots:** Automated via `grim` and `slurp` with notifications.

## 📂 Structure

.config/
├── wayfire.ini        # Main Wayfire configuration
├── waybar1/           # Waybar configs, styles, and scripts
│   ├── config-wayfire # Top bar configuration
│   ├── config-bottom  # Bottom dock configuration
│   ├── style.css      # Main grey theme
│   └── scripts/       # Weather and player scripts
└── rofi/              # Rofi themes (powermenu, confirm)


## ⚙️ Installation

1. **Clone the repo:**
   ```bash
   git clone https://codeberg.org/WgpArch/wayfire.git ~/.dotfiles/wayfire
